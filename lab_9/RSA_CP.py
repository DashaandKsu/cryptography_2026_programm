"""
Цифровая подпись RSA (учебная реализация).

Идея защиты:
- Генерация: N = P·Q, φ(N) = (P−1)(Q−1), выбирают E взаимно простое с φ(N),
  секретный D: E·D ≡ 1 (mod φ(N)) — подпись тем, кто знает D.
- Сообщение сжимают хешем H(M) (здесь — квадратичная итерация по mod p).
- Подпись: S = H(M)^D mod N. Проверка: S^E mod N должно совпасть с H(M).

Что знать преподавателю: роль открытого (N,E) и секретного D; почему нужно
gcd(E, φ)=1; почему подписывают хеш, а не длинный текст; ограничения учебного хеша (малый mod p).
"""
# Кодирование букв: 32 строчные буквы (а…я) с й между и и к — как в типовых примерах RSA в методичке.
# Буква ё не входит в таблицу; заменяем на е.
alphabet = {
    'а': 1, 'б': 2, 'в': 3, 'г': 4, 'д': 5, 'е': 6, 'ж': 7, 'з': 8, 'и': 9, 'й': 10,
    'к': 11, 'л': 12, 'м': 13, 'н': 14, 'о': 15, 'п': 16, 'р': 17, 'с': 18,
    'т': 19, 'у': 20, 'ф': 21, 'х': 22, 'ц': 23, 'ч': 24, 'ш': 25,
    'щ': 26, 'ъ': 27, 'ы': 28, 'ь': 29, 'э': 30, 'ю': 31, 'я': 32,
}

ALPHABET_SIZE = len(alphabet)  # 32

def preprocess_message(message):
    # Убираем пробелы и кодируем точку буквами; й не склеиваем с и (иначе меняется хеш, как в примерах к заданию).
    message = message.replace(" ", "")
    message = message.replace(".", "тчк")
    message = message.lower()
    message = message.replace("ё", "е")
    return message

def quadratic_hash(message, p):
    # Упрощённая хеш-функция квадратичной свёртки: h_i = (h_{i-1} + M_i)^2 mod p, h_0 = 0.
    # Выход в Z_p; модуль p (47) 
    h = 0
    for char in message:
        if char not in alphabet:
            raise ValueError(f"Символ '{char}' отсутствует в алфавите.")
        m_i = alphabet[char]
        h = ((h + m_i) ** 2) % p
    return h

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    # Расширенный алгоритм Евклида: a^{-1} (mod m), нужен для D = E^{-1} mod φ(N).
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_int_input(prompt, min_value=2, prime_required=False, not_equal=None):
    while True:
        try:
            value = int(input(prompt))
            if value < min_value:
                print(f"Число должно быть не меньше {min_value}.")
                continue
            if prime_required and not is_prime(value):
                print("Число должно быть простым.")
                continue
            if not_equal is not None and value == not_equal:
                print(f"Число не должно быть равно {not_equal}.")
                continue
            return value
        except ValueError:
            print("Введите целое число.")

def generate_keys(p, q, e_input):
    # φ(N) = (p−1)(q−1); D = E^{-1} mod φ(N).
    n = p * q
    phi = (p - 1) * (q - 1)
    if gcd(e_input, phi) != 1:
        raise ValueError("E не является взаимно простым с φ(N).")
    d = mod_inverse(e_input, phi)
    return n, e_input, d

def sign(message, d, n):
    # Подпись RSA: S = M^D mod N; здесь M = hash_value.
    return pow(message, d, n)

def verify(signature, e, n):
    # Восстановление «подписанного» хеша: M' = S^E mod N, сравнивают с H(M).
    return pow(signature, e, n)

def menu():
    print("\n--- МЕНЮ ---")
    print("1. Создать цифровую подпись (RSA)")
    print("2. Проверить цифровую подпись (RSA)")
    print("0. Выйти")

