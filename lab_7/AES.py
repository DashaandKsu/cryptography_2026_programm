alphabet_lower_1 = ['а','б','в','г','д','е','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я',' ']
def index_in_alphabet_lower_1(letter): 
    # выводит индекс буквы в алфавите
    for i in range(len(alphabet_lower_1)):
        if letter == alphabet_lower_1[i]:
            return i
    return False

def translate_to_hex(text): 
    # на вход, например: красивыми
    new_text = ""
    for i in range(len(text)):
        variable = index_in_alphabet_lower_1(text[i])
        new_text += f"0x{variable:02x}"[2:]
    return new_text # на выход, например: 0a10001108021b0c08

def translate_from_hex(text): 
    # на вход, например: 0a10001108021b0c08
    new_text = ""
    for i in range(0, len(text), 2):
        new_text += alphabet_lower_1[(int(text[i], 16) * 16 + int(text[i+1], 16)) % 33]
    return new_text # на выход, например: красивыми

def prepare_text_for_enc(text):
    text = text.replace(',', 'зпт') # все запятые меняем на зпт
    text = text.replace('.', 'тчк') # все точки меняем на тчк
    text = text.replace(':', 'двтч') # все двоеточия меняем на двтч
    text = text.replace('-', 'тиретире') # все тире меняем на тиретире
    text = text.replace(';', 'запчк')
    text = text.replace('—', 'длинтре')
    text = text.replace('«', 'кавычкаодин')
    text = text.replace('»', 'кавычкадва')
    text = text.replace('ё', 'е')
    text = text.replace('Ё', 'Е')
    text = text.lower()
    return text

def end_text_of_decr(text):
    text = text.replace('зпт', ',')
    text = text.replace('тчк', '.')
    text = text.replace('двтч', ':')
    text = text.replace('тиретире', '-')
    text = text.replace('длинтре', '—')
    text = text.replace('запчк', ';')
    text = text.replace('кавычкаодин', '«')
    text = text.replace('кавычкадва', '»')
    return text

Sbox = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B,
0xFE, 0xD7, 0xAB, 0x76,
0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF,
0x9C, 0xA4, 0x72, 0xC0,
0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1,
0x71, 0xD8, 0x31, 0x15,
0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2,
0xEB, 0x27, 0xB2, 0x75,
0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3,
0x29, 0xE3, 0x2F, 0x84,
0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39,

0x4A, 0x4C, 0x58, 0xCF,
0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F,
0x50, 0x3C, 0x9F, 0xA8,
0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21,
0x10, 0xFF, 0xF3, 0xD2,
0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D,
0x64, 0x5D, 0x19, 0x73,
0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14,
0xDE, 0x5E, 0x0B, 0xDB,
0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62,
0x91, 0x95, 0xE4, 0x79,
0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA,
0x65, 0x7A, 0xAE, 0x08,
0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F,
0x4B, 0xBD, 0x8B, 0x8A,
0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9,
0x86, 0xC1, 0x1D, 0x9E,
0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9,
0xCE, 0x55, 0x28, 0xDF,
0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F,
0xB0, 0x54, 0xBB, 0x16,
)
InvSbox = (
0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E,
0x81, 0xF3, 0xD7, 0xFB,
0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44,
0xC4, 0xDE, 0xE9, 0xCB,
0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B,
0x42, 0xFA, 0xC3, 0x4E,
0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49,
0x6D, 0x8B, 0xD1, 0x25,
0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC,
0x5D, 0x65, 0xB6, 0x92,
0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57,
0xA7, 0x8D, 0x9D, 0x84,
0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05,
0xB8, 0xB3, 0x45, 0x06,
0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03,
0x01, 0x13, 0x8A, 0x6B,
0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE,
0xF0, 0xB4, 0xE6, 0x73,
0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8,
0x1C, 0x75, 0xDF, 0x6E,
0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E,
0xAA, 0x18, 0xBE, 0x1B,
0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE,
0x78, 0xCD, 0x5A, 0xF4,
0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59,
0x27, 0x80, 0xEC, 0x5F,
0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F,
0x93, 0xC9, 0x9C, 0xEF,
0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C,
0x83, 0x53, 0x99, 0x61,
0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63,
0x55, 0x21, 0x0C, 0x7D,
)
xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)
Rcon = (
0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)

