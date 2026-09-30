# Instruktor uchun qo'llanma

Bu fayl faqat **kundalik ishlatish** uchun. Texnik tafsilotlar (nega
bunday qurilgan, arxitektura) uchun `README.md`ga qarang.

---

## 1. Bir martalik tayyorgarlik (imtihondan oldin)

VM'da (sudo huquqli user bilan):

```bash
git clone <repo-manzili> ~/linux-foundation-exam
cd ~/linux-foundation-exam
chmod +x provision_containers.sh grade.sh build.sh module1
```

Birinchi safar bitta sinov useri bilan tekshiring:

```bash
sudo ./provision_containers.sh -n 1 -p sinov
```

Bu bir necha daqiqa oladi (birinchi marta `incus` o'rnatiladi va
"shablon" tayyorlanadi). Oxirida chiqadigan `ssh sinov1@... -p 2200`
buyrug'i bilan o'zingiz kirib, savollar ro'yxati chiqishini tasdiqlang.

Ishlasa, sinov useri kerak emas -- shunchaki e'tiborsiz qoldiring,
haqiqiy talabalarni yaratganda avtomatik boshqa nomlar olishadi.

---

## 2. Imtihon kuni: talabalarni yaratish

```bash
sudo ./provision_containers.sh -n 25          # talaba1..talaba25
```

yoki aniq ism-familiya bilan:

```bash
sudo ./provision_containers.sh ali vali guli
```

Oxirida jadval chiqadi:

```
USER             PAROL            PORT     ULANISH
talaba1          Gulquyosh88      2201     ssh talaba1@172.20.10.3 -p 2201
talaba2          Nokbehi11        2202     ssh talaba2@172.20.10.3 -p 2202
...
```

Bu jadval `credentials_containers_<sana>.txt` fayliga ham saqlanadi:

```bash
cat credentials_containers_*.txt
```

**Har bir talabaga faqat o'zining qatorini bering** (user, parol, port).
Talaba shu `ssh ... -p <port>` buyrug'i bilan kirsa, imtihon **o'zi
avtomatik boshlanadi** -- hech narsa o'rnatishning, ishga tushirishning
hojati yo'q.

---

## 3. Imtihon davomida

Talaba tomonidan:
1. SSH bilan kiradi -> 20 ta savol ro'yxati chiqadi (ball ko'rsatilmaydi).
2. Erkin ishlaydi (odatdagi bash, hech qanday cheklov yo'q).
3. Tugatgach, terminalga `submit` deb yozadi -> bir marta tasdiqlaydi ->
   tamom. Ikkinchi marta `submit` ishlamaydi.

Sizga hech narsa qilish shart emas -- shunchaki kutasiz.

---

## 4. Imtihondan keyin: natijalarni ko'rish

```bash
sudo ./grade.sh --all          # barcha talabalar, qisqa xulosa
sudo ./grade.sh talaba1        # bitta talaba, har savol bo'yicha batafsil
```

**Muhim:** `./module1 --grade` (host'ning o'zida, `incus exec`siz)
ishlatmang -- u sizning o'z hisobingizni tekshiradi, talabalarnikini
emas. Har doim `grade.sh` orqali, konteyner nomi bilan ishlating.

---

## 5. Savol qo'shdingiz yoki xato tuzatdingiz -- yangilash

Manba kodni (`exam/module1/questions.py`) tahrirlagach:

```bash
git add -A && git commit -m "..."   # (ixtiyoriy, lekin tavsiya etiladi)
sudo ./provision_containers.sh --refresh-all
```

Bu **barcha mavjud** talaba konteynerlarining imtihon kodini yangilaydi
-- parollariga va hozirgача qilingan ishlariga (`~/javoblar`, holat)
tegmaydi. Yangi talaba qo'shish uchun oddiy `-n <son>` yetarli.

---

## 6. Tez-tez uchraydigan muammolar

**"No root device could be found" / birinchi ishga tushirishda xato**
`incus` hali sozlanmagan bo'lishi mumkin:
```bash
sudo incus admin init --auto
```
so'ng `provision_containers.sh`ni qayta ishga tushiring.

**`pip install pyarmor` "externally-managed-environment" xatosi beradi**
Bezovta bo'lmang -- `build.sh` buni o'zi avtomatik hal qiladi (mahalliy
virtualenv yaratadi). Hech narsa qo'lda qilishning hojati yo'q.

**Talaba SSH bilan kira olmayapti**
- Parolni to'g'ri ko'chirganingizni tekshiring (`credentials_containers_*.txt`).
- Port raqami to'g'riligini tekshiring (`sudo incus list` orqali qaysi
  konteyner qaysi portda ekanini ko'rish mumkin: `incus config device
  show <user>`).

**Konteynerlar ro'yxatini ko'rish / boshqarish**
```bash
sudo incus list                 # barcha konteynerlar va holati
sudo incus exec talaba1 -- bash # konteyner ichiga qo'lda kirish (debug uchun)
sudo incus delete -f talaba1    # bitta talaba konteynerini butunlay o'chirish
```

**Hammasini boshidan boshlashim kerak (yangi imtihon oqimi)**
Eski konteynerlarni o'chirib, qaytadan yarating:
```bash
sudo incus list --format csv -c n | grep -v '^examtpl' | xargs -I{} sudo incus delete -f {}
sudo ./provision_containers.sh -n 25
```
