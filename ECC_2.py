# -*- coding: utf8 -*-
import random

# ---------- Вспомогательные математические функции ----------
def mod_pow(base, exp, mod):
    """Быстрое возведение в степень по модулю"""
    return pow(base, exp, mod)

def mod_inv(a, m):
    """Обратный элемент по модулю (расширенный алгоритм Евклида)"""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y
    g, x, y = egcd(a, m)
    if g != 1:
        return None
    return x % m

def is_prime(n, k=10):
    """Тест Миллера-Рабина на простоту"""
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

# ---------- Эллиптическая кривая и точка ----------
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
            return "O"
        return f"({self.x},{self.y})"

def point_add(P, Q, a, p):
    """Сложение двух точек на кривой y² = x³ + a*x + b (mod p)"""
    if P.infinity: return Q
    if Q.infinity: return P
    if P.x == Q.x and P.y != Q.y:
        return ECPoint(infinity=True)
    if P == Q:
        return point_double(P, a, p)
    # lambda = (y2 - y1) / (x2 - x1) mod p
    num = (Q.y - P.y) % p
    den = (Q.x - P.x) % p
    inv_den = mod_inv(den, p)
    if inv_den is None:
        return ECPoint(infinity=True)
    lam = (num * inv_den) % p
    x3 = (lam * lam - P.x - Q.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return ECPoint(x3, y3)

def point_double(P, a, p):
    """Удвоение точки"""
    if P.infinity or P.y == 0:
        return ECPoint(infinity=True)
    # lambda = (3x² + a) / (2y) mod p
    num = (3 * P.x * P.x + a) % p
    den = (2 * P.y) % p
    inv_den = mod_inv(den, p)
    if inv_den is None:
        return ECPoint(infinity=True)
    lam = (num * inv_den) % p
    x3 = (lam * lam - 2 * P.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return ECPoint(x3, y3)

def point_mul(k, P, a, p):
    """Умножение точки на скаляр (double-and-add)"""
    result = ECPoint(infinity=True)
    base = P
    while k > 0:
        if k & 1:
            result = point_add(result, base, a, p)
        base = point_double(base, a, p)
        k >>= 1
    return result

def is_on_curve(P, a, b, p):
    """Проверка, лежит ли точка на кривой"""
    if P.infinity:
        return True
    left = (P.y * P.y) % p
    right = (P.x * P.x * P.x + a * P.x + b) % p
    return left == right

def check_discriminant(a, b, p):
    """Проверка 4a³ + 27b² ≠ 0 mod p"""
    disc = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    return disc != 0

# ---------- Проверка параметров ----------
def validate_params(a, b, p, G, cB):
    """Возвращает (True, 'OK') или (False, сообщение_об_ошибке)"""
    if p <= 3:
        return False, f"p = {p} должно быть > 3"
    if not is_prime(p):
        return False, f"p = {p} не простое"
    if not check_discriminant(a, b, p):
        return False, "Дискриминант равен 0 (кривая сингулярна). Выберите другие a, b."
    if not is_on_curve(G, a, b, p):
        return False, f"Точка G {G} не лежит на кривой"
    if not (1 < cB < p):   # в реальности нужно 1 < cB < q, но для демо используем p
        return False, f"Секретный ключ cB должен быть 1 < cB < {p}"
    return True, "Параметры корректны"

# ---------- Шифрование ----------
def encrypt(m, a, b, p, G, cB, k):
    """
    Шифрует число m (0 < m < p).
    Возвращает (R, e) или (None, сообщение_об_ошибке).
    """
    # Проверка m
    if not (0 < m < p):
        return None, f"Сообщение m должно быть 0 < m < {p}"
    # Открытый ключ DB = [cB]G
    DB = point_mul(cB, G, a, p)
    # R = [k]G
    R = point_mul(k, G, a, p)
    # P = [k]DB
    P = point_mul(k, DB, a, p)
    if P.infinity:
        return None, "P = O, выберите другой k"
    # e = m * x_P mod p
    e = (m * P.x) % p
    return (R, e), None

# ---------- Расшифрование ----------
def decrypt(R, e, a, b, p, cB):
    """
    Расшифровывает пару (R, e).
    Возвращает m или None при ошибке.
    """
    if not is_on_curve(R, a, b, p):
        return None, "Точка R не лежит на кривой"
    # Q = [cB]R
    Q = point_mul(cB, R, a, p)
    if Q.infinity:
        return None, "Q = O, расшифрование невозможно"
    # x⁻¹ mod p
    x_inv = mod_inv(Q.x, p)
    if x_inv is None:
        return None, f"Нет обратного для x = {Q.x} mod {p}"
    m = (e * x_inv) % p
    return m, None

# ---------- Учебный пример (маленькая кривая) ----------
def load_example():
    p = 47
    a = 1
    b = 4
    G = ECPoint(0, 2)       # лежит на кривой y² = x³ + x + 4 mod 47
    cB = 7                  # секретный ключ
    k = 5                   # случайное
    message = 12            # число для шифрования (0 < m < 47)
    return a, b, p, G, cB, k, message

# ---------- Основная программа ----------
def main():
    print("ECC (Эль-Гамаль на эллиптических кривых)")
    print("1 - Зашифровать число")
    print("2 - Расшифровать")
    print("3 - Загрузить учебный пример")
    choice = input("Ваш выбор: ").strip()

    if choice == '3':
        a, b, p, G, cB, k, m = load_example()
        print("\nЗагружены параметры учебной кривой:")
        print(f"p = {p}, a = {a}, b = {b}")
        print(f"G = {G}")
        print(f"Секретный ключ cB = {cB}")
        print(f"Случайное k = {k}")
        print(f"Сообщение m = {m}")

        # Проверка
        ok, err = validate_params(a, b, p, G, cB)
        if not ok:
            print(f"Ошибка в учебном примере: {err}")
            return

        # Шифрование
        (R, e), err = encrypt(m, a, b, p, G, cB, k)
        if err:
            print(f"Ошибка шифрования: {err}")
        else:
            print(f"\nОткрытый ключ DB = [{cB}]G = {point_mul(cB, G, a, p)}")
            print(f"Шифртекст: R = {R}, e = {e}")

            # Расшифрование
            m_dec, err = decrypt(R, e, a, b, p, cB)
            if err:
                print(f"Ошибка расшифрования: {err}")
            else:
                print(f"Расшифрованное сообщение: {m_dec}")
                if m_dec == m:
                    print("✅ Успешно!")
                else:
                    print("❌ Ошибка: m_dec != m")
        return

    if choice == '1':
        try:
            m = int(input("Введите число для шифрования (m): "))
            a = int(input("a = "))
            b = int(input("b = "))
            p = int(input("p (простое > 3) = "))
            xg = int(input("G.x = "))
            yg = int(input("G.y = "))
            G = ECPoint(xg, yg)
            cB = int(input("Секретный ключ cB (1 < cB < p) = "))
            k = int(input("Случайное k (1 < k < p) = "))

            ok, err = validate_params(a, b, p, G, cB)
            if not ok:
                print(f"Ошибка параметров: {err}")
                return
            if not (1 < k < p):
                print(f"k должно быть 1 < k < {p}")
                return

            (R, e), err = encrypt(m, a, b, p, G, cB, k)
            if err:
                print(f"Ошибка шифрования: {err}")
            else:
                DB = point_mul(cB, G, a, p)
                print(f"\nОткрытый ключ DB = {DB}")
                print(f"Шифртекст: {R} {e}")
                print("Для расшифрования используйте эти параметры и тот же cB.")
        except ValueError:
            print("Ошибка ввода числа.")

    elif choice == '2':
        try:
            cipher = input("Введите шифртекст в формате '(x,y) e': ")
            parts = cipher.strip().split()
            if len(parts) != 2:
                print("Неверный формат. Ожидается: (x,y) e")
                return
            R_str = parts[0].strip('()')
            xr, yr = map(int, R_str.split(','))
            R = ECPoint(xr, yr)
            e = int(parts[1])

            a = int(input("a = "))
            b = int(input("b = "))
            p = int(input("p = "))
            cB = int(input("Секретный ключ cB = "))

            # Проверка базовых параметров (без G, т.к. он не нужен для расшифрования)
            if p <= 3 or not is_prime(p):
                print("p должно быть простым > 3")
                return
            if not check_discriminant(a, b, p):
                print("Дискриминант равен 0")
                return

            m, err = decrypt(R, e, a, b, p, cB)
            if err:
                print(f"Ошибка расшифрования: {err}")
            else:
                print(f"Расшифрованное сообщение: {m}")
        except ValueError:
            print("Ошибка ввода числа.")

    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()