import math

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
    # Только русские буквы (включая ё)
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
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
    b = a - 1
    factors = prime_factors(m)
    return (a % 2 == 1 and 
            math.gcd(c, m) == 1 and 
            all(b % p == 0 for p in factors) and 
            a < 100 and
            t0 < 100 and 
            c < 100 and 
            a > 1)

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
            t0 = int(input("T0: "))
            a = int(input("a: "))
            c = int(input("c: "))
            m = int(input("m: "))
            
            if check_conditions(a, c, m, t0):
                encrypted = shenon(text, t0, a, c, m)
                print("\nРезультат шифрования:")
                print(' '.join(encrypted))
            else:
                print("Ошибка: не выполнены условия для генератора!")
        
        elif choice == '2':
            text = input("Введите зашифрованный текст (без пробелов): ").replace(' ', '')
            t0 = int(input("T0: "))
            a = int(input("a: "))
            c = int(input("c: "))
            m = int(input("m: "))
            
            if check_conditions(a, c, m, t0):
                decrypted = shenon(text, t0, a, c, m, k=1)
                print("\nРезультат расшифровки:")
                print(''.join(decrypted))
            else:
                print("Ошибка: не выполнены условия для генератора!")
        
        elif choice == '3':
            print("Выход из программы...")
            break
        
        else:
            print("Неверный выбор! Попробуйте снова.")

if __name__ == "__main__":
    main()
