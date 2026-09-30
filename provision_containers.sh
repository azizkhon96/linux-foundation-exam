#!/usr/bin/env bash
# Har bir talaba uchun ALOHIDA, to'liq izolyatsiyalangan LXD/incus
# konteyner (systemd, cron, apt bilan -- kichik virtual mashina kabi)
# yaratadi. Bitta VM ichida bir nechta Linux user (provision_students.sh)
# o'rniga -- bu /tmp, /etc/passwd, o'rnatilgan paketlar, crontab kabi
# global narsalarning talabalar orasida ARALASHIB ketishining oldini oladi.
#
# ISHLATISH:
#   sudo ./provision_containers.sh -n 15              # student1..student15
#   sudo ./provision_containers.sh ali vali guli       # aniq nomlar bilan
#   sudo ./provision_containers.sh -n 5 -p talaba      # talaba1..talaba5
#
# Materiallarni yangilagandan keyin (savol qo'shdingiz, bug tuzatdingiz):
#   sudo ./provision_containers.sh --refresh-all       # BARCHA konteynerlar
#   sudo ./provision_containers.sh --refresh user1 user2
#
# Shablon (golden image) ni majburan qayta qurish:
#   sudo ./provision_containers.sh --rebuild-template -n 0
#
# Talab qilinadi: root (sudo) huquqi. incus o'zi topilmasa avtomatik
# o'rnatiladi va ishga tushiriladi (apt install incus + incus admin init).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_ALIAS="examtpl-module1"
BASE_IMAGE="images:ubuntu/24.04"
PREFIX="student"
COUNT=0
USERNAMES=()
REFRESH=0
REFRESH_ALL=0
REBUILD_TEMPLATE=0
PORT_START=2200

usage() {
    grep '^#' "$0" | sed 's/^#//' | sed '1,2d'
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n) COUNT="$2"; shift 2 ;;
        -p|--prefix) PREFIX="$2"; shift 2 ;;
        --refresh) REFRESH=1; shift ;;
        --refresh-all) REFRESH=1; REFRESH_ALL=1; shift ;;
        --rebuild-template) REBUILD_TEMPLATE=1; shift ;;
        --port-start) PORT_START="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) USERNAMES+=("$1"); shift ;;
    esac
done

if [[ "$EUID" -ne 0 ]]; then
    echo "Xato: bu skript root (sudo) huquqi bilan ishga tushirilishi kerak." >&2
    exit 1
fi

# ------------------------------------------------------------------
# 1) incus mavjudligini va ishlayotganini ta'minlash
# ------------------------------------------------------------------
if ! command -v incus >/dev/null 2>&1; then
    echo "incus topilmadi -- o'rnatilmoqda..."
    apt-get update -qq
    apt-get install -y -qq incus
fi

need_init=0
if ! incus list >/dev/null 2>&1; then
    need_init=1
elif ! incus storage list --format csv -c n 2>/dev/null | grep -q .; then
    # `incus list` sozlanmagan holatda ham muvaffaqiyatli (bo'sh ro'yxat)
    # qaytishi mumkin -- haqiqiy belgi: birorta ham storage pool yo'qligi
    # (bunda konteyner yaratish "No root device could be found" bilan
    # muvaffaqiyatsiz tugaydi).
    need_init=1
fi
if [[ "$need_init" -eq 1 ]]; then
    echo "incus hali sozlanmagan -- avtomatik init qilinmoqda..."
    incus admin init --auto
fi

HOST_IP="$(ip -4 -o addr show scope global | awk '{print $4}' | cut -d/ -f1 | head -1)"
HOST_IP="${HOST_IP:-<VM_IP>}"

