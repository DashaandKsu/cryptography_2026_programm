def text_to_hex(text):
    try:
        encoded = text.encode('utf-8')
        return encoded.hex(), None
    except Exception as e:
        return None, f"Ошибка при преобразовании текста в HEX: {e}"


def hex_to_text(hex_str):
    try:
        hex_str = hex_str.replace(' ', '')
        raw = bytes.fromhex(hex_str)
        text = raw.decode('utf-8', errors='replace')
        return text, None
    except Exception as e:
        return None, f"Ошибка при преобразовании HEX в текст: {e}"


def postprocess_text(text):
    return text.replace('\x00', '').strip()


def detect_input_type(text):        #функция определения типа ввода
    text = text.replace(' ', '')
    if len(text) == 0:      #если ничего не введено - вернуть empty
        return 'empty'
    if all(c in '0123456789abcdefABCDEF' for c in text):        #если все символы HEX - вернуть, что введена HEX-строка
        return 'hex'
    return 'text'       #иначе - вернуть, что введён текст


PI = [      #таблица S-блока замены
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135,
    21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177,
    50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87,
    223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3,
    224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74,
    167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
    173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59,
    7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
    225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97,
    32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82,
    89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182
]

R_COEFFS = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]   #коэффициенты для линейного преобразования R

INV_PI = [0] * 256      #инвертированная таблица замены S-блока
for i, val in enumerate(PI):
    INV_PI[val] = i


def hex_to_bytes(hex_str):      #функция преобразования HEX-строки в список байтов
    hex_str = hex_str.replace(' ', '').upper()
    return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]


def bytes_to_hex(bytes_list):       #функция преобразования списка байтов в HEX-строку
    return ''.join(f'{b:02x}'.upper() for b in bytes_list)


def bytes_to_int_be(bytes_list):        #преобразование списка байт в целое число (big-endian)
    result = 0
    for b in bytes_list:
        result = (result << 8) | b
    return result


def int_to_bytes_be(x, length=16):      #преобразование целого числа в список байт (big-endian)
    result = []
    for i in range(length - 1, -1, -1):
        result.append((x >> (i * 8)) & 0xFF)
    return result


def gf_mul(a, b):       #умножение в поле GF(2^8) c образующим многочленом x^8 + x^7 + x^6 + x + 1
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit:
            a ^= 0xC3
        b >>= 1
    return p & 0xFF


def X(k, a):        #функция наложения ключа (сложение по модулю 2)
    return k ^ a


def S(a):       #нелинейное преобразование (S-блок замены)
    bytes_a = int_to_bytes_be(a, 16)
    transformed = [PI[b] for b in bytes_a]
    return bytes_to_int_be(transformed)


def S_inv(a):       #обратное нелинейное преобразование (обратный S-блок замены)
    bytes_a = int_to_bytes_be(a, 16)
    transformed = [INV_PI[b] for b in bytes_a]
    return bytes_to_int_be(transformed)


def R(a):       #линейное преобразование R
    bytes_a = int_to_bytes_be(a, 16)        #разбиение на 16 байт

    l_val = 0       #стартовое значение эпсилона
    for i in range(16):     #повторить 16 раз
        term = gf_mul(R_COEFFS[i], bytes_a[i])      #умножить байт на линейный коэффицент в поле GF(2^8)
        l_val ^= term       #добавить результат умножения в эпсилон по модулю 2

    result_bytes = [l_val] + bytes_a[:-1]       #значение эпсилона становится старшим, остальные байты сдвигаются
    return bytes_to_int_be(result_bytes)        #преобразовать список байт в целое число


