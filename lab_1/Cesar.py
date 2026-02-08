# Шифр Цезаря: сдвиг буквы на k позиций вперёд (шифрование) или назад (расшифрование).

# Общие функции подготовки текста и знаков препинания — как в Атбаш
from lab_1.atbash import (
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"  # 32 буквы без ё


def _shift_letter(symbol, k, encrypt):
    """Сдвиг одной буквы: вперёд (шифр) или назад (расшифр). Регистр сохраняется."""
    letter = symbol.lower()
    if letter not in RUS_ALPHABET:
        return symbol
    pos = RUS_ALPHABET.index(letter)
    new_pos = (pos + k) % 32 if encrypt else (pos - k + 32) % 32
    res = RUS_ALPHABET[new_pos]
    return res.upper() if symbol.isupper() else res


def _caesar(text, k, encrypt):
    """Шифрование или расшифрование текста сдвигом на k (encrypt=True/False)."""
    return "".join(_shift_letter(s, k, encrypt) for s in text)


def _get_key(key, prompt):
    """Проверка ключа: целое число. Если key не передан — запрос с клавиатуры."""
    if key is None:
        key = input(prompt).strip()
    if key == "":
        raise ValueError("Ключ не введён.")
    try:
        return int(key)
    except ValueError:
        raise ValueError("Ключ должен быть целым числом.")


def encrypt_text(text, key=None):
    """Зашифровать текст. Ключ k — сдвиг по алфавиту. Результат — группы по 5 символов."""
    k = _get_key(key, "Введите ключ (целое число — сдвиг): ")
    punct = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct)
    encrypted = _caesar(prepared, k, encrypt=True)
    return split_into_groups_of_five(encrypted).upper()


def decrypt_text(text, key=None):
    """Расшифровать текст. Ключ k — тот же, что при шифровании."""
    k = _get_key(key, "Введите ключ (сдвиг при шифровании): ")
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    text_clean = text.replace(" ", "").lower()
    decrypted = _caesar(text_clean, k, encrypt=False)
    return restore_punctuation_from_codes(decrypted, code_to_punct)
