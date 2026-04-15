# -*- coding: utf8 -*-
import random

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'  # алфавит не используется, но оставлен для единообразия

# ---------- Вспомогательные функции ----------
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

def generate_prime(bits):
    """Генерация простого числа заданной битовой длины"""
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_random(max_val):
    """Генерация случайного числа в диапазоне [2, max_val-1]"""
    return random.randint(2, max_val - 1)

def gcd(a, b):
    """Наибольший общий делитель (не используется, но оставлена для совместимости)"""
    while b:
        a, b = b, a % b
    return a

# ---------- Основная логика протокола ----------
def diffie_hellman():
    print("=== Протокол обмена ключами Диффи-Хеллмана ===\n")
    print("Введите общие параметры n и a (1 < a < n).")
    print("Рекомендуется n — большое простое число.")

    # Ввод общих параметров
    while True:
        try:
            n = int(input("n = "))
            a = int(input("a = "))
            if not (1 < a < n):
                print("Ошибка: должно быть 1 < a < n. Повторите ввод.")
                continue
            if not is_prime(n):
                print("Предупреждение: n не является простым. Для безопасности лучше использовать простое n.")
            break
        except ValueError:
            print("Ошибка ввода числа.")

    # Ввод или генерация секретных ключей
    print("\n--- Секретные ключи ---")
    choice = input("Сгенерировать секретные ключи автоматически? (y/n): ").strip().lower()
    if choice == 'y':
        KA = generate_random(n)
        KB = generate_random(n)
        # Гарантируем, что ключи разные и не 0/1
        while KB == KA or KB <= 1:
            KB = generate_random(n)
        print(f"Сгенерирован KA = {KA}")
        print(f"Сгенерирован KB = {KB}")
    else:
        while True:
            try:
                KA = int(input("Введите секретный ключ стороны A (KA, 2 <= KA < n): "))
                KB = int(input("Введите секретный ключ стороны B (KB, 2 <= KB < n): "))
                if not (2 <= KA < n) or not (2 <= KB < n):
                    print("Ошибка: ключи должны быть в диапазоне [2, n-1].")
                    continue
                if KA == KB:
                    print("Ошибка: KA и KB должны быть разными.")
                    continue
                break
            except ValueError:
                print("Ошибка ввода числа.")

    # Вычисление открытых ключей
    YA = mod_pow(a, KA, n)
    YB = mod_pow(a, KB, n)
    print(f"\nОткрытый ключ стороны A: YA = a^KA mod n = {a}^{KA} mod {n} = {YA}")
    print(f"Открытый ключ стороны B: YB = a^KB mod n = {a}^{KB} mod {n} = {YB}")

    # Обмен ключами (имитация)
    print("\n--- Обмен открытыми ключами ---")
    input("Нажмите Enter, чтобы выполнить обмен...")
    # Стороны получают открытые ключи друг друга
    YA_received = YA
    YB_received = YB
    print(f"Сторона A получила YB = {YB_received}")
    print(f"Сторона B получила YA = {YA_received}")

    # Вычисление общего секретного ключа
    print("\n--- Вычисление общего секретного ключа ---")
    K_A = mod_pow(YB_received, KA, n)
    K_B = mod_pow(YA_received, KB, n)
    print(f"Сторона A вычисляет K = YB^KA mod n = {YB_received}^{KA} mod {n} = {K_A}")
    print(f"Сторона B вычисляет K = YA^KB mod n = {YA_received}^{KB} mod {n} = {K_B}")

    # Проверка результата
    print("\n=== Результат ===")
    if K_A == K_B:
        print(f"Общий секретный ключ успешно выработан: K = {K_A}")
    else:
        print(f"Ошибка! Ключи не совпадают: K_A = {K_A}, K_B = {K_B}")

    # Дополнительные проверки безопасности (как в C++ версии)
    if K_A == 0 or K_A == 1:
        print(" Внимание: общий ключ равен 0 или 1, что небезопасно. Выберите другие параметры.")
    if K_A == YA or K_A == YB:
        print(" Внимание: общий ключ совпадает с одним из открытых ключей. Выберите другие параметры.")

def main():
    while True:
        diffie_hellman()
        again = input("\nПовторить? (y/n): ").strip().lower()
        if again != 'y':
            break
    print("Программа завершена.")

if __name__ == "__main__":
    main()