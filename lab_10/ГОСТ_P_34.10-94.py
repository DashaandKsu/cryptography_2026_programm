# -*- coding: utf8 -*-
import random

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPHABET_SIZE = len(alf)  # 32

# ---------- Вспомогательные функции ----------
def textToNumbers(text):
    res = []
    for ch in text:
        idx = alf.find(ch)
        if idx != -1:
            res.append(idx + 1)
    return res

def tchk_zpt(s):
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
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
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

# ---------- Генерация параметров ----------
def generate_prime(bits):
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_keys(bits_p=16, bits_q=12):
    while True:
        p = generate_prime(bits_p)
        q = generate_prime(bits_q)
        if (p - 1) % q == 0:
            break
    a = 2
    while mod_pow(a, q, p) != 1:
        a += 1
        if a >= p:
            return generate_keys(bits_p, bits_q)
    x = random.randint(2, q - 1)
    y = mod_pow(a, x, p)
    # k сгенерируем позже отдельно
    return p, q, a, x, y

def generate_k(q, p, a, x, hash_val):
    """Генерирует k, гарантируя r≠0 и s≠0"""
    while True:
        k = random.randint(2, q - 1)
        r = (mod_pow(a, k, p)) % q
        if r == 0:
            continue
        hm = hash_val % q
        if hm == 0:
            hm = 1
        s = (x * r + k * hm) % q
        if s == 0:
            continue
        return k

# ---------- Проверка параметров ----------
def check_params(p, q, a, x=0, k=0):
    if p <= ALPHABET_SIZE:
        return False, f'p = {p} слишком мало, должно быть > {ALPHABET_SIZE} (размер алфавита)'
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
    steps = []
    steps.append('=== Генерация подписи ===')
    steps.append(f'Параметры: p={p}, q={q}, a={a}, x={x}, k={k}')

    hm = text % q
    if hm == 0:
        hm = 1
        steps.append(f'H(m) mod q = 0 → устанавливаем H(m)=1')
    steps.append(f'H(m) mod q = {hm}')

    ak_mod_p = mod_pow(a, k, p)
    r = ak_mod_p % q
    steps.append(f'r = (a^k mod p) mod q = ({a}^{k} mod {p}) mod {q} = {ak_mod_p} mod {q} = {r}')
    if r == 0:
        steps.append('ОШИБКА: r = 0. Необходимо выбрать другое k.')
        return None, None, None, steps

    xr = (x * r) % q
    khm = (k * hm) % q
    s = (xr + khm) % q
    steps.append(f's = (x*r + k*H(m)) mod q = ({x}*{r} + {k}*{hm}) mod {q} = ({xr} + {khm}) mod {q} = {s}')
    if s == 0:
        steps.append('ОШИБКА: s = 0. Необходимо выбрать другое k.')
        return None, None, None, steps

    y = mod_pow(a, x, p)
    steps.append(f'Открытый ключ y = a^x mod p = {a}^{x} mod {p} = {y}')
    steps.append(f'Подпись: r = {r}, s = {s}')
    return r, s, y, steps

# ---------- Проверка подписи ----------
def check_signature(text, r, s, p, q, a, y):
    steps = []
    steps.append('=== Проверка подписи ===')
    steps.append(f'Параметры: p={p}, q={q}, a={a}, y={y}')
    steps.append(f'Полученная подпись: r={r}, s={s}')

    if not (0 < r < q):
        steps.append(f'ОШИБКА: r = {r} не удовлетворяет 0 < r < q = {q}')
        return False, f'Подпись неверна: r вне диапазона', steps
    if not (0 < s < q):
        steps.append(f'ОШИБКА: s = {s} не удовлетворяет 0 < s < q = {q}')
        return False, f'Подпись неверна: s вне диапазона', steps
    steps.append('Проверка диапазонов r и s пройдена')

    hm = text % q
    if hm == 0:
        hm = 1
        steps.append('H(m) mod q = 0 → H(m)=1')
    steps.append(f'H(m) mod q = {hm}')

    v = mod_pow(hm, q - 2, q)
    steps.append(f'v = H(m)^(q-2) mod q = {hm}^{q-2} mod {q} = {v}')

    z1 = (s * v) % q
    steps.append(f'z1 = s * v mod q = {s} * {v} mod {q} = {z1}')

    z2 = ((q - r) * v) % q
    steps.append(f'z2 = (q - r) * v mod q = ({q} - {r}) * {v} mod {q} = {z2}')

    a_z1 = mod_pow(a, z1, p)
    y_z2 = mod_pow(y, z2, p)
    product = (a_z1 * y_z2) % p
    u = product % q
    steps.append(f'a^z1 mod p = {a}^{z1} mod {p} = {a_z1}')
    steps.append(f'y^z2 mod p = {y}^{z2} mod {p} = {y_z2}')
    steps.append(f'(a^z1 * y^z2) mod p = {a_z1} * {y_z2} mod {p} = {product}')
    steps.append(f'u = (a^z1 * y^z2 mod p) mod q = {product} mod {q} = {u}')

    if u == r:
        steps.append(f'u = {u} равно r = {r} → подпись верна')
        return True, f'Подпись верна (u = r = {u})', steps
    else:
        steps.append(f'u = {u} не равно r = {r} → подпись неверна')
        return False, f'Подпись неверна (u = {u}, r = {r})', steps

