import math 
import random

alf = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n%i == 0:
            return False
    return True

def textToNumbers(text):
    return [alf.find(char)+1 for char in text]

def tchk_zpt(n):
    return n.replace('.','тчк').replace(',','зпт').replace(' ', 'прб').lower()

def tchk_zpt_back(n):
    return n.replace('тчк', '.').replace('зпт', ',').replace('прб', ' ')

def numbersToText(numbers):
    return ''.join(alf[num-1] for num in numbers)

def encrypt_elgamal(text, p, g, x):
    """Шифрование Эль-Гамаля: p — простое >32, g и x — как в интерактивном режиме."""
    text = tchk_zpt(text)
    nums = textToNumbers(text)
    if not is_prime(p) or p <= 32:
        raise ValueError("p должно быть простым числом больше 32.")
    f = p - 1
    if not (1 < x < p - 1):
        raise ValueError(f"x должно быть в диапазоне 1 < x < {p - 1}.")
    if not (1 < g < p - 1):
        raise ValueError(f"g должно быть в диапазоне 1 < g < {p - 1}.")
    y = pow(g, x, p)
    encrypted = []
    for num in nums:
        k = random.randint(2, f - 1) # случайное число k в диапазоне 2 до f-1, для каждого символа уже выбирается свой случайный k, Случайность «спрятана» в k: при том же m другой k даёт другие a и b.
        print("K = ", k)
        while math.gcd(k, f) != 1:
            k = random.randint(2, f - 1)
        a = pow(g, k, p) # вычисление a = g^k mod p
        b = (pow(y, k, p) * num) % p
        encrypted.append(f"{a}.{b}")
    cipher = " ".join(encrypted)
    return cipher, p, g, y


def encryption(text):
    while True:
        p = int(input("Введите p (простое >32): "))
        if is_prime(p) and p > 32:
            break
        print("Некорректное p!")
    x = int(input(f"Введите секретный ключ x (1<{p-1}): "))
    g = int(input(f"Введите g (1<{p-1}): "))
    cipher, p_, g_, y = encrypt_elgamal(text, p, g, x)
    print(f"\nОткрытые ключи: p={p_}, g={g_}, y={y}")
    return cipher

def decryption(p, x, ciphertext):
    decrypted_nums = []
    for pair in ciphertext.split():
        a, b = map(int, pair.split('.'))
        s = pow(a, x, p)
        m = (b * pow(s, p-2, p)) % p  # Используем малую теорему Ферма для обратного элемента
        decrypted_nums.append(m)
    return numbersToText(decrypted_nums)

def main():
    choice = input('Выберите действие:\n1. Зашифровать\n2. Расшифровать\n> ')

    if choice == '1':
        text = input("Введите текст: ")
        encrypted = encryption(text)
        print("\nРезультат шифрования:")
        print(encrypted)
        
    elif choice == '2':
        p = int(input("Введите модуль p: "))
        x = int(input("Введите секретный ключ x: "))
        ciphertext = input("Введите зашифрованный текст: ")
        
        try:
            decrypted = decryption(p, x, ciphertext)
            print("\nРезультат расшифрования:")
            print(tchk_zpt_back(decrypted))
        except Exception as e:
            print(f"Ошибка: {str(e)}")
    else:
        print("Неизвестный режим.")

if __name__ == "__main__":
    main()


"""1. Зашифровать
2. Расшифровать
> 1
Введите текст: макадамия
Введите p (простое >32): 47
Введите секретный ключ x (1<46): 3
Введите g (1<46): 3
K =  18
K =  5
K =  11
K =  29
K =  13
K =  16
K =  44
K =  32
K =  45

Открытые ключи: p=47, g=3, y=27

Результат шифрования:
7.41 8.42 4.46 24.6 36.19 21.2 28.39 18.36 16.36"""