# Шифр Плэйфера: 6 колонок × 5 строк (30 ячеек, И/Й и Ъ/Ь объединены, без цифр).
# Работа с текстом (подготовка, группы по 5, восстановление знаков) — через lab_1.atbash.

from lab_1.atbash import (
    RUS_ALPHABET,
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

TABLE_ALPHABET = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЭЮЯ'
ROWS = 5
COLS = 6
SEPARATOR = 'Ъ'


def _norm(ch):
    ch = ch.upper().replace('Ё', 'Е').replace('Й', 'И').replace('Ь', 'Ъ')
    return ch


def validate_key(key):
    if not key:
        return False, "Ключ не может быть пустым"
    key_norm = _norm(key)
    seen = set()
    for ch in key_norm:
        if ch not in TABLE_ALPHABET:
            return False, f"Ключ содержит недопустимый символ: {ch}"
        if ch in seen:
            return False, "Ключ не должен содержать повторяющихся букв"
        seen.add(ch)
    return True, "Ключ корректен"

def generate_table(key):
    key_norm = _norm(key)
    used = set()
    key_chars = []
    for ch in key_norm:
        if ch in TABLE_ALPHABET and ch not in used:
            used.add(ch)
            key_chars.append(ch)
    for ch in TABLE_ALPHABET:
        if ch not in used:
            key_chars.append(ch)
    table = [key_chars[i * COLS:(i + 1) * COLS] for i in range(ROWS)]
    return table


def display_table(key):
    table = generate_table(key)
    print("\nТаблица Плэйфера (6 колонок × 5 строк):")
    print("-" * (4 * COLS + 5))
    for row in table:
        print("| " + " | ".join(row) + " |")
        print("-" * (4 * COLS + 5))


def find_position(table, ch):
    ch = _norm(ch)
    for r in range(ROWS):
        for c in range(COLS):
            if table[r][c] == ch:
                return r, c
    raise ValueError(f"Символ {ch} не найден в таблице")

#вставляется разделитель Ъ в двух случаях: между двумя одинаковыми буквами и в конце текста, 
# если длина после обработки нечётная — чтобы всегда было чётное число символов для разбиения на пары#
def preprocess_text(text):
    text = ''.join(_norm(ch) for ch in text if _norm(ch) in TABLE_ALPHABET)
    processed = []
    i = 0
    while i < len(text):
        processed.append(text[i])
        if i + 1 < len(text) and text[i] == text[i + 1]:
            processed.append(SEPARATOR)
        i += 1
    if len(processed) % 2 != 0:
        processed.append(SEPARATOR)
    return ''.join(processed)


def encrypt_pair(table, a, b):
    r1, c1 = find_position(table, a)
    r2, c2 = find_position(table, b)

    # одна строка
    if r1 == r2:
        return table[r1][(c1 + 1) % COLS], table[r2][(c2 + 1) % COLS]

    # один столбец
    elif c1 == c2:
        return table[(r1 + 1) % ROWS][c1], table[(r2 + 1) % ROWS][c2]

    # прямоугольник
    else:
        return table[r1][c2], table[r2][c1]


def decrypt_pair(table, a, b):
    r1, c1 = find_position(table, a)
    r2, c2 = find_position(table, b)

    # одна строка
    if r1 == r2:
        return table[r1][(c1 - 1) % COLS], table[r2][(c2 - 1) % COLS]

    # один столбец
    elif c1 == c2:
        return table[(r1 - 1) % ROWS][c1], table[(r2 - 1) % ROWS][c2]

    # прямоугольник
    else:
        return table[r1][c2], table[r2][c1]


def encrypt(text, key):
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    plain = ''.join(_norm(ch) for ch in prepared if _norm(ch) in TABLE_ALPHABET)
    processed = preprocess_text(plain)

    table = generate_table(key)
    result = []
    for i in range(0, len(processed), 2):
        enc_a, enc_b = encrypt_pair(table, processed[i], processed[i + 1])
        result.append(enc_a)
        result.append(enc_b)

    return split_into_groups_of_five(''.join(result)).upper()

# Символ пропускается (не попадает в out), только если это SEPARATOR ('Ъ') и при этом:
#он между двумя одинаковыми буквами (s[i - 1] == s[i + 1]) — это тот «Ъ», который вставили между дублем;
#или он последний в строке (i == len(s) - 1) — это «Ъ», добавленный для чётной длины.
#Во всех остальных случаях символ добавляется в результат.

def _remove_filler(s):
    out = []
    i = 0
    while i < len(s):
        skip = False
        if s[i] == SEPARATOR:
            if i > 0 and i + 1 < len(s) and s[i - 1] == s[i + 1]:
                skip = True
            elif i == len(s) - 1:
                skip = True
        if skip:
            i += 1
            continue
        out.append(s[i])
        i += 1
    return ''.join(out)


def decrypt(text, key):
    text_clean = text.replace(" ", "").upper()
    text_clean = ''.join(ch for ch in text_clean if ch in TABLE_ALPHABET)

    table = generate_table(key)
    result = []
    for i in range(0, len(text_clean), 2):
        dec_a, dec_b = decrypt_pair(table, text_clean[i], text_clean[i + 1])
        result.append(dec_a)
        result.append(dec_b)

    decrypted = _remove_filler(''.join(result))
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    return restore_punctuation_from_codes(decrypted.lower(), code_to_punct)


def playfair_mode():
    key = input("Введите ключевое слово: ").strip()
    valid, message = validate_key(key)

    if not valid:
        print("Ошибка:", message)
        return

    display_table(key)

    while True:
        print("\n1. Зашифровать")
        print("2. Расшифровать")
        print("0. Назад")

        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break

        if choice not in ("1", "2"):
            print("Введите 1, 2 или 0.")
            continue

        text = input("Введите текст: ").strip()

        if not text:
            print("Текст не введён.")
            continue

        if choice == "1":
            result = encrypt(text, key)
        else:
            result = decrypt(text, key)

        print("Результат:", result)