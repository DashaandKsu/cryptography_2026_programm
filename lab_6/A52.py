import collections

# Алфавит в нижнем регистре
alphabet_lower_2 = [
    'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й',
    'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у',
    'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
    'э', 'ю', 'я', 
]

def prepare_text_for_enc2(text):
    """Подготавливает текст для шифрования."""
    text = text.replace(' ', 'прбл')
    text = text.replace(',', 'зпт')  
    text = text.replace('.', 'тчк')  
    text = text.replace(':', 'двтч')  
    text = text.replace('-', 'тиретире')  
    text = text.replace(';', 'запчк')
    text = text.replace('—', 'длинтре')
    text = text.replace('«', 'кавычкаодин')
    text = text.replace('»', 'кавычкадва')
    text = text.replace('ё', 'е')
    text = text.replace('Ё', 'Е')
    return text.lower()

def end_text_of_decr2(text):
    """Восстанавливает текст после расшифровки."""
    text = text.replace('прбл', ' ')
    text = text.replace('зпт', ',')
    text = text.replace('тчк', '.')
    text = text.replace('двтч', ':')
    text = text.replace('тиретире', '-')
    text = text.replace('длинтре', '—')
    text = text.replace('запчк', ';')
    text = text.replace('кавычкаодин', '«')
    text = text.replace('кавычкадва', '»')
    return text

def index_in_lower_2(letter):
    """Возвращает индекс буквы в алфавите."""
    for i in range(len(alphabet_lower_2)):
        if letter == alphabet_lower_2[i]:
            return i
    return False

def bits_to_text(bit_str):
    """Преобразует бинарную строку обратно в текст."""
    result = ""
    for i in range(0, len(bit_str), 5):  # Каждая буква представлена 5 битами
        binary_letter = bit_str[i:i+5]
        index = int(binary_letter, 2)
        result += alphabet_lower_2[index]
    return result

def A5_2_one_frame(key, frame, text):
    key = [int(i) for i in key]
    frame = [int(i) for i in frame]
    text = [int(i) for i in text]

    # Инициализация 4 регистров
    R1 = collections.deque([0]*19)
    R2 = collections.deque([0]*22) 
    R3 = collections.deque([0]*23)
    R4 = collections.deque([0]*17)  # Контрольный регистр

    
    for i in range(64):
        # Заполнение регистров ключом
        R1.append(key[i % 64] ^ R1[18] ^ R1[17] ^ R1[16] ^ R1[13])
        R2.append(key[i % 64] ^ R2[21] ^ R2[20])
        R3.append(key[i % 64] ^ R3[22] ^ R3[21] ^ R3[20] ^ R3[7])
        R4.append(key[i % 64] ^ R4[16] ^ R4[11])  # Полином X^17 + X^12 + 1
        
        # Обновление регистров
        R1.popleft()
        R2.popleft() 
        R3.popleft()
        R4.popleft()

    # Генерация гаммы 
    G = []
    for _ in range(114):
        # Мажоритарная функция от R4[3], R4[7], R4[10]
        maj_bits = [R4[3], R4[7], R4[10]]
        majority = sorted(maj_bits)[1]
        
        # Тактирование регистров
        if R4[3] == majority: R2 = clock(R2, 21)
        if R4[7] == majority: R3 = clock(R3, 22)
        if R4[10] == majority: R1 = clock(R1, 18)
        
        # Генерация выходного бита
        out_bit = R1[0] ^ R2[0] ^ R3[0] ^ (
            (R1[12] & R2[9]) | 
            (R1[12] & R3[13]) | 
            (R2[9] & R3[13])
        )
        G.append(out_bit)
        
        # Тактирование R4
        R4.append(R4[-1] ^ R4[-6] ^ 1)
        R4.popleft()

   
    return ''.join(str(text[i] ^ G[i]) for i in range(114))

def clock(register, length):
    """Тактирование регистра с обратной связью"""
    feedback = register[-1]
    if length == 18:  # Для R1
        feedback ^= register[13] ^ register[16] ^ register[17]
    elif length == 21:  # Для R2
        feedback ^= register[20]
    elif length == 22:  # Для R3
        feedback ^= register[7] ^ register[20] ^ register[21]
    register.append(feedback)
    register.popleft()
    return register

