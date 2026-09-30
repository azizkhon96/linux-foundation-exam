#!/usr/bin/env bash
# Imtihon VM'ida talaba (student) muhitlarini bitta buyruq bilan yaratadi:
#   - user(lar) yaratadi
#   - har biriga sodda, o'qish/aytish oson parol generatsiya qiladi
#   - shifrlangan imtihon materialini (dist/) shu userning uyiga joylaydi
#   - SSH orqali kirganda imtihon avtomatik boshlanadigan qilib sozlaydi
#   - oxirida barcha user/parol ro'yxatini chiqaradi va faylga saqlaydi
#
# ISHLATISH:
#   sudo ./provision_students.sh student1 student2 student3
#   sudo ./provision_students.sh -n 5                # student1..student5
#   sudo ./provision_students.sh -n 5 -p talaba       # talaba1..talaba5
#   sudo ./provision_students.sh -n 10 --dist /path/to/dist
#
# Agar 'dist/' ni tuzatib (masalan pyarmor build muammosidan keyin) qayta
# qursangiz, ALLAQACHON YARATILGAN userlarning imtihon materialini
# yangilash uchun --refresh qo'shing (parol/user O'ZGARMAYDI, faqat
# module1-exam/ qayta nusxalanadi, talabaning ~/javoblar va ~/.exam
# holati SAQLANIB QOLADI):
#   sudo ./provision_students.sh --refresh user1 user2
#   sudo ./provision_students.sh --refresh -n 5 -p talaba
#
# Har birini QO'LDA sanashning hojati yo'q -- /home/*/module1-exam mavjud
# BARCHA userlarni (nechta bo'lishidan qat'iy nazar) birdaniga yangilash:
#   sudo ./provision_students.sh --refresh-all
#
# Talab qilinadi: root (sudo) huquqi.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
PREFIX="student"
COUNT=0
USERNAMES=()
REFRESH=0
REFRESH_ALL=0

usage() {
    grep '^#' "$0" | sed 's/^#//' | sed '1,2d'
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n) COUNT="$2"; shift 2 ;;
        -p|--prefix) PREFIX="$2"; shift 2 ;;
        --dist) DIST_DIR="$2"; shift 2 ;;
        --refresh) REFRESH=1; shift ;;
        --refresh-all) REFRESH=1; REFRESH_ALL=1; shift ;;
        -h|--help) usage ;;
        *) USERNAMES+=("$1"); shift ;;
    esac
done

if [[ "$EUID" -ne 0 ]]; then
    echo "Xato: bu skript root (sudo) huquqi bilan ishga tushirilishi kerak." >&2
    echo "Masalan: sudo $0 $*" >&2
    exit 1
fi

# --refresh-all: qo'lda sanashning hojati yo'q -- /home/*/module1-exam
# papkasiga ega BARCHA userlarni o'zi topib, USERNAMES ro'yxatini to'ldiradi
if [[ "$REFRESH_ALL" -eq 1 ]]; then
    for d in /home/*/module1-exam; do
        [[ -d "$d" ]] || continue
        USERNAMES+=("$(basename "$(dirname "$d")")")
    done
    if [[ ${#USERNAMES[@]} -eq 0 ]]; then
        echo "Xato: /home/*/module1-exam ga ega hech qanday user topilmadi." >&2
        exit 1
    fi
    echo "Topilgan userlar (${#USERNAMES[@]} ta): ${USERNAMES[*]}"
fi

# -n berilgan bo'lsa, avtomatik nomlar generatsiya qilamiz (mavjud
# userlar bilan to'qnashmasligi uchun keyingi bo'sh raqamdan boshlanadi)
if [[ "$COUNT" -gt 0 ]]; then
    i=1
    added=0
    while [[ $added -lt $COUNT ]]; do
        candidate="${PREFIX}${i}"
        if ! id "$candidate" &>/dev/null; then
            USERNAMES+=("$candidate")
            added=$((added + 1))
        fi
        i=$((i + 1))
    done
fi

