# Шифр Виженера: самоключ (гамма = ключ + открытый текст) и шифртекст (гамма = ключ + шифртекст). Ключ — одна буква.

from lab_1.atbash import (
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

# Режимы: "самоключ" (autokey) — гамма = ключ + открытый текст; "шифртекст" — гамма = ключ + шифртекст
MODE_AUTOKEY = 1
MODE_CIPHERTEXT = 2


def _check_key_letter(key):
    """Ключ — одна буква алфавита."""
    key = key.strip().lower()
    if len(key) != 1 or key not in RUS_ALPHABET:
        raise ValueError("Ключ должен быть одной буквой русского алфавита.")
    return key


def _encrypt_autokey(text, key_letter):
    """Самоключ: гамма = ключ + открытый текст."""
    n = len(RUS_ALPHABET)
    gamma = [key_letter] + [c for c in text if c in RUS_ALPHABET]
    out = []
    j = 0
    for c in text:
        if c in RUS_ALPHABET:
            ti = RUS_ALPHABET.index(c)
            gi = RUS_ALPHABET.index(gamma[j])
            out.append(RUS_ALPHABET[(ti + gi) % n])
            j += 1
        else:
            out.append(c)
    return "".join(out)


def _decrypt_autokey(text, key_letter):
    """Самоключ: гамма восстанавливается по открытому тексту."""
    n = len(RUS_ALPHABET)
    gamma = [key_letter]
    out = []
    for c in text:
        if c in RUS_ALPHABET:
            si = RUS_ALPHABET.index(c)
            gi = RUS_ALPHABET.index(gamma[-1])
            ti = (si - gi) % n
            letter = RUS_ALPHABET[ti]
            out.append(letter)
            gamma.append(letter)
        else:
            out.append(c)
    return "".join(out)


def _encrypt_ciphertext_key(text, key_letter):
    """Шифртекст: гамма = ключ + шифртекст (одна буква ключа)."""
    n = len(RUS_ALPHABET)
    gamma = [key_letter]
    out = []
    for c in text:
        if c in RUS_ALPHABET:
            ti = RUS_ALPHABET.index(c)
            gi = RUS_ALPHABET.index(gamma[-1])
            si = (ti + gi) % n
            letter = RUS_ALPHABET[si]
            out.append(letter)
            gamma.append(letter)
        else:
            out.append(c)
    return "".join(out)


def _decrypt_ciphertext_key(text, key_letter):
    """Шифртекст: гамма = ключ + шифртекст."""
    n = len(RUS_ALPHABET)
    gamma = [key_letter]
    out = []
    for c in text:
        if c in RUS_ALPHABET:
            si = RUS_ALPHABET.index(c)
            gi = RUS_ALPHABET.index(gamma[-1])
            ti = (si - gi) % n
            out.append(RUS_ALPHABET[ti])
            gamma.append(c)  # в гамму идёт буква шифртекста
        else:
            out.append(c)
    return "".join(out)


def encrypt_text(text, key_letter=None, mode=None):
    """Полный цикл шифрования. Ключ — одна буква. Режим: 1 — самоключ, 2 — шифртекст."""
    if key_letter is None:
        key_letter = input("Введите ключ (одна буква): ").strip()
    key_letter = _check_key_letter(key_letter)
    if mode is None:
        m = input("Режим: 1 — самоключ, 2 — шифртекст: ").strip()
        mode = int(m) if m in ("1", "2") else MODE_AUTOKEY
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    if mode == MODE_CIPHERTEXT:
        encrypted = _encrypt_ciphertext_key(prepared, key_letter)
    else:
        encrypted = _encrypt_autokey(prepared, key_letter)
    return split_into_groups_of_five(encrypted).upper()


def decrypt_text(text, key_letter=None, mode=None):
    """Полный цикл расшифрования. Ключ и режим — те же, что при шифровании."""
    if key_letter is None:
        key_letter = input("Введите ключ (одна буква): ").strip()
    key_letter = _check_key_letter(key_letter)
    if mode is None:
        m = input("Режим: 1 — самоключ, 2 — шифртекст: ").strip()
        mode = int(m) if m in ("1", "2") else MODE_AUTOKEY
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    text_clean = text.replace(" ", "").lower()
    if mode == MODE_CIPHERTEXT:
        decrypted = _decrypt_ciphertext_key(text_clean, key_letter)
    else:
        decrypted = _decrypt_autokey(text_clean, key_letter)
    return restore_punctuation_from_codes(decrypted, code_to_punct)
