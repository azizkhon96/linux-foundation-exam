"""
1-modul: savollar va ularning tekshiruv qoidalari.

Savollar kurs materiallariga (materials/1-modul/) moslab tuzilgan: fayl
tizimi/navigatsiya, filtrlar (grep), arxivlash, user/group, ruxsatlar,
paket boshqaruvi, find, servis, ssh, cron, protsess boshqaruvi.

YANGI SAVOL QO'SHISH: pastdagi QUESTIONS ro'yxatiga yangi `_q(...)` qatori
qo'shing va unga mos `check_N` funksiyasini yozing. Boshqa hech narsani
o'zgartirish shart emas -- dvigatel (exam/core.py) avtomatik ishlaydi.

Har bir `check_*` funksiyasi `ctx` (context) dict qabul qiladi:
    ctx["home"]         -- talabaning uy direktoriyasi
    ctx["state"]        -- shu modul uchun saqlangan holat (setup() paytida
                            yaratilgan qiymatlar, masalan baseline ro'yxatlar)
    ctx["read_answer"]  -- ~/javoblar/<savol_id>.txt faylini o'qiydi (yo'q
                            bo'lsa None qaytaradi)
    ctx["run"](cmd)     -- komandani ishga tushiradi: (returncode, stdout, stderr)
    ctx["sudo_run"](cmd)-- xuddi shu, lekin `sudo` bilan (root kerak bo'lganda)
    ctx["normalize"](s) -- ortiqcha probel/bo'sh qatorlarni yumshatadi

Tekshiruv funksiyasi True/False (yoki shunga o'xshash) qaytarishi kerak.
"""
import os
import re
import stat as stat_mod
import subprocess
import tarfile

import grp
import pwd


