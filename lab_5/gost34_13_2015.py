from typing import List

table = [
    [0xc, 0x4, 0x6, 0x2, 0xa, 0x5, 0xb, 0x9, 0xe, 0x8, 0xd, 0x7, 0x0, 0x3, 0xf, 0x1],
    [0x6, 0x8, 0x2, 0x3, 0x9, 0xa, 0x5, 0xc, 0x1, 0xe, 0x4, 0x7, 0xb, 0xd, 0x0, 0xf],
    [0xb, 0x3, 0x5, 0x8, 0x2, 0xf, 0xa, 0xd, 0xe, 0x1, 0x7, 0x4, 0xc, 0x9, 0x6, 0x0],
    [0xc, 0x8, 0x2, 0x1, 0xd, 0x4, 0xf, 0x6, 0x7, 0x0, 0xa, 0x5, 0x3, 0xe, 0x9, 0xb],
    [0x7, 0xf, 0x5, 0xa, 0x8, 0x1, 0x6, 0xd, 0x0, 0x9, 0x3, 0xe, 0xb, 0x4, 0x2, 0xc],
    [0x5, 0xd, 0xf, 0x6, 0x9, 0x2, 0xc, 0xa, 0xb, 0x7, 0x8, 0x1, 0x4, 0x3, 0xe, 0x0],
    [0x8, 0xe, 0x2, 0x5, 0x6, 0x9, 0x1, 0xc, 0xf, 0x4, 0xb, 0x0, 0xd, 0xa, 0x3, 0x7],
    [0x1, 0x7, 0xe, 0xd, 0x0, 0x5, 0x8, 0x3, 0x4, 0xf, 0xa, 0x6, 0x9, 0xc, 0xb, 0x2],
]

# Тестовые векторы ГОСТ Р 34.13-2015 (приложение А)
P_TEST = ["92def06b3c130a59", "db54c704f8189d20", "4a98fb2e67a8024c", "8912409b17b57e41"]
C_TEST = ["4e98110c97b7b93c", "3e250d93d6e85d69", "136d868807b2dbef", "568eb680ab52a12d"]
KEY_TEST = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
IV_TEST = "12345678"


def split_by(text: str, size: int) -> List[str]:
    return [text[i:i+size] for i in range(0, len(text), size)]


def block_checker(block_list: List[str], size: int):
    for i in range(len(block_list)):
        if len(block_list[i]) != size:
            block_list[i] = block_list[i].zfill(size)


def t(int32: int) -> int:
    # Нелинейное преобразование: итерация по тетрадам в обратном порядке (от старших к младшим)
    y = 0
    for i in reversed(range(8)):
        j = (int32 >> (4 * i)) & 0xf
        y <<= 4
        y ^= table[i][j]
    return y


def F(iv_vec: List[str], m_key: List[str]):
    """Раундовая функция сети Фейстеля. iv_vec — список из двух 32-битных бинарных строк."""
    N1, N2 = "", ""
    for i in m_key:
        N1 = iv_vec[0]
        N2 = iv_vec[1]
        # Сложение по модулю 2^32 + S-блоки + циклический сдвиг влево на 11
        S1 = hex((int(N2, 2) + int(i, 2)) % (2 ** 32))[2:].zfill(8)
        S1 = hex(t(int(S1, 16)))
        S1 = bin(int(S1, 16))[2:].zfill(32)
        S1 = S1[11:] + S1[:11]
        S2 = bin(int(N1, 2) ^ int(S1, 2))[2:].zfill(32)
        N1 = bin(int(N2, 2))[2:].zfill(32)
        iv_vec[0] = N1
        N2 = S2
        iv_vec[1] = S2
    return N2, N1


def encode(open_text_hex: str, iv_hex8: str, key: str) -> str:
    """Гаммирование CTR. Принимает hex открытого текста, 8-символьный IV и 64-символьный ключ.
    Возвращает hex-строку без префикса 0x."""
    # Переводим блоки открытого текста в бинарный вид
    blocks_hex = split_by(open_text_hex, 16)
    open_bin = "".join([bin(int(b, 16))[2:].zfill(64) for b in blocks_hex])
    open_blocks = split_by(open_bin, 64)

    # Строим расписание ключей: 32 подключа в бинарном виде
    key_parts = split_by(key, 8)
    key_schedule = []
    for _ in range(3):
        key_schedule.extend(key_parts)
    key_schedule.extend(key_parts[::-1])
    key_bin_str = "".join(key_schedule)
    key_bin = bin(int(key_bin_str, 16))[2:].zfill(256)
    sub_keys = split_by(key_bin, 32)

    # IV: 8 hex → 32 бит, дополняем нулями справа до 64 бит
    iv_bin = bin(int(iv_hex8, 16))[2:].zfill(32)
    iv_bin = iv_bin + "0" * (64 - len(iv_bin))

    result_bin = ""
    for block in open_blocks:
        iv_vec = split_by(iv_bin, 32)
        saved_iv = "".join(iv_vec)

        N1, N2 = F(iv_vec, sub_keys)
        gamma = N1 + N2

        for j in range(len(block)):
            result_bin += str(int(block[j]) ^ int(gamma[j]))

        # Увеличиваем счётчик на 1
        iv_bin = bin(int(saved_iv, 2) + 1)[2:].zfill(64)

    return hex(int(result_bin, 2))[2:].zfill(len(open_text_hex))


def gamma_magma():
    key = input()
    IV = input()

    try:
        int(key, 16)
    except Exception:
        print("Ключ должен состоять из hex-символов!")
        return
    if len(key) != 64:
        print("Ключ должен содержать 64 hex-символа!")
        return

    try:
        int(IV, 16)
    except Exception:
        print("IV должен состоять из hex-символов!")
        return
    if len(IV) != 8:
        print("IV должен содержать ровно 8 hex-символов!")
        return

    opt = input("Выберите действие:\n1) ГОСТ\n2) Зашифровать текст\n3) Расшифровать текст\n")

    if opt == "1":
        open_hex = "".join(P_TEST)
        encrypted = encode(open_hex, IV, key)
        print("Шифртекст:", encrypted, encrypted == "".join(C_TEST))
        decrypted = encode(encrypted, IV, key)
        print("Расшифрование:", decrypted, decrypted == open_hex)

    elif opt == "2":
        text = input("Введите текст: ")
        text_h = bytearray(text, "utf-8").hex()
        block_list = split_by(text_h, 32)
        # Последний блок дополняем нулями справа (чтобы обрезка при расшифровании работала корректно)
        for i in range(len(block_list)):
            if len(block_list[i]) != 32:
                block_list[i] = block_list[i].ljust(32, '0')
        enc_blocks = [encode(block, IV, key) for block in block_list]
        print("Зашифрованный текст:", "".join(enc_blocks))

    elif opt == "3":
        text_h = input("Введите текст: ")
        block_list = split_by(text_h, 32)
        block_checker(block_list, 32)
        dec_blocks = [encode(block, IV, key) for block in block_list]
        dec = "".join(dec_blocks)
        # Обрезаем дополняющие нули справа (до кратности 2 для валидного hex)
        dec_stripped = dec.rstrip('0')
        if len(dec_stripped) % 2 != 0:
            dec_stripped += '0'
        print("Расшифрованный hex:", dec)
        try:
            print("Открытый текст:", bytearray.fromhex(dec_stripped).decode("utf-8"))
        except Exception:
            print("Открытый текст:", dec)

    else:
        print("Неверный выбор!")


def main():
    gamma_magma()


if __name__ == "__main__":
    main()
