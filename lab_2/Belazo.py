# Шифр Белазо (исправленный вариант)

from lab_1.atbash import (
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def _get_key(key, prompt="Введите ключ (слово или фраза): "):
    """Если key не передан — запрос с клавиатуры."""
    if key is None:
        key = input(prompt).strip()
    if not key:
        raise ValueError("Ключ не введён.")
    return key


# Создание матрицы Белазо по ключу
def create_matrix(key):
    key = key.lower()
    matrix = []

    # Первая строка — полный алфавит
    matrix.append(RUS_ALPHABET)

    # Остальные строки — каждая начинается с буквы ключа
    for k in key:
        index = RUS_ALPHABET.index(k)
        row = RUS_ALPHABET[index:] + RUS_ALPHABET[:index]
        matrix.append(row)

    return matrix


# Шифрование
def encrypt_belazo(text, key):
    text = text.lower()
    key = key.lower()
    result = ""
    matrix = create_matrix(key)

    # повторяем ключ под текстом
    repeated_key = ""
    while len(repeated_key) < len(text):
        repeated_key += key
    repeated_key = repeated_key[:len(text)]

    for i in range(len(text)):
        letter = text[i]
        k_letter = repeated_key[i]

        if letter in RUS_ALPHABET:
            # Столбец = позиция буквы текста в первой строке
            col = matrix[0].index(letter)
            # Строка = строка в матрице для этой позиции ключа
            row_index = (i % len(key)) + 1  # +1 потому что первая строка = алфавит
            result += matrix[row_index][col]
        else:
            result += letter

    return result


# Расшифрование
def decrypt_belazo(text, key):
    text = text.lower()
    key = key.lower()
    result = ""
    matrix = create_matrix(key)

    # повторяем ключ под текстом
    repeated_key = ""
    while len(repeated_key) < len(text):
        repeated_key += key
    repeated_key = repeated_key[:len(text)]

    for i in range(len(text)):
        letter = text[i]
        # Строка в матрице для этой позиции ключа
        row_index = (i % len(key)) + 1
        row = matrix[row_index]
        if letter in row:
            col = row.index(letter)
            result += matrix[0][col]
        else:
            result += letter

    return result


# Полный цикл шифрования
def encrypt_text(text, key=None):
    if key is None:
        key = input("Введите ключ (слово или фраза): ").strip()
    if not key:
        raise ValueError("Ключ не введён.")
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    encrypted = encrypt_belazo(prepared, key)
    return split_into_groups_of_five(encrypted).upper()


# Полный цикл расшифрования
def decrypt_text(text, key=None):
    if key is None:
        key = input("Введите ключ (тот же, что при шифровании): ").strip()
    if not key:
        raise ValueError("Ключ не введён.")
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    text_clean = text.replace(" ", "").lower()
    decrypted = decrypt_belazo(text_clean, key)
    return restore_punctuation_from_codes(decrypted, code_to_punct)
