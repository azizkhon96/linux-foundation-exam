#!/usr/bin/env bash
# Talabalarga beriladigan, pyarmor bilan shifrlangan versiyani tayyorlaydi.
#
# Manba kod (exam/ va module1) ochiq holda qoladi -- siz shu yerda tahrirlaysiz.
# Ushbu skript esa dist/ papkasida shifrlangan, tarqatishga tayyor nusxa yaratadi.
#
# Ishlatish:
#   ./build.sh
#
# MUHIM: bu skriptni har doim IMTIHON VM'INING O'ZIDA ishga tushiring (yoki
# u bilan bir xil Python minor-versiyali muhitda). pyarmor runtime build
# qilingan Python versiyasiga qat'iy bog'liq -- boshqa mashinada qilingan
# build boshqa Python versiyasida "undefined symbol" xatosi bilan ishlamay
# qoladi.
#
# pyarmor kerak, lekin uni qo'lda o'rnatishning hojati yo'q -- agar tizimda
# topilmasa, bu skript o'zi mahalliy virtualenv (.buildvenv/) yaratib,
# o'sha yerga o'rnatadi (Ubuntu 23.04+ va 24.04'dagi PEP 668
# "externally-managed-environment" cheklovini aylanib o'tish uchun ham shu
# yo'l ishlatiladi).

set -euo pipefail
cd "$(dirname "$0")"

if command -v pyarmor >/dev/null 2>&1; then
    PYARMOR=pyarmor
else
    echo "pyarmor tizimda topilmadi -- o'rnatishga urinilmoqda..."
    PYARMOR=""
    # 1-urinish: mahalliy virtualenv (toza, tavsiya etiladigan yo'l).
    if python3 -m venv .buildvenv 2>/tmp/build-venv-err.log \
        && .buildvenv/bin/pip install --quiet --upgrade pip 2>>/tmp/build-venv-err.log \
        && .buildvenv/bin/pip install --quiet pyarmor 2>>/tmp/build-venv-err.log; then
        PYARMOR="$(pwd)/.buildvenv/bin/pyarmor"
    else
        echo "Ogohlantirish: virtualenv orqali o'rnatish muvaffaqiyatsiz bo'ldi" \
             "(ko'pincha 'ensurepip'/python3-venv paket muammosi). Log: /tmp/build-venv-err.log" >&2
        echo "2-urinish: tizim pip'i bilan (--break-system-packages)..." >&2
        rm -rf .buildvenv
        if pip3 install --quiet --break-system-packages --user pyarmor 2>/tmp/build-pip-err.log; then
            PYARMOR="$(python3 -c 'import site,os;print(os.path.join(site.USER_BASE,"bin","pyarmor"))')"
        fi
    fi
    if [[ -z "$PYARMOR" || ! -x "$PYARMOR" ]]; then
        echo "Xato: pyarmor hech qanday usul bilan o'rnatilmadi." >&2
        echo "Qo'lda urinib ko'ring: pip3 install --break-system-packages pyarmor" >&2
        exit 1
    fi
fi

echo "Pyarmor versiyasi:"
"$PYARMOR" --version
echo "Ishlatilayotgan python3: $(python3 --version)"

rm -rf dist
mkdir -p dist

# exam/ paketini (rekursiv) va module1 kirish skriptini birga shifrlaymiz,
# shunda ular bitta umumiy runtime bilan ishlaydi.
"$PYARMOR" gen -O dist -r exam module1

# --- O'Z-O'ZINI SINASH (smoke test) ---
# pyarmor runtime build qilingan Python versiyasiga qat'iy bog'liq bo'lgani
# uchun ("undefined symbol" xatosi boshqa versiyada), yangi qurilgan
# dist/module1'ni DARHOL shu yerda, real ishga tushirib tekshiramiz.
# Muvaffaqiyatsiz bo'lsa, build XATO deb e'lon qilinadi -- hech qachon
# "muvaffaqiyatli" deb chiqib, aslida ishlamaydigan dist qoldirmaydi.
echo
echo "O'z-o'zini sinash (smoke test)..."
SMOKE_HOME="$(mktemp -d)"
if EXAM_NO_EXEC=1 HOME="$SMOKE_HOME" python3 dist/module1 >"$SMOKE_HOME/out.log" 2>&1; then
    SMOKE_OK=1
else
    SMOKE_OK=0
fi
# smoke-test 20-savol uchun ('examdaemon') fon jarayon yaratadi -- faqat
# shu SMOKE_HOME'ga tegishli nusxani, aniq yo'l bo'yicha tozalaymiz
# (boshqa hech qanday -- masalan haqiqiy talabaning -- jarayoniga tegmaymiz).
pkill -9 -f "^$SMOKE_HOME/\.exam/module1/examdaemon" 2>/dev/null || true

if [[ "$SMOKE_OK" -ne 1 ]]; then
    echo "XATO: yangi qurilgan dist/module1 ishga tushmadi!" >&2
    echo "--- xato matni ---" >&2
    cat "$SMOKE_HOME/out.log" >&2
    echo "------------------" >&2
    rm -rf "$SMOKE_HOME"
    echo >&2
    echo "dist/ papkasi ATAYLAB saqlanmadi (buzuq holda qoldirmaslik uchun)." >&2
    rm -rf dist
    exit 1
fi
rm -rf "$SMOKE_HOME"

echo "OK: dist/module1 muvaffaqiyatli ishga tushdi (python3 $(python3 --version 2>&1 | awk '{print $2}'))."
echo
echo "Tayyor: dist/ papkasida shifrlangan versiya joylashgan."
echo "Talabalarga FAQAT 'dist/' papkani bering -- manba kodni (exam/, module1) emas."
echo
echo "Sinab ko'rish:"
echo "    cd dist && ./module1"
