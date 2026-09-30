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
    echo "pyarmor tizimda topilmadi -- mahalliy virtualenv (.buildvenv/) orqali o'rnatilmoqda..."
    python3 -m venv .buildvenv
    .buildvenv/bin/pip install --quiet --upgrade pip
    .buildvenv/bin/pip install --quiet pyarmor
    PYARMOR="$(pwd)/.buildvenv/bin/pyarmor"
fi

echo "Pyarmor versiyasi:"
"$PYARMOR" --version
echo "Ishlatilayotgan python3: $(python3 --version)"

rm -rf dist
mkdir -p dist

# exam/ paketini (rekursiv) va module1 kirish skriptini birga shifrlaymiz,
# shunda ular bitta umumiy runtime bilan ishlaydi.
"$PYARMOR" gen -O dist -r exam module1

echo
echo "Tayyor: dist/ papkasida shifrlangan versiya joylashgan."
echo "Talabalarga FAQAT 'dist/' papkani bering -- manba kodni (exam/, module1) emas."
echo
echo "Sinab ko'rish:"
echo "    cd dist && ./module1"