# ------------------------------------------------------------------
# 2) Shablon (golden image) tayyorligini ta'minlash
# ------------------------------------------------------------------
ensure_template() {
    if incus image list --format csv -c l 2>/dev/null | grep -qx "$TEMPLATE_ALIAS" && [[ "$REBUILD_TEMPLATE" -ne 1 ]]; then
        echo "Shablon '$TEMPLATE_ALIAS' allaqachon mavjud (qayta qurish uchun --rebuild-template)."
        return
    fi

    echo "Shablon tayyorlanmoqda ('$TEMPLATE_ALIAS') -- bir martalik, bir necha daqiqa vaqt oladi..."
    incus image delete "$TEMPLATE_ALIAS" >/dev/null 2>&1 || true
    incus delete -f examtpl-builder >/dev/null 2>&1 || true

    incus launch "$BASE_IMAGE" examtpl-builder
    _wait_ready examtpl-builder

    incus exec examtpl-builder -- bash -c "
        apt-get update -qq
        apt-get install -y -qq openssh-server tree psmisc python3-venv python3-pip >/dev/null
        systemctl enable --now ssh
    "

    incus exec examtpl-builder -- mkdir -p /opt/linux-foundation-exam
    incus file push -r "$SCRIPT_DIR/exam" examtpl-builder/opt/linux-foundation-exam/ 2>&1 | tail -3
    incus file push "$SCRIPT_DIR/module1" "$SCRIPT_DIR/build.sh" \
        examtpl-builder/opt/linux-foundation-exam/ 2>&1 | tail -3
    incus exec examtpl-builder -- chmod +x /opt/linux-foundation-exam/module1 /opt/linux-foundation-exam/build.sh
    incus exec examtpl-builder -- bash -c "
        chmod +x /opt/linux-foundation-exam/build.sh
        cd /opt/linux-foundation-exam
        ./build.sh
        chmod 755 dist/module1
        rm -rf .buildvenv exam module1 build.sh
    "

    incus stop examtpl-builder
    incus publish examtpl-builder --alias "$TEMPLATE_ALIAS" >/dev/null
    incus delete examtpl-builder
    echo "Shablon tayyor: $TEMPLATE_ALIAS"
}

_wait_ready() {
    local name="$1" i=0
    until incus exec "$name" -- true >/dev/null 2>&1; do
        i=$((i + 1))
        if [[ $i -gt 60 ]]; then
            echo "Xato: '$name' konteyner 60s ichida tayyor bo'lmadi." >&2
            exit 1
        fi
        sleep 1
    done
}

_next_free_port() {
    local port="$PORT_START"
    while incus list --format csv -c n 2>/dev/null | while read -r c; do incus config device list "$c" 2>/dev/null; done | grep -q ":$port$" \
        || ss -ltn 2>/dev/null | grep -q ":$port "; do
        port=$((port + 1))
    done
    echo "$port"
}

# ------------------------------------------------------------------
# 3) Talaba konteynerini o'rnatish / yangilash
# ------------------------------------------------------------------
WORDS=(olma armut anor uzum tut behi nok gilos shaftoli
       osmon quyosh yulduz bulut yomgir shamol tog dengiz
       daryo kol qum tosh gul bogcha bahor yoz kuz qish
       kitob qalam maktab bola sher qoplon burgut lochin)

gen_password() {
    local w1 w2 digits
    w1="${WORDS[$RANDOM % ${#WORDS[@]}]}"
    w2="${WORDS[$RANDOM % ${#WORDS[@]}]}"
    digits=$((10 + RANDOM % 90))
    w1="$(tr '[:lower:]' '[:upper:]' <<<"${w1:0:1}")${w1:1}"
    echo "${w1}${w2}${digits}"
}

install_materials() {
    # Konteyner ICHIDAGI /opt/linux-foundation-exam/dist ni shablonning
    # o'zidagi (yoki --refresh paytida qayta qurilgan) dist/ bilan
    # yangilaydi. Talabaning ~/javoblar, ~/.exam holatiga tegmaydi.
    local cname="$1"
    incus file push -r "$DIST_SRC/." "$cname/opt/linux-foundation-exam/dist/" >/dev/null 2>&1 \
        || { incus exec "$cname" -- rm -rf /opt/linux-foundation-exam/dist; \
             incus file push -r "$DIST_SRC" "$cname/opt/linux-foundation-exam/dist" >/dev/null; }
    incus exec "$cname" -- chmod 755 /opt/linux-foundation-exam/dist/module1
}

