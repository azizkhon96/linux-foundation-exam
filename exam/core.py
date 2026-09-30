"""
Umumiy imtihon dvigateli (engine).

Bu fayl barcha modullar (module1, module2, ...) uchun umumiy va o'zgarmaydi.
Har bir modul faqat o'zining `questions.py` faylini yozadi (savollar ro'yxati +
tekshiruv funksiyalari) va shu Engine klassini chaqiradi.

Talabalarga tarqatishda bu fayl `exam/module*/questions.py` bilan birga
pyarmor orqali shifrlanadi (qarang: build.sh). Shuning uchun bu yerga
yozilgan matnlar (savol matnlari, javoblar) talabaga ko'rinmaydi.
"""
import getpass
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from os.path import expanduser

HOME = expanduser("~")

# pyarmor shifrlagach bu qiymat bytecode ichida yashiringan bo'ladi.
# U faqat report.json faylini tasodifiy tahrirlashdan saqlash uchun ishlatiladi --
# YAKUNIY (haqiqiy) baholash har doim "grade" rejimidagi LIVE tekshiruvdir,
# shuning uchun bu kalitning oshkor bo'lishi baholash xavfsizligiga ta'sir qilmaydi.
_SECRET = b"linux-foundation-exam-report-key-v1"


def _sign(data: bytes) -> str:
    return hmac.new(_SECRET, data, hashlib.sha256).hexdigest()


def run(cmd, timeout=15):
    """Komandani shell orqali ishga tushiradi. (returncode, stdout, stderr) qaytaradi."""
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)


def sudo_run(cmd, timeout=30):
    """Root huquqi kerak bo'lgan tekshiruvlar uchun (masalan: root crontabini o'qish).

    Interaktiv terminalda `sudo` parolni to'g'ridan-to'g'ri tty'dan so'raydi,
    shuning uchun bu chaqiruv `submit` jarayonida parol so'rashi mumkin -- bu
    kutilgan holat.
    """
    return run("sudo -n " + cmd + " 2>/dev/null || sudo " + cmd, timeout=timeout)


def normalize(text):
    """Ortiqcha probel/bo'sh qatorlardagi farqlarni yumshatish uchun."""
    lines = [ln.strip() for ln in text.strip().splitlines()]
    return "\n".join(ln for ln in lines if ln != "")


def read_answer(home, task_id):
    path = os.path.join(home, "javoblar", "%s.txt" % task_id)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except OSError:
        return None


