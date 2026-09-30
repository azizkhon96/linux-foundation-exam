"""
1-modul: savollar va ularning tekshiruv qoidalari.

Savollar kurs materiallariga (materials/1-modul/, ayniqsa Vazifalar-matni.txt
va Amaliyot-1.txt) so'zma-so'z moslab tuzilgan: fayl tizimi/navigatsiya,
filtrlar (grep), arxivlash, user/group, ruxsatlar, paket boshqaruvi, find,
servis, ssh, cron, protsess boshqaruvi.

MUHIM QOIDA: savol matnida hech qachon "BITTA komanda bilan" yoki "HARFLAR
orqali" / "RAQAMLAR orqali" kabi USUL (qanday bajarilgani) haqida talab
qo'yilmasin -- tekshiruv faqat YAKUNIY holatga (fayl bormi, ruxsat
to'g'rimi va h.k.) asoslangani uchun, QANDAY bajarilganini bilib bo'lmaydi.
Faqat NATIJA tavsiflansin.

YANGI SAVOL QO'SHISH: pastdagi QUESTIONS ro'yxatiga yangi `_q(...)` qatori
qo'shing va unga mos `check_N` funksiyasini yozing.

Har bir `check_*` funksiyasi `ctx` (context) dict qabul qiladi:
    ctx["home"]         -- talabaning uy direktoriyasi
    ctx["state"]        -- shu modul uchun saqlangan holat
    ctx["read_answer"]  -- ~/javoblar/<savol_id>.txt faylini o'qiydi
    ctx["run"](cmd)     -- komandani ishga tushiradi: (returncode, stdout, stderr)
    ctx["sudo_run"](cmd)-- xuddi shu, lekin 'sudo' bilan
    ctx["normalize"](s) -- ortiqcha probel/bo'sh qatorlarni yumshatadi
"""
import os
import re
import shutil
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

    # 10-savol uchun: useradd bilan YANGI qo'shilgan userni aniqlash uchun
    # boshlang'ich (mavjud) userlar ro'yxatini eslab qolamiz.
    extra["baseline_users"] = sorted(u.pw_name for u in pwd.getpwall())

    # 5-savol uchun: grep natijasi /etc/passwd ga YANGI user qo'shilishidan
    # (10-savol) OLDIN yoki KEYIN bajarilishidan qat'iy nazar bir xil
    # bo'lishi uchun, "/bin/bash" shell'iga ega userlar ro'yxatini HOZIROQ
    # eslab qolamiz.
    extra["baseline_bash_users"] = sorted(
        u.pw_name for u in pwd.getpwall() if u.pw_shell == "/bin/bash"
    )

    # 20-savol uchun: 'examdaemon' nomli, killall/pkill orqali nomi bo'yicha
    # to'xtatiladigan haqiqiy fon jarayon yaratamiz.
    daemon_dir = os.path.join(home, ".exam", "module1")
    os.makedirs(daemon_dir, exist_ok=True)
    daemon_path = os.path.join(daemon_dir, "examdaemon")
    try:
        shutil.copy("/bin/sleep", daemon_path)
        os.chmod(daemon_path, 0o755)
        subprocess.Popen(
            [daemon_path, "100000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass

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


def _student_username(ctx):
    """Talabaning o'z username'i -- provisioning HOME=/home/<user> qilib
    sozlagani uchun, home yo'lining oxirgi qismidan olinadi (bu --grade
    root sifatida ishga tushirilganda ham to'g'ri ishlaydi)."""
    return os.path.basename(ctx["home"].rstrip("/"))


# ------------------------------------------------------------------
# Tekshiruv funksiyalari
# ------------------------------------------------------------------
def check_1(ctx):
    """1-savol: uy direktoriyasiga qaytib, joriy direktoriyani chiqarish."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    return ans.strip() == ctx["home"]


def check_2(ctx):
    """2-savol: 'tree' bilan '/' direktoriyasining 2 qatlamini ko'rish."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
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
    """3-savol: o'rnatilgan (installed) paketlar ro'yxati."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    lines = [l for l in ans.strip().splitlines() if l.strip()]
    if len(lines) < 20:
        return False
    pattern = re.compile(r"^\S+/\S+[, ].*\[installed")
    matched = sum(1 for l in lines if pattern.search(l))
    return matched >= len(lines) * 0.9


# --- 4-savol: 'kitoblar/' fayl-papka arxitekturasi ---
_KITOBLAR = {
    "afsona": ["olmos_tosh", "suv_parilari", "yashirin_orol"],
    "ertak": ["bilmasvoyning_sarguzashtlari", "bugirsoq", "echki_bolalari", "sariq_devni_minib"],
    "fantastik": ["batman", "robot", "urgimchak_odam"],
    "roman": ["graf_monte_kristo", "ikki_eshik_orasi", "temir_niqob"],
}


def check_4(ctx):
    """4-savol: 'kitoblar' papka arxitekturasini yaratish."""
    base = os.path.join(ctx["home"], "kitoblar")
    if not os.path.isdir(base):
        return False
    for folder, files in _KITOBLAR.items():
        if not os.path.isdir(os.path.join(base, folder)):
            return False
        for fname in files:
            if not os.path.isfile(os.path.join(base, folder, fname)):
                return False
    return True


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
        found.add(line.split(":", 1)[0])
    current_bash_users = {
        u.pw_name for u in pwd.getpwall() if u.pw_shell == "/bin/bash"
    }
    # Talaba bu savolni 10-savoldan OLDIN ham, KEYIN ham bajargan bo'lishi
    # mumkin -- ikkalasi ham haqiqatan to'g'ri javob.
    return baseline <= found <= current_bash_users


def check_6(ctx):
    """6-savol: dir1/dir2/dir3/dir4 ichma-ich papkalar."""
    return os.path.isdir(os.path.join(ctx["home"], "dir1", "dir2", "dir3", "dir4"))


def check_7(ctx):
    """7-savol: /etc dan ~/etc.tar.xz arxiv olish (xz formatida)."""
    path = os.path.join(ctx["home"], "etc.tar.xz")
    if not os.path.isfile(path):
        return False
    try:
        with tarfile.open(path, "r:xz") as tf:
            names = tf.getnames()
    except Exception:
        return False
    has_etc_content = any(
        "os-release" in n or n.strip("/").split("/")[-1] == "etc" for n in names
    )
    return has_etc_content and len(names) > 5


def check_8(ctx):
    """8-savol: /etc dan ~/etc.tar.gz arxiv olish (gzip formatida)."""
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
    """9-savol: gzip paketini apt orqali hold qilish."""
    rc, out, _ = ctx["run"]("apt-mark showhold")
    return rc == 0 and "gzip" in out


def check_10(ctx):
    """10-savol: useradd bilan yangi user (home + /bin/bash)."""
    for u in _new_users(ctx):
        if u.pw_shell == "/bin/bash" and u.pw_dir.startswith("/home/") and os.path.isdir(u.pw_dir):
            return True
    return False


def check_11(ctx):
    """11-savol: find /etc -size +100k."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    _, out, _ = ctx["run"]("find /etc -type f -size +100k")
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
    """13-savol: 'my-file' yaratib, uning user VA guruh egasini bitta
    komanda bilan 'root' ga o'zgartirish (mustaqil, boshqa savolga
    bog'liq emas)."""
    path = os.path.join(ctx["home"], "my-file")
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return False
    return st.st_uid == 0 and st.st_gid == 0


# --- 14/15-savollar: bir nechta fayl, bir nechta ruxsat qiymati ---
_LETTER_PERMS = {"perm-a": 0o777, "perm-b": 0o754, "perm-c": 0o660}
_NUMBER_PERMS = {"perm-x": 0o555, "perm-y": 0o711, "perm-z": 0o440}


def check_14(ctx):
    """14-savol: 3 ta faylga turli ruxsatlar berish."""
    home = ctx["home"]
    return all(_stat_mode(os.path.join(home, f)) == m for f, m in _LETTER_PERMS.items())


def check_15(ctx):
    """15-savol: yana 3 ta faylga turli ruxsatlar berish."""
    home = ctx["home"]
    return all(_stat_mode(os.path.join(home, f)) == m for f, m in _NUMBER_PERMS.items())


def check_16(ctx):
    """16-savol: 'linux' guruhini yaratib, O'ZINI shu guruhga qo'shish
    (mustaqil, boshqa savolga bog'liq emas)."""
    try:
        linux_group = grp.getgrnam("linux")
    except KeyError:
        return False
    username = _student_username(ctx)
    if username in linux_group.gr_mem:
        return True
    # asosiy (primary) guruh sifatida ham qabul qilinadi
    try:
        return pwd.getpwnam(username).pw_gid == linux_group.gr_gid
    except KeyError:
        return False


def check_17(ctx):
    """17-savol: sshd protsessining PID'ini pidof/pgrep orqali topish."""
    ans = ctx["read_answer"]()
    if not ans:
        return False
    tokens = ans.split()
    if not tokens:
        return False
    found_valid = False
    for tok in tokens:
        if not tok.isdigit():
            return False
        try:
            with open("/proc/%s/comm" % tok) as f:
                comm = f.read().strip()
        except OSError:
            continue
        if "sshd" in comm:
            found_valid = True
    return found_valid


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
    """19-savol: root crontabiga @daily maxsus vaqt belgisi bilan yozuv
    qo'shish."""
    rc, out, _ = ctx["sudo_run"]("crontab -l -u root")
    if rc != 0:
        return False
    pattern = re.compile(r"^\s*@daily\s+.*\btrue\b", re.MULTILINE)
    return bool(pattern.search(out))


def check_20(ctx):
    """20-savol: 'examdaemon' nomli jarayonni NOMI orqali (killall/pkill)
    to'xtatish."""
    for pid_dir in os.listdir("/proc"):
        if not pid_dir.isdigit():
            continue
        try:
            with open("/proc/%s/comm" % pid_dir) as f:
                comm = f.read().strip()
        except OSError:
            continue
        if comm != "examdaemon":
            continue
        try:
            with open("/proc/%s/stat" % pid_dir) as f:
                content = f.read()
            state_char = content.rsplit(")", 1)[-1].split()[0]
        except (OSError, IndexError):
            return False
        if state_char != "Z":
            return False
    return True


# ------------------------------------------------------------------
# Savollar ro'yxati
# ------------------------------------------------------------------
QUESTIONS = [
    _q(
        1, 3,
        "Uy (home) direktoriyangizga qaytib, joriy direktoriyani ekranga "
        "chiqarish buyrug'ini yozing va natijani ~/javoblar/1.txt fayliga "
        "yo'naltiring (> orqali)",
        check_1,
    ),
    _q(
        2, 3,
        "'tree' buyrug'idan foydalanib, '/' (root) direktoriyasi ichidagi "
        "papkalarning FAQAT 2 qatlam chuqurlikdagi tarkibini ko'ring va "
        "natijani ~/javoblar/2.txt fayliga yo'naltiring (> orqali)",
        check_2,
    ),
    _q(
        3, 3,
        "'apt' yordamida tizimingizga hozircha O'RNATILGAN (installed) "
        "paketlar ro'yxatini ko'ring, natijani ~/javoblar/3.txt fayliga "
        "yo'naltiring (> orqali)",
        check_3,
    ),
    _q(
        4, 3,
        "Uy direktoriyangizda quyidagi papka-fayl arxitekturasini yarating "
        "(oxirida turgan nomlar -- fayl, boshqalari -- papka):\n"
        "    kitoblar/\n"
        "    +-- afsona\n"
        "    |   +-- olmos_tosh\n"
        "    |   +-- suv_parilari\n"
        "    |   +-- yashirin_orol\n"
        "    +-- ertak\n"
        "    |   +-- bilmasvoyning_sarguzashtlari\n"
        "    |   +-- bugirsoq\n"
        "    |   +-- echki_bolalari\n"
        "    |   +-- sariq_devni_minib\n"
        "    +-- fantastik\n"
        "    |   +-- batman\n"
        "    |   +-- robot\n"
        "    |   +-- urgimchak_odam\n"
        "    +-- roman\n"
        "        +-- graf_monte_kristo\n"
        "        +-- ikki_eshik_orasi\n"
        "        +-- temir_niqob",
        check_4,
    ),
    _q(
        5, 3,
        "/etc/passwd faylidan 'grep' orqali faqat '/bin/bash' bilan "
        "tugagan qatorlarni filtrlab, ~/javoblar/5.txt fayliga yo'naltiring "
        "(> orqali)",
        check_5,
    ),
    _q(
        6, 3,
        "Uy direktoriyangizda dir1/dir2/dir3/dir4 ko'rinishidagi ichma-ich "
        "papkalarni yarating",
        check_6,
    ),
    _q(
        7, 3,
        "/etc papkadan, uy direktoriyangizga etc.tar.xz nomli arxiv oling "
        "(tar, xz formatida)",
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
        "gzip nomli paketni keyingi upgrade'lardan apt orqali olib "
        "tashlang",
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
        "'find' buyrug'i yordamida /etc ichidan hajmi 100KB dan katta "
        "bo'lgan fayllarni toping, natijasini ~/javoblar/11.txt fayliga "
        "yo'naltiring (> orqali)",
        check_11,
    ),
    _q(
        12, 3,
        "'systemctl status'dan foydalanib 'cron' xizmatining holatini "
        "tekshiring, natijasini ~/javoblar/12.txt fayliga yo'naltiring "
        "(> orqali)",
        check_12,
    ),
    _q(
        13, 3,
        "Uy direktoriyangizda 'my-file' nomli bo'sh fayl yarating, so'ng "
        "uning HAM user, HAM guruh egasini BITTA komanda bilan 'root'ga "
        "o'zgartiring (masalan: chown user:group fayl)",
        check_13,
    ),
    _q(
        14, 3,
        "Uy direktoriyangizda perm-a, perm-b, perm-c nomli fayllar "
        "yarating va ularga mos ravishda quyidagi ruxsatlarni bering: "
        "perm-a: rwxrwxrwx; perm-b: rwxr-xr--; perm-c: rw-rw----",
        check_14,
    ),
    _q(
        15, 3,
        "Uy direktoriyangizda perm-x, perm-y, perm-z nomli fayllar "
        "yarating va ularga mos ravishda quyidagi ruxsatlarni bering: "
        "perm-x: 555; perm-y: 711; perm-z: 440",
        check_15,
    ),
    _q(
        16, 3,
        "'linux' nomli yangi guruh yarating va O'ZINGIZNI shu guruhga "
        "qo'shing ('usermod -aG' yoki 'gpasswd -a')",
        check_16,
    ),
    _q(
        17, 3,
        "'sshd' protsessining PID (protsess raqami)ni FAQAT raqam holida "
        "('pidof' yoki 'pgrep' orqali) aniqlang, natijani ~/javoblar/17.txt "
        "fayliga yo'naltiring (> orqali)",
        check_17,
    ),
    _q(
        18, 3,
        "ed25519 algoritmi bilan ssh kalit juftligi yarating",
        check_18,
    ),
    _q(
        19, 3,
        "Super user (root) crontabiga @daily maxsus vaqt belgisi bilan "
        "/usr/bin/true buyrug'ini bajaradigan vazifa qo'shing (masalan: "
        "'@daily /usr/bin/true')",
        check_19,
    ),
    _q(
        20, 3,
        "Sizning hisobingiz ostida 'examdaemon' nomli fon jarayon ishga "
        "tushirilgan. Uni PID orqali EMAS, balki NOMI orqali ('killall' "
        "yoki 'pkill' bilan) to'xtating",
        check_20,
    ),
]
