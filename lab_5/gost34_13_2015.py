from typing import List

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

def split_key(key: str) -> List[str]:
    # Делим ключ на 8-символьные блоки (4 блока по 8 символов, повторяем 3 раза + обратный порядок)
    blocks = [key[i:i+8] for i in range(0, len(key), 8)]
    return blocks * 3 + blocks[::-1]

def t(a: str) -> str:
    # S-box подстановка (a - hex строка длиной 8)
    return ''.join([hex(table[index][int(i, 16)])[2:] for index, i in enumerate(a)])

def cyclic_shift_left(value: int, shift: int, bits=32):
    return ((value << shift % bits) & ((1 << bits) - 1) | (value >> (bits - shift % bits))) & ((1 << bits) - 1)

def g(key: str, a: str) -> str:
    # key и a - hex строки длиной 8
    s = (int(key, 16) + int(a, 16)) % 2 ** 32
    s_hex = hex(s)[2:].zfill(8)
    t_s = t(s_hex)
    shifted = cyclic_shift_left(int(t_s, 16), 11)
    return hex(shifted)[2:].zfill(8)

def G(a1, a0, key) -> str:
    # a1, a0, key - hex строки длиной 8
    return hex(int(g(key, a0), 16) ^ int(a1, 16))[2:].zfill(8)

class KeyError(Exception):
    pass

def check_params(input: str, key: str):
    try:
        int(input, 16)
        assert len(input) == 16
        assert len(key) == 64
    except Exception:
        raise KeyError("Неправильные входные параметры")

def encrypt_block(message: str, keys: List[str]) -> str:
    a1, a0 = message[0:8], message[8:]
    for key in keys:
        a1, a0 = a0, G(a1, a0, key)
    return a0 + a1

def to_hex(input: str) -> str:
    try:
        int(input, 16)
        return input
    except Exception:
        return input.encode('utf-8').hex()

def from_hex(hex_str: str) -> str:
    try:
        return bytes.fromhex(hex_str).decode('utf-8')
    except Exception:
        return hex_str

def pad_hex_block(block: str, block_size: int = 16) -> str:
    # Дополнение блока нулями справа до block_size
    return block.ljust(block_size, '0')

def gamma_magma(mode="enc"):
    # Ввод данных
    if input("Вы вводите сообщение в hex? Y/N: ").strip().upper() == "Y":
        message = input("Введите сообщение: ").strip()
    else:
        message = input("Введите сообщение: ").strip()
        message = to_hex(message)

    key = input("Введите ключ (64 hex-символа): ").strip()
    IV = input("Введите инициализирующий вектор (8 hex-символов): ").strip()
    IV = IV.ljust(16, '0')  # Делаем IV 16-символьным

    # Проверка ключа и IV
    if len(key) != 64:
        print("Ключ должен содержать 64 hex-символа!")
        return
    if len(IV) != 16:
        print("IV должен содержать 16 hex-символов!")
        return

    keys = split_key(key)
    total = ""
    blocks = [message[i:i+16] for i in range(0, len(message), 16)]
    # Последний блок дополняем нулями, если не хватает
    if len(blocks[-1]) < 16:
        blocks[-1] = pad_hex_block(blocks[-1], 16)

    current_iv = IV
    for idx, p_i in enumerate(blocks):
        ek = encrypt_block(current_iv, keys)
        c_i = hex(int(ek, 16) ^ int(p_i, 16))[2:].zfill(16)
        if mode == "enc":
            print(f'C{idx}: {c_i}')
            total += c_i
        else:
            print(f'P{idx}: {c_i}')
            total += c_i
        # Увеличиваем IV
        current_iv = hex((int(current_iv, 16) + 1) % (1 << 64))[2:].zfill(16)
    print("\nРезультат (hex):")
    print(total)
    if mode == "dec":
        # Обрезаем возможные лишние нули (если последний блок был дополнен)
        total = total.rstrip('0')
        print("\nРасшифрованный текст:")
        print(from_hex(total))

def main():
    print("Выберите режим работы:")
    print("1. Шифрование")
    print("2. Расшифрование")
    choice = input("Ваш выбор (1/2): ").strip()
    if choice == "1":
        gamma_magma("enc")
    elif choice == "2":
        gamma_magma("dec")
    else:
        print("Неверный выбор!")

if __name__ == "__main__":
    main()
