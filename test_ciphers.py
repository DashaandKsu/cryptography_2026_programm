"""
Автоматическая проверка шифров на тексте из text.txt.
Шифрует и сразу расшифровывает — показывает что было, что получилось, совпало ли.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# --- загрузка текста -----------------------------------------------------------
TEXT_FILE = os.path.join(os.path.dirname(__file__), "text.txt")

def load_text():
    with open(TEXT_FILE, encoding="utf-8") as f:
        return f.read().strip()

# --- маркеры для A5/1, A5/2 (только буквы русского алфавита) ------------------
_A5_CODES = {
    "…":  "мнтч",  # троеточие — в первую очередь, до замены точки!
    ".":  "тчк",
    ",":  "зпт",
    ":":  "двтч",
    ";":  "тчзп",
    "!":  "вскл",
    "?":  "впрс",
    "–": "тир",   # en dash
    "—": "тир",   # em dash
    "-":  "тир",
    " ":  "прбл",
    "«":  "кавл",
    "»":  "кавп",
}

_A5_CODES_REV = {v: k for k, v in _A5_CODES.items()}

def a5_text_prepare(text: str) -> str:
    """Заменяем знаки препинания и пробелы маркерами, убираем ё."""
    text = text.replace("ё", "е").replace("Ё", "Е")
    for ch, code in _A5_CODES.items():
        text = text.replace(ch, code)
    return text.lower()

def a5_text_restore(text: str) -> str:
    """Восстанавливаем знаки из маркеров."""
    for code, ch in _A5_CODES_REV.items():
        text = text.replace(code, ch)
    return text

# --- AES: русский текст ↔ hex -------------------------------------------------
from lab_7.AES import AES as _AES_CLASS, prepare_text_for_enc, end_text_of_decr
from lab_7.AES import translate_to_hex as aes_to_hex, translate_from_hex as aes_from_hex

def aes_text_to_hex(text: str) -> str:
    """Подготовка текста к AES: маркеры + hex."""
    prepared = prepare_text_for_enc(text)
    return aes_to_hex(prepared)

def aes_hex_to_text(hex_str: str) -> str:
    """Из hex обратно в читаемый текст."""
    return end_text_of_decr(aes_from_hex(hex_str))

def aes_pad_hex(hex_str: str) -> str:
    """Дополняет hex до кратного 32 нулями справа."""
    rem = len(hex_str) % 32
    if rem:
        hex_str += "0" * (32 - rem)
    return hex_str

def aes_encrypt_text(text: str, key_hex: str) -> str:
    key_int = int(key_hex, 16)
    aes = _AES_CLASS(key_int)
    h = aes_text_to_hex(text)
    h = aes_pad_hex(h)
    result = ""
    for i in range(0, len(h), 32):
        block = int(h[i:i+32], 16)
        result += format(aes.encrypt(block), "032x")
    return result

def aes_decrypt_text(cipher_hex: str, key_hex: str) -> str:
    key_int = int(key_hex, 16)
    aes = _AES_CLASS(key_int)
    result_hex = ""
    for i in range(0, len(cipher_hex), 32):
        block = int(cipher_hex[i:i+32], 16)
        result_hex += format(aes.decrypt(block), "032x")
    # убираем нулевое дополнение справа
    result_hex = result_hex.rstrip("0")
    if len(result_hex) % 2 != 0:
        result_hex = "0" + result_hex
    return aes_hex_to_text(result_hex)

# --- ГОСТ Магма (lab_7) -------------------------------------------------------
from lab_7.MagmA import magma_encrypt as gost_enc_block, magma_decrypt as gost_dec_block
from lab_7.MagmA import pkcs7_pad, pkcs7_unpad
from lab_7.auxilary import split_by as lab7_split_by

def gost_magma_encrypt(text: str, key_hex: str) -> str:
    raw = text.encode("utf-8")
    raw_padded = pkcs7_pad(raw, 8)
    hex_str = raw_padded.hex()
    blocks = lab7_split_by(hex_str, 16)
    return "".join(hex(gost_enc_block(b, key_hex))[2:].zfill(16) for b in blocks)

def gost_magma_decrypt(cipher_hex: str, key_hex: str) -> str:
    blocks = lab7_split_by(cipher_hex, 16)
    dec_hex = "".join(hex(gost_dec_block(b, key_hex))[2:].zfill(16) for b in blocks)
    plain = pkcs7_unpad(bytearray.fromhex(dec_hex))
    return plain.decode("utf-8")

# --- RSA -----------------------------------------------------------------------
from lab_8.RSA import encrypt as rsa_enc, des as rsa_dec, modinv, phi, prepare_text as rsa_prepare, restore_text as rsa_restore

# --- A5/1, A5/2 ----------------------------------------------------------------
from lab_6 import utils as lab6_utils
from lab_6.A5 import encrypt_decrypt as a5_enc_dec
from lab_6.A52 import encrypt_decrypt as a52_enc_dec

# --- Шеннон --------------------------------------------------------------------
from lab_5.shenon import shenon, check_conditions

# ==============================================================================
# Вспомогательные функции вывода (стиль main.py)
# ==============================================================================

SEP = "=" * 50

def header(title: str):
    print()
    print(SEP)
    print(f"  {title}")
    print(SEP)

def ok_or_fail(original: str, restored: str) -> str:
    return "✓ Совпадает" if original == restored else "✗ НЕ совпадает"

def show_result(original: str, encrypted, decrypted: str, compare_with: str = None, note: str = ""):
    """
    original       — исходный текст (для отображения)
    encrypted      — зашифрованный текст
    decrypted      — расшифрованный текст
    compare_with   — с чем сравниваем (если None — с original)
    note           — пояснение почему compare_with отличается от original
    """
    print(f"\nИсходный текст (начало):\n  {original[:80]}...")
    print(f"\nЗашифрованный текст (начало):\n  {str(encrypted)[:120]}...")
    print(f"\nРасшифрованный текст (начало):\n  {decrypted[:80]}...")
    target = compare_with if compare_with is not None else original
    status = ok_or_fail(target, decrypted)
    if note:
        print(f"\nПроверка: {status}  [{note}]")
    else:
        print(f"\nПроверка: {status}")


def run_all():
    text = load_text()
    print(SEP)
    print("  АВТОПРОВЕРКА ШИФРОВ")
    print(f"  Длина текста: {len(text)} символов")
    print(SEP)

    # ------------------------------------------------------------------
    # 1. Шеннон (шифр 18 в main.py)
    # ------------------------------------------------------------------
    header("Шифр Шеннона (lab_5/shenon.py)")
    t0, a, c, m = 7, 5, 3, 37
    print(f"Параметры: T0={t0}, a={a}, c={c}, m={m}")
    ok, errors, warnings = check_conditions(a, c, m, t0)
    if not ok:
        print("Ошибка параметров:", errors)
    else:
        if warnings:
            for w in warnings:
                print("  Предупреждение:", w)
        encrypted_parts = shenon(text, t0, a, c, m)
        encrypted_str = " ".join(encrypted_parts)
        encrypted_clean = encrypted_str.replace(" ", "")
        decrypted_parts = shenon(encrypted_clean, t0, a, c, m, k=1)
        decrypted = "".join(decrypted_parts)
        # shenon внутри делает preprocess (нижний регистр, ё→е, маркеры) — берём это за эталон
        from lab_5.shenon import preprocess_text as shenon_preprocess, postprocess_text as shenon_postprocess
        shenon_reference = shenon_postprocess(
            ''.join([ch for ch in shenon_preprocess(text) if ch in "абвгдежзийклмнопрстуфхцчшщъыьэюя"])
        )
        show_result(text, encrypted_str, decrypted,
                    compare_with=shenon_reference,
                    note="сравниваем с текстом после preprocess Шеннона (нижний регистр, ё→е)")

    # ------------------------------------------------------------------
    # 2. ГОСТ Магма lab_7 (шифр 17 в main.py)
    # ------------------------------------------------------------------
    header("ГОСТ 28147-89 Магма (lab_7/MagmA.py)")
    gost_key = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    print(f"Ключ (256 бит): {gost_key}")
    try:
        enc_gost = gost_magma_encrypt(text, gost_key)
        dec_gost = gost_magma_decrypt(enc_gost, gost_key)
        show_result(text, enc_gost, dec_gost)
    except Exception as e:
        print(f"Ошибка: {e}")

    # ------------------------------------------------------------------
    # 3. AES (шифр 21 в main.py)
    # ------------------------------------------------------------------
    header("AES-128 (lab_7/AES.py)")
    aes_key = "2b7e151628aed2a6abf7158809cf4f3c"
    print(f"Ключ (128 бит): {aes_key}")
    try:
        enc_aes = aes_encrypt_text(text, aes_key)
        dec_aes = aes_decrypt_text(enc_aes, aes_key)
        # AES prepare_text переводит в нижний регистр и заменяет знаки маркерами — берём за эталон
        aes_reference = end_text_of_decr(prepare_text_for_enc(text))
        show_result(text, enc_aes, dec_aes,
                    compare_with=aes_reference,
                    note="сравниваем с текстом после prepare_text AES (нижний регистр)")
    except Exception as e:
        print(f"Ошибка: {e}")

    # ------------------------------------------------------------------
    # 4. RSA (шифр 24 в main.py)
    #    Берём небольшие простые — хватит чтобы n > 32 и n > len(alphabet)
    #    Для демонстрации: p=61, q=53 → n=3233, phi=3120, e=17, d=2753
    # ------------------------------------------------------------------
    header("RSA (lab_8/RSA.py)")
    p_rsa, q_rsa = 61, 53
    n_rsa = p_rsa * q_rsa
    phi_rsa = phi(p_rsa, q_rsa)
    e_rsa = 17
    d_rsa = modinv(e_rsa, phi_rsa)
    print(f"p={p_rsa}, q={q_rsa}, n={n_rsa}, e={e_rsa}, d={d_rsa}")
    try:
        enc_rsa = rsa_enc(text, n_rsa, e_rsa)
        dec_rsa = rsa_dec(enc_rsa, n_rsa, d_rsa)
        # RSA prepare_text: нижний регистр, ё→е, маркеры — берём за эталон
        rsa_reference = rsa_restore(rsa_prepare(text))
        show_result(text, enc_rsa, dec_rsa,
                    compare_with=rsa_reference,
                    note="сравниваем с текстом после prepare RSA (нижний регистр, ё→е)")
    except Exception as e:
        print(f"Ошибка: {e}")

    # ------------------------------------------------------------------
    # 5. A5/1 (шифр 15 в main.py)
    # ------------------------------------------------------------------
    header("A5/1 (lab_6/A5.py)")
    a5_key = "абвгдежзийклм"   # 13 букв × 5 бит = 65 бит → берём первые 64
    a5_frame = 42
    print(f"Ключ: {a5_key}  Кадр: {a5_frame}")
    print("(пробелы и знаки препинания заменяются маркерами и обратно)")
    try:
        text_prepared = a5_text_prepare(text)
        enc_a5 = a5_enc_dec(text_prepared, a5_key, a5_frame)
        # A5 возвращает верхний регистр → приводим к нижнему перед restore маркеров
        dec_a5_raw = a5_enc_dec(enc_a5, a5_key, a5_frame).lower()
        dec_a5 = a5_text_restore(dec_a5_raw)
        # эталон — текст после a5_prepare (нижний регистр, ё→е, маркеры восстановлены)
        a5_reference = a5_text_restore(text_prepared)
        show_result(text, enc_a5, dec_a5,
                    compare_with=a5_reference,
                    note="сравниваем с текстом после подготовки: нижний регистр, ё→е")
    except Exception as e:
        print(f"Ошибка: {e}")

    # ------------------------------------------------------------------
    # 6. A5/2 (шифр 16 в main.py)
    # ------------------------------------------------------------------
    header("A5/2 (lab_6/A52.py)")
    print(f"Ключ: {a5_key}  Кадр: {a5_frame}")
    print("(пробелы и знаки препинания заменяются маркерами и обратно)")
    try:
        text_prepared = a5_text_prepare(text)
        enc_a52 = a52_enc_dec(text_prepared, a5_key, a5_frame)
        dec_a52_raw = a52_enc_dec(enc_a52, a5_key, a5_frame).lower()
        dec_a52 = a5_text_restore(dec_a52_raw)
        a52_reference = a5_text_restore(text_prepared)
        show_result(text, enc_a52, dec_a52,
                    compare_with=a52_reference,
                    note="сравниваем с текстом после подготовки: нижний регистр, ё→е")
    except Exception as e:
        print(f"Ошибка: {e}")

    # ------------------------------------------------------------------
    print()
    print(SEP)
    print("  Проверка завершена.")
    print(SEP)


if __name__ == "__main__":
    run_all()