def create_signature():
    # Требование N > |алфавит|: иначе при других схемах кодирования блоки текста
    # могли бы совпадать по mod N; для текущей схемы (хеш mod 47) критичен именно хеш < N.
    while True:
        P = get_int_input('Введите P (простое число > 1): ', min_value=2, prime_required=True)
        Q = get_int_input('Введите Q (простое число > 1 и не равно P): ', min_value=2, prime_required=True, not_equal=P)
        N = P * Q
        if N <= ALPHABET_SIZE:
            print(f"Модуль N = P * Q = {N} должен быть больше мощности алфавита ({ALPHABET_SIZE}).")
            continue
        break

    phi = (P - 1) * (Q - 1)

    # Ввод сообщения
    raw_message = input("Введите текст для подписи: ")
    processed_message = preprocess_message(raw_message)

    hash_p = 47  # тот же модуль, что и в check_signature()
    try:
        hash_value = quadratic_hash(processed_message, hash_p)
    except ValueError as err:
        print(err)
        return

    print(f"Хэш-образ: {hash_value}")

    # Ввод E
    while True:
        try:
            E = int(input(f"Введите E (целое число > 1 и < {N}, взаимно простое с φ(N)={phi}): "))
            if E <= 1 or E >= N:
                print(f"E должно быть больше 1 и меньше {N}.")
                continue
            if gcd(E, phi) != 1:
                print(f"E должно быть взаимно простым с φ(N)={phi}.")
                continue
            break
        except ValueError:
            print("Введите целое число.")

    try:
        N, E, D = generate_keys(P, Q, E)
    except ValueError as err:
        print(err)
        return

    print(f"Открытые ключи: N = {N}, E = {E}")
    print(f"Секретный ключ D = {D}")

    signature = sign(hash_value, D, N)
    print(f"Подпись: {signature}")

    print("\n--- Для проверки подписи используйте следующие значения ---")
    print(f"Текст: {raw_message}")
    print(f"Хэш-образ: {hash_value}")
    print(f"Подпись: {signature}")
    print(f"Открытые ключи: N = {N}, E = {E}")

def check_signature():
    raw_message = input("Введите исходный текст: ")
    processed_message = preprocess_message(raw_message)

    hash_p = 47  # тот же модуль, что и при создании подписи
    try:
        hash_value = quadratic_hash(processed_message, hash_p)
    except ValueError as err:
        print(err)
        return

    signature = get_int_input("Введите подпись (целое число > 1): ", min_value=2)
    E = get_int_input("Введите открытый ключ E (целое число > 1): ", min_value=2)
    N = get_int_input("Введите открытый ключ N (целое число > 1): ", min_value=2)

    decrypted_hash = verify(signature, E, N)  # S^E mod N
    print(f"Вычисленный хэш из подписи: {decrypted_hash}")
    print(f"Ожидаемый хэш: {hash_value}")
    if decrypted_hash == hash_value:
        print("Подпись верна")
    else:
        print("Подпись неверна")

def main():
    while True:
        menu()
        choice = input("Выберите действие: ")
        if choice == "1":
            create_signature()
        elif choice == "2":
            check_signature()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()


    """--- МЕНЮ ---
1. Создать цифровую подпись (RSA)
2. Проверить цифровую подпись (RSA)
0. Выйти
Выберите действие: 1
Введите P (простое число > 1): 37
Введите Q (простое число > 1 и не равно P): 11
Введите текст для подписи: лето
Хэш-образ: 16
Введите E (целое число > 1 и < 407, взаимно простое с φ(N)=360): 7
Открытые ключи: N = 407, E = 7
Секретный ключ D = 103
Подпись: 268

--- Для проверки подписи используйте следующие значения ---
Текст: лето
Хэш-образ: 16
Подпись: 268
Открытые ключи: N = 407, E = 7

--- МЕНЮ ---
1. Создать цифровую подпись (RSA)
2. Проверить цифровую подпись (RSA)
0. Выйти
Выберите действие: 2
Введите исходный текст: лето
Введите подпись (целое число > 1): 268
Введите открытый ключ E (целое число > 1): 7
Введите открытый ключ N (целое число > 1): 407
Вычисленный хэш из подписи: 16
Ожидаемый хэш: 16
Подпись верна"""



    """--- МЕНЮ ---
1. Создать цифровую подпись (RSA)
2. Проверить цифровую подпись (RSA)
0. Выйти
Выберите действие: 1
Введите P (простое число > 1): 37
Введите Q (простое число > 1 и не равно P): 11
Введите текст для подписи: лето
Хэш-образ: 16
Введите E (целое число > 1 и < 407, взаимно простое с φ(N)=360): 7
Открытые ключи: N = 407, E = 7
Секретный ключ D = 103
Подпись: 268

--- Для проверки подписи используйте следующие значения ---
Текст: лето
Хэш-образ: 16
Подпись: 268
Открытые ключи: N = 407, E = 7

--- МЕНЮ ---
1. Создать цифровую подпись (RSA)
2. Проверить цифровую подпись (RSA)
0. Выйти
Выберите действие: 2
Введите исходный текст: лето
Введите подпись (целое число > 1): 268
Введите открытый ключ E (целое число > 1): 7
Введите открытый ключ N (целое число > 1): 407
Вычисленный хэш из подписи: 16
Ожидаемый хэш: 16
Подпись верна"""