def text2matrix(text):
    """
    Преобразует текст в матрицу.
    
    :param text: Исходный текст.
    :return: Матрица байтов.
    """
    matrix = []
    for i in range(16):
        byte = (text >> (8 * (15 - i))) & 0xFF
        if i % 4 == 0:
            matrix.append([byte])
        else:
            matrix[i//4].append(byte)
    return matrix

def matrix2text(matrix):
    """
    Преобразует матрицу обратно в текст.
    
    :param matrix: Матрица байтов.
    :return: Исходный текст.
    """
    text = 0
    for i in range(4):
        for j in range(4):
            text |= (matrix[i][j] << (120 - 8 * (4 * i + j)))
    return text

class AES:
    def __init__(self, master_key):
        """
        Инициализирует объект AES с заданным мастер-ключом.
        
        :param master_key: Мастер-ключ.
        """
        self.change_key(master_key)  # Инициализация ключей раундов

    def change_key(self, master_key):
        """
        Обновляет ключи раундов на основе нового мастер-ключа.
        
        :param master_key: Новый мастер-ключ.
        """
        self.round_keys = text2matrix(master_key)  # Преобразование ключа в матрицу
        # print(self.round_keys)  # Отладочный вывод (закомментирован)
        
        # Генерация ключей для всех раундов (10 раундов, 11 ключей)
        for i in range(4, 4 * 11):
            self.round_keys.append([])  # Добавление нового пустого ключа раунда
            if i % 4 == 0:  # Для каждого 4-го ключа особый алгоритм генерации
                # Первый байт нового ключа
                byte = self.round_keys[i - 4][0] \
                       ^ Sbox[self.round_keys[i - 1][1]] \
                       ^ Rcon[i // 4]
                self.round_keys[i].append(byte)
                # Остальные 3 байта нового ключа
                for j in range(1, 4):
                    byte = self.round_keys[i - 4][j] \
                           ^ Sbox[self.round_keys[i - 1][(j + 1) % 4]]
                    self.round_keys[i].append(byte)
            else:  # Для остальных ключей - просто XOR с предыдущим ключом
                for j in range(4):
                    byte = self.round_keys[i - 4][j] \
                           ^ self.round_keys[i - 1][j]
                    self.round_keys[i].append(byte)
        # print(self.round_keys)  # Отладочный вывод (закомментирован)

    def encrypt(self, plaintext):
        """Шифрование открытого текста"""
        self.plain_state = text2matrix(plaintext)  # Преобразование текста в матрицу состояний
        self.__add_round_key(self.plain_state, self.round_keys[:4])  # Начальное добавление ключа
    
        # 9 основных раундов шифрования
        for i in range(1, 10):
            self.__round_encrypt(self.plain_state, self.round_keys[4 * i: 4 * (i + 1)])
    
        # Финальный раунд (без MixColumns)
        self.__sub_bytes(self.plain_state)  # Байтовая замена
        self.__shift_rows(self.plain_state)  # Сдвиг строк
        self.__add_round_key(self.plain_state, self.round_keys[40:])  # Добавление ключа
    
        return matrix2text(self.plain_state)  # Преобразование результата в текст

    def decrypt(self, ciphertext):
        """Дешифрование зашифрованного текста"""
        self.cipher_state = text2matrix(ciphertext)  # Преобразование текста в матрицу состояний
        self.__add_round_key(self.cipher_state, self.round_keys[40:])  # Начальное добавление ключа
    
        # Обратные преобразования финального раунда
        self.__inv_shift_rows(self.cipher_state)  # Обратный сдвиг строк
        self.__inv_sub_bytes(self.cipher_state)  # Обратная байтовая замена
    
        # 9 основных раундов дешифрования
        for i in range(9, 0, -1):
            self.__round_decrypt(self.cipher_state, self.round_keys[4 * i: 4 * (i + 1)])
    
        self.__add_round_key(self.cipher_state, self.round_keys[:4])  # Финальное добавление ключа
    
        return matrix2text(self.cipher_state)  # Преобразование результата в текст

    def __add_round_key(self, s, k):
        """Добавление ключа раунда (XOR состояния с ключом)"""
        for i in range(4):
            for j in range(4):
                s[i][j] ^= k[i][j]  # Побитовый XOR каждого элемента состояния с ключом

    def __round_encrypt(self, state_matrix, key_matrix):
        """Один раунд шифрования"""
        self.__sub_bytes(state_matrix)  # Байтовая замена
        self.__shift_rows(state_matrix)  # Сдвиг строк
        self.__mix_columns(state_matrix)  # Перемешивание столбцов
        self.__add_round_key(state_matrix, key_matrix)  # Добавление ключа раунда

    def __round_decrypt(self, state_matrix, key_matrix):
        """Один раунд дешифрования"""
        self.__add_round_key(state_matrix, key_matrix)  # Добавление ключа раунда
        self.__inv_mix_columns(state_matrix)  # Обратное перемешивание столбцов
        self.__inv_shift_rows(state_matrix)  # Обратный сдвиг строк
        self.__inv_sub_bytes(state_matrix)  # Обратная байтовая замена

    def __sub_bytes(self, s):
        """Байтовая замена с использованием S-блока"""
        for i in range(4):
             for j in range(4):
                 s[i][j] = Sbox[s[i][j]]  # Замена каждого байта по таблице Sbox

    def __inv_sub_bytes(self, s):
        """Обратная байтовая замена с использованием обратного S-блока"""
        for i in range(4):
            for j in range(4):
                s[i][j] = InvSbox[s[i][j]]  # Замена каждого байта по таблице InvSbox

    def __shift_rows(self, s):
    
        s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1],
        s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2],
        s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3],

    def __inv_shift_rows(self, s):
    # Исправленная версия для 128-битного AES
        s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]  # было 3 значения справа
        s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]  # добавить 4-й элемент
        s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]
        return s


    def __mix_single_column(self, a):
    
        t = a[0] ^ a[1] ^ a[2] ^ a[3]  # Временная переменная для XOR всех элементов столбца
        u = a[0]  # Сохранение первого элемента столбца
        a[0] ^= t ^ xtime(a[0] ^ a[1])  # Преобразование первого элемента
        a[1] ^= t ^ xtime(a[1] ^ a[2])  # Преобразование второго элемента
        a[2] ^= t ^ xtime(a[2] ^ a[3])  # Преобразование третьего элемента
        a[3] ^= t ^ xtime(a[3] ^ u)  # Преобразование четвертого элемента

    def __mix_columns(self, s):
        """Применение MixColumns ко всей матрице состояний"""
        for i in range(4):  # Для каждого из 4 столбцов
            self.__mix_single_column(s[i])  # Применяем перемешивание к столбцу

    def __inv_mix_columns(self, s):
        """Обратное преобразование MixColumns"""
        for i in range(4):  # Для каждого из 4 столбцов
            u = xtime(xtime(s[i][0] ^ s[i][2]))  # Промежуточные вычисления
            v = xtime(xtime(s[i][1] ^ s[i][3]))  # Промежуточные вычисления
            s[i][0] ^= u  # Применение к первому элементу
            s[i][1] ^= v  # Применение ко второму элементу
            s[i][2] ^= u  # Применение к третьему элементу
            s[i][3] ^= v  # Применение к четвертому элементу
        self.__mix_columns(s)  # Дополнительное применение MixColumns