class Engine:
    def __init__(self, module_name, questions, setup_fn=None):
        self.module_name = module_name
        self.questions = questions
        self.setup_fn = setup_fn
        self.state_dir = os.path.join(HOME, ".exam", module_name)
        self.state_path = os.path.join(self.state_dir, "state.json")
        self.report_path = os.path.join(self.state_dir, "report.json")
        self.answers_dir = os.path.join(HOME, "javoblar")

    # ---------------- holat (state) ----------------
    def _load_state(self):
        if os.path.isfile(self.state_path):
            try:
                with open(self.state_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_state(self, state):
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    # ---------------- birinchi marta ishga tushirish ----------------
    def _first_time_setup(self):
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.answers_dir, exist_ok=True)
        state = {"started_at": time.time(), "submitted": False}
        if self.setup_fn:
            extra = self.setup_fn(HOME) or {}
            state.update(extra)
        self._save_state(state)
        self._ensure_submit_command()
        return state

    def _ensure_submit_command(self):
        """`~/bin/submit` komandasini yaratadi va uni PATH'ga qo'shadi (bir marta)."""
        bin_dir = os.path.join(HOME, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        submit_path = os.path.join(bin_dir, "submit")
        entry = os.path.abspath(sys.argv[0])
        script = "#!/bin/bash\nexec python3 %s --submit\n" % entry
        with open(submit_path, "w") as f:
            f.write(script)
        os.chmod(submit_path, 0o755)

        bashrc = os.path.join(HOME, ".bashrc")
        marker_begin = "# >>> exam-engine (%s) >>>" % self.module_name
        marker_end = "# <<< exam-engine (%s) <<<" % self.module_name
        try:
            with open(bashrc) as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        if marker_begin not in content:
            with open(bashrc, "a") as f:
                f.write(
                    "\n%s\nexport PATH=\"$HOME/bin:$PATH\"\n%s\n"
                    % (marker_begin, marker_end)
                )

    # ---------------- vazifalar ro'yxatini chiqarish ----------------
    def _question_text(self, q, state):
        text = q["text"]
        return text(state) if callable(text) else text

    def _print_tasks(self, state):
        print()
        print("=" * 64)
        print(" %s -- Imtihon topshiriqlari" % self.module_name.upper())
        print("=" * 64)
        for q in self.questions:
            print("\n%2d-savol (%d ball): %s" % (q["id"], q["points"], self._question_text(q, state)))
        print()
        print("-" * 64)
        if state.get("submitted"):
            print("Siz ushbu imtihonni allaqachon YAKUNIY topshirgansiz.")
            print("Qayta topshirib bo'lmaydi.")
        else:
            print("Ishlaringiz tugagach, terminalga shunchaki quyidagini yozing:\n")
            print("    submit\n")
            print("DIQQAT: 'submit' FAQAT BIR MARTA ishlaydi va uni qaytarib bo'lmaydi.")
        print("-" * 64)
        print()

    # ---------------- tekshirish ----------------
    def _make_ctx(self, q, state):
        return {
            "home": HOME,
            "state": state,
            "read_answer": (lambda tid=q["id"]: read_answer(HOME, tid)),
            "run": run,
            "sudo_run": sudo_run,
            "normalize": normalize,
        }

    def _run_checks(self, state, verbose=False):
        results = []
        total = 0
        maxtotal = 0
        for q in self.questions:
            maxtotal += q["points"]
            ctx = self._make_ctx(q, state)
            try:
                ok = bool(q["check"](ctx))
            except Exception as e:
                ok = False
                if verbose:
                    print("  [xato] %s-savolni tekshirishda ichki xatolik: %s" % (q["id"], e))
            pts = q["points"] if ok else 0
            total += pts
            results.append({"id": q["id"], "points": pts, "max": q["points"], "passed": ok})
            if verbose:
                mark = " OK " if ok else "YO'Q"
                print("  %2d-savol [%s] %d/%d ball" % (q["id"], mark, pts, q["points"]))
        return results, total, maxtotal

    def _save_report(self, results, total, maxtotal):
        report = {
            "module": self.module_name,
            "user": getpass.getuser(),
            "submitted_at": time.time(),
            "total": total,
            "max": maxtotal,
            "results": results,
        }
        raw = json.dumps(report, sort_keys=True).encode()
        report["signature"] = _sign(raw)
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=2)
        try:
            os.chmod(self.report_path, 0o600)
        except OSError:
            pass

    # ---------------- submit (talaba uchun, faqat bir marta) ----------------
    def do_submit(self):
        state = self._load_state()
        if not state:
            print("Xato: imtihon hali boshlanmagan.")
            sys.exit(1)
        if state.get("submitted"):
            print("Xato: bu imtihon allaqachon yakuniy topshirilgan. Qayta topshirib bo'lmaydi.")
            sys.exit(1)

        print("DIQQAT: 'submit' FAQAT BIR MARTA ishlaydi va uni qaytarib bo'lmaydi.")
        try:
            answer = input("Rostdan ham yakuniy topshirmoqchimisiz? (ha/yo'q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBekor qilindi. Hech narsa topshirilmadi.")
            sys.exit(0)
        if answer not in ("ha", "ha.", "yes", "y"):
            print("Bekor qilindi. Hech narsa topshirilmadi.")
            sys.exit(0)

        results, total, maxtotal = self._run_checks(state, verbose=False)
        self._save_report(results, total, maxtotal)
        state["submitted"] = True
        state["submitted_at"] = time.time()
        self._save_state(state)

        print()
        print("Ishingiz muvaffaqiyatli topshirildi.")
        print("Natija faqat instruktorga ko'rinadi. Omad tilaymiz!")

    # ---------------- grade (faqat instruktor uchun, LIVE tekshiruv) ----------------
    def do_grade(self):
        state = self._load_state()
        if not state:
            print("Bu foydalanuvchida hali imtihon boshlanmagan (holat topilmadi).")
            sys.exit(1)

        print("=== %s: LIVE tekshiruv (instruktor rejimi) ===" % self.module_name)
        results, total, maxtotal = self._run_checks(state, verbose=True)
        print()
        print("Umumiy ball (LIVE): %d / %d" % (total, maxtotal))

        if state.get("submitted"):
            print("Talaba 'submit' qilgan vaqt: %s" % time.ctime(state.get("submitted_at", 0)))
        else:
            print("DIQQAT: talaba hali 'submit' qilmagan!")

        if os.path.isfile(self.report_path):
            with open(self.report_path) as f:
                saved = json.load(f)
            sig = saved.pop("signature", None)
            raw = json.dumps(saved, sort_keys=True).encode()
            valid = sig is not None and hmac.compare_digest(sig, _sign(raw))
            print()
            print("Saqlangan report.json imzosi: %s" % ("TO'G'RI" if valid else "NOTO'G'RI / TAHRIRLANGAN!"))
            print("Saqlangan (submit paytidagi) natija: %d / %d" % (saved.get("total", -1), saved.get("max", -1)))
            print("(Eslatma: yakuniy baho sifatida yuqoridagi LIVE natijadan foydalaning.)")

    def do_status(self):
        state = self._load_state()
        if not state:
            print("Holat: imtihon hali boshlanmagan.")
        elif state.get("submitted"):
            print("Holat: TOPSHIRILGAN (%s)" % time.ctime(state.get("submitted_at", 0)))
        else:
            print("Holat: hali topshirilmagan.")

    # ---------------- asosiy kirish nuqtasi ----------------
    def main(self, argv=None):
        argv = argv if argv is not None else sys.argv[1:]

        if "--submit" in argv:
            self.do_submit()
            return
        if "--grade" in argv:
            self.do_grade()
            return
        if "--status" in argv:
            self.do_status()
            return

        state = self._load_state()
        if not state:
            state = self._first_time_setup()

        self._print_tasks(state)

        # DIQQAT: submit qilingan bo'lsa ham bashga tushiramiz -- aks holda
        # talaba qaytadan SSH bilan kirganda (masalan tasodifan uzilib
        # qolsa) darhol sessiyasi yopilib, o'z akkauntidan butunlay
        # chetlanib qoladi (chunki bu jarayon .bash_profile orqali `exec`
        # bilan chaqirilgan -- login shell'ning o'rnini bosgan).
        if os.environ.get("EXAM_NO_EXEC") != "1":
            os.execvp("bash", ["bash"])
