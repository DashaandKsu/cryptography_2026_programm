def on_bytes(stroka):
    if stroka.startswith('0x'):
        stroka = stroka[2:]
    temp = []
    for i in range(0, len(stroka), 2):
        temp.append(f'0x{stroka[i]}{stroka[i+1]}')
    return temp
"""Эта функция преобразует шестнадцатеричную строку в список байтов:

Проверяет наличие префикса '0x' и удаляет его если есть
Создает список байтов, группируя символы попарно
Каждая пара символов преобразуется в отдельный байт с префиксом '0x'"""


def mult_galua(a, b):
    pole = [8, 7, 6, 1, 0]
    a = format(a, '08b')
    b = format(b, '08b')
    """Эта функция выполняет умножение двух чисел в поле Галуа GF(2^8):

Определяет поле с помощью многочлена 
Преобразует входные числа в двоичную форму (8 бит)
Использует массив pole для определения коэффициентов многочлена"""

    pole_a = []
    pole_b = []
    for i in range(len(a)):
        if a[i] == '1':
            pole_a.append(7 - i)
        if b[i] == '1':
            pole_b.append(7 - i)

    mult_pole = []
    for i in range(len(pole_a)):
        for j in range(len(pole_b)):
            if not (pole_a[i] + pole_b[j]) in mult_pole:
                mult_pole.append(pole_a[i] + pole_b[j])
            else:
                mult_pole.pop(mult_pole.index(pole_a[i] + pole_b[j]))

    max_num = 0
    for elem in mult_pole:
        if elem > max_num:
            max_num = elem

    while max_num > 7:
        mult = max_num - 8
        for i in range(len(pole)):
            if (pole[i] + mult) in mult_pole:
                mult_pole.pop(mult_pole.index(pole[i] + mult))
            else:
                mult_pole.append(pole[i] + mult)

        max_num = 0
        for elem in mult_pole:
            if elem > max_num:
                max_num = elem

    res = 0
    for elem in mult_pole:
        res += 2 ** elem

    return res


def L(stroka):
    arr = [1, 148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148]

    temp = stroka
    temp.reverse()
    """Эта функция выполняет линейное преобразование блока данных:

Использует фиксированный массив коэффициентов
Разворачивает входной блок для последующих операций
Выполняет циклические XOR операции с коэффициентами
"""

    for i in range(16):
        num = 0
        for j in range(len(temp)):
            num ^= mult_galua(int(temp[j], 16), arr[j])
        num = '0x' + format(num, '02x')

        for j in range(1, len(temp)):
            temp[j-1] = temp[j]
        temp[-1] = num

    temp.reverse()
    return temp


def S(stroka):
    res = []
    table = [252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77, 233, 119, 240, 219, 147, 46, 153,
             186, 23, 54, 241, 187, 20, 205, 95, 193, 249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142,
             79, 5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31, 235, 52, 44, 81, 234, 200, 72,
             171, 242, 42, 104, 162, 253, 58, 206, 204, 181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183,
             93, 135, 21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177, 50, 117, 25, 61,
             255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87, 223, 245, 36, 169, 62, 168, 67, 201, 215, 121,
             214, 246, 124, 34, 185, 3, 224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74, 167,
             151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65, 173, 69, 70, 146, 39, 94, 85, 47, 140,
             163, 165, 125, 105, 213, 149, 59, 7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
             225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97, 32, 113, 103, 164, 45, 43, 9,
             91, 203, 155, 37, 208, 190, 229, 108, 82, 89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57,
             75, 99, 182]

    for elem in stroka:
        res.append('0x' + format(table[int(elem, 16)], '02x'))

    return res
"""Функции реализуют нелинейную подстановку:

S выполняет прямую подстановку через S-блок
S_de выполняет обратную подстановку
Используют предопределенную таблицу подстановок"""


def S_de(stroka):
    res = []
    table = [252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77, 233, 119, 240, 219, 147, 46, 153,
             186, 23, 54, 241, 187, 20, 205, 95, 193, 249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142,
             79, 5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31, 235, 52, 44, 81, 234, 200, 72,
             171, 242, 42, 104, 162, 253, 58, 206, 204, 181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183,
             93, 135, 21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177, 50, 117, 25, 61,
             255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87, 223, 245, 36, 169, 62, 168, 67, 201, 215, 121,
             214, 246, 124, 34, 185, 3, 224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74, 167,
             151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65, 173, 69, 70, 146, 39, 94, 85, 47, 140,
             163, 165, 125, 105, 213, 149, 59, 7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
             225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97, 32, 113, 103, 164, 45, 43, 9,
             91, 203, 155, 37, 208, 190, 229, 108, 82, 89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57,
             75, 99, 182]

    for elem in stroka:
        res.append('0x' + format(table.index(int(elem, 16)), '02x'))

    return res