def AES_encryption(text, key, flag_hex="Да"):
    """
    Шифрует текст с помощью AES.
    
    :param text: Текст для шифрования.
    :param key: Ключ шифрования.
    :param flag_hex: Флаг, указывающий, является ли ключ шестнадцатеричным.
    :return: Зашифрованный текст или сообщение об ошибке.
    """
    if len(key) != 32:  # Проверка длины ключа (128 бит в hex-представлении)
        return "Неверный размер ключа (ключ должен быть 128 бит)!"
    
    # if not (text[0] in "0123456789abcdef"):  # Если текст не в hex-формате
    #     text = prepare_text_for_enc(text)  # Подготовка текста
    #     text = translate_in_hex(text)  # Перевод в hex
    
    key = int(key, 16)  # Преобразование hex-ключа в число
    AES1 = AES(key)  # Создание объекта AES с ключом
    encrypted = ""  # Результирующая строка
    
    # Шифрование по блокам по 32 hex-символа (128 бит)
    for i in range(0, len(text), 32):
        text_ = int(text[i:(i+32)], 16)  # Текущий блок текста
        temp = hex(AES1.encrypt(text_))[2:]  # Шифрование блока
        while (len(temp) % 32 != 0):  # Дополнение нулями до 32 символов
            temp = '0' + temp
        encrypted += temp  # Добавление к результату

    # Обработка последнего неполного блока
    lack = len(encrypted) % 32
    if lack != 0:
        text_ = int(text[(-1)*lack - 1:], 16)  # Последний неполный блок
        temp = hex(AES1.encrypt(text_))[2:]  # Шифрование блока
        while (len(temp) % 32 != 0):  # Дополнение нулями
            temp = '0' + temp
        encrypted += temp  # Добавление к результату

    if flag_hex == "Да":  # Если нужен hex-результат
        return encrypted
    else:  # Если нужен текстовый результат
        if len(encrypted) % 2 != 0:  # Проверка четности длины
            encrypted = '0' + encrypted  # Дополнение нулем
        return end_text_of_decr(translate_from_hex(encrypted))  # Преобразование в текст

