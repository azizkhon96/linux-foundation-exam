# Linux Foundation kursi -- imtihon skripti

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
- **Faqat ekranga chiqaradigan (`pwd`, `tree`, `ls -la /run`, `find`, `w`, `ps|grep`, `systemctl status`) savollar natijani faylga yozishni talab qiladi** (`~/javoblar/N.txt`), chunki holat-asosidagi tekshiruv uchun biror "iz" qolishi kerak. Ba'zi javoblar (masalan `find /etc -name os-release`) instruktor tomonidan **live** qayta ishga tushirilib solishtiriladi; boshqalari (masalan `/run` yoki `ps`) doimo o'zgarib turgani uchun struktura bo'yicha tekshiriladi.
- **14/15-savollar endi ikkita alohida faylda** (`~/my-file`, `~/my-file2`) -- eski versiyada ikkalasi ham bitta faylga chmod qilar edi, shuning uchun 15-savol 14-ni "yozib yuborar" edi.
- **19-savol** (`crontab -e`) endi aniq bitta yozuv qo'shishni talab qiladi -- shunchaki `crontab -e`ni ochib yopish hech narsani o'zgartirmaydi, tekshirish uchun aniq natija kerak.
- **20-savol** endi **dinamik PID** bilan ishlaydi -- har talaba uchun skript o'zi haqiqiy fon jarayon yaratadi va uning PID'ini savol matnida ko'rsatadi, shuning uchun `kill -9 30025` kabi "hech qachon mavjud bo'lmagan PID" muammosi yo'qoladi.
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

**Muhim eslatma:** imtihon VM'laridagi Python versiyasini tekshiring va build shu versiyaga mos yoki undan past versiyada qilinganiga ishonch hosil qiling (pyarmor 9.x runtime ko'p Python 3.x versiyalar bilan mos ishlaydi, lekin VM image tayyorlangach bir marta `dist/module1`ni o'sha VM'da sinab ko'rish tavsiya etiladi).

## Talab qilinadigan huquqlar

Deyarli barcha tekshiruvlar oddiy foydalanuvchi huquqi bilan ishlaydi (fayl `stat`, `/etc/passwd` o'qish, `apt-mark showhold` va h.k. -- bularning barchasi world-readable). Faqat **19-savol** (root crontabini o'qish) `sudo` talab qiladi -- bu safar `submit` yoki `--grade` ishga tushganda interaktiv `sudo` parol so'rovi chiqishi mumkin, bu normal holat.

## Ma'lum cheklovlar / e'tiborga olinishi kerak narsalar

- **17-savol** (`systemctl status network-manager`) -- ba'zi distributivlarda (netplan/systemd-networkd ishlatuvchi) `network-manager` xizmati umuman bo'lmasligi mumkin. Agar imtihon VM tasviringizda boshqa tarmoq xizmati ishlatilsa, savol matni yoki tekshiruvni moslashtiring.
- **`tree`** paketi VM tasvirida oldindan o'rnatilgan bo'lishi kerak (2-savol).
- 2-savol tekshiruvi endi to'liq live-diff emas (chunki `/proc`, `/tmp` kabi joylar doimo o'zgarib turadi) -- struktura bo'yicha (asosiy tub papkalar + xulosa qatori bor-yo'qligi) tekshiriladi.