def form_key(stroka):
    key = []
    first = on_bytes(stroka[0])
    second = on_bytes(stroka[1])
    key.append([first, second])
    """Функция генерирует расписание ключей для всех раундов шифрования:

Преобразует половинки ключа в байты
Генерирует промежуточные ключи через итеративные преобразования
Применяет функции L и S для модификации ключей"""

    array_const = []
    for i in range(1, 33):
        constant = hex(i)
        if len(constant) < 4:
            constant = f'0x{"0" * 30}0{constant[-1]}'
        else:
            constant = '0x' + ("0" * 30) + constant[2:]

        array_const.append(L(on_bytes(constant)))

    count = 0
    for i in range(4):
        key.append(list(key[-1]))
        for k in range(8):
            temp = []
            for j in range(16):
                temp.append('0x' + format(int(key[-1][0][j], 16) ^ int(array_const[count][j], 16), '02x'))

            temp = S(temp)
            temp = L(temp)

            for j in range(16):
                temp[j] = '0x' + format(int(temp[j], 16) ^ int(key[-1][1][j], 16), '02x')

            key[-1][1] = key[-1][0]
            key[-1][0] = temp

            count += 1

    res = []
    for i in range(len(key)):
        res.append(key[i][0])
        res.append(key[i][1])

    return res


def kuznechik_encrypt(stroka, key):
    if len(stroka) != 32:
        raise ValueError("Сообщение должно быть длиной 32 символа (128 бит).")
    stroka = on_bytes('0x' + stroka)
    key = form_key(key)

    for i in range(9):
        temp = []
        for j in range(16):
            temp.append('0x' + format(int(stroka[j], 16) ^ int(key[i][j], 16), '02x'))

        temp = S(temp)
        temp = L(temp)

        stroka = temp

    res = []
    for j in range(16):
        res.append('0x' + format(int(stroka[j], 16) ^ int(key[9][j], 16), '02x'))

    return res
"""Функции реализуют основной алгоритм шифрования и дешифрования:

Проверяют корректность входных данных
Выполняют необходимые преобразования формата
Применяют раунды шифрования/дешифрования
Используют функции L, S/S_de для каждого раунда"""


def kuznechik_decrypt(stroka, key):
    if len(stroka) != 16:
        raise ValueError("Зашифрованное сообщение должно быть длиной 16 байт (128 бит).")
    key = form_key(key)

    for i in range(9):
        temp = []
        for j in range(16):
            temp.append('0x' + format(int(stroka[j], 16) ^ int(key[9 - i][j], 16), '02x'))

        temp.reverse()
        temp = L(temp)
        temp.reverse()

        temp = S_de(temp)

        stroka = temp

    res = []
    for j in range(16):
        res.append('0x' + format(int(stroka[j], 16) ^ int(key[0][j], 16), '02x'))

    return res


def split_key(string, chunk_size):
    if len(string) != 64:
        raise ValueError("Ключ должен быть длиной 64 символа (256 бит).")
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]

"""Функция разделяет шестнадцатеричный ключ на части заданного размера."""

def main():
    while True:
        print("\n*** Кузнечик (ГОСТ Р 34.12-2015) ***")
        print("1. Зашифровать сообщение")
        print("2. Расшифровать сообщение")
        print("3. Выйти")
        choice = input("Выберите режим (1-3): ")

        if choice == '1':
            key_input = input("Введите ключ (64 hex-символа): ")
            try:
                key = split_key(key_input, 32)
            except ValueError as e:
                print(e)
                continue
            temp = input("Введите сообщение в формате hex (32 символа): ")
            if len(temp) != 32:
                print("Сообщение должно быть длиной 32 символа (128 бит).")
                continue
            try:
                shifr = kuznechik_encrypt(temp, key)
                print('SHIFR =', ''.join([x[2:] for x in shifr]))
            except Exception as e:
                print("Ошибка при шифровании:", e)

        elif choice == '2':
            key_input = input("Введите ключ (64 hex-символа): ")
            try:
                key = split_key(key_input, 32)
            except ValueError as e:
                print(e)
                continue
            temp = input("Введите зашифрованное сообщение в формате hex (32 символа): ")
            if len(temp) != 32:
                print("Зашифрованное сообщение должно быть длиной 32 символа (128 бит).")
                continue
            try:
                # Преобразуем hex-строку в массив байтов, как ожидает функция
                shifr = on_bytes('0x' + temp)
                deshifr = kuznechik_decrypt(shifr, key)
                print('DESHIFR =', ''.join([x[2:] for x in deshifr]))
            except Exception as e:
                print("Ошибка при расшифровке:", e)

        elif choice == '3':
            print("Выход.")
            break
        else:
            print("Некорректный выбор. Введите 1, 2 или 3.")

if __name__ == "__main__":
    main()



# 8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef - ключ 
# 1122334455667700ffeeddccbbaa9988 - сообщение

#блоки все сразу, если не хватает, то добавлять нулями!