def R_inv(a):       #обратное линейное преобразование R
    bytes_a = int_to_bytes_be(a, 16)        #разбить на 16 байт

    a14_to_a0 = bytes_a[1:]     #получить 15 неизменённых байт
    a15 = bytes_a[0]        #получить эпсилон

    l_val = 0       #стартовое значение эпсилона
    for i in range(16):     #повторить 16 раз
        if i < 15:      #если номер итерации меньше 15
            val = bytes_a[i + 1]    #взять значение следующего байта
        else:   #иначе - конечное значение эпсилон
            val = a15
        term = gf_mul(R_COEFFS[i], val)     #умножить байт на линейный коэффицент в поле GF(2^8)
        l_val ^= term       #добавить результат умножения в эпсилон по модулю 2

    result_bytes = a14_to_a0 + [l_val]      #значение байта, полученного обратно из эпсилона - младшее, остальные сдвигаются
    return bytes_to_int_be(result_bytes)        #преобразовать список байт в целое число


def L(a):       #линейное преобразование L (применить линейное преобразование R 16 раз)
    for _ in range(16):
        a = R(a)
    return a


def L_inv(a):       #обратное линейное преобразование L (применить обратное линейное преобразование R 16 раз)
    for _ in range(16):
        a = R_inv(a)
    return a


def LSX(k, a):      #композиция LSX: сначала выполнить XOR с ключом, потом нелинейное преобразование (S-блок замены), в конце линейное преобразование L
    return L(S(X(k, a)))


def F(k, a1, a0):       #функция F для развёртывания ключа
    return (LSX(k, a1) ^ a0, a1)


def get_C(i):       #возвращает константу C_i = l(Vec128(i))
    bytes_i = int_to_bytes_be(i, 16)
    val_i = bytes_to_int_be(bytes_i)
    return L(val_i)


def expand_key(key_hex):        #развёртывание 256-битного ключа в 10 итерационных ключей
    key_bytes = hex_to_bytes(key_hex)

    K1_bytes = key_bytes[:16]       #первые 16 байт - первый ключ
    K2_bytes = key_bytes[16:]       #вторые 16 байт - второй ключ

    K1 = bytes_to_int_be(K1_bytes)
    K2 = bytes_to_int_be(K2_bytes)

    keys = [K1, K2]

    for i in range(1, 5):       #повторить 4 раза
        a1, a0 = keys[2 * i - 2], keys[2 * i - 1]       #получить позапрошлый и прошлый ключ

        for j in range(1, 9):       #повторить 8 раз
            C = get_C(8 * (i - 1) + j)      #получить константу C_i
            a1, a0 = F(C, a1, a0)       #расчитать функцию F

        keys.append(a1)     #добавление ключей
        keys.append(a0)

    return keys[:10]


def encrypt_block(plaintext_hex, keys):     #шифрование одного 128-битного блока
    a = bytes_to_int_be(hex_to_bytes(plaintext_hex))        #преобразование HEX в число

    state = a
    for i in range(9):      #9 раундов LSX
        state = LSX(keys[i], state)

    state = X(keys[9], state)   #последний раунд X с последним ключом
    return bytes_to_hex(int_to_bytes_be(state, 16))


def decrypt_block(ciphertext_hex, keys):        #расшифрование одного 128-битного блока

    b = bytes_to_int_be(hex_to_bytes(ciphertext_hex))   #преобразование HEX в число

    state = b
    state = X(keys[9], state)       #X с последним ключом

    for i in range(8, -1, -1):      #9 раундов применения L_inv, S_inv, X с обратным порядком ключей
        state = L_inv(state)
        state = S_inv(state)
        state = X(keys[i], state)

    return bytes_to_hex(int_to_bytes_be(state, 16))


def split_blocks(hex_string, block_size=32):        #разбиение HEX-строку на блоки по 32 символа
    blocks = []
    for i in range(0, len(hex_string), block_size):
        block = hex_string[i:i + block_size]
        if len(block) < block_size:
            block = block.ljust(block_size, '0')
        blocks.append(block)
    return blocks


def encrypt_text(plain_hex, keys):      #шифрование текста с разбиением на блоки
    blocks = split_blocks(plain_hex)
    encrypted_blocks = []
    for block in blocks:
        encrypted = encrypt_block(block, keys)
        encrypted_blocks.append(encrypted)
    return ''.join(encrypted_blocks)


