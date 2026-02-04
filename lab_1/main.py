# Русский алфавит без буквы "ё"
RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

# Словарь замены знаков препинания на коды
PUNCTUATION_TO_CODE = {
    ".": "тчк",
    ",": "зпт",
    ":": "двтч",
    ";": "тчзп",
    "!": "вскл",
    "?": "впрс",
    "-": "тир"
}

# Обратный словарь для расшифрования
CODE_TO_PUNCTUATION = {v: k for k, v in PUNCTUATION_TO_CODE.items()}


def normalize_text(text: str) -> str:
    """
    Нормализация текста перед шифрованием:
    - перевод в нижний регистр
    - замена "ё" на "е"
    - замена знаков препинания на коды
    - удаление пробелов
    """
    # нижний регистр
    text = text.lower()
    # замена "ё" на "е"
    text = text.replace("ё", "е")
    # замена знаков препинания на трехбуквенные коды
    result = ""
    for ch in text:
        if ch == " ":
            continue
        result += PUNCTUATION_TO_CODE.get(ch, ch)

    return result


def atbash_cipher(text: str, alphabet: str) -> str:
    """
    Шифр Атбаш.
    Для каждой буквы находим ее позицию в алфавите и берем
    симметричную букву с конца алфавита.
    """
    result = ""
    n = len(alphabet)

    for ch in text:
        if ch in alphabet:
            index = alphabet.index(ch)
            result += alphabet[n - 1 - index]
        else:
            result += ch

    return result


def format_in_groups_of_five(text: str) -> str:
    """
    Разбивает текст на группы по 5 символов для вывода.
    """
    result = ""
    for i, ch in enumerate(text):
        if i > 0 and i % 5 == 0:
            result += " "
        result += ch
    return result


def restore_punctuation(text: str) -> str:
    """
    Восстанавливает знаки препинания из кодов.
    """
    result = ""
    i = 0

    while i < len(text):
        replaced = False
        for code, symbol in CODE_TO_PUNCTUATION.items():
            if text.startswith(code, i):
                result += symbol
                i += len(code)
                replaced = True
                break
        if not replaced:
            result += text[i]
            i += 1

    return result


def main() -> None:
    print("Шифр Атбаш для русского алфавита (без буквы 'ё')")

    original_text = input("Введите исходный текст: ")

    # Предварительная обработка
    normalized_text = normalize_text(original_text)

    # Шифрование
    encrypted_text = atbash_cipher(normalized_text, RUS_ALPHABET)
    print("\nШифртекст:")
    print(format_in_groups_of_five(encrypted_text))

    # Расшифрование (Атбаш симметричен)
    decrypted_text = atbash_cipher(encrypted_text, RUS_ALPHABET)
    readable_text = restore_punctuation(decrypted_text)

    print("\nРасшифрованный текст:")
    print(readable_text)


if __name__ == "__main__":
    main()
