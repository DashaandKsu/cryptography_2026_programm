# -*- coding: utf8 -*-
import random

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

# ---------- Вспомогательные функции ----------
def textToNumbers(text):
    """Преобразование строки в список чисел (индекс в алфавите + 1)"""
    res = []
    for ch in text:
        idx = alf.find(ch)
        if idx != -1:
            res.append(idx + 1)
    return res

def tchk_zpt(s):
    """Замена знаков препинания на буквенные сочетания и приведение к нижнему регистру"""
    s = s.replace('.', 'тчк')
    s = s.replace(',', 'зпт')
    return s.lower()

def hesh(text, module):
    """Квадратичная свёртка (хеш-функция)"""
    nums = textToNumbers(text)
    h = 0
    for m in nums:
        h = ((h + m) ** 2) % module
    return h

def mod_pow(base, exp, mod):
    """Быстрое возведение в степень по модулю"""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result

def is_prime(n, k=10):
    """Тест Миллера-Рабина на простоту"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Представим n-1 как d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def gcd(a, b):
    """Наибольший общий делитель"""
    while b:
        a, b = b, a % b
    return a

# ---------- Генерация параметров ----------
def generate_prime(bits):
    """Генерация простого числа заданной битовой длины"""
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_keys(bits_p=16, bits_q=12):
    """Автоматическая генерация параметров p, q, a, x, k, y"""
    while True:
        p = generate_prime(bits_p)
        q = generate_prime(bits_q)
        if (p - 1) % q == 0:
            break

    # Поиск a: 1 < a < p-1, a^q mod p == 1
    a = 2
    while mod_pow(a, q, p) != 1:
        a += 1
        if a >= p:
            # Начинаем заново с новым p,q (на практике маловероятно)
            return generate_keys(bits_p, bits_q)

    x = random.randint(2, q - 1)
    k = random.randint(2, q - 1)
    y = mod_pow(a, x, p)

    return p, q, a, x, k, y

# ---------- Проверка параметров ----------
def check_params(p, q, a, x=0, k=0):
    """Полная проверка корректности параметров (возвращает True и сообщение или False и ошибку)"""
    if not is_prime(p):
        return False, f'p = {p} не является простым числом'
    if not is_prime(q):
        return False, f'q = {q} не является простым числом'
    if (p - 1) % q != 0:
        return False, f'q = {q} не является делителем p-1 = {p-1}'
    if not (1 < a < p - 1):
        return False, f'a должно быть в диапазоне 1 < a < {p-1}'
    if mod_pow(a, q, p) != 1:
        return False, f'Условие a^q mod p = 1 не выполняется: {a}^{q} mod {p} = {mod_pow(a, q, p)}'
    if x != 0 and not (1 < x < q):
        return False, f'x должен быть в диапазоне 1 < x < {q}'
    if k != 0 and not (1 < k < q):
        return False, f'k должен быть в диапазоне 1 < k < {q}'
    return True, 'Параметры корректны'

# ---------- Генерация подписи ----------
def generate_signature(text, p, q, a, x, k):
    """
    Возвращает кортеж: (r, s, y, steps) или сообщение об ошибке.
    steps - список строк с описанием шагов (как в C++ версии).
    """
    steps = []
    steps.append('=== Генерация подписи ===')
    steps.append(f'Параметры: p={p}, q={q}, a={a}, x={x}, k={k}')

    # 1. Вычисление хеша
    hm = text % q
    if hm == 0:
        hm = 1
        steps.append(f'H(m) mod q = 0 → устанавливаем H(m)=1')
    steps.append(f'H(m) mod q = {hm}')

    # 2. r = (a^k mod p) mod q
    ak_mod_p = mod_pow(a, k, p)
    r = ak_mod_p % q
    steps.append(f'r = (a^k mod p) mod q = ({a}^{k} mod {p}) mod {q} = {ak_mod_p} mod {q} = {r}')
    if r == 0:
        steps.append('ОШИБКА: r = 0. Необходимо выбрать другое k.')
        return None, None, None, steps

    # 3. s = (x*r + k*H(m)) mod q
    xr = (x * r) % q
    khm = (k * hm) % q
    s = (xr + khm) % q
    steps.append(f's = (x*r + k*H(m)) mod q = ({x}*{r} + {k}*{hm}) mod {q} = ({xr} + {khm}) mod {q} = {s}')
    if s == 0:
        steps.append('ОШИБКА: s = 0. Необходимо выбрать другое k.')
        return None, None, None, steps

    # Открытый ключ
    y = mod_pow(a, x, p)
    steps.append(f'Открытый ключ y = a^x mod p = {a}^{x} mod {p} = {y}')

    steps.append(f'Подпись: r = {r}, s = {s}')
    return r, s, y, steps

# ---------- Проверка подписи ----------
def check_signature(text, r, s, p, q, a, y):
    """
    Возвращает строку с результатом проверки и список шагов.
    """
    steps = []
    steps.append('=== Проверка подписи ===')
    steps.append(f'Параметры: p={p}, q={q}, a={a}, y={y}')
    steps.append(f'Полученная подпись: r={r}, s={s}')

    # Шаг 1: проверка диапазонов
    if not (0 < r < q):
        steps.append(f'ОШИБКА: r = {r} не удовлетворяет 0 < r < q = {q}')
        return False, f'Подпись неверна: r вне диапазона', steps
    if not (0 < s < q):
        steps.append(f'ОШИБКА: s = {s} не удовлетворяет 0 < s < q = {q}')
        return False, f'Подпись неверна: s вне диапазона', steps
    steps.append('Проверка диапазонов r и s пройдена')

    # Шаг 2: вычисление хеша
    hm = text % q
    if hm == 0:
        hm = 1
        steps.append('H(m) mod q = 0 → H(m)=1')
    steps.append(f'H(m) mod q = {hm}')

    # Шаг 3: v = H(m)^(q-2) mod q
    v = mod_pow(hm, q - 2, q)
    steps.append(f'v = H(m)^(q-2) mod q = {hm}^{q-2} mod {q} = {v}')

    # Шаг 4: z1 = s * v mod q
    z1 = (s * v) % q
    steps.append(f'z1 = s * v mod q = {s} * {v} mod {q} = {z1}')

    # Шаг 5: z2 = (q - r) * v mod q
    z2 = ((q - r) * v) % q
    steps.append(f'z2 = (q - r) * v mod q = ({q} - {r}) * {v} mod {q} = {z2}')

    # Шаг 6: u = (a^z1 * y^z2 mod p) mod q
    a_z1 = mod_pow(a, z1, p)
    y_z2 = mod_pow(y, z2, p)
    product = (a_z1 * y_z2) % p
    u = product % q
    steps.append(f'a^z1 mod p = {a}^{z1} mod {p} = {a_z1}')
    steps.append(f'y^z2 mod p = {y}^{z2} mod {p} = {y_z2}')
    steps.append(f'(a^z1 * y^z2) mod p = {a_z1} * {y_z2} mod {p} = {product}')
    steps.append(f'u = (a^z1 * y^z2 mod p) mod q = {product} mod {q} = {u}')

    # Шаг 7: сравнение
    if u == r:
        steps.append(f'u = {u} равно r = {r} → подпись верна')
        return True, f'Подпись верна (u = r = {u})', steps
    else:
        steps.append(f'u = {u} не равно r = {r} → подпись неверна')
        return False, f'Подпись неверна (u = {u}, r = {r})', steps

# ---------- Основная программа ----------
def main():
    print("ЭЦП ГОСТ Р 34.10-94 (улучшенная версия)")
    print("Выберите действие:")
    print("1 - Подписать сообщение")
    print("2 - Проверить подпись")
    print("3 - Сгенерировать ключи и подписать сообщение")
    what = input("Ваш выбор (1/2/3): ").strip()

    if what == '1' or what == '3':
        text = input("Введите открытый текст: ")
        text = tchk_zpt(text)

        # Ввод параметров (вручную или авто)
        if what == '1':
            # Ручной ввод
            while True:
                try:
                    p = int(input("Введите простое p: "))
                    q = int(input(f"Введите простое q (делитель {p-1}): "))
                    a = int(input(f"Введите a (1 < a < {p-1}, a^{q} mod {p} = 1): "))
                    x = int(input(f"Введите секретный ключ x (1 < x < {q}): "))
                    k = int(input(f"Введите случайное k (1 < k < {q}): "))
                except ValueError:
                    print("Ошибка ввода числа. Попробуйте снова.")
                    continue

                ok, msg = check_params(p, q, a, x, k)
                if not ok:
                    print(f"Ошибка: {msg}")
                    continue
                # Дополнительная проверка r != 0 (будет внутри generate_signature)
                break
        else:
            # Автоматическая генерация
            print("Генерация параметров (16-битное p, 12-битное q)...")
            p, q, a, x, k, y_gen = generate_keys(16, 12)
            print(f"Сгенерированы параметры:")
            print(f"  p = {p}")
            print(f"  q = {q}")
            print(f"  a = {a}")
            print(f"  x = {x} (секретный)")
            print(f"  k = {k} (случайное)")
            print(f"  y = {y_gen} (открытый ключ)")

        # Ввод модуля хеширования
        n = int(input("Введите модуль для хеширования n (рекомендуется > 32): "))
        hash_val = hesh(text, n)
        print(f"Хеш-образ сообщения: {hash_val}")

        # Генерация подписи
        r, s, y_calc, steps = generate_signature(hash_val, p, q, a, x, k)
        for step in steps:
            print(step)

        if r is None:
            print("Не удалось создать подпись. Попробуйте другое k.")
            return

        print(f"\n=== Результат ===")
        print(f"Подпись: r = {r}, s = {s}")
        print(f"Открытый ключ Y = {y_calc}")
        print("Для проверки подписи используйте эти значения и исходное сообщение.")

    elif what == '2':
        text = input("Введите сообщение (оригинал): ")
        text = tchk_zpt(text)

        while True:
            try:
                p = int(input("Введите p: "))
                q = int(input(f"Введите q (делитель {p-1}): "))
                a = int(input("Введите a: "))
                y = int(input("Введите открытый ключ Y: "))
            except ValueError:
                print("Ошибка ввода числа. Попробуйте снова.")
                continue

            ok, msg = check_params(p, q, a)
            if not ok:
                print(f"Ошибка: {msg}")
                continue
            break

        n = int(input("Введите модуль для хеширования n: "))
        hash_val = hesh(text, n)
        print(f"Хеш-образ сообщения: {hash_val}")

        r = int(input("Введите r (первый параметр подписи): "))
        s = int(input("Введите s (второй параметр подписи): "))

        valid, message, steps = check_signature(hash_val, r, s, p, q, a, y)
        for step in steps:
            print(step)
        print(f"\n=== Результат проверки ===\n{message}")

    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()