# ---------- Основная программа ----------
def main():
    print("ЭЦП ГОСТ Р 34.10-94 (исправленная версия)")
    print("Выберите действие:")
    print("1 - Подписать сообщение")
    print("2 - Проверить подпись")
    print("3 - Сгенерировать ключи и подписать сообщение")
    what = input("Ваш выбор (1/2/3): ").strip()

    if what == '1' or what == '3':
        text = input("Введите открытый текст: ")
        text = tchk_zpt(text)

        if what == '1':
            while True:
                try:
                    p = int(input(f"Введите простое p (> {ALPHABET_SIZE}): "))
                    if p <= ALPHABET_SIZE:
                        print(f"Ошибка: p должно быть больше {ALPHABET_SIZE} (размер алфавита).")
                        continue
                    if not is_prime(p):
                        print(f"Ошибка: {p} не простое число.")
                        continue

                    print(f"Возможные значения q (простые делители {p-1}):")
                    possible_q = []
                    for i in range(2, p):
                        if (p - 1) % i == 0 and is_prime(i):
                            possible_q.append(i)
                            print(f"  {i}")
                    if not possible_q:
                        print("Нет простых делителей. Выберите другое p.")
                        continue

                    q = int(input("Введите q из списка: "))
                    if q not in possible_q:
                        print("q должно быть из предложенных вариантов.")
                        continue

                    print(f"Возможные значения a (1 < a < {p-1}, a^{q} mod {p} = 1):")
                    possible_a = []
                    for i in range(2, p-1):
                        if mod_pow(i, q, p) == 1:
                            possible_a.append(i)
                            print(f"  {i}")
                    if not possible_a:
                        print("Нет подходящих a. Выберите другие p и q.")
                        continue

                    a = int(input("Введите a из списка: "))
                    if a not in possible_a:
                        print("a должно быть из предложенных вариантов.")
                        continue

                    x = int(input(f"Введите секретный ключ x (1 < x < {q}): "))
                    if not (1 < x < q):
                        print(f"x должен быть в диапазоне 1 < x < {q}")
                        continue

                    # Выбор способа ввода k
                    k_choice = input("Сгенерировать k автоматически? (y/n): ").strip().lower()
                    n = p  # модуль хеширования = p
                    hash_val = hesh(text, n)
                    print(f"Хеш-образ сообщения: {hash_val} (модуль n=p={n})")

                    if k_choice == 'y':
                        k = generate_k(q, p, a, x, hash_val)
                        print(f"Автоматически сгенерировано k = {k}")
                    else:
                        while True:
                            k = int(input(f"Введите случайное k (1 < k < {q}): "))
                            if not (1 < k < q):
                                print(f"k должен быть в диапазоне 1 < k < {q}")
                                continue
                            # предварительно проверим r и s
                            r_test = mod_pow(a, k, p) % q
                            if r_test == 0:
                                print("r = 0, выберите другое k")
                                continue
                            hm_test = hash_val % q
                            if hm_test == 0:
                                hm_test = 1
                            s_test = (x * r_test + k * hm_test) % q
                            if s_test == 0:
                                print("s = 0, выберите другое k")
                                continue
                            break

                    ok, msg = check_params(p, q, a, x, k)
                    if not ok:
                        print(f"Ошибка: {msg}")
                        continue
                    break
                except ValueError:
                    print("Ошибка ввода числа. Попробуйте снова.")
        else:
            print("Генерация параметров (16-битное p, 12-битное q)...")
            while True:
                p, q, a, x, y_gen = generate_keys(16, 12)
                if p > ALPHABET_SIZE:
                    break
            print(f"Сгенерированы параметры:")
            print(f"  p = {p}")
            print(f"  q = {q}")
            print(f"  a = {a}")
            print(f"  x = {x} (секретный)")
            n = p
            hash_val = hesh(text, n)
            print(f"Хеш-образ сообщения: {hash_val} (модуль n=p={n})")
            k = generate_k(q, p, a, x, hash_val)
            print(f"  k = {k} (автоматически сгенерировано)")
            y_gen = mod_pow(a, x, p)
            print(f"  y = {y_gen} (открытый ключ)")

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
                p = int(input(f"Введите p (> {ALPHABET_SIZE}): "))
                if p <= ALPHABET_SIZE:
                    print(f"p должно быть > {ALPHABET_SIZE}.")
                    continue

                print(f"Возможные q (простые делители {p-1}):")
                possible_q = []
                for i in range(2, p):
                    if (p - 1) % i == 0 and is_prime(i):
                        possible_q.append(i)
                        print(f"  {i}")

                q = int(input("Введите q из списка: "))
                if q not in possible_q:
                    print("q должно быть из предложенных вариантов.")
                    continue

                a = int(input("Введите a: "))
                y = int(input("Введите открытый ключ Y: "))

                ok, msg = check_params(p, q, a)
                if not ok:
                    print(f"Ошибка: {msg}")
                    continue
                break
            except ValueError:
                print("Ошибка ввода числа.")

        n = p
        hash_val = hesh(text, n)
        print(f"Хеш-образ сообщения: {hash_val} (модуль n=p={n})")

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