# ------------------------------------------------------------------
# Bir martalik tayyorgarlik (imtihon birinchi marta ishga tushganda)
# ------------------------------------------------------------------
def setup(home):
    extra = {}

    # 13/14/15-savollar uchun maxsus fayllar
    my_file = os.path.join(home, "my-file")
    my_file2 = os.path.join(home, "my-file2")
    open(my_file, "a").close()
    open(my_file2, "a").close()

    # 10/16-savollar uchun: useradd bilan YANGI qo'shilgan userni aniqlash
    # uchun boshlang'ich (mavjud) userlar ro'yxatini eslab qolamiz.
    extra["baseline_users"] = sorted(u.pw_name for u in pwd.getpwall())

    # 5-savol uchun: grep natijasi /etc/passwd ga YANGI user qo'shilishidan
    # (10-savol) OLDIN yoki KEYIN bajarilishidan qat'iy nazar bir xil
    # bo'lishi uchun, "/bin/bash" shell'iga ega userlar ro'yxatini HOZIROQ
    # (hali hech narsa o'zgarmagan holatda) eslab qolamiz.
    extra["baseline_bash_users"] = sorted(
        u.pw_name for u in pwd.getpwall() if u.pw_shell == "/bin/bash"
    )

    # 20-savol uchun: haqiqiy, "o'ldirsa bo'ladigan" fon jarayon yaratamiz va
    # uning PID'ini savol matnida ko'rsatamiz.
    proc = subprocess.Popen(
        ["sleep", "100000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    extra["task20_pid"] = proc.pid

    return extra


def _q(id, points, text, check):
    return {"id": id, "points": points, "text": text, "check": check}


def _stat_mode(path):
    try:
        return stat_mod.S_IMODE(os.stat(path).st_mode)
    except FileNotFoundError:
        return None


def _new_users(ctx):
    """setup() paytida mavjud bo'lmagan, imtihon davomida qo'shilgan userlar."""
    baseline = set(ctx["state"].get("baseline_users", []))
    return [u for u in pwd.getpwall() if u.pw_name not in baseline]


# ------------------------------------------------------------------
# Tekshiruv funksiyalari
# ------------------------------------------------------------------
def check_1(ctx):
    """1-savol: uy direktoriyasini ekranga chiqarish (pwd)."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    return ans.strip() == ctx["home"]


def check_2(ctx):
    """2-savol: 'tree -L 2 /' natijasi."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    # DIQQAT: bu yerda LIVE-diff ishlatilmaydi -- "/" ostidagi /proc, /tmp,
    # /run kabi papkalar imtihon davomida doimiy o'zgarib turadi (PID'lar,
    # talabaning o'zi yaratgan fayllar va h.k.), shuning uchun exact-match
    # doimo barqaror ishlamaydi. O'rniga tuzilma bo'yicha tekshiramiz:
    # haqiqiy tree xulosasi bormi va asosiy tub papkalar sanab o'tilganmi.
    lines = ans.strip().splitlines()
    if len(lines) < 15:
        return False
    has_summary = any(
        "director" in l.lower() and "file" in l.lower() for l in lines
    )
    expected_roots = {"etc", "home", "var", "usr", "tmp"}
    found_roots = set()
    for l in lines:
        parts = l.split()
        if not parts:
            continue
        name = parts[-1].strip("/")
        if name in expected_roots:
            found_roots.add(name)
    return has_summary and len(found_roots) >= 4


def check_3(ctx):
    """3-savol: 'apt list' natijasi (paket ro'yxati)."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    lines = [l for l in ans.strip().splitlines() if l.strip()]
    pattern = re.compile(r"^\S+/\S+\s+\S+\s+\S+")
    matched = sum(1 for l in lines if pattern.match(l))
    return matched > 50


def check_4(ctx):
    """4-savol: /tmp/file1, file2, file3 yaratish."""
    return all(os.path.isfile("/tmp/file%d" % i) for i in (1, 2, 3))


def check_5(ctx):
    """5-savol: /etc/passwd dan '/bin/bash' bilan tugagan qatorlarni grep
    orqali filtrlab faylga yozish."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    baseline = set(ctx["state"].get("baseline_bash_users", []))
    if not baseline:
        return False
    found = set()
    for line in ans.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        username = line.split(":", 1)[0]
        found.add(username)

    # Talaba bu savolni 10-savoldan OLDIN ham, KEYIN ham bajargan bo'lishi
    # mumkin -- ikkalasi ham haqiqatan to'g'ri javob (chunki 10-savol aynan
    # shu /etc/passwd faylini o'zgartiradi). Shuning uchun bitta "qotib
    # qolgan" ro'yxatga emas, balki oraliqqa solishtiramiz: javob kamida
    # imtihon boshidagi (baseline) userlarni o'z ichiga olishi, va hozirgi
    # haqiqiy /bin/bash userlaridan oshib ketmasligi kerak.
    current_bash_users = {
        u.pw_name for u in pwd.getpwall() if u.pw_shell == "/bin/bash"
    }
    return baseline <= found <= current_bash_users


def check_6(ctx):
    """6-savol: /tmp/bir/ikki/uch ichma-ich papkalar."""
    return os.path.isdir("/tmp/bir/ikki/uch")


def check_7(ctx):
    """7-savol: /etc ni /tmp ga to'liq nusxalash."""
    return os.path.isdir("/tmp/etc") and os.path.isfile("/tmp/etc/passwd")


def check_8(ctx):
    """8-savol: /etc dan ~/etc.tar.gz arxiv olish."""
    path = os.path.join(ctx["home"], "etc.tar.gz")
    if not os.path.isfile(path):
        return False
    try:
        with tarfile.open(path, "r:gz") as tf:
            names = tf.getnames()
    except Exception:
        return False
    has_etc_content = any(
        "os-release" in n or n.strip("/").split("/")[-1] == "etc" for n in names
    )
    return has_etc_content and len(names) > 5


def check_9(ctx):
    """9-savol: gzip paketini apt-mark hold qilish."""
    rc, out, _ = ctx["run"]("apt-mark showhold")
    return rc == 0 and "gzip" in out


def check_10(ctx):
    """10-savol: useradd bilan yangi user (home + /bin/bash)."""
    for u in _new_users(ctx):
        if u.pw_shell == "/bin/bash" and u.pw_dir.startswith("/home/") and os.path.isdir(u.pw_dir):
            return True
    return False


def check_11(ctx):
    """11-savol: find /etc -name os-release."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    # find/bfs o'zga (huquqsiz) papkalarga kira olmasa ham exit-kodni 1 qilib
    # qo'yishi mumkin, shu bilan birga to'g'ri natijani ham chiqaradi -- shu
    # sababli returncode emas, chiqishning o'zi solishtiriladi.
    _, out, _ = ctx["run"]("find /etc -name os-release")
    if not out.strip():
        return False
    return ctx["normalize"](ans) == ctx["normalize"](out)


def check_12(ctx):
    """12-savol: 'cron' xizmatining holatini (systemctl status) saqlash."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    low = ans.lower()
    return "cron" in low and ("active:" in low or "loaded:" in low)


def check_13(ctx):
    """13-savol: ~/my-file egasini root ga o'zgartirish."""
    path = os.path.join(ctx["home"], "my-file")
    try:
        return os.stat(path).st_uid == 0
    except FileNotFoundError:
        return False


def check_14(ctx):
    """14-savol: ~/my-file ga harflar orqali 555 (r-xr-xr-x) berish."""
    path = os.path.join(ctx["home"], "my-file")
    return _stat_mode(path) == 0o555


def check_15(ctx):
    """15-savol: ~/my-file2 ga raqamlar orqali 554 (r-xr-xr--) berish."""
    path = os.path.join(ctx["home"], "my-file2")
    return _stat_mode(path) == 0o554


def check_16(ctx):
    """16-savol: 'linux' nomli guruh yaratib, yangi useringizni qo'shish."""
    try:
        linux_group = grp.getgrnam("linux")
    except KeyError:
        return False
    new_usernames = {u.pw_name for u in _new_users(ctx)}
    members = set(linux_group.gr_mem)
    # a'zo bo'lgan userlardan kamida bittasi shu imtihon davomida
    # yaratilgan (yangi) user bo'lishi kerak
    return bool(members & new_usernames)


def check_17(ctx):
    """17-savol: 'ps aux | grep ssh' natijasini saqlash."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    lines = [l for l in ans.strip().splitlines() if l.strip()]
    return len(lines) >= 1 and all("ssh" in l.lower() for l in lines)


def check_18(ctx):
    """18-savol: ed25519 algoritmi bilan ssh kalit yaratish."""
    pub = os.path.join(ctx["home"], ".ssh", "id_ed25519.pub")
    priv = os.path.join(ctx["home"], ".ssh", "id_ed25519")
    if not (os.path.isfile(pub) and os.path.isfile(priv)):
        return False
    try:
        with open(pub) as f:
            content = f.read()
    except OSError:
        return False
    return content.startswith("ssh-ed25519")


def check_19(ctx):
    """19-savol: root crontabiga aniq yozuv qo'shish."""
    rc, out, _ = ctx["sudo_run"]("crontab -l -u root")
    if rc != 0:
        return False
    return "0 5 * * * /usr/bin/true" in out


def check_20(ctx):
    """20-savol: ko'rsatilgan PID'li jarayonni kill -9 bilan to'xtatish."""
    pid = ctx["state"].get("task20_pid")
    if not pid:
        return False
    stat_path = "/proc/%d/stat" % pid
    if not os.path.exists(stat_path):
        return True  # jarayon butunlay yo'q -- o'ldirilgan va reap qilingan
    try:
        with open(stat_path) as f:
            # format: "pid (comm) STATE ..." -- STATE 'Z' = zombie, ya'ni
            # jarayon allaqachon o'ldirilgan, faqat hali ota-jarayon
            # tomonidan "reap" qilinmagan (bu talabaga bog'liq emas).
            content = f.read()
        state_char = content.rsplit(")", 1)[-1].split()[0]
        return state_char == "Z"
    except (OSError, IndexError):
        return True


# ------------------------------------------------------------------
# Savollar ro'yxati
# ------------------------------------------------------------------
QUESTIONS = [
    _q(
        1, 3,
        "Uy (home) direktoriyangizga o'ting va joylashuvni ~/javoblar/1.txt "
        "fayliga yozing (masalan: cd ~ && pwd > ~/javoblar/1.txt)",
        check_1,
    ),
    _q(
        2, 3,
        "'tree -L 2 /' buyrug'i yordamida '/' direktoriyasining 2 qatlamini "
        "ko'ring, natijasini ~/javoblar/2.txt fayliga yozing",
        check_2,
    ),
    _q(
        3, 3,
        "'apt list' buyrug'i natijasini ekranga scroll qilinadigan holda "
        "('less' orqali) ko'ring, so'ng xuddi shu ro'yxatni "
        "~/javoblar/3.txt fayliga yozing",
        check_3,
    ),
    _q(
        4, 3,
        "/tmp direktoriyasida file1, file2 va file3 nomli fayllarni BITTA "
        "komanda bilan yarating (cd va ; ishlatish mumkin emas)",
        check_4,
    ),
    _q(
        5, 3,
        "/etc/passwd faylidan 'grep' orqali faqat '/bin/bash' bilan "
        "tugagan qatorlarni filtrlab, ~/javoblar/5.txt fayliga yozing",
        check_5,
    ),
    _q(
        6, 3,
        "/tmp ichida bir/ikki/uch nomli ichma-ich papkalarni BITTA komanda "
        "bilan yarating (cd va ; ishlatish mumkin emas)",
        check_6,
    ),
    _q(
        7, 3,
        "/etc papkani, ichidagi hammasi bilan, /tmp papkaga ko'chiring "
        "(backup nusxa)",
        check_7,
    ),
    _q(
        8, 3,
        "/etc papkadan, uy direktoriyangizga etc.tar.gz nomli arxiv oling "
        "(tar, gzip formatida)",
        check_8,
    ),
    _q(
        9, 3,
        "gzip nomli paketni keyingi upgrade'lardan olib tashlang "
        "('apt-mark hold')",
        check_9,
    ),
    _q(
        10, 3,
        "'useradd' yordamida istalgan nomli, home direktoriyasi va "
        "/bin/bash shell'iga ega yangi user yarating",
        check_10,
    ),
    _q(
        11, 3,
        "/etc ichidan os-release nomli faylni 'find' orqali qidiring, "
        "natijasini ~/javoblar/11.txt fayliga yozing",
        check_11,
    ),
    _q(
        12, 3,
        "'systemctl status'dan foydalanib 'cron' xizmatining holatini "
        "tekshiring, natijasini ~/javoblar/12.txt fayliga yozing",
        check_12,
    ),
    _q(
        13, 3,
        "~/my-file faylining user egasini root ga o'zgartiring ('chown')",
        check_13,
    ),
    _q(
        14, 3,
        "~/my-file fayliga harflar orqali (masalan: ugo=rx) r-xr-xr-x (555) "
        "ruxsatini bering",
        check_14,
    ),
    _q(
        15, 3,
        "~/my-file2 fayliga raqamlar orqali r-xr-xr-- (554) ruxsatini bering",
        check_15,
    ),
    _q(
        16, 3,
        "'linux' nomli yangi guruh yarating va 10-savolda yaratgan "
        "useringizni shu guruhga qo'shing ('usermod -aG' yoki 'gpasswd -a')",
        check_16,
    ),
    _q(
        17, 3,
        "Barcha jarayonlar orasidan 'ssh' so'zini 'grep' orqali filtrlab, "
        "~/javoblar/17.txt fayliga yozing",
        check_17,
    ),
    _q(
        18, 3,
        "ed25519 algoritmi bilan ssh kalit juftligi yarating",
        check_18,
    ),
    _q(
        19, 3,
        "Super user (root) crontabiga quyidagi yozuvni qo'shing: "
        "'0 5 * * * /usr/bin/true'",
        check_19,
    ),
    _q(
        20, 3,
        lambda state: (
            "PID={} bo'lgan jarayonni zudlik bilan to'xtatish komandasini "
            "bering".format(state.get("task20_pid", "?"))
        ),
        check_20,
    ),
]
