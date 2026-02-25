# Шифр Магма (GOST): таблица подстановок PI, преобразование T и обратное T.
# Текст: буквы алфавита -> индексы в hex, блоками по 4 байта (8 hex-символов).

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

PI = [
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1]
]


def GOST_Magma_T(in_data, out_data):
    for i in range(4):
        first_part_byte = (in_data[i] & 0xF0) >> 4
        sec_part_byte = in_data[i] & 0x0F
        first_part_byte = PI[i * 2][first_part_byte]
        sec_part_byte = PI[i * 2 + 1][sec_part_byte]
        out_data[i] = hex((first_part_byte << 4) | sec_part_byte)[2:].zfill(2)


def GOST_Magma_T_reverse(in_data, out_data):
    for i in range(4):
        first_part_byte = int(in_data[i][0], 16)
        sec_part_byte = int(in_data[i][1], 16)
        first_part_byte = PI[i * 2].index(first_part_byte)
        sec_part_byte = PI[i * 2 + 1].index(sec_part_byte)
        out_data[i] = (first_part_byte << 4) | sec_part_byte


def divide_text(n):
    """Текст -> строка hex (2 символа на букву по индексу в alf)."""
    return ''.join(format(alf.find(c), '02x') for c in n.lower() if c in alf)


def divide_oct(hex_str):
    """Строка hex разбивается на группы по 8 символов с ведущими нулями."""
    result_text = ''
    counter = 1
    for i in range(len(hex_str)):
        result_text += hex_str[i]
        if counter % 8 == 0:
            result_text += " "
        counter += 1
    result_text = result_text.split()
    for i in range(len(result_text)):
        while len(result_text[i]) < 8:
            result_text[i] = "0" + result_text[i]
    return result_text


def encrypt_text(text: str) -> str:
    """Шифрование по вашему коду: ввод 8 hex-символов -> преобразование T -> результат hex."""
    input_data = text.replace(' ', '').strip().lower()
    input_data = ''.join(c for c in input_data if c in '0123456789abcdef')
    if len(input_data) != 8:
        return ''
    try:
        in_data = [int(input_data[i : i + 2], 16) for i in range(0, 8, 2)]
    except ValueError:
        return ''
    out_data = [0] * 4
    GOST_Magma_T(in_data, out_data)
    return ''.join(out_data)


def decrypt_text(text: str) -> str:
    """Обратное преобразование по вашему коду: ввод 8 hex (результат T) -> T_reverse -> hex."""
    input_data = text.replace(' ', '').strip().lower()
    input_data = ''.join(c for c in input_data if c in '0123456789abcdef')
    if len(input_data) != 8:
        return ''
    in_data = [input_data[i : i + 2] for i in range(0, 8, 2)]
    out_data = [0] * 4
    GOST_Magma_T_reverse(in_data, out_data)
    return ''.join(format(byte, '02x') for byte in out_data)


def main():
    """Консоль: ввод hex (8 символов) -> T -> вывод -> T_reverse -> вывод."""
    print("Шифр Магма (преобразование T)")
    while True:
        print("\n1. Блок 8 hex-символов (T и T_reverse)")
        print("2. Зашифровать текст (русские буквы)")
        print("3. Расшифровать текст (hex)")
        print("4. Выход")
        choice = input("Выбор: ").strip()
        if choice == '4':
            break
        if choice == '1':
            input_data = input("Введите 8 hex-символов (например fdb97531): ").strip()
            if len(input_data) != 8:
                print("Нужно ровно 8 hex-символов.")
                continue
            try:
                in_data = [int(input_data[i : i + 2], 16) for i in range(0, 8, 2)]
            except ValueError:
                print("Некорректный hex.")
                continue
            out_data = [0] * 4
            GOST_Magma_T(in_data, out_data)
            enc = ''.join(out_data)
            print("Результат шифрования:", enc)
            in_data_reverse = [0] * 4
            GOST_Magma_T_reverse(out_data, in_data_reverse)
            back = ''.join(format(b, '02x') for b in in_data_reverse)
            print("Результат обратного преобразования:", back)
        elif choice == '2':
            t = input("Введите текст: ").strip()
            print("Результат:", encrypt_text(t))
        elif choice == '3':
            t = input("Введите hex (можно с пробелами): ").strip()
            print("Результат:", decrypt_text(t))
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