"""
подпись (1)

ЭЦП ГОСТ Р 34.10-94 (исправленная версия)
Выберите действие:
1 - Подписать сообщение
2 - Проверить подпись
3 - Сгенерировать ключи и подписать сообщение
Ваш выбор (1/2/3): 1
Введите открытый текст: тест
Введите простое p (> 32): 47
Возможные значения q (простые делители 46):
  2
  23
Введите q из списка: 23
Возможные значения a (1 < a < 46, a^23 mod 47 = 1):
  2
  3
  4
  6
  7
  8
  9
  12
  14
  16
  17
  18
  21
  24
  25
  27
  28
  32
  34
  36
  37
  42
Введите a из списка: 3
Введите секретный ключ x (1 < x < 23): 2
Введите случайное k (1 < k < 23): 3
Введите модуль для хеширования n (рекомендуется > 32): 47
Хеш-образ сообщения: 9
=== Генерация подписи ===
Параметры: p=47, q=23, a=3, x=2, k=3
H(m) mod q = 9
r = (a^k mod p) mod q = (3^3 mod 47) mod 23 = 27 mod 23 = 4
s = (x*r + k*H(m)) mod q = (2*4 + 3*9) mod 23 = (8 + 4) mod 23 = 12
Открытый ключ y = a^x mod p = 3^2 mod 47 = 9
Подпись: r = 4, s = 12

=== Результат ===
Подпись: r = 4, s = 12
Открытый ключ Y = 9
Для проверки подписи используйте эти значения и исходное сообщение.



проверка подписи (2)
Выберите действие:
1 - Подписать сообщение
2 - Проверить подпись
3 - Сгенерировать ключи и подписать сообщение
Ваш выбор (1/2/3): 2
Введите сообщение (оригинал): тест
Введите p (> 32): 47
Возможные q (простые делители 46):
  2
  23
Введите q из списка: 23
Введите a: 3
Введите открытый ключ Y: 9
Введите модуль для хеширования n: 47
Хеш-образ сообщения: 9
Введите r (первый параметр подписи): 4
Введите s (второй параметр подписи): 12
=== Проверка подписи ===
Параметры: p=47, q=23, a=3, y=9
Полученная подпись: r=4, s=12
Проверка диапазонов r и s пройдена
H(m) mod q = 9
v = H(m)^(q-2) mod q = 9^21 mod 23 = 18
z1 = s * v mod q = 12 * 18 mod 23 = 9
z2 = (q - r) * v mod q = (23 - 4) * 18 mod 23 = 20
a^z1 mod p = 3^9 mod 47 = 37
y^z2 mod p = 9^20 mod 47 = 2
(a^z1 * y^z2) mod p = 37 * 2 mod 47 = 27
u = (a^z1 * y^z2 mod p) mod q = 27 mod 23 = 4
u = 4 равно r = 4 → подпись верна

=== Результат проверки ===
Подпись верна (u = r = 4)"""    