def decrypt_text(cipher_hex, keys):     #расшифрование текста с разбиением на блоки
    blocks = split_blocks(cipher_hex)
    decrypted_blocks = []
    for block in blocks:
        decrypted = decrypt_block(block, keys)
        decrypted_blocks.append(decrypted)

    result = ''.join(decrypted_blocks)
    # Удаляем нулевое дополнение
    while len(result) > 0 and result.endswith('00'):
        result = result[:-2]
    return result


def kuznyechik_cipher(text, question2):     #главная функция

    input_type = detect_input_type(text)        #определение типа ввода

    if input_type == 'empty':       #ничего не введено - вернуть ошибку и завершить программу
        return "Ошибка: пустой текст"

    if input_type == 'text':        #введён текст - преобразовать текст в HEX
        hex_str, error = text_to_hex(text)
        if error:
            return error
        text = hex_str
        print(f"Текст преобразован в HEX: {text}")

    text = text.replace(' ', '').upper()

    for char in text:       #проверка, что все символы - HEX
        if char not in '0123456789ABCDEF':
            return f"Ошибка: символ '{char}' не является hex-цифрой"

    key_hex = input("Введите 256-битный ключ (64 шестнадцатеричных символа):\n> ").replace(' ', '').upper()     #ввод ключа
    if len(key_hex) != 64:      #длина ключа не равна 64 - вернуть ошибку и завершить программу
        return f"Ошибка: ключ должен быть 64 hex-символа, получено {len(key_hex)}"
    for char in key_hex:        #проверка, что все символы ключа - HEX
        if char not in '0123456789ABCDEF':
            return f"Ошибка: в ключе недопустимый символ '{char}'"

    keys = expand_key(key_hex)      #развёртывание ключей

    try:
        if question2 == 1:  #если шифрование

            if len(text) % 32 != 0:     #дополнить текст до длины, кратной 32
                text = text.ljust(((len(text) + 31) // 32) * 32, '0')
                print(f"HEX-строка дополнена нулями до длины, кратной 32: {text}")

            blocks = split_blocks(text, 32)     #разбиение на блоки по 32 символа
            print(f"Текст разбит на {len(blocks)} блоков по 32 hex-символа")

            result_hex = encrypt_text(text, keys)       #шифрование текста
            formatted = ' '.join(result_hex[i:i+4] for i in range(0, len(result_hex), 4))       #добавление пробелов каждые 4 символа
            return f"Зашифрованный текст (hex): {formatted}"        #возвращение результата

        else:       #если расшифрование

            blocks = split_blocks(text, 32)     #разбиение на блоки по 32 символа
            print(f"Текст разбит на {len(blocks)} блоков по 32 hex-символа")

            result_hex = decrypt_text(text, keys)       #расшифрование текста
            formatted = ' '.join(result_hex[i:i+4] for i in range(0, len(result_hex), 4))       #добавление пробела каждые 4 символа

            text_result, error = hex_to_text(result_hex)        #преобразование в текст
            if not error and text_result:
                print(f"\nРезультат в русском алфавите: {postprocess_text(text_result)}")       #возвращение результата в текстовом формате

            return f"Расшифрованный текст (hex): {formatted}"       #возвращение результата в HEX-формате

    except Exception as e:
        return f"Ошибка при выполнении: {e}"


if __name__ == "__main__":
    print("Выбран алгоритм №19")
    print("\nВыберите, что необходимо сделать:")
    print(" 1 - Зашифровать")
    print(" 2 - Расшифровать")

    while True:
        choice = input()
        if choice in ('1', '2'):
            break
        print("Введите 1 или 2")

    question2 = int(choice)
    print(f"Вы выбрали: {choice}")

    text = input("Введите текст для работы:\n")

    result = kuznyechik_cipher(text, question2)
    print(result)
