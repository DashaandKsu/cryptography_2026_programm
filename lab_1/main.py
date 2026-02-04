# Русский алфавит без буквы "ё"
RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def replace_punctuation_to_codes(text: str) -> str:
    """
    Заменяет знаки препинания на трехбуквенные коды.
    "." -> "тчк", "," -> "зпт", "-" -> "тир"
    Остальные символы остаются без изменений.
    """
    result = ""
    for ch in text:
        if ch == ".":
            result += "тчк"
        elif ch == ",":
            result += "зпт"
        elif ch == "-":
            result += "тир"
        else:
            result += ch
    return result


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
    text = replace_punctuation_to_codes(text)
    # удаление всех пробелов
    text_without_spaces = ""
    for ch in text:
        if ch != " ":
            text_without_spaces += ch
    return text_without_spaces


def atbash_cipher(text: str, alphabet: str) -> str:
    """
    Шифр Атбаш.
    Для каждой буквы находим ее позицию в алфавите и берем
    симметричную букву с конца алфавита.
    Для символов вне алфавита замены не делаем.
    """
    result = ""
    n = len(alphabet)

    for ch in text:
        if ch in alphabet:
            index = alphabet.index(ch)
            mirrored_index = n - 1 - index
            result += alphabet[mirrored_index]
        else:
            # символ не из алфавита оставляем без изменений
            result += ch

    return result


def format_in_groups_of_five(text: str) -> str:
    """
    Разбивает строку на группы по 5 символов.
    Между группами добавляется пробел.
    """
    groups = []
    current_group = ""

    for i, ch in enumerate(text):
        current_group += ch
        # когда группа достигла 5 символов, добавляем ее в список
        if (i + 1) % 5 == 0:
            groups.append(current_group)
            current_group = ""

    # добавляем последнюю неполную группу, если она есть
    if current_group:
        groups.append(current_group)

    # объединяем группы через пробел
    return " ".join(groups)


def restore_punctuation_from_codes(text: str) -> str:
    """
    Восстанавливает знаки препинания из трехбуквенных кодов:
    "тчк" -> ".", "зпт" -> ",", "тир" -> "-"
    Остальные символы копируются как есть.
    """
    result = ""
    i = 0
    while i < len(text):
        # проверяем три символа вперед для кода
        if text[i:i + 3] == "тчк":
            result += "."
            i += 3
        elif text[i:i + 3] == "зпт":
            result += ","
            i += 3
        elif text[i:i + 3] == "тир":
            result += "-"
            i += 3
        else:
            result += text[i]
            i += 1
    return result


def restore_readable_text(decoded_text: str, original_text: str) -> str:
    """
    Делает текст читаемым:
    - знаки препинания уже восстановлены
    - пробелы берем из исходного текста

    Буквы берутся из декодированного текста, пробелы и переводы строк
    копируются из исходного.
    """
    result = ""
    j = 0  # индекс по decoded_text

    for ch in original_text:
        # сохраняем любые пробельные символы как есть
        if ch.isspace():
            result += ch
        else:
            # берем следующий символ из расшифрованной строки
            if j < len(decoded_text):
                result += decoded_text[j]
                j += 1
            else:
                # на всякий случай, если что-то пошло не так
                result += ch

    return result


def main() -> None:
    """Главная функция программы."""
    # 1. Ввод исходного текста
    print("Шифр Атбаш для русского алфавита (без буквы 'ё').")
    original_text = input("Введите исходный литературный текст: ")

    # 2. Нормализация текста
    normalized_text = normalize_text(original_text)

    # 3. Шифрование Атбаш
    cipher_text = atbash_cipher(normalized_text, RUS_ALPHABET)

    # 4. Форматирование вывода по 5 символов
    formatted_cipher_text = format_in_groups_of_five(cipher_text)

    print("\nШифртекст:")
    print(formatted_cipher_text)

    # 5. Расшифрование только что полученного шифртекста
    #    Сначала убираем пробелы между группами
    cipher_text_no_spaces = ""
    for ch in formatted_cipher_text:
        if ch != " ":
            cipher_text_no_spaces += ch

    # 6. Применяем Атбаш снова (операция симметричная)
    decoded_normalized_text = atbash_cipher(cipher_text_no_spaces, RUS_ALPHABET)

    # 7. Восстанавливаем знаки препинания из кодов
    decoded_with_punctuation = restore_punctuation_from_codes(decoded_normalized_text)

    # 8. Восстанавливаем пробелы по исходному тексту
    readable_text = restore_readable_text(decoded_with_punctuation, original_text)

    print("\nРасшифрованный текст:")
    print(readable_text)


if __name__ == "__main__":
    main()
