from typing import List

# S-box (таблица подстановки) размером 8×16
table = [
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 10, 5, 3, 14, 9, 11, 0],  # добавлен 0 в конец
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1]
]

def split_key(key: str) -> List[str]:
    """Разделяет 64-символьный hex-ключ на 8 частей по 8 символов (32 бита)"""
    return [key[i:i+8] for i in range(0, len(key), 8)]

def t(a: str) -> str:
    """Преобразование через таблицы подстановки (S-box)"""
    return ''.join([hex(table[index][int(i, 16)])[2:] for index, i in enumerate(a)])

def cyclic_shift_left(value: int, shift: int, bits=32) -> int:
    """Циклический сдвиг влево на shift бит в пределах bits"""
    shift %= bits
    mask = (1 << bits) - 1
    return ((value << shift) & mask) | (value >> (bits - shift))

def g(key: str, a: str) -> str:
    """
    Раундовая функция:
    - сложение ключа и данных по модулю 2^32
    - замена через S-блоки (функция t)
    - циклический сдвиг влево на 11 бит
    Возвращает 8-символьную hex-строку.
    """
    # сложение
    s = (int(a, 16) + int(key, 16)) & 0xFFFFFFFF
    # замена через S-блоки
    s_hex = format(s, '08x')
    substituted = t(s_hex)
    # циклический сдвиг
    shifted = cyclic_shift_left(int(substituted, 16), 11)
    return format(shifted, '08x')

def G(left: str, right: str, key: str) -> str:
    """
    Функция, используемая в сети Фейстеля:
    new_right = left XOR g(right, key)
    """
    f_out = g(key, right)
    return hex(int(left, 16) ^ int(f_out, 16))[2:].zfill(8)

def encrypt(message: str, keys: List[str]) -> str:
    """
    Шифрование одного 64-битного блока (16 hex-символов)
    с использованием 8 раундов сети Фейстеля.
    """
    a1, a0 = message[0:8], message[8:]  # левая и правая половины
    for key in keys:
        a1, a0 = a0, G(a1, a0, key)     # стандартный шаг сети Фейстеля
    return a0 + a1                       # перестановка после последнего раунда

def to_hex(input: str) -> str:
    """Преобразует строку в hex, если она ещё не в hex-формате."""
    try:
        # если это уже hex-число, просто убираем 0x
        return hex(int(input, 16))[2:]
    except Exception:
        # иначе кодируем utf-8
        return input.encode('utf-8').hex()

class KeyError(Exception):
    pass

def check_params(msg: str, key: str):
    """Проверяет корректность входных данных."""
    try:
        tmp = int(msg, 16)
        tmp = int(key, 16)
        assert len(msg) == 16
        assert len(key) == 64
    except Exception as e:
        raise KeyError("Неправильные входные параметры")

def gamma_magma():
    """Режим гаммирования (CTR) для алгоритма Магма."""
    answer = input("Вы вводите сообщение в hex? Y/N: ")
    if answer.upper() == "Y":
        message = input("Введите сообщение: ")
    else:
        message = input("Введите сообщение: ")
        message = to_hex(message)

    key = input("Введите ключ: ")
    IV = input("Введите инициализирующий вектор: ")
    while len(IV) < 16:
        IV += '0'          # дополняем до 16 hex-символов
    IV = IV[:16]           # обрезаем, если длиннее

    keys = split_key(key)
    total = ""

    for i in range(len(message) // 16):
        p_i = message[i*16:(i+1)*16]
        ek = encrypt(IV, keys)                     # шифруем IV
        c_i = hex(int(ek, 16) ^ int(p_i, 16))[2:].zfill(16)  # XOR и дополнение нулями
        print(f'c_{i} = {c_i}')
        total += c_i
        # увеличиваем IV на 1 и сохраняем 16 hex-цифр
        IV = hex((int(IV, 16) + 1) & 0xFFFFFFFFFFFFFFFF)[2:].zfill(16)

    print("Зашифрованное сообщение:", total)

if __name__ == "__main__":
    gamma_magma()