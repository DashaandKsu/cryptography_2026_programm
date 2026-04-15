# -*- coding: utf-8 -*-
import sys

# 1. Расширенный алфавит (добавьте еще символы, если нужно)
alphabet = (
    'абвгдёежзийклмнопрстуфхцчшщъыьэюя'
    ' .,;:-—!?()«»"0123456789'
)

# 2. Преобразование текста в k-последовательность
def text_to_k_sequence(text, alphabet):
    seq = []
    for ch in text.lower():
        if ch in alphabet:
            seq.append(alphabet.index(ch) + 1)  # k начинается с 1
        else:
            print(f"Символ '{ch}' не входит в алфавит ECC! Добавьте его в alphabet.")
            sys.exit(1)
    return seq

# 3. Преобразование k-последовательности обратно в текст
def k_sequence_to_text(seq, alphabet):
    text = ''
    for k in seq:
        if 1 <= k <= len(alphabet):
            text += alphabet[k-1]
        else:
            text += '?'
    return text

# 4. Пример функции умножения точки на k (toy-curve, для теста)
def ecc_multiply(k, G, a, p):
    # Это простая "игрушечная" версия: для реального ECC используйте свою функцию!
    # Здесь просто складываем G k раз (неэффективно, только для демонстрации)
    x, y = G
    rx, ry = x, y
    for _ in range(k-1):
        # Простейшее сложение: (x, y) + (x, y) = (x+1, y+1) mod p
        rx = (rx + x) % p
        ry = (ry + y) % p
    return (rx, ry)

def main():
    print("=== Подготовка текста для ECC ===")
    text = input("Введите текст для ECC-шифрования:\n")
    print("\nИспользуемый алфавит:")
    print(alphabet)
    k_seq = text_to_k_sequence(text, alphabet)
    print("\nK-последовательность (индексы символов):")
    print(k_seq)

    # Пример: обратное преобразование
    restored = k_sequence_to_text(k_seq, alphabet)
    print("\nВосстановленный текст (проверка):")
    print(restored)

    # Пример: вычисление точек [k]G для toy-curve
    print("\n=== Пример вычисления точек ECC ===")
    a = 2
    p = 97
    G = (3, 6)
    print(f"Параметры toy-кривой: a={a}, p={p}, G={G}")
    print("Первые 10 точек для k из последовательности:")
    for i, k in enumerate(k_seq[:10]):
        P = ecc_multiply(k, G, a, p)
        print(f"[{k}]G = {P}")

if __name__ == "__main__":
    main()
