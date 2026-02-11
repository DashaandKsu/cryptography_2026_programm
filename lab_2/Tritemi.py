# lab_3/tritemius.py

from lab_1.atbash import (
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"  # 32 буквы

def encrypt_tritemius(text, alphabet=RUS_ALPHABET):
    """Шифрует текст методом Тритемия"""
    n = len(alphabet)
    # Подготовка текста: нижний регистр, знаки препинания заменены, пробелы убраны
    punct_codes = create_punctuation_codes()
    prepared_text = prepare_text_for_encryption(text, punct_codes)
    
    encrypted = ""
    for j, letter in enumerate(prepared_text):
        if letter in alphabet:
            i = alphabet.index(letter)
            # Формула Тритемия: сдвиг зависит от позиции j
            y_index = (i + j) % n
            encrypted += alphabet[y_index]
        else:
            # оставляем символы, которых нет в алфавите
            encrypted += letter
    return split_into_groups_of_five(encrypted).upper()


def decrypt_tritemius(text, alphabet=RUS_ALPHABET):
    """Расшифровывает текст методом Тритемия. Восстанавливает пробелы и знаки препинания из кодов."""
    n = len(alphabet)
    # Убираем пробелы между группами по 5 (как в зашифрованном выводе)
    text_clean = text.replace(" ", "").lower()
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())

    decrypted = ""
    for j, letter in enumerate(text_clean):
        if letter in alphabet:
            y_index = alphabet.index(letter)
            # обратная формула для расшифровки
            x_index = (y_index - j) % n
            decrypted += alphabet[x_index]
        else:
            decrypted += letter
    return restore_punctuation_from_codes(decrypted, code_to_punct)