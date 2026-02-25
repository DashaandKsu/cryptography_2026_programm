from typing import List

"""Таблица подстановок (S-box)"""
table = [
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1]
]
"""Функция разделения ключа"""
def split_key(key: str) -> List[str]:
    """
    Split key in 32 parts
    :param key: str
    :return: List[arr]
    """
    #порядок ключа и его вывод списка из 32 по 8 хекс используется в 106-110
    return [key[i:i+8] for j in range(3) for i in range(0, len(key), 8)] + [(key)[::-1][i:i+8][::-1] for i in range(0, len(key), 8)]


"""Функция t-перестановки"""
def t(a: str) -> str:
    """
    Perform t permutation (S-table)
    :param a:
    :return: str
    """
    return ''.join([hex(table[index][int(i, 16)])[2:] for index, i in enumerate(a)])
"""Преобразует каждый бит во входной строке
Использует индекс из таблицы для получения нового значения
Объединяет результаты обратно в строку"""


"""Циклический сдвиг влево"""
def cyclic_shift_left(value: int, shift: int, bits=32):
    """
    Perform cycle shift_lift
    :param value: int
    :param shift: int
    :param bits: int (default: 32)
    :return:
    """
    return ((value << shift % bits) & ((1 << bits) - 1) | (value >> (bits - shift % bits))) & ((1 << bits) - 1)

"""Функция g-перестановки"""
def g(key: str, a: str) -> str:
    """
    Perform g-permutation
    :param key: str
    :param a: str
    :return: str
    """
    return hex(cyclic_shift_left(int(t(hex((int(key, 16) + int(a, 16)) % 2 ** 32)[2:].zfill(8)), 16), 11))[2:]
"""Складывает ключ и входную строку по модулю 2^32
Применяет t-перестановку
Выполняет циклический сдвиг на 11 позиций"""

def G(a1, a0, key) -> str:
    """
    Perform G-permutation
    :param a1: str
    :param a0: str
    :param key: str
    :return: str
    """
    return hex(int(g(key, a0), 16) ^ int(a1, 16))[2:]


class KeyError(Exception):
    pass

def check_params(input: str, key: str):
    try:
        tmp = int(input, 16)
        tmp = int(input, 16)
        assert len(input) == 16
        assert len(key) == 64
    except Exception as _:
        raise KeyError("Неправильные входные параметры")


def encrypt(message: str, keys: List[str]) -> str:
    """
    Encrypt message on feistel network
    :param message: str
    :param keys: str
    :return: str
    """
    assert len(keys) == 32
    a1, a0 = message[0:8], message[8:]
    cnt = 0
    print(f'(a1, a0) = ({a1}, {a0})')
    #При шифровании ключи берутся в том же порядке, в каком их вернул split_key:
    for index, key in enumerate(keys):
        a1, a0 = a0, G(a1, a0, key)
        print(f'G[K{cnt + 1}] ({a1}, {a0})')
        cnt += 1
    return a0 + a1
"""Разделяет входное сообщение на две части
Применяет раунды шифрования с использованием ключей
Возвращает зашифрованное сообщение"""


def network():
    choice = int(input("Зашифровать - 1 или расшифровать - 2 "))
    message = input("Введите сообщение: ")
    key = input("Введите ключ: ")
    check_params(message, key)
    keys = split_key(key)
    if choice == 1:
        encrypt_message = encrypt(message, keys)
        print(f'encrypt {encrypt_message}')
    #При расшифровке порядок явно меняется на обратный вызовом keys.reverse():
    else:
        keys.reverse()
        decrypt_message = encrypt(message, keys)
        print(f'decrypt {decrypt_message}')

if __name__ == '__main__':
    network()
    # print(t("fdb97531"))
    # print(t("2a196f34"))
    # print(t("ebd9f03a"))
    # print(t("b039bb3d"))