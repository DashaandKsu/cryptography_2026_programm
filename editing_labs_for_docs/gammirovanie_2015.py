def text_to_hex(text):
    try:
        encoded = text.encode('cp1251')
        hex_str = encoded.hex().upper()
        return hex_str, None
    except Exception as e:
        return None, f"Ошибка кодирования текста: {e}"


def hex_to_text(hex_str):
    try:
        hex_str = hex_str.replace(' ', '')
        # убираем хвостовые нули паддинга
        b = bytes.fromhex(hex_str)
        b = b.rstrip(b'\x00')
        text = b.decode('cp1251')
        return text, None
    except Exception as e:
        return None, f"Ошибка декодирования HEX: {e}"


def postprocess_text(text):
    return text


def detect_input_type(text):        #функция определения типа ввода
    text = text.replace(' ', '')
    if len(text) == 0:      #если пустой текст - вернуть empty
        return 'empty'
    if all(c in '0123456789abcdefABCDEF' for c in text):        #если все символы HEX - вернуть, что введена HEX-строка
        return 'hex'
    return 'text'       #иначе - введён текст


def hex_to_bin(hex_str, bit_len):       #функция преобразования HEX-строки в двоичную фиксированной длины
    return bin(int(hex_str, 16))[2:].zfill(bit_len)


def bin_to_hex(bin_str, hex_len):       #функция преобразования двоичной строки в HEX-строку фиксированной длины
    return format(int(bin_str, 2), f'0{hex_len}x').upper()


def split_blocks(text, block_size):     #функция разбиения строки на блоки фиксированной длины
    return [text[i:i + block_size] for i in range(0, len(text), block_size)]


S_BOX = [       #таблица S-блока замены
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]


def s_box_transform(value_hex):     #t-преобразование (S-блок замены)
    res = []
    for i, ch in enumerate(value_hex):
        nibble = int(ch, 16)
        transformed = S_BOX[7 - i][nibble]
        res.append(format(transformed, '01x'))
    return ''.join(res).upper()


def g_transform(key_hex, data_hex):     #G[k]
    a = int(data_hex, 16)
    k = int(key_hex, 16)
    s = (a + k) & 0xFFFFFFFF
    s_hex = format(s, '08x').upper()
    t_hex = s_box_transform(s_hex)
    t_int = int(t_hex, 16)
    g_int = ((t_int << 11) | (t_int >> (32 - 11))) & 0xFFFFFFFF
    return format(g_int, '08x').upper()


def one_round(key_hex, left_hex, right_hex):        #один раунд сети Фейстеля
    g = g_transform(key_hex, right_hex)
    g_int = int(g, 16)
    left_int = int(left_hex, 16)
    new_right = format(g_int ^ left_int, '08x').upper()
    return right_hex, new_right


def last_round(key_hex, left_hex, right_hex):       #последний раунд сети Фейстеля (G*[K])
    g = g_transform(key_hex, right_hex)
    g_int = int(g, 16)
    left_int = int(left_hex, 16)
    new_left = format(g_int ^ left_int, '08x').upper()
    return new_left + right_hex


def expand_key(key_hex):        #развёртывание 256-битного ключа в 32 раундовых 8-битных ключей
    parts = split_blocks(key_hex, 8)
    round_keys = []
    for _ in range(3):
        round_keys.extend(parts)
    round_keys.extend(parts[::-1])
    return round_keys


def encrypt_block(block_hex, round_keys):       #шифрование одного 64-битного блока
    left = block_hex[:8]
    right = block_hex[8:]
    for i in range(31):
        left, right = one_round(round_keys[i], left, right)
    return last_round(round_keys[31], left, right)


