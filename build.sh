#!/usr/bin/env bash
# Talabalarga beriladigan, pyarmor bilan shifrlangan versiyani tayyorlaydi.
#
# Manba kod (exam/ va module1) ochiq holda qoladi -- siz shu yerda tahrirlaysiz.
# Ushbu skript esa dist/ papkasida shifrlangan, tarqatishga tayyor nusxa yaratadi.
#
# Ishlatish:
#   ./build.sh
#
# Talab qilinadi: pip install pyarmor  (yoki: python3 -m venv .venv && .venv/bin/pip install pyarmor)

set -euo pipefail
cd "$(dirname "$0")"

if ! command -v pyarmor >/dev/null 2>&1; then
    echo "Xato: pyarmor topilmadi." >&2
    echo "O'rnatish: pip install pyarmor  (yoki virtualenv ichida)" >&2
    exit 1
fi

echo "Pyarmor versiyasi:"
pyarmor --version

rm -rf dist
mkdir -p dist

# exam/ paketini (rekursiv) va module1 kirish skriptini birga shifrlaymiz,
# shunda ular bitta umumiy runtime bilan ishlaydi.
pyarmor gen -O dist -r exam module1

echo
echo "Tayyor: dist/ papkasida shifrlangan versiya joylashgan."
echo "Talabalarga FAQAT 'dist/' papkani bering -- manba kodni (exam/, module1) emas."
echo
echo "Sinab ko'rish:"
echo "    cd dist && ./module1"
