#!/usr/bin/env bash
# Talaba konteynerini tekshirish uchun qisqa yordamchi
# (uzun 'incus exec ... -- bash -c "HOME=... python3 ... --grade"' o'rniga).
#
# ISHLATISH:
#   sudo ./grade.sh sinov1        -- bitta talabani (LIVE) tekshirish, batafsil
#   sudo ./grade.sh --all         -- barcha konteynerlarni tekshirish (qisqa xulosa)
#
# Talab qilinadi: root (sudo) huquqi (incus buyruqlari uchun).

set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
    echo "Xato: bu skript root (sudo) huquqi bilan ishga tushirilishi kerak." >&2
    echo "Masalan: sudo $0 $*" >&2
    exit 1
fi

grade_one() {
    local cname="$1"
    incus exec "$cname" -- bash -c "HOME=/home/$cname python3 /opt/linux-foundation-exam/dist/module1 --grade"
}

if [[ "${1:-}" == "--all" ]]; then
    found=0
    while IFS= read -r c; do
        [[ -z "$c" || "$c" == examtpl-* ]] && continue
        found=1
        echo "================ $c ================"
        # Bitta talabaning natijasi olinmasa ham (masalan hali imtihonni
        # boshlamagan bo'lsa, module1 --grade xato kod bilan chiqadi),
        # 'set -e'+'pipefail' butun ro'yxatni to'xtatib qo'ymasligi kerak.
        grade_one "$c" 2>&1 | tail -4 || true
        echo
    done < <(incus list --format csv -c n 2>/dev/null)
    if [[ "$found" -eq 0 ]]; then
        echo "Hech qanday talaba konteyneri topilmadi." >&2
        exit 1
    fi
    exit 0
fi

if [[ -z "${1:-}" ]]; then
    echo "Ishlatish:" >&2
    echo "  sudo ./grade.sh <konteyner-nomi>   -- bitta talabani batafsil tekshirish" >&2
    echo "  sudo ./grade.sh --all              -- barchasini qisqa xulosa bilan" >&2
    exit 1
fi

cname="$1"
if ! incus info "$cname" >/dev/null 2>&1; then
    echo "Xato: '$cname' nomli konteyner topilmadi." >&2
    echo "Mavjud konteynerlar:" >&2
    incus list --format csv -c n >&2
    exit 1
fi

grade_one "$cname"