def A_5_2_encryption(text, key, flag_bin="Нет"):
   """Шифрует текст с использованием алгоритма A5/2."""
   
   first_length = len(text)  # Сохраняем исходную длину текста
   
   if not(text[0].isdigit()):  # Если текст не в бинарном формате
       processed_text = prepare_text_for_enc2(text)  # Подготавливаем текст для шифрования
       bin_text = ""  # Строка для бинарного представления
       
       # Конвертируем каждый символ в 5-битное представление
       for char in processed_text:
           idx = index_in_lower_2(char)  # Получаем индекс символа в алфавите
           if idx is False:  # Если символ не найден в алфавите
               return f"Ошибка: символ '{char}' отсутствует в алфавите"
           bin_text += f"{idx:05b}"  # Добавляем 5-битное представление символа
       first_length = len(processed_text) * 5  # Вычисляем длину в битах
       text = bin_text  # Заменяем текст на бинарное представление
   
   # Обработка ключа
   if not(key[0].isdigit()):  # Если ключ не в бинарном формате
       bin_key = ""  # Строка для бинарного ключа
       
       # Конвертируем каждый символ ключа в 5-битное представление
       for char in key:
           idx = index_in_lower_2(char)  # Получаем индекс символа
           if idx is False:  # Если символ не найден
               return f"Ошибка в ключе: символ '{char}' отсутствует в алфавите"
           bin_key += f"{idx:05b}"  # Добавляем 5-битное представление
       
       # Проверка длины ключа
       if len(bin_key) < 64:
           return "Ключ слишком короткий (требуется длина в64 бита)"
       
       key = bin_key[:64]  # Берем первые 64 бита
   
   elif len(key) != 64:  # Если ключ в бинарном формате, но не 64 бита
       return "Некорректная длина ключа (требуется длина в64 бита)"
   
   # Дополнение текста до длины, кратной 114 битам
   while (len(text) % 114 != 0): 
       text += '0'  # Добавляем нулевые биты
   
   s = ""  # Результирующая зашифрованная строка
   j = 0  # Счетчик фреймов
   
   # Обработка текста фреймами по 114 бит
   for i in range(0, len(text), 114):
       # Шифруем фрейм с помощью A5_2_one_frame
       s += A5_2_one_frame(key, ('0b{0:0>22b}'.format(j))[2:], text[i:(i+114)])
       j += 1  # Увеличиваем счетчик фреймов
   
   result = s[:first_length]  # Обрезаем до исходной длины
   
   # Возвращаем результат в бинарном или текстовом формате
   return result if flag_bin == "Да" else bits_to_text(result)

def A_5_2_decryption(text, key, flag_bin="Нет"):
    """Расшифровывает текст с использованием алгоритма A5/2."""
    
    first_length = len(text)  # Сохраняем исходную длину текста
    
    if not (text[0].isdigit()):  # Если текст не в бинарном формате
        # Преобразуем текст в бинарную строку
        bin_text = ""
        for char in text:
            idx = index_in_lower_2(char)  # Получаем индекс символа
            if idx is False:  # Если символ не найден
                return f"Ошибка: символ '{char}' отсутствует в алфавите"
            bin_text += f"{idx:05b}"  # Добавляем 5-битное представление
        first_length = len(bin_text)  # Обновляем длину в битах
        text = bin_text  # Заменяем текст на бинарное представление
    
    # Обработка ключа
    if not (key[0].isdigit()):  # Если ключ не в бинарном формате
        bin_key = ""
        for char in key:
            idx = index_in_lower_2(char)  # Получаем индекс символа
            if idx is False:  # Если символ не найден
                return f"Ошибка в ключе: символ '{char}' отсутствует в алфавите"
            bin_key += f"{idx:05b}"  # Добавляем 5-битное представление
        
        # Проверка длины ключа
        if len(bin_key) < 64:
            return "Ключ слишком короткий (требуется длина в 64 бита)"
        key = bin_key[:64]  # Берем первые 64 бита
    else:
        if len(key) != 64:  # Если ключ в бинарном формате, но не 64 бита
            return "Некорректная длина ключа (требуется длина в 64 бита)"
    
    # Дополнение текста до длины, кратной 114 битам
    while len(text) % 114 != 0:  
        text += '0'  # Добавляем нулевые биты
    
    s = ""  # Результирующая расшифрованная строка
    j = 0  # Счетчик фреймов
    
    # Обработка текста фреймами по 114 бит
    for i in range(0, len(text), 114):
        # Расшифровываем фрейм с помощью A5_2_one_frame
        s += A5_2_one_frame(key, f"{j:022b}", text[i:(i + 114)])
        j += 1  # Увеличиваем счетчик фреймов
    
    s = s[:first_length]  # Обрезаем до исходной длины
    
    if flag_bin == "Да":  # Если нужен бинарный вывод
        return s
    
    # Преобразуем бинарную строку обратно в текст
    s1 = ""
    for i in range(0, len(s), 5):  # Обрабатываем по 5 бит
        temp = s[i:(i + 5)]  # Берем 5 бит
        temp = int(temp, 2)  # Конвертируем в число
        s1 += alphabet_lower_2[temp]  # Получаем соответствующий символ
    
    return end_text_of_decr2(s1)  # Возвращаем расшифрованный текст после постобработки

# Блок ввода данных для программы (запускается только при прямом запуске A52.py)
if __name__ == "__main__":
    str_ = input("Введите текст: ")
    cipher = input("Введите алгоритм: ")
    switch = input("Введите режим шифра (зашифрование/расшифрование): ")

    with open("file.txt", "w", encoding="utf-8") as f_new:
         # Выбор функции в зависимости от введённых данных
         if cipher == "А5 /2" and switch == "з":
             key1=input("Введите ключ: ")
             print(A_5_2_encryption(str_, key1))
             
         elif cipher == "А5 /2" and switch == "р":
             key1=input("Введите ключ: ")
             print(A_5_2_decryption(str_, key1))
