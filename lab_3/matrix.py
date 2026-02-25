# Матричный шифр (шифр Хилла): шифрование блоками через умножение на ключевую матрицу по модулю алфавита.
# Работа с текстом (подготовка, восстановление знаков) — только через lab_1.atbash.

import random
from fractions import Fraction

from lab_1.atbash import (
    RUS_ALPHABET,
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)


def _letter_to_index(letter: str) -> int:
    return RUS_ALPHABET.index(letter.lower())


def _index_to_letter(idx: int) -> str:
    return RUS_ALPHABET[idx % 32]


def matrix_encrypt(text: str, key_matrix):
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    plain = [c for c in prepared if c in RUS_ALPHABET]
    original_len = len(plain)
    n = len(key_matrix)
    while len(plain) % n != 0:
        plain.append(random.choice(RUS_ALPHABET))
    blocks = [plain[i : i + n] for i in range(0, len(plain), n)]
    result = []
    for block in blocks:
        vec = [_letter_to_index(ch) for ch in block]
        out_vec = [0] * n
        for i in range(n):
            total = 0
            for j in range(n):
                total += key_matrix[i][j] * vec[j]
            out_vec[i] = total
        result.extend(out_vec)
    return " ".join(str(x) for x in result), original_len


def invert_matrix(matrix):
    n = len(matrix)
    augmented = []
    for i in range(n):
        row = [Fraction(x) for x in matrix[i]] + [
            Fraction(1 if j == i else 0) for j in range(n)
        ]
        augmented.append(row)
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if augmented[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return None
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        factor = augmented[col][col]
        for j in range(2 * n):
            augmented[col][j] /= factor
        for row in range(n):
            if row != col and augmented[row][col] != 0:
                factor = augmented[row][col]
                for j in range(2 * n):
                    augmented[row][j] -= factor * augmented[col][j]
    return [row[n:] for row in augmented]


def matrix_decrypt(cipher_str: str, key_matrix, original_len: int = None):
    numbers = list(map(int, cipher_str.strip().split()))
    n = len(key_matrix)
    inv_matrix = invert_matrix(key_matrix)
    if inv_matrix is None:
        raise ValueError("Матрица необратима")
    blocks = [numbers[i : i + n] for i in range(0, len(numbers), n)]
    result_chars = []
    for block in blocks:
        vec = [Fraction(0) for _ in range(n)]
        for i in range(n):
            total = Fraction(0)
            for j in range(n):
                total += inv_matrix[i][j] * block[j]
            vec[i] = total
        indices = [int(round(v)) for v in vec]
        result_chars.extend(_index_to_letter(idx) for idx in indices)
    plain_letters = "".join(result_chars)
    if original_len is not None:
        plain_letters = plain_letters[:original_len]
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    return restore_punctuation_from_codes(plain_letters, code_to_punct)


def is_matrix_invertible(matrix):
    n = len(matrix)
    if n < 3:
        return False
    return invert_matrix(matrix) is not None


def input_matrix():
    """Ввод матрицы с клавиатуры с проверкой обратимости и размера >=3."""
    while True:
        try:
            n = int(input("Введите размер матрицы (n x n, n>=3): "))
            if n < 3:
                print("Размер должен быть не меньше 3.")
                continue
            matrix = []
            print("Введите строки матрицы, элементы через пробел:")
            for i in range(n):
                row = list(map(int, input(f"Строка {i + 1}: ").split()))
                if len(row) != n:
                    print(f"Ожидалось {n} чисел, попробуйте снова.")
                    break
                matrix.append(row)
            else:
                if is_matrix_invertible(matrix):
                    print("\nКлючевая матрица принята:")
                    for row in matrix:
                        print(" ", row)
                    return matrix
                else:
                    print("Матрица необратима (определитель 0). Попробуйте другую.")
        except ValueError:
            print("Некорректный ввод. Попробуйте снова.")


def encrypt_text(text: str) -> str:
    """Шифрование с запросом ключевой матрицы из консоли (для вызова из main.py)."""
    key_matrix = input_matrix()
    cipher_str, original_len = matrix_encrypt(text, key_matrix)
    print("Длина исходного текста (для расшифровки):", original_len)
    return cipher_str


def decrypt_text(text: str) -> str:
    """Расшифрование с запросом матрицы из консоли (для вызова из main.py). Длина исходного текста неизвестна — вывод без обрезки."""
    key_matrix = input_matrix()
    return matrix_decrypt(text, key_matrix)


def matrix_mode():
    print("\n--- Матричный шифр ---")
    print("Введите ключевую матрицу (целые числа).")
    key_matrix = input_matrix()
    while True:
        print("\n1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("0. Вернуться в главное меню")
        sub = input("Выбор: ").strip()
        if sub == "0":
            break
        elif sub in ("1", "2"):
            text = input("Введите текст: ").strip()
            if not text:
                print("Текст не может быть пустым.")
                continue
            try:
                if sub == "1":
                    cipher, orig_len = matrix_encrypt(text, key_matrix)
                    print("Зашифрованный текст (числа):", cipher)
                    print(f"(Длина исходного текста после подготовки: {orig_len})")
                else:
                    plain = matrix_decrypt(text, key_matrix)
                    print("Расшифрованный текст:", plain)
            except Exception as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод.")
