import math

# Алфавит для символьной гаммы (32 символа, без "ё")
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
MODULUS = len(ALPHABET)  # m определяется размером алфавита

def preprocess_text(text):
    # Заменяем спецсимволы на маркеры
    replacements = {
        ' ': 'прб',
        '.': 'тчк',
        ',': 'зпт',
        '!': 'вск',
        '?': 'впр',
        '-': 'дфс',
        '—': 'тре',
        ':': 'дво',
        ';': 'тчзпт',
        '(': 'скобо',
        ')': 'скобз',
        '«': 'елл',
        '»': 'елп',
        '"': 'ковыч'
    }
    text = text.lower()
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def postprocess_text(text):
    # Восстанавливаем спецсимволы из маркеров
    replacements = {
        'прб': ' ',
        'тчк': '.',
        'зпт': ',',
        'вск': '!',
        'впр': '?',
        'дфс': '-',
        'тре': '—',
        'дво': ':',
        'тчзпт': ';',
        'скобо': '(',
        'скобз': ')',
        'елл': '«',
        'елп': '»',
        'ковыч': '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def shenon(crypto_text, t_0, a, c, m, k=0):
    # Только русские буквы из заданного алфавита (без "ё")
    alphabet = ALPHABET
    digits = len(str(len(alphabet)))  # Кол-во цифр для кодировки одной буквы

    if k == 0:  # Шифрование
        crypto_text_d = preprocess_text(crypto_text)
        # Оставляем только буквы алфавита
        crypto_text_d = ''.join([ch for ch in crypto_text_d if ch in alphabet])
    else:  # Расшифровка
        crypto_text_d = crypto_text

    crypto_text_encrypt = ''
    table_d = [t_0]

    for _ in range(len(crypto_text_d)):
        # Генерация гаммы по модулю m (задан пользователем)
        table_d.append((a * table_d[-1] + c) % m)

    if k == 0:  # Шифрование
        for i in range(len(crypto_text_d)):
            num = (alphabet.index(crypto_text_d[i]) + 1 + table_d[i]) % len(alphabet)
            num = len(alphabet) if num == 0 else num
            crypto_text_encrypt += str(num).zfill(digits)
        group_size = 5 * digits
        return [crypto_text_encrypt[i:i+group_size] for i in range(0, len(crypto_text_encrypt), group_size)]
    elif k == 1:  # Расшифровка
        if len(crypto_text_d) % digits != 0:
            return ["Ошибка: некорректная длина шифртекста"]
        decrypted = []
        for i in range(0, len(crypto_text_d), digits):
            num = (int(crypto_text_d[i:i+digits]) - table_d[i//digits] - 1) % len(alphabet)
            decrypted.append(alphabet[num])
        decrypted_text = ''.join(decrypted)
        # Восстанавливаем спецсимволы
        return [postprocess_text(decrypted_text)]

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def check_conditions(a, c, m, t0):
    errors = []

    # Модуль не должен быть меньше размера алфавита
    if m < MODULUS:
        errors.append(f"m ({m}) меньше размера алфавита ({MODULUS})")

    b = a - 1
    factors = prime_factors(m)

    # Условия максимального периода для символьной гаммы:
    # a – нечетное число
    if a % 2 == 0:
        errors.append(f"a ({a}) должно быть нечётным")

    # c – взаимно просто с модулем m
    if math.gcd(c, m) != 1:
        errors.append(f"c ({c}) должно быть взаимно просто с m ({m})")

    # b = a – 1 кратно p для каждого простого p, делителя m
    if not all(b % p == 0 for p in factors):
        errors.append(f"a - 1 ({b}) должно быть кратно каждому простому делителю модуля m")

    # b кратно 4, если m кратно 4
    if m % 4 == 0 and b % 4 != 0:
        errors.append(f"a - 1 ({b}) должно быть кратно 4, так как m ({m}) кратно 4")

    # Дополнительные разумные ограничения
    if a <= 1:
        errors.append(f"a ({a}) должно быть больше 1")
    if not (0 <= t0 < m):
        errors.append(f"T0 ({t0}) должно быть в диапазоне [0, m)")
    if not (0 <= c < m):
        errors.append(f"c ({c}) должно быть в диапазоне [0, m)")

    return len(errors) == 0, errors

def main():
    while True:
        print("\n" + "="*20)
        print("Меню шифра Шеннона")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        
        choice = input("Выберите действие (1-3): ")
        
        if choice == '1':
            text = input("Введите текст: ")
            print(f"\nИспользуемый алфавит ({MODULUS} символов): {ALPHABET}")
            m = int(input("Введите модуль m (>= размер алфавита): "))
            t0 = int(input("T0: "))
            a = int(input("a: "))
            c = int(input("c: "))
            
            ok, errors = check_conditions(a, c, m, t0)
            if ok:
                encrypted = shenon(text, t0, a, c, m)
                print("\nРезультат шифрования:")
                print(' '.join(encrypted))
            else:
                print("Ошибка: не выполнены условия для генератора!")
                for err in errors:
                    print(" -", err)
        
        elif choice == '2':
            text = input("Введите зашифрованный текст (без пробелов): ").replace(' ', '')
            print(f"\nИспользуемый алфавит ({MODULUS} символов): {ALPHABET}")
            m = int(input("Введите модуль m (>= размер алфавита): "))
            t0 = int(input("T0: "))
            a = int(input("a: "))
            c = int(input("c: "))
            
            ok, errors = check_conditions(a, c, m, t0)
            if ok:
                decrypted = shenon(text, t0, a, c, m, k=1)
                print("\nРезультат расшифровки:")
                print(''.join(decrypted))
            else:
                print("Ошибка: не выполнены условия для генератора!")
                for err in errors:
                    print(" -", err)
        
        elif choice == '3':
            print("Выход из программы...")
            break
        
        else:
            print("Неверный выбор! Попробуйте снова.")

if __name__ == "__main__":
    main()

#чтобы модуль определялся алфавитом и не меньше чем алфавит, первым должен выделяться модуль, должна быть проверка на соответствие ключей, так как например 3 3 3 по ключам быть не может