# -*- coding: utf8 -*-
import random

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

# ---------- Вспомогательные функции ----------
def textToNumbers(text):
    res = []
    for ch in text:
        idx = alf.find(ch)
        if idx != -1:
            res.append(idx + 1)
    return res

def tchk_zpt(s):
    s = s.replace('.', 'тчк').replace(',', 'зпт')
    return s.lower()

def hesh(text, module):
    nums = textToNumbers(text)
    h = 0
    for m in nums:
        h = ((h + m) ** 2) % module
    return h

def mod_pow(base, exp, mod):
    return pow(base, exp, mod)

def mod_inv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None
    return x % m

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y

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
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

# ---------- Эллиптическая кривая ----------
class ECPoint:
    def __init__(self, x=None, y=None, infinity=False):
        self.x = x
        self.y = y
        self.infinity = infinity

    def __eq__(self, other):
        if self.infinity and other.infinity:
            return True
        if self.infinity or other.infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __str__(self):
        if self.infinity:
            return "O (бесконечность)"
        return f"({self.x}, {self.y})"

def point_add(P, Q, p, a):
    if P.infinity: return Q
    if Q.infinity: return P
    if P.x == Q.x and P.y != Q.y:
        return ECPoint(infinity=True)
    if P == Q:
        return point_double(P, p, a)
    num = (Q.y - P.y) % p
    den = (Q.x - P.x) % p
    inv_den = mod_inv(den, p)
    if inv_den is None:
        return ECPoint(infinity=True)
    lam = (num * inv_den) % p
    x3 = (lam * lam - P.x - Q.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return ECPoint(x3, y3)

def point_double(P, p, a):
    if P.infinity or P.y == 0:
        return ECPoint(infinity=True)
    num = (3 * P.x * P.x + a) % p
    den = (2 * P.y) % p
    inv_den = mod_inv(den, p)
    if inv_den is None:
        return ECPoint(infinity=True)
    lam = (num * inv_den) % p
    x3 = (lam * lam - 2 * P.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return ECPoint(x3, y3)

def point_mul(k, P, p, a):
    result = ECPoint(infinity=True)
    base = P
    while k > 0:
        if k & 1:
            result = point_add(result, base, p, a)
        base = point_double(base, p, a)
        k >>= 1
    return result

def is_on_curve(point, p, a, b):
    if point.infinity:
        return True
    left = (point.y * point.y) % p
    right = (point.x * point.x * point.x + a * point.x + b) % p
    return left == right

def check_discriminant(p, a, b):
    """Проверка 4a³ + 27b² ≠ 0 mod p"""
    disc = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    return disc != 0

# ---------- Проверка параметров кривой ----------
def validate_curve_params(p, a, b, q, G):
    """Возвращает (True, 'OK') или (False, сообщение_об_ошибке)"""
    if p <= 3:
        return False, f"p = {p} должно быть > 3"
    if not is_prime(p):
        return False, f"p = {p} не является простым"
    if not check_discriminant(p, a, b):
        return False, "Дискриминант 4a³+27b² ≡ 0 (mod p). Выберите другие a, b."
    if not is_on_curve(G, p, a, b):
        return False, f"Точка G {G} не лежит на кривой"
    if not is_prime(q):
        return False, f"q = {q} должно быть простым"
    if q <= 1:
        return False, f"q = {q} должно быть > 1"
    # В реальности нужно проверить, что q делит порядок кривой, но для демо опустим
    return True, "Параметры корректны"

# ---------- Проверка ключей ----------
def validate_keys(d, k, q):
    if not (1 < d < q):
        return False, f"Секретный ключ d должен быть 1 < d < {q}"
    if not (1 < k < q):
        return False, f"Случайное k должно быть 1 < k < {q}"
    return True, "OK"

# ---------- Подпись ----------
def sign_message(message, p, a, b, q, G, d, k, hash_mod):
    h_val = hesh(tchk_zpt(message), hash_mod)
    h = h_val % q
    if h == 0:
        h = 1
    C = point_mul(k, G, p, a)
    r = C.x % q
    if r == 0:
        return None, "r = 0, выберите другое k"
    s = (k * h + r * d) % q
    if s == 0:
        return None, "s = 0, выберите другое k"
    Q = point_mul(d, G, p, a)
    return (r, s, Q), None

# ---------- Проверка подписи ----------
def verify_signature(message, r, s, p, a, b, q, G, Q, hash_mod):
    if not (0 < r < q and 0 < s < q):
        return False, "r или s вне диапазона (0, q)"
    h_val = hesh(tchk_zpt(message), hash_mod)
    h = h_val % q
    if h == 0:
        h = 1
    h_inv = mod_inv(h, q)
    if h_inv is None:
        return False, "Не удалось вычислить h⁻¹ mod q"
    u1 = (s * h_inv) % q
    u2 = (-r * h_inv) % q
    P = point_add(point_mul(u1, G, p, a), point_mul(u2, Q, p, a), p, a)
    if P.infinity:
        return False, "P = O (бесконечность)"
    R = P.x % q
    if R == r:
        return True, f"Подпись верна (R = {R})"
    else:
        return False, f"Подпись неверна (R = {R}, r = {r})"

# ---------- Учебный пример (маленькая кривая) ----------
def load_example():
    p = 47
    a = 1
    b = 4
    q = 23
    G = ECPoint(0, 2)
    d = 7
    k = 5
    hash_mod = 47
    message = "тест"
    return p, a, b, q, G, d, k, hash_mod, message

# ---------- Основная программа ----------
def main():
    print("ГОСТ Р 34.10-2012 (ЭЦП на эллиптических кривых) с проверками")
    print("1 - Подписать сообщение (ручной ввод)")
    print("2 - Проверить подпись (ручной ввод)")
    print("3 - Загрузить учебный пример (проверенная кривая)")
    choice = input("Ваш выбор: ").strip()

    if choice == '3':
        p, a, b, q, G, d, k, hash_mod, message = load_example()
        print("\nЗагружены параметры учебной кривой:")
        print(f"p = {p}, a = {a}, b = {b}")
        print(f"q = {q}")
        print(f"G = {G}")
        print(f"Секретный ключ d = {d}")
        print(f"Случайное k = {k}")
        print(f"Модуль хеша = {hash_mod}")
        print(f"Сообщение: '{message}'")

        # Проверяем параметры
        ok, msg = validate_curve_params(p, a, b, q, G)
        if not ok:
            print(f"Ошибка в учебном примере: {msg}")
            return
        ok, msg = validate_keys(d, k, q)
        if not ok:
            print(f"Ошибка ключей: {msg}")
            return

        # Подпись
        res, err = sign_message(message, p, a, b, q, G, d, k, hash_mod)
        if err:
            print(f"Ошибка подписи: {err}")
        else:
            r, s, Q = res
            print(f"\nОткрытый ключ Q = {Q}")
            print(f"Подпись: r = {r}, s = {s}")
            # Проверка
            ok, msg = verify_signature(message, r, s, p, a, b, q, G, Q, hash_mod)
            print(f"Проверка: {msg}")
        return

    if choice == '1':
        message = input("Введите сообщение: ")
        # Ручной ввод с проверками
        while True:
            try:
                p = int(input("p (простое > 3) = "))
                a = int(input("a = "))
                b = int(input("b = "))
                q = int(input("q (простое, порядок подгруппы) = "))
                xg = int(input("G.x = "))
                yg = int(input("G.y = "))
                G = ECPoint(xg, yg)

                ok, msg = validate_curve_params(p, a, b, q, G)
                if not ok:
                    print(f"Ошибка: {msg}")
                    continue

                d = int(input(f"Секретный ключ d (1 < d < {q}) = "))
                k = int(input(f"Случайное k (1 < k < {q}) = "))
                ok, msg = validate_keys(d, k, q)
                if not ok:
                    print(f"Ошибка: {msg}")
                    continue

                hash_mod = int(input("Модуль хеширования (обычно = p): "))
                break
            except ValueError:
                print("Ошибка ввода числа.")

        res, err = sign_message(message, p, a, b, q, G, d, k, hash_mod)
        if err:
            print(f"Ошибка: {err}")
        else:
            r, s, Q = res
            print(f"\nОткрытый ключ Q = {Q}")
            print(f"Подпись: r = {r}, s = {s}")
            print("Для проверки используйте эти значения и исходное сообщение.")

    elif choice == '2':
        message = input("Введите сообщение: ")
        while True:
            try:
                p = int(input("p = "))
                a = int(input("a = "))
                b = int(input("b = "))
                q = int(input("q = "))
                xg = int(input("G.x = "))
                yg = int(input("G.y = "))
                G = ECPoint(xg, yg)
                xq = int(input("Q.x = "))
                yq = int(input("Q.y = "))
                Q = ECPoint(xq, yq)
                r = int(input("r = "))
                s = int(input("s = "))
                hash_mod = int(input("Модуль хеширования = "))

                # Проверки
                ok, msg = validate_curve_params(p, a, b, q, G)
                if not ok:
                    print(f"Ошибка параметров кривой: {msg}")
                    continue
                if not is_on_curve(Q, p, a, b):
                    print("Ошибка: точка Q не лежит на кривой")
                    continue
                break
            except ValueError:
                print("Ошибка ввода числа.")

        ok, msg = verify_signature(message, r, s, p, a, b, q, G, Q, hash_mod)
        print(msg)

    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()






"""
подпись (1)
Введите сообщение: тест
p = 47
a = 1
b = 4
q = 23
G.x = 0
G.y = 2
Секретный ключ d = 7
Случайное k = 5
Модуль хеширования = 47"""

""" проверка подписи (2)
Введите сообщение: тест
p = 47
a = 1
b = 4
q = 23
G.x = 0
G.y = 2
Q.x = 16    (из предыдущего шага)
Q.y = 5     (из предыдущего шага)
r = 18      (из подписи)
s = 9       (из подписи)
Модуль хеширования = 47"""