def ctr_transform(data_hex, key_hex, iv_hex):       #режим гаммирования CTR по ГОСТ-Р 34.13-2015
    round_keys = expand_key(key_hex)        #развёртывание ключей
    blocks = split_blocks(data_hex, 16)     #разбиение текста на 64-битные блоки
    result = []     #инициализация результата
    counter = int(iv_hex, 16) << 32     #начальное значение счётчика: синхрпосылка с циклическим сдвигом на 32-бита
    for block in blocks:        #для каждого блока текста
        ctr_hex = format(counter, '016x').upper()       #64-битный счётчик
        gamma_block = encrypt_block(ctr_hex, round_keys)        #шифрование счётчика - получение гаммы
        block_int = int(block, 16)
        gamma_int = int(gamma_block, 16)
        res_int = block_int ^ gamma_int     #XOR открытого текста с гаммой
        res_hex = format(res_int, '016x').upper()       #результат шифрования блока
        result.append(res_hex)
        counter += 1        #увеличение счётчика
    return ''.join(result)


def magma_cipher(text, question2):      #главная функция

    input_type = detect_input_type(text)        #определение типа ввода

    if input_type == 'empty':       #ничего не введено - вывести ошибку и завершить программу
        return "Ошибка: пустой текст"

    if input_type == 'text':        #введён текст - перевести в HEX-строку
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
    if len(key_hex) != 64:      #если длина ключа не ранва 64 - вывести ошибку и завершить программу
        return f"Ошибка: ключ должен быть 64 hex-символа, получено {len(key_hex)}"
    if not all(c in '0123456789ABCDEF' for c in key_hex):       #если не все символы HEX, то вывести ошибку и завершить программу
        return "Ошибка: ключ содержит недопустимые символы"

    iv_hex = input("Введите синхропосылку IV (8 шестнадцатеричных символов):\n> ").replace(' ', '').upper()     #ввод синхрпосылки IV
    if len(iv_hex) != 8:        #если длина не равна 8 - вывести ошибку и завершить программу
        return f"Ошибка: IV должна быть 8 hex-символов, получено {len(iv_hex)}"
    if not all(c in '0123456789ABCDEF' for c in iv_hex):        #если не все символы HEX - вывести ошибку и завершить программу
        return "Ошибка: IV содержит недопустимые символы"

    if len(text) % 16 != 0:     #если длина текста не кратна 16, то дополняем текст нулями справа до длины, кратной 16
        padding = 16 - (len(text) % 16)
        text = text + '0' * padding
        print(f"HEX-строка дополнена нулями до длины, кратной 16: {text}")

    blocks = [text[i:i + 16] for i in range(0, len(text), 16)]      #разбиваем текст на блоки по 16 символов
    print(f"Текст разбит на {len(blocks)} блоков по 16 hex-символов")

    try:
        result_hex = ctr_transform(text, key_hex, iv_hex)       #шифруем

        if question2 == 1:      #если шифрование 0 вывести результат, добавив пробелы каждые 4 символа
            formatted = ' '.join(result_hex[i:i + 4] for i in range(0, len(result_hex), 4))
            return f"Зашифрованный текст (hex): {formatted}"

        else:       #если расшифрование - вывести результат в русском алфавите и HEX

            text_result, error = hex_to_text(result_hex)
            if not error and text_result:
                print(f"\nРезультат в русском алфавите: {postprocess_text(text_result)}")

            formatted = ' '.join(result_hex[i:i + 4] for i in range(0, len(result_hex), 4))
            return f"Расшифрованный текст (hex): {formatted}"

    except Exception as e:
        return f"Ошибка при выполнении: {e}"


if __name__ == "__main__":
    print("Выбран алгоритм гаммирования (ГОСТ Р 34.13-2015)\n")
    print("Выберите, что необходимо сделать:")
    print(" 1 - Зашифровать")
    print(" 2 - Расшифровать")

    while True:
        choice = input().strip()
        if choice in ('1', '2'):
            break
        print("Введите 1 или 2")

    question2 = int(choice)
    print(f"\nВы выбрали: {choice}")

    text = input("Введите текст для работы:\n").strip()

    result = magma_cipher(text, question2)
    print(result)
