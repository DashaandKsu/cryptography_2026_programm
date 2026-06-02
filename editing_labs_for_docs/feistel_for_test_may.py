# вспомогательные функции (были в utils, перенесены для локального запуска)

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'


def text_to_hex(text):
    """Преобразование русского текста в HEX-строку через индексы алфавита."""
    result = ''
    for ch in text.lower():
        if ch in ALPHABET:
            result += format(ALPHABET.index(ch), '02x')
        elif ch == 'ё':
            result += format(ALPHABET.index('е'), '02x')
        else:
            return '', f"Ошибка: символ '{ch}' не найден в алфавите"
    return result, ''


def hex_to_text(hex_str):
    """Преобразование HEX-строки обратно в русский текст."""
    hex_str = hex_str.replace(' ', '').lower()
    if len(hex_str) % 2 != 0:
        return '', 'Ошибка: нечётная длина HEX-строки'
    result = ''
    for i in range(0, len(hex_str), 2):
        val = int(hex_str[i:i+2], 16)
        if val < len(ALPHABET):
            result += ALPHABET[val]
        else:
            return '', f"Ошибка: значение {val} вне алфавита"
    return result, ''


def postprocess_text(text):
    """Постобработка текста (здесь просто возвращает как есть)."""
    return text


def detect_input_type(text):        #функция определения типа ввода
    text = text.replace(' ', '')
    if len(text) == 0:      #если ничего не введено - вернуть, что пустой текст
        return 'empty'
    if all(c in '0123456789abcdefABCDEF' for c in text):        #если все символы принадлежат HEX-алфавиту - вернуть, что введена HEX-строка
        return 'hex'
    return 'text'       #иначе вернуть, что введён текст


PI = [      #таблица замены S-блока
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

PI_INV = []     #инициализация инвертированной таблицы замены S-блока
for pi in PI:   #для каждой строки в PI
    inv = [0] * 16      #временно заполнить строку нулями
    for i, val in enumerate(pi):    #для каждой пары индекс(i)-значение(val) в строке PI
        inv[val] = i    #добавить на позицию val записать значение i
    PI_INV.append(inv)  #добавить строку в PI_INV

def t_transform(hex_string):    #функция шифрования S-блока

    hex_string = hex_string.lower()     #приводим строку к нижнему регистру
    nibbles = list(hex_string)      #создаём список из 8 HEX-значений
    result_nibbles = []     #инициализация выходного блока

    for i in range(8):      #для i от 0 до 7
        nibble = nibbles[i]     #получить i-ое HEX-значение исходного блока
        nibble_value = int(nibble, 16)      #перевести i-ое HEX-значение исходного блока в 10СС
        pi_index = 7 - i        #получить индекс строки таблицы замены PI
        substituted_value = PI[pi_index][nibble_value]      #получить шифрзначение - по таблице замены PI взять столбец, соответствующий HEX-значению i-ого символа исходного блока, и (7-i)-ую строку
        result_nibbles.append(hex(substituted_value)[2:])   #перевести шифрзначение в HEX и добавить в результат

    return ''.join(result_nibbles)      #возвращение выходного блока


def t_transform_inverse(hex_string):        #функция расшифрования S-блока

    hex_string = hex_string.lower()     #приводим строку к нижнему регистру
    nibbles = list(hex_string)      #создаём список из 8 HEX-значений
    result_nibbles = []     #инициализация выходного блока

    for i in range(8):       #для i от 0 до 7
        nibble = nibbles[i]     #получить i-ое HEX-значение блока шифртекста
        nibble_value = int(nibble, 16)      #перевести i-ое HEX-значение блока шифртекста в 10СС
        pi_index = 7 - i        #получить индекс строки инвертированной таблицы замены PI_INV
        original_value = PI_INV[pi_index][nibble_value]     #получить расшифрованное значение - по инвертированной таблице замены PI_INV взять столбец, соответствующий HEX-значению i-ого символа блока шифртекста, и (7-i)-ую строку
        result_nibbles.append(hex(original_value)[2:])      #перевести расшифрованное значение в HEX и добавить в результат

    return ''.join(result_nibbles)      #возвращение выходного блока


def format_hex_with_spaces(hex_string):     #функция форматирования HEX-строки - пробел каждые 4 символа
    return ' '.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))


def gost_t_transform(text, question2):      #главная функция
    input_type = detect_input_type(text)        #определение типа ввода

    if input_type == 'empty':       #если строка text - пустая, то вывести ошибку и завершить программу
        return "Ошибка: пустой текст"

    if input_type == 'text':        #сли введён текст - то преобразовать text в HEX-строку
        hex_str, error = text_to_hex(text)
        if error:       #если в text символ не из алфавита - вывести ошибку и завершить программу
            return error
        text = hex_str
        print(f"Текст преобразован в HEX: {text}")

    text = text.replace(' ', '').lower()

    if len(text) % 8 != 0:      #дополнение HEX-строки до длины, кратной 8
        padding = 8 - (len(text) % 8)
        text = text + '0' * padding
        print(f"HEX-строка дополнена нулями до длины, кратной 8: {text}")

    blocks = [text[i:i + 8] for i in range(0, len(text), 8)]    #разбиение HEX-строки на блоки по 8 символов

    if question2 == 1:      #если шифрование
        result_blocks = []      #инициализация результата
        for block in blocks:    #для каждого блока (block) в списке (blocks)
            transformed = t_transform(block)    #шифрование блока
            result_blocks.append(transformed)   #добавление выходного блока в результат

        result = ''.join(result_blocks)     #объединение всех выходных блоков
        formatted_result = format_hex_with_spaces(result.upper())   #постобработка результата - добавление пробела каждые 4 символа
        return f"Результат прямого t-преобразования: {formatted_result}"    #возвращение результата

    else:       #если расшифрование
        result_blocks = []      #инициализация результата
        for block in blocks:    #для каждого блока (block) в списке (blocks)
            transformed = t_transform_inverse(block)    #расшифрование блока
            result_blocks.append(transformed)       #добавление выходного блока в результат

        result = ''.join(result_blocks)     #объединение всех выходных блоков
        formatted_result = format_hex_with_spaces(result.upper())   #постобработка результата - добавление пробела каждые 4 символа

        text_result, error = hex_to_text(result)        #преобразование HEX-строки результата в текст
        if not error and text_result:
            print(f"\nРезультат в русском алфавите: {postprocess_text(text_result)}") #постобработка текста

        return f"Результат обратного t-преобразования: {formatted_result}"      #возвращение результата


if __name__ == "__main__":
    print("Выбран алгоритм №7")
    print("Выберите, что необходимо сделать:")
    print(" 1 - Зашифровать")
    print(" 2 - Расшифровать")
    question2 = int(input().strip())
    print(f"Вы выбрали: {question2}")
    print("Введите текст для работы:")
    text = input()
    result = gost_t_transform(text, question2)
    print(result)