create_student() {
    local user="$1" port password cname="$1"

    if incus info "$cname" >/dev/null 2>&1; then
        echo "Xato: '$cname' nomli konteyner allaqachon mavjud, o'tkazib yuborildi (--refresh bilan yangilang)." >&2
        return
    fi

    port="$(_next_free_port)"
    password="$(gen_password)"

    incus launch "$TEMPLATE_ALIAS" "$cname" >/dev/null
    _wait_ready "$cname"

    incus exec "$cname" -- bash -c "
        useradd -m -s /bin/bash '$user'
        echo '$user:$password' | chpasswd
        usermod -aG sudo '$user'
        cat >> /home/$user/.bash_profile <<'PROF'

if [ -z \"\${MODULE1_STARTED:-}\" ]; then
    export MODULE1_STARTED=1
    exec /opt/linux-foundation-exam/dist/module1
fi
PROF
        chown $user:$user /home/$user/.bash_profile
    "
    incus config device add "$cname" sshfwd proxy \
        listen=tcp:0.0.0.0:"$port" connect=tcp:127.0.0.1:22 >/dev/null

    echo "$user:$password" >> "$CRED_FILE"
    printf "%-16s %-16s %-8s %s\n" "$user" "$password" "$port" \
        "ssh $user@$HOST_IP -p $port"
}

refresh_student() {
    local cname="$1"
    if ! incus info "$cname" >/dev/null 2>&1; then
        printf "%-16s %s\n" "$cname" "konteyner topilmadi, o'tkazib yuborildi"
        return
    fi
    install_materials "$cname"
    printf "%-16s %s\n" "$cname" "materiallar yangilandi (parol/holat o'zgarmadi)"
}

# ------------------------------------------------------------------
# Asosiy oqim
# ------------------------------------------------------------------
ensure_template

if [[ "$REFRESH_ALL" -eq 1 ]]; then
    USERNAMES=()
    while IFS= read -r n; do
        [[ -n "$n" ]] && USERNAMES+=("$n")
    done < <(incus list --format csv -c n 2>/dev/null | grep -v '^examtpl-builder$')
    if [[ ${#USERNAMES[@]} -eq 0 ]]; then
        echo "Xato: hech qanday mavjud konteyner topilmadi." >&2
        exit 1
    fi
    echo "Topilgan konteynerlar (${#USERNAMES[@]} ta): ${USERNAMES[*]}"
fi

if [[ "$COUNT" -gt 0 ]]; then
    i=1
    added=0
    while [[ $added -lt $COUNT ]]; do
        candidate="${PREFIX}${i}"
        if ! incus info "$candidate" >/dev/null 2>&1; then
            USERNAMES+=("$candidate")
            added=$((added + 1))
        fi
        i=$((i + 1))
    done
fi

if [[ ${#USERNAMES[@]} -eq 0 ]]; then
    if [[ "$REBUILD_TEMPLATE" -eq 1 ]]; then
        echo "Shablon qayta qurildi, boshqa amal so'ralmagan."
        exit 0
    fi
    echo "Xato: kamida bitta user nomi, -n <son> yoki --refresh-all ko'rsating." >&2
    usage
fi

if [[ "$REFRESH" -eq 1 ]]; then
    # Refresh uchun dist/ ni bir marta, alohida vaqtinchalik konteynerda
    # (shablon asosida) qayta quramiz -- har bir talaba konteynerida
    # qayta pyarmor ishlatishning hojati yo'q, hammasi bitta buildni oladi.
    echo "Yangi dist/ tayyorlanmoqda (bitta marta, hamma uchun)..."
    incus delete -f examtpl-refresh >/dev/null 2>&1 || true
    incus launch "$TEMPLATE_ALIAS" examtpl-refresh >/dev/null
    _wait_ready examtpl-refresh
    incus exec examtpl-refresh -- bash -c "rm -rf /opt/linux-foundation-exam-src && mkdir -p /opt/linux-foundation-exam-src"
    incus file push -r "$SCRIPT_DIR/exam" examtpl-refresh/opt/linux-foundation-exam-src/ 2>&1 | tail -3
    incus file push "$SCRIPT_DIR/module1" "$SCRIPT_DIR/build.sh" \
        examtpl-refresh/opt/linux-foundation-exam-src/ 2>&1 | tail -3
    incus exec examtpl-refresh -- bash -c "
        chmod +x /opt/linux-foundation-exam-src/module1 /opt/linux-foundation-exam-src/build.sh
        cd /opt/linux-foundation-exam-src && rm -rf dist .buildvenv && ./build.sh && chmod 755 dist/module1
    "
    DIST_LOCAL="$(mktemp -d)"
    incus file pull -r examtpl-refresh/opt/linux-foundation-exam-src/dist "$DIST_LOCAL/" >/dev/null 2>&1
    DIST_SRC="$DIST_LOCAL/dist"
    incus delete -f examtpl-refresh >/dev/null 2>&1 || true

    printf "%-16s %s\n" "KONTEYNER" "HOLAT"
    printf "%-16s %s\n" "---------" "-----"
    for u in "${USERNAMES[@]}"; do
        refresh_student "$u"
    done
    rm -rf "$DIST_LOCAL"
    exit 0
fi

TS="$(date +%Y%m%d_%H%M%S)"
CRED_FILE="$SCRIPT_DIR/credentials_containers_${TS}.txt"
: > "$CRED_FILE"
chmod 600 "$CRED_FILE"

printf "%-16s %-16s %-8s %s\n" "USER" "PAROL" "PORT" "ULANISH"
printf "%-16s %-16s %-8s %s\n" "----" "-----" "----" "-------"
for u in "${USERNAMES[@]}"; do
    create_student "$u"
done

echo
if [[ -s "$CRED_FILE" ]]; then
    echo "Parollar ro'yxati saqlandi: $CRED_FILE (faqat root o'qiy oladi)"
else
    rm -f "$CRED_FILE"
fi
