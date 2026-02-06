# Модуль шифра Атбаш (лабораторная 1).
# Содержит все функции для шифрования и расшифрования.

# Алфавит русского языка без буквы "ё" (32 буквы)
RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def create_punctuation_codes():
    """Словарь замены знаков препинания на трехбуквенные коды."""
    codes = {}
    codes["."] = "тчк"
    codes[","] = "зпт"
    codes[":"] = "двтч"
    codes[";"] = "тчзп"
    codes["!"] = "вскл"
    codes["?"] = "впрс"
    codes["-"] = "тир"
    return codes


def create_code_to_punctuation(punctuation_codes):
    """Обратный словарь: код -> знак препинания."""
    reverse_codes = {}
    for znak in punctuation_codes:
        kod = punctuation_codes[znak]
        reverse_codes[kod] = znak
    return reverse_codes


def prepare_text_for_encryption(text, punctuation_codes):
    """Подготовка текста: нижний регистр, ё->е, знаки в коды, без пробелов."""
    text = text.lower()
    text = text.replace("ё", "е")
    result = ""
    for symbol in text:
        if symbol == " ":
            continue
        elif symbol in punctuation_codes:
            result = result + punctuation_codes[symbol]
        else:
            result = result + symbol
    return result


def encrypt_atbash(text, alphabet):
    """Шифрование по методу Атбаш."""
    alphabet_length = len(alphabet)
    encrypted = ""
    for symbol in text:
        if symbol in alphabet:
            position = 0
            for i in range(alphabet_length):
                if alphabet[i] == symbol:
                    position = i
                    break
            mirror_position = alphabet_length - 1 - position
            encrypted_symbol = alphabet[mirror_position]
            encrypted = encrypted + encrypted_symbol
        else:
            encrypted = encrypted + symbol
    return encrypted


def split_into_groups_of_five(text):
    """Разбивка текста на группы по 5 символов с пробелами."""
    result = ""
    counter = 0
    for symbol in text:
        if counter > 0 and counter % 5 == 0:
            result = result + " "
        result = result + symbol
        counter = counter + 1
    return result


def restore_punctuation_from_codes(text, code_to_punctuation):
    """Восстановление знаков препинания из кодов."""
    result = ""
    position = 0
    while position < len(text):
        code_found = False
        for kod in code_to_punctuation:
            kod_length = len(kod)
            if position + kod_length <= len(text):
                text_piece = text[position:position + kod_length]
                if text_piece == kod:
                    znak = code_to_punctuation[kod]
                    result = result + znak
                    position = position + kod_length
                    code_found = True
                    break
        if code_found == False:
            result = result + text[position]
            position = position + 1
    return result


def decrypt_atbash(encrypted_text, alphabet):
    """Расшифрование Атбаш (то же действие, что и шифрование)."""
    return encrypt_atbash(encrypted_text, alphabet)


# Функции для использования из main.py: полный цикл шифрования/расшифрования

def encrypt_text(text):
    """
    Зашифровать текст по Атбаш.
    Возвращает строку в группах по 5 символов (для вывода в консоль).
    """
    punct_codes = create_punctuation_codes()
    prepared = prepare_text_for_encryption(text, punct_codes)
    encrypted = encrypt_atbash(prepared, RUS_ALPHABET)
    grouped = split_into_groups_of_five(encrypted)
    return grouped.upper()


def decrypt_text(text):
    """
    Расшифровать текст по Атбаш.
    Принимает строку (можно с пробелами между группами).
    Возвращает читаемый текст с восстановленными знаками препинания.
    """
    code_to_punct = create_code_to_punctuation(create_punctuation_codes())
    # Убираем пробелы из ввода
    text_no_spaces = text.replace(" ", "").lower()
    decrypted = decrypt_atbash(text_no_spaces, RUS_ALPHABET)
    return restore_punctuation_from_codes(decrypted, code_to_punct)
