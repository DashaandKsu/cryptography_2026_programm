from typing import List
import math
from pprint import pprint
from typing import List

"""Функция получения индексов символа"""
def all_indexes(key: str, ch: str) -> List[int]:

    return [index for index, i in enumerate(key) if i == ch]
"""Принимает ключевой строку key и символ ch
Использует генератор списков для поиска всех позиций символа в ключе
Возвращает список индексов, где найден символ
Например, если key="abcab" и ch='a', вернет [0, 3]"""


"""Функция создания массива порядка"""
def arr_from_key(key: str) -> List[int]:
    arr = [0 for _ in range(len(key))]
    indexes = {}
    for i in key:
        indexes[i] = all_indexes(key, i)
    indexes = dict(sorted(indexes.items(), key=lambda x:x[0]))
    idx = 1
    for i in indexes:
        for index in indexes[i]:
            arr[index] = idx
            idx += 1
    return arr
"""Создает массив для определения порядка колонн в шифровании
Использует словарь indexes для хранения позиций каждого символа ключа
Сортирует символы ключа по алфавиту
Назначает номера колоннам в порядке появления символов в отсортированном ключе
Например, для ключа "красный":"""


def encrypt(message: str, key: str) -> str:
    message = list(message)
    arr = arr_from_key(key)
    n = len(arr)

    matrix = [['' for _ in range(n)] for _ in range(math.ceil(len(message) / n))]
    cols, rows = len(matrix[0]), len(matrix)
    for i in range(rows):
        for j in range(cols):
            matrix[i][j] = message.pop(0)
            if not message:
                break
    tmp = []
    for col in range(cols):
        tmp.append(''.join([matrix[row][col] for row in range(rows)]))
    return ''.join([x[0] for x in sorted(zip(tmp, arr), key=lambda x:x[1])])
"""Преобразует сообщение в список символов для удобной работы
Создает матрицу размером (длина_сообщения/n × n)
Заполняет матрицу построчно слева направо
Читает символы столбцами и объединяет их в строки
Сортирует полученные строки согласно порядку колонн из массива arr"""


def decrypt(encypted_message: str, key: str) -> str:
    encypted_message = list(encypted_message)
    arr = arr_from_key(key)
    print(arr)
    matrix = [['' for _ in range(len(arr))] for _ in range(math.ceil(len(encypted_message) / len(arr)))]
    long = (len(encypted_message) % len(arr))
    idx = 1
    while idx <= len(arr):
        x = arr.index(idx)
        offset = 0
        if x >= long and long != 0:
            offset = 1
        for row in range(len(matrix) - offset):
            matrix[row][x] = encypted_message.pop(0)
        idx += 1
    return ''.join([''.join(x) for x in matrix]).replace('прб', ' ').replace('зпт', ',').replace('тчк', '.')
"""Преобразует зашифрованные символы обратно в матрицу
Учитывает длину строки при заполнении последних столбцов
Объединяет символы построчно
Восстанавливает пробелы, запятые и точки из специальных обозначений"""


def vertical():
    choice = int(input("Зашифровать - 1 или расшифровать - 2 "))
    key = input("Введите ключ: ")
    message = input("Введите сообщение: ").replace(" ", "прб").replace(",", "зпт").replace(".", 'тчк').replace(':', '').replace(';', '').replace('!', '').replace('?', '').lower()
    if choice == 1:
        print(f"Зашифрованное сообщение {encrypt(message, key)}")
    else:
        print(f"Расшифрованное сообщение {decrypt(message, key)}")
"""Предоставляет интерактивный интерфейс для пользователя
Подготавливает текст к обработке, заменяя специальные символы
Выполняет либо шифрование, либо дешифрование в зависимости от выбора пользователя"""

if __name__ == '__main__':
    vertical()