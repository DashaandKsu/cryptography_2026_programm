import math

alha = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

SPECIALS = {
    ',': 'зпт', '.': 'тчк', ' ': 'прбл', ':': 'двтч', ';': 'тчзпт',
    '-': 'тире', '—': 'длтре', '«': 'каво', '»': 'кавд',
    # ё/Ё не в алфавите — только нормализация в «е» в prepare_text (иначе REV['е']→«ё» портит весь текст)
    '?': 'впрс', '!': 'вскл', '(': 'скб1', ')': 'скб2',
    '"': 'кавчк', "'": 'апстр', '\n': 'нстр', '\r': 'возвр',
    '0': 'циф0', '1': 'циф1', '2': 'циф2', '3': 'циф3', '4': 'циф4',
    '5': 'циф5', '6': 'циф6', '7': 'циф7', '8': 'циф8', '9': 'циф9',
}

SPECIALS_REV = {v: k for k, v in SPECIALS.items()}

def prepare_text(text):
    text = text.replace("ё", "е").replace("Ё", "е")
    for k, v in SPECIALS.items():
        text = text.replace(k, v)
    return text.lower()

def restore_text(text):
    for v, k in SPECIALS_REV.items():
        text = text.replace(v, k)
    return text

def is_prime(n):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def encrypt(text, n, e):
    text = prepare_text(text)
    message = ''
    block_len = len(str(n))
    for i in text:
        if i not in alha:
            raise ValueError(f"Символ '{i}' не найден в алфавите")
        index1 = alha.index(i) + 1
        num = pow(index1, e, n)
        message += str(num).zfill(block_len)
    return message

def phi(p, q):
    return (p - 1) * (q - 1)

def modinv(e, phi):
    g, x, y = extended_gcd(e, phi)
    if g != 1:
        raise Exception('Обратный элемент не существует')
    else:
        return x % phi

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_gcd(b % a, a)
        return (g, x - (b // a) * y, y)

def des(text, n, d):
    message = ''
    block_len = len(str(n))
    for i in range(0, len(text), block_len):
        c = int(text[i:i+block_len])
        m = pow(c, d, n)
        if m < 1 or m > len(alha):
            raise ValueError(f"Некорректное значение при дешифровке: {m}")
        message += alha[m-1]
    return restore_text(message)

def get_prime_input(prompt, min_n=0):
    while True:
        try:
            num = int(input(prompt))
            if not is_prime(num):
                print("Число должно быть простым!")
                continue
            if min_n > 0 and num < min_n:
                print(f"Число должно быть не меньше {min_n}")
                continue
            return num
        except ValueError:
            print("Пожалуйста, введите целое число.")

def get_e_input(phi_n):
    while True:
        try:
            e = int(input(f"Введите e (1 < e < {phi_n}, взаимно простое с {phi_n}): "))
            if e <= 1 or e >= phi_n:
                print(f"e должно быть в диапазоне 1 < e < {phi_n}")
                continue
            if math.gcd(e, phi_n) != 1:
                print(f"e должно быть взаимно простым с {phi_n}")
                continue
            return e
        except ValueError:
            print("Пожалуйста, введите целое число.")

def encryption_mode():
    print("\n=== РЕЖИМ ШИФРОВАНИЯ ===")
    while True:
        p = get_prime_input("Введите первое простое число p (минимум 3): ", 3)
        q = get_prime_input("Введите второе простое число q (минимум 3): ", 3)
        if p == q:
            print("p и q должны быть разными!")
            continue
        n = p * q
        if n < 33:
            print(f"n = {n} должен быть ≥33!")
            continue
        break
    phi_n = phi(p, q)
    print(f"\nφ(n) = {phi_n}")
    e = get_e_input(phi_n)
    try:
        d = modinv(e, phi_n)
    except Exception as ex:
        print(f"Ошибка вычисления d: {ex}")
        return
    if e == d:
        print("\nОШИБКА: Открытый (e) и секретный (d) ключи совпадают!")
        print("Это делает систему уязвимой. Пожалуйста, выберите другие параметры.")
        return
    print("\n=== КЛЮЧИ ===")
    print(f"Открытый ключ (n, e): ({n}, {e})")
    print(f"Секретный ключ (n, d): ({n}, {d})")
    text = input("\nВведите текст для шифрования: ")
    try:
        encrypted = encrypt(text, n, e)
        print("\nРезультат шифрования:")
        print(encrypted)
    except Exception as ex:
        print(f"Ошибка шифрования: {ex}")

def decryption_mode():
    print("\n=== РЕЖИМ РАСШИФРОВАНИЯ ===")
    print("\nВыберите способ ввода:")
    print("1. Через секретный ключ (n, d)")
    print("2. Через параметры p, q и e")
    choice = input("Ваш выбор (1-2): ").strip()
    if choice == '1':
        try:
            n = int(input("Введите модуль n: "))
            d = int(input("Введите секретный ключ d: "))
        except ValueError:
            print("Ошибка ввода чисел!")
            return
    elif choice == '2':
        p = get_prime_input("Введите простое число p: ")
        q = get_prime_input("Введите простое число q: ")
        e = int(input("Введите экспоненту e: "))
        n = p * q
        phi_n = phi(p, q)
        try:
            d = modinv(e, phi_n)
        except Exception as ex:
            print(f"Ошибка вычисления d: {ex}")
            return
    else:
        print("Неверный выбор!")
        return
    print("\n=== ИСПОЛЬЗУЕМЫЕ КЛЮЧИ ===")
    print(f"Модуль n: {n}")
    print(f"Секретный ключ d: {d}")
    ciphertext = input("\nВведите зашифрованный текст: ").strip()
    try:
        decrypted = des(ciphertext, n, d)
        print("\nРезультат расшифрования:")
        print(decrypted)
    except Exception as ex:
        print(f"Ошибка расшифрования: {ex}")

def main():
    while True:
        print("\n" + "="*40)
        print("1. Шифрование текста")
        print("2. Расшифрование текста")
        print("3. Выход")
        choice = input("Выберите действие (1-3): ").strip()
        if choice == '1':
            encryption_mode()
        elif choice == '2':
            decryption_mode()
        elif choice == '3':
            print("Завершение работы...")
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()



#1. Шифрование текста
#2. Расшифрование текста
#3. Выход
#Выберите действие (1-3): 1

#Введите первое простое число p (минимум 3): 3
#Введите второе простое число q (минимум 3): 11

#φ(n) = 20

#=== КЛЮЧИ ===
#Открытый ключ (n, e): (33, 3)
#Секретный ключ (n, d): (33, 7)

#Введите текст для шифрования: лучшеголубьвтарелкезптчемглухарьнатокутчк

#Результат шифрования:
#1214301618310912140802272801291812111817042830181931121422012902050128091114283011
