"""
Проверка AES.py по тестовому вектору FIPS-197 (без ручного ввода).
Запуск из папки lab_7:  python run_aes_selftest.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(HERE, "test_aes_input.txt")
EXPECTED_PATH = os.path.join(HERE, "test_aes_expected_fips.txt")

def main():
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        expected = f.read().strip().lower()

    with open(INPUT_PATH, encoding="utf-8") as f:
        stdin_text = f.read()

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "AES.py")],
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=HERE,
    )

    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"[0-9a-f]{32}", out, re.IGNORECASE)
    if not m:
        print("Не удалось найти hex-шифртекст в выводе программы.")
        print("--- вывод ---")
        print(out)
        sys.exit(1)

    got = m.group(0).lower()
    if got == expected:
        print("OK: шифртекст совпадает с FIPS-197:", got)
        sys.exit(0)

    print("ОШИБКА: ожидалось", expected)
    print("получено     ", got)
    sys.exit(1)

if __name__ == "__main__":
    main()