if [[ ${#USERNAMES[@]} -eq 0 ]]; then
    echo "Xato: kamida bitta user nomi, -n <son> yoki --refresh-all ko'rsating." >&2
    usage
fi

# dist/ topilmasa, avtomatik build qilishga urinamiz
if [[ ! -d "$DIST_DIR" ]]; then
    echo "Ogohlantirish: '$DIST_DIR' topilmadi. './build.sh' orqali qurishga urinaman..."
    if [[ -x "$SCRIPT_DIR/build.sh" ]]; then
        "$SCRIPT_DIR/build.sh"
    else
        echo "Xato: build.sh topilmadi." >&2
        exit 1
    fi
fi

# --- O'Z-O'ZINI SINASH (smoke test) ---
# Hech qaysi userga (yangi ham, --refresh ham) BUZUQ dist hech qachon
# nusxalanmasligi uchun -- avval bir marta, haqiqatan ishga tushirib
# tekshiramiz. Muammo topilsa, butun skript to'xtaydi va hech kimga
# tegmaydi (allaqachon buzuq nusxalangan userlar bo'lsa ham, ular
# o'zgarishsiz qoladi -- kamida yangi buzuq nusxalar qo'shilmaydi).
echo "'$DIST_DIR/module1' sinovdan o'tkazilmoqda..."
SMOKE_HOME="$(mktemp -d)"
if EXAM_NO_EXEC=1 HOME="$SMOKE_HOME" python3 "$DIST_DIR/module1" >"$SMOKE_HOME/out.log" 2>&1; then
    SMOKE_OK=1
else
    SMOKE_OK=0
fi
if [[ -f "$SMOKE_HOME/.exam/module1/state.json" ]]; then
    SMOKE_PID="$(python3 -c "import json;print(json.load(open('$SMOKE_HOME/.exam/module1/state.json')).get('task20_pid',''))" 2>/dev/null || true)"
    [[ -n "$SMOKE_PID" ]] && kill -9 "$SMOKE_PID" 2>/dev/null || true
fi
if [[ "$SMOKE_OK" -ne 1 ]]; then
    echo "XATO: '$DIST_DIR/module1' ishga tushmadi -- hech qanday userga nusxalanmaydi!" >&2
    echo "--- xato matni ---" >&2
    cat "$SMOKE_HOME/out.log" >&2
    echo "------------------" >&2
    rm -rf "$SMOKE_HOME"
    echo >&2
    echo "Tuzatish: shu VM'da 'rm -rf dist .buildvenv && ./build.sh' ni qayta ishga tushiring," >&2
    echo "keyin shu provision_students.sh buyrug'ini qayta bering." >&2
    exit 1
fi
rm -rf "$SMOKE_HOME"
echo "OK: dist ishlayapti, davom etilmoqda."
echo

# --- Sodda, o'qish/aytish oson parol generatori ---
WORDS=(olma armut anor uzum tut behi nok gilos shaftoli
       osmon quyosh yulduz bulut yomgir shamol tog dengiz
       daryo kol qum tosh gul bogcha bahor yoz kuz qish
       kitob qalam maktab bola sher qoplon burgut lochin)

gen_password() {
    local w1 w2 digits
    w1="${WORDS[$RANDOM % ${#WORDS[@]}]}"
    w2="${WORDS[$RANDOM % ${#WORDS[@]}]}"
    digits=$((10 + RANDOM % 90))
    # Birinchi harfni katta qilamiz -- o'qishga qulay, murakkablikka ozgina yordam
    w1="$(tr '[:lower:]' '[:upper:]' <<<"${w1:0:1}")${w1:1}"
    echo "${w1}${w2}${digits}"
}

# exam materialini (dist/) berilgan userning uyiga joylaydi va
# .bash_profile orqali avtomatik boshlashni sozlaydi. Parolga tegmaydi --
# yangi user yaratishda ham, mavjud userni --refresh qilishda ham ishlatiladi.
install_materials() {
    local user="$1" home exam_dir profile
    home="/home/$user"
    exam_dir="$home/module1-exam"

    rm -rf "$exam_dir"
    cp -r "$DIST_DIR" "$exam_dir"
    chown -R root:root "$exam_dir"
    chmod -R go+rX "$exam_dir"
    chmod 755 "$exam_dir/module1"

    # SSH orqali kirganda imtihon avtomatik boshlanadi (bir marta, login shell'da)
    profile="$home/.bash_profile"
    if ! grep -q "MODULE1_STARTED" "$profile" 2>/dev/null; then
        cat >> "$profile" <<EOF

# --- imtihon: avtomatik boshlash ---
if [ -z "\${MODULE1_STARTED:-}" ]; then
    export MODULE1_STARTED=1
    exec "$exam_dir/module1"
fi
EOF
        chown "$user:$user" "$profile"
    fi
}

TS="$(date +%Y%m%d_%H%M%S)"
CRED_FILE="$SCRIPT_DIR/credentials_${TS}.txt"
: > "$CRED_FILE"
chmod 600 "$CRED_FILE"

printf "%-16s %-16s %s\n" "USER" "PAROL" "HOLAT"
printf "%-16s %-16s %s\n" "----" "-----" "-----"

declare -A SEEN_PASSWORDS

for user in "${USERNAMES[@]}"; do
    if id "$user" &>/dev/null; then
        if [[ "$REFRESH" -eq 1 ]]; then
            install_materials "$user"
            printf "%-16s %-16s %s\n" "$user" "-" "materiallar yangilandi (parol o'zgarmadi)"
        else
            printf "%-16s %-16s %s\n" "$user" "-" "MAVJUD, o'tkazib yuborildi (--refresh bilan yangilash mumkin)"
        fi
        continue
    fi

    if [[ "$REFRESH" -eq 1 ]]; then
        printf "%-16s %-16s %s\n" "$user" "-" "MAVJUD EMAS, --refresh uni yaratmaydi"
        continue
    fi

    password="$(gen_password)"
    while [[ -n "${SEEN_PASSWORDS[$password]:-}" ]]; do
        password="$(gen_password)"
    done
    SEEN_PASSWORDS["$password"]=1

    useradd -m -s /bin/bash "$user"
    echo "${user}:${password}" | chpasswd
    usermod -aG sudo "$user"

    install_materials "$user"

    echo "${user}:${password}" >> "$CRED_FILE"
    printf "%-16s %-16s %s\n" "$user" "$password" "yaratildi"
done

echo
if [[ -s "$CRED_FILE" ]]; then
    echo "Parollar ro'yxati saqlandi: $CRED_FILE (faqat root o'qiy oladi)"
else
    rm -f "$CRED_FILE"
fi
