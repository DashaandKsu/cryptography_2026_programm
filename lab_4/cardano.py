from copy import deepcopy
import random

from lab_1.atbash import (
    RUS_ALPHABET,
    create_punctuation_codes,
    create_code_to_punctuation,
    prepare_text_for_encryption,
    split_into_groups_of_five,
    restore_punctuation_from_codes,
)

# Решётка 6×10: 0 — вырез (отверстие), 1 — закрытая ячейка. Всего 15 вырезов на одно положение; 4 положения = 60 ячеек.
trafar = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0, 1, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 0, 0, 1, 1, 0]
]
RUSSIAN_ALP = RUS_ALPHABET

def rotate_1(grille):
    return [row[::-1] for row in grille]


def rotate_2(grille):
    return [grille[5 - row][:] for row in range(len(grille))]


def _cutout_positions(grille):
    """Список координат (i, j) вырезов в порядке по строкам слева направо."""
    return [(i, j) for i in range(len(grille)) for j in range(len(grille[0])) if not grille[i][j]]


def get_rotation_positions(grille):
    """Возвращает для каждого из 4 положений решётки список из 15 координат (i, j) вырезов.
    Порядок: исходное, rotate_1, rotate_2, rotate_1(rotate_2)."""
    g = deepcopy(grille)
    positions = [_cutout_positions(g)]
    g = rotate_1(g)
    positions.append(_cutout_positions(g))
    g = rotate_2(g)
    positions.append(_cutout_positions(g))
    g = rotate_1(g)
    positions.append(_cutout_positions(g))
    return positions


def encrypt(message, grille):
    """Шифрование списка символов message решёткой grille (0 — вырез, 1 — закрыто). Не изменяет переданную grille."""
    message = list(message)
    grille = deepcopy(grille)
    # Пустышки: пока длина сообщения не делится на 60, к нему в конец по одной добавляется
    # случайная буква из русского алфавита (RUSSIAN_ALP[random.randint(0, 31)]).
    # Итог: сначала идёт весь текст, потом дописываются случайные буквы-«пустышки», пока
    # общая длина не станет 60, 120, 180 и т.д. При расшифровке хвостовые буквы отбрасываются
    # по сохранённой длине исходного текста.
    while len(message) % 60 != 0:
        message.append(RUSSIAN_ALP[random.randint(0, 31)])
    res = ''
    while message:
        work = deepcopy(grille)
        tmp_matrix = [['' for _ in range(10)] for _ in range(6)]
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not tmp_matrix[i][j] and not work[i][j]:
                    tmp_matrix[i][j] = message.pop(0)
        work = rotate_1(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not tmp_matrix[i][j] and not work[i][j]:
                    tmp_matrix[i][j] = message.pop(0)
        work = rotate_2(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not tmp_matrix[i][j] and not work[i][j]:
                    tmp_matrix[i][j] = message.pop(0)
        work = rotate_1(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not tmp_matrix[i][j] and not work[i][j]:
                    tmp_matrix[i][j] = message.pop(0)
        for row in tmp_matrix:
            res += ''.join(row)
    return res


def encrypt_with_details(message, grille, orig_len=None):
    """Шифрование с возвратом данных для визуализации: матрица 6×10, пометки пустышек, позиции по поворотам.
    Возвращает (ciphertext, orig_len, blocks). Каждый элемент blocks: dict с ключами:
    - matrix: 6×10 заполненная матрица букв;
    - is_padding: 6×10 bool (True = пустышка);
    - rotation_positions: список из 4 списков координат (i,j) вырезов для каждого поворота."""
    message = list(message)
    grille = deepcopy(grille)
    if orig_len is None:
        orig_len = len(message)
    while len(message) % 60 != 0:
        message.append(RUSSIAN_ALP[random.randint(0, 31)])
    rotation_positions = get_rotation_positions(grille)
    res = ''
    blocks = []
    block_start = 0
    while message:
        work = deepcopy(grille)
        tmp_matrix = [['' for _ in range(10)] for _ in range(6)]
        is_padding = [[False] * 10 for _ in range(6)]
        num_real_in_block = min(60, max(0, orig_len - block_start))
        idx_in_block = 0
        for pos_list in rotation_positions:
            for i, j in pos_list:
                ch = message.pop(0)
                tmp_matrix[i][j] = ch
                is_padding[i][j] = idx_in_block >= num_real_in_block
                idx_in_block += 1
            work = rotate_1(work) if idx_in_block == 15 else (rotate_2(work) if idx_in_block == 30 else rotate_1(work))
        for row in tmp_matrix:
            res += ''.join(row)
        blocks.append({
            'matrix': [row[:] for row in tmp_matrix],
            'is_padding': [row[:] for row in is_padding],
            'rotation_positions': rotation_positions,
        })
        block_start += 60
    return res, orig_len, blocks


def decrypt(message, grille):
    """Расшифрование: message — список символов, grille — решётка. Не изменяет переданную grille."""
    message = list(message)
    grille = deepcopy(grille)
    res = ''
    total_len = len(message)
    while len(res) < total_len:
        tmp_matrix = [['' for _ in range(10)] for _ in range(6)]
        for i in range(len(tmp_matrix)):
            for j in range(len(tmp_matrix[0])):
                tmp_matrix[i][j] = message.pop(0)
        work = deepcopy(grille)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not work[i][j]:
                    res += tmp_matrix[i][j]
        work = rotate_1(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not work[i][j]:
                    res += tmp_matrix[i][j]
        work = rotate_2(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not work[i][j]:
                    res += tmp_matrix[i][j]
        work = rotate_1(work)
        for i in range(len(work)):
            for j in range(len(work[0])):
                if not work[i][j]:
                    res += tmp_matrix[i][j]
    return res


def encrypt_text(text: str):
    """Полный цикл шифрования: подготовка текста (знаки в коды), шифр решёткой, группы по 5.
    Возвращает (строка_шифртекста_по_5_символов, длина_подготовленного_текста) — длина нужна для расшифровки."""
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    orig_len = len(prepared)
    encrypted = encrypt(list(prepared), trafar)
    return split_into_groups_of_five(encrypted).upper(), orig_len


def encrypt_text_with_details(text: str):
    """Как encrypt_text, но дополнительно возвращает блоки для визуализации (матрицы, пустышки, повороты)."""
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    orig_len = len(prepared)
    encrypted, _, blocks = encrypt_with_details(list(prepared), trafar, orig_len)
    return split_into_groups_of_five(encrypted).upper(), orig_len, blocks


def decrypt_text(text: str, original_len: int = None) -> str:
    """Полный цикл расшифрования: убрать пробелы, расшифровать, обрезать до original_len (если задан), восстановить знаки препинания."""
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    text_clean = text.replace(" ", "").lower()
    decrypted = decrypt(list(text_clean), trafar)
    if original_len is not None:
        decrypted = decrypted[:original_len]
    return restore_punctuation_from_codes(decrypted, code_to_punct)

def cardano():
    """Консольный режим решётки Кардано."""
    choice = int(input("1 - для шифрования, 2 - для расшифрования: "))
    text = input("Введите сообщение: ").strip()
    if choice == 1:
        cipher, orig_len = encrypt_text(text)
        print("Зашифрованное сообщение:", cipher)
        print("Длина исходного текста (для расшифровки):", orig_len)
    else:
        print("Расшифрованное сообщение:", decrypt_text(text))


def run_cardano_gui():
    """Запуск оконного интерфейса с визуальной решёткой."""
    from lab_4 import cardano_gui
    cardano_gui.run()


if __name__ == "__main__":
    cardano()