def AES_decryption(text, key, flag_hex="Да"):
    """
    Расшифровывает текст с помощью AES.
    
    :param text: Текст для расшифрования.
    :param key: Ключ расшифрования.
    :param flag_hex: Флаг, указывающий, является ли текст шестнадцатеричным.
    :return: Расшифрованный текст или сообщение об ошибке.
    """
    if len(key) != 32:  # Проверка длины ключа (128 бит в hex-представлении)
        return "Неверный размер ключа (ключ должен быть 128 бит)!"
    
    # if not (text[0] in "0123456789abcdef"):  # Если текст не в hex-формате
    #     text = prepare_text_for_enc(text)  # Подготовка текста
    #     text = translate_in_hex(text)  # Перевод в hex
    
    key = int(key, 16)  # Преобразование hex-ключа в число
    AES1 = AES(key)  # Создание объекта AES с ключом
    decrypted = ""  # Результирующая строка
    
    # Расшифрование по блокам по 32 hex-символа (128 бит)
    for i in range(0, len(text), 32):
        text_ = int(text[i:(i + 32)], 16)  # Текущий блок текста
        temp = hex(AES1.decrypt(text_))[2:]  # Расшифрование блока
        while (len(temp) % 32 != 0):  # Дополнение нулями до 32 символов
            temp = '0' + temp
        decrypted += temp  # Добавление к результату
    
    # Обработка последнего неполного блока
    lack = len(decrypted) % 32
    if lack != 0:
        text_ = int(text[(-1) * lack - 1:], 16)  # Последний неполный блок
        temp = hex(AES1.decrypt(text_))[2:]  # Расшифрование блока
        while (len(temp) % 32 != 0):  # Дополнение нулями
            temp = '0' + temp
        decrypted += temp  # Добавление к результату
    
    if flag_hex == "Да":  # Если нужен hex-результат
        return decrypted
    else:  # Если нужен текстовый результат
        if len(decrypted) % 2 != 0:  # Проверка четности длины
            decrypted = '0' + decrypted  # Дополнение нулем
        return end_text_of_decr(translate_from_hex(decrypted))  # Преобразование в текст


if __name__ == "__main__":
    # Блок, где мы вводим данные для программы, кроме ключа.
    str_ = input("Введите текст: ").strip()
    cipher = input("Введите алгоритм: ").strip()
    switch_raw = input("Введите режим шифра (зашифрование/расшифрование): ")
    switch = switch_raw.strip().casefold()

    is_encrypt = switch == "зашифрование"
    is_decrypt = switch == "расшифрование"

    if cipher == "AES" and is_encrypt:
        key1 = input("Введите ключ: ").strip()
        flag_hex1 = input("Переводить в 16СС на выходе? (Да/Нет) : ").strip()
        print(AES_encryption(str_, key1, flag_hex1))

    elif cipher == "AES" and is_decrypt:
        key1 = input("Введите ключ: ").strip()
        flag_hex1 = input("Переводить в 16СС на выходе? (Да/Нет): ").strip()
        print(AES_decryption(str_, key1, flag_hex1))

    elif cipher == "AES":
        print(
            "Режим не распознан: введите целиком «зашифрование» или «расшифрование» "
            f"(сейчас: {switch_raw!r})."
        )
    else:
        print(f"Алгоритм не поддерживается или опечатка (сейчас: {cipher!r}). Ожидается: AES.")

# FIPS-197
# plaintext: 00112233445566778899aabbccddeeff
# key:       000102030405060708090a0b0c0d0e0f
#       69c4e0d86a7b0430d8cdb78070b4c55a