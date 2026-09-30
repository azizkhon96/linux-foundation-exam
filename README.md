# Linux Foundation kursi -- imtihon skripti

## Joylashtirish: ikkita usul bor

**Tavsiya etiladi: `provision_containers.sh`** -- har talaba uchun ALOHIDA,
to'liq izolyatsiyalangan LXD/incus konteyner (systemd+cron+apt bilan, kichik
VM kabi) yaratadi. Bitta VM ichida ko'p talaba bo'lganda `/tmp`, `/etc/passwd`,
o'rnatilgan paketlar, `crontab -u root` kabi GLOBAL narsalar talabalar
o'rtasida ARALASHIB ketishi mumkin edi (bitta talabaning ishi boshqasining
hisobiga yozilib qolishi) -- konteynerlar buni butunlay yo'qotadi.

```bash
sudo apt install incus      # birinchi marta (skript o'zi ham o'rnatadi)
sudo ./provision_containers.sh -n 15
```

Batafsil: "Talabalar uchun konteyner muhitini yaratish" bo'limiga qarang.

**Eski usul: `provision_students.sh`** -- bitta VM ichida har talaba uchun
alohida Linux user yaratadi (`/home/user1`, `/home/user2`, ...). Oddiyroq,
lekin yuqoridagi kontaminatsiya muammosiga ega. Faqat juda cheklangan
resurs (konteyner ishga tushirib bo'lmaydigan VM) holatida ishlatilsin.

## Qanday ishlaydi (qisqacha)

1. Talaba SSH orqali VM ga kiradi, `./module1` ni ishga tushiradi.
2. Skript birinchi marta ishga tushganda:
   - Kerakli fayllarni tayyorlaydi (`~/my-file`, `~/my-file2`),
   - Fon jarayon yaratadi (20-savol uchun) va uning PID'ini eslab qoladi,
   - Mavjud userlar ro'yxatini eslab qoladi (10-savol uchun),
   - `~/bin/submit` komandasini yaratadi va uni PATH'ga qo'shadi,
   - **Barcha 20 ta topshiriqni bittada ro'yxat qilib ko'rsatadi** (ball bilan),
   - `bash`ni ishga tushiradi -- talaba shu yerdan boshlab **to'liq, erkin, oddiy bash**da ishlaydi (tab-completion, vim, less -- hammasi ishlaydi).
3. Ishi tugagach, talaba **`submit`** deb yozadi:
   - Bir marta tasdiqlashni so'raydi ("Rostdan ham...?"),
   - Tizim holatini tekshiradi va natijani **imzolangan** holda saqlaydi,
   - Talabaga faqat "muvaffaqiyatli topshirildi" deb ko'rsatadi -- **ball ko'rsatilmaydi**.
   - Ikkinchi marta `submit` ishlamaydi.
4. Instruktor keyinroq VM'ga kirib:
   ```
   ./module1 --grade
   ```
   deb, **LIVE** (o'sha paytdagi haqiqiy tizim holatiga asoslangan) natijani va har bir savol bo'yicha batafsil ballarni ko'radi.

## Nega bunday qurildi (asosiy dizayn qarorlari)

- **Komanda matni emas, tizim holati tekshiriladi.** Eski skript `~/.bash_history`ning oxirgi qatorini o'qib, uni aniq matn bilan solishtirar edi -- bu shell-injection, quoting va "faqat bitta to'g'ri yozilish shakli" muammolarini keltirib chiqargan edi. Yangi versiyada har bir savol **natijani** tekshiradi (fayl bormi, ruxsat to'g'rimi, user yaratilganmi va h.k.) -- shuning uchun turlicha, lekin to'g'ri yozilgan komandalar ham qabul qilinadi.
- **Faqat ekranga chiqaradigan savollar** (`pwd`, `tree`, `apt list`, `find`, `pidof`, `systemctl status`) natijani faylga yozishni talab qiladi (`~/javoblar/N.txt`), chunki holat-asosidagi tekshiruv uchun biror "iz" qolishi kerak. Barqaror natijalar (masalan `find /etc -size +100k`) instruktor tomonidan **live** qayta ishga tushirilib solishtiriladi; o'zgaruvchan/katta natijalar (masalan `apt list`) struktura bo'yicha tekshiriladi.
- **14/15-savollar endi har biri 3 tadan ALOHIDA fayl** (`perm-a/b/c`, `perm-x/y/z`) -- bir faylni ikki marta chmod qilishning ustma-ust yozilish muammosi yo'q, va materialdagi "bir nechta ruxsat qiymatini bir yo'la bajarish" uslubiga mos.
- **19-savol** (`crontab`) endi aniq bir haftalik `/etc` backup vazifasini talab qiladi -- shunchaki `crontab -e`ni ochib yopish hech narsani o'zgartirmaydi, tekshirish uchun aniq natija kerak.
- **20-savol** endi **nomi bilan** ('examdaemon', `killall`/`pkill` orqali) to'xtatishni talab qiladi -- har talaba konteyneri alohida bo'lgani uchun PID shart emas, va bu 17-savoldagi (PID bo'yicha `pidof`) ko'nikmadan farqli, alohida protsess-boshqaruv ko'nikmasini sinaydi. **DIQQAT:** `killall` `psmisc` paketiga tegishli -- konteyner shabloniga (`provision_containers.sh`) kiritilgan, lekin eski (`provision_students.sh`) yo'l bilan VM'ga qo'lda o'rnatish kerak bo'lishi mumkin (`apt install psmisc`).
- **`submit` faqat bir marta ishlaydi**, holat `~/.exam/module1/state.json`da saqlanadi.
- **Natija talabaga ko'rinmaydi**, faqat instruktorga (`--grade`). Saqlangan `report.json` HMAC bilan imzolangan (tasodifiy tahrirlashni aniqlash uchun), lekin **haqiqiy, ishonchli baho har doim `--grade` orqali LIVE hisoblanadi** -- talaba root huquqiga ega bo'lishi mumkinligi sababli, faylga to'liq ishonib bo'lmaydi. Diqqat: barcha tekshiruvlar "doimiy holat"ga asoslangani uchun (masalan o'ldirilgan jarayon abadiy o'lik qoladi), `--grade`ni istalgan payt -- hatto imtihondan keyin ham -- qayta ishga tushirish mumkin.

## Fayl tuzilishi

```
exam/
  core.py              -- umumiy dvigatel (barcha modullar uchun bir xil)
  module1/
    questions.py        -- 1-modul savollari + tekshiruv funksiyalari
module1                 -- ishga tushiriladigan fayl (dev/ochiq versiya)
build.sh                 -- pyarmor bilan shifrlangan versiya tayyorlaydi -> dist/
dist/                    -- (build.sh dan keyin paydo bo'ladi) talabalarga BERILADIGAN versiya
module1.py               -- ESKI skript (solishtirish/tarix uchun saqlangan, ishlatilmaydi)
```

## Yangi savol qo'shish

`exam/module1/questions.py` faylini oching, pastdagi `QUESTIONS` ro'yxatiga yangi qator qo'shing:

```python
_q(21, 3, "Yangi savol matni...", check_21)
```

va unga mos `check_21(ctx)` funksiyasini yozing (yuqoridagi boshqa `check_*` funksiyalariga qarang -- ular namuna sifatida xizmat qiladi). Boshqa hech narsani o'zgartirish shart emas.

Yangi modul (module2, module3...) qo'shish uchun `exam/module2/` papkasini xuddi `module1/` kabi yarating (o'z `questions.py`, o'z `setup()` funksiyasi bilan) va `module2` nomli entry-script yozing -- `module1` faylidagi naqshni takrorlang.

## Pyarmor bilan shifrlash (talabalarga berish uchun)

```bash
pip install pyarmor      # bir marta
./build.sh                # har safar savol qo'shgan/o'zgartirgandan keyin
```

Natija `dist/` papkasida paydo bo'ladi -- **faqat shu papkani** talabalarga bering (`exam/`, `module1`, `questions.py` manba kodini emas). Sinab ko'rish: `cd dist && ./module1`.

Tekshirilgan: pyarmor 9.2.7 bilan `exam/` paketi + `module1` entry-script birga shifrlanadi, bitta umumiy runtime bilan ishlaydi, va manba matnlari (savollar, fayl nomlari) shifrlangan fayllarda oddiy `grep` bilan topilmaydi.

**MUHIM (tekshirib tasdiqlangan):** pyarmor runtime (`pyarmor_runtime_*.so`) build qilingan Python versiyasiga qat'iy bog'liq -- ular orasida umumiy moslik YO'Q. Masalan Python 3.14'da qilingan build Ubuntu 22.04'ning Python 3.10'ida `ImportError: undefined symbol: PyLongWriter_Discard` xatosi bilan ishlamay qoladi. Shuning uchun:

- **`./build.sh`ni har doim aynan imtihon VM'ining o'zida ishga tushiring** (yoki VM bilan bir xil Python minor-versiyali muhitda). Boshqa mashinada build qilib, faylni ko'chirib qo'yish ISHLAMAYDI.
- `provision_students.sh` shuni hisobga oladi: agar `dist/` topilmasa, o'zi avtomatik `./build.sh`ni ishga tushiradi -- shu VM'ning python3 va pyarmor'i bilan. Shuning uchun eng oddiy yo'l: manba kodni (`exam/`, `module1`, `build.sh`, `provision_students.sh`) VM'ga ko'chiring, `pip install pyarmor` qiling va to'g'ridan-to'g'ri `provision_students.sh`ni ishga tushiring -- u kerakli build'ni o'zi qiladi.

## Talabalar uchun konteyner muhitini yaratish (tavsiya etiladi)

VM'da manba kod bo'lgach (git clone yoki nusxalash orqali):

```bash
sudo ./provision_containers.sh -n 15              # talaba1..talaba15
sudo ./provision_containers.sh ali vali guli       # aniq nomlar bilan
sudo ./provision_containers.sh -n 10 -p ozod       # ozod1..ozod10
```

Birinchi ishga tushirishda skript avtomatik ravishda:
1. `incus` (LXD'ning ochiq hamjamiyat versiyasi) topilmasa o'rnatadi va sozlaydi (`incus admin init --auto`),
2. **Shablon (golden image)** tayyorlaydi -- bitta konteyner ochib, kerakli paketlarni (`openssh-server`, `tree`, `psmisc`, `cron` -- allaqachon bor) o'rnatadi, `pyarmor` bilan shu KONTEYNERNING o'zida (to'g'ri Python versiyasi bilan) build qiladi, smoke-test qiladi, va `examtpl-module1` nomi bilan saqlaydi. Bu bosqich bir necha daqiqa oladi, lekin **faqat bir marta** bajariladi.
3. Har bir talaba uchun: shablondan sekundlar ichida yangi konteyner kloni yaratadi, ichida user+parol o'rnatadi, `sudo` guruhiga qo'shadi, SSH orqali kirilganda imtihon avtomatik boshlanadigan qilib sozlaydi, va noyob host-port orqali SSH kirish imkonini ochadi (`incus config device add ... proxy`).
4. Oxirida `user | parol | port | ulanish-komandasi` jadvalini chiqaradi va `credentials_containers_<sana>.txt` fayliga saqlaydi.

Talaba ulanadi:
```bash
ssh talaba1@<VM_IP> -p 2200
```
(port har bir talaba uchun individual, 2200 dan boshlab ketma-ket).

**Materiallarni yangilagach** (savol qo'shdingiz yoki `exam/`ni tahrirladingiz):
```bash
sudo ./provision_containers.sh --refresh-all       # BARCHA konteynerlar, parol/holatga tegmasdan
sudo ./provision_containers.sh --refresh user1 user2
sudo ./provision_containers.sh --rebuild-template -n 0   # shablonni majburan qayta qurish
```

Instruktor natijani ko'rish uchun konteyner ichiga kiradi:
```bash
incus exec talaba1 -- bash -c "HOME=/home/talaba1 python3 /opt/linux-foundation-exam/dist/module1 --grade"
```

**Nega konteyner, nega oddiy VM-user emas:** ko'p savol GLOBAL tizim holatiga tegadi (`/tmp`, `/etc/passwd`, o'rnatilgan paketlar, root crontab). Bitta VM'da bir nechta Linux user bo'lsa, bir talabaning ishi (masalan `/tmp/file1` yaratishi) boshqa talabaning shu savolini ham "yechilgan" ko'rsatishi mumkin edi -- bu real holatda kuzatilgan va tasdiqlangan muammo. Har biriga alohida konteyner (o'z `/tmp`, `/etc`, userlari, cron'i bilan) buni tag'in yo'qotadi.

**Tekshirilgan:** nested incus muhitida (Ubuntu 24.04, real systemd+cron+python3.12) to'liq oqim -- shablon qurish, talaba yaratish, real SSH login (port-forwarding orqali), va barcha 20 savolga to'g'ri javob bilan 60/60 ball -- tasdiqlangan.

## Talabalar uchun user muhitini bitta buyruq bilan yaratish (eski usul, kontaminatsiya xavfi bilan)

VM tayyor bo'lgach (manba kod VM'ga ko'chirilgan, `pip install pyarmor` qilingan holda):

```bash
sudo ./provision_students.sh -n 15              # talaba1..talaba15 (avtomatik nomlar)
sudo ./provision_students.sh ali vali guli       # aniq nomlar bilan
sudo ./provision_students.sh -n 10 -p ozod       # ozod1..ozod10
```

Har bir user uchun skript avtomatik ravishda:
- `useradd -m -s /bin/bash` bilan user yaratadi va `sudo` guruhiga qo'shadi (ko'p savollar root huquqi talab qiladi),
- oson o'qiladigan/aytiladigan parol generatsiya qiladi (masalan `Gulquyosh88`),
- shifrlangan imtihon materialini (`dist/`) `~/module1-exam/` ga joylaydi, `root:root` egaligida va faqat o'qish/ishga tushirish huquqi bilan (talaba tekshiruv kodini o'zgartira olmaydi),
- **SSH orqali kirishning o'zida imtihon avtomatik boshlanadigan** qilib `~/.bash_profile`ga yoziladi -- talaba hech qanday buyruq bilmasdan, shunchaki SSH orqali kirsa, savollar ro'yxatini ko'radi va erkin bashga tushadi.
- Oxirida barcha `user:parol` juftliklarini ekranga chiqaradi va `credentials_<sana>.txt` fayliga (faqat root o'qiy oladigan, `chmod 600`) saqlaydi.

**Diqqat:**
- Mavjud (allaqachon yaratilgan) userlar o'tkazib yuboriladi -- xavfsizlik uchun ustidan yozilmaydi.
- `credentials_*.txt` fayllarini hech qachon git'ga qo'shmang (`.gitignore`da allaqachon istisno qilingan) -- ular parollarni ochiq matnda saqlaydi.
- SSH serverda `PasswordAuthentication yes` yoqilganligini o'zingiz tekshiring (`/etc/ssh/sshd_config`) -- bu skript uni o'zgartirmaydi, chunki bu butun VM xavfsizligiga tegishli global sozlama.

## Talab qilinadigan huquqlar

Deyarli barcha tekshiruvlar oddiy foydalanuvchi huquqi bilan ishlaydi (fayl `stat`, `/etc/passwd` o'qish, `apt-mark showhold` va h.k. -- bularning barchasi world-readable). Faqat **19-savol** (root crontabini o'qish) `sudo` talab qiladi -- bu safar `submit` yoki `--grade` ishga tushganda interaktiv `sudo` parol so'rovi chiqishi mumkin, bu normal holat.

## Ma'lum cheklovlar / e'tiborga olinishi kerak narsalar

- **17-savol** (`systemctl status network-manager`) -- ba'zi distributivlarda (netplan/systemd-networkd ishlatuvchi) `network-manager` xizmati umuman bo'lmasligi mumkin. Agar imtihon VM tasviringizda boshqa tarmoq xizmati ishlatilsa, savol matni yoki tekshiruvni moslashtiring.
- **`tree`** paketi VM tasvirida oldindan o'rnatilgan bo'lishi kerak (2-savol).
- 2-savol tekshiruvi endi to'liq live-diff emas (chunki `/proc`, `/tmp` kabi joylar doimo o'zgarib turadi) -- struktura bo'yicha (asosiy tub papkalar + xulosa qatori bor-yo'qligi) tekshiriladi.
