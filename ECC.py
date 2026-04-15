import math

# Расширенный алфавит (добавьте нужные символы)
alphabet = (
    'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    ' .,;:-—!?()«»"0123456789'
)

def text_to_k_sequence(text, alphabet):
    seq = []
    for ch in text.lower():
        if ch in alphabet:
            seq.append(alphabet.index(ch) + 1)
        else:
            raise ValueError(
                f"Символ '{ch}' не входит в алфавит ECC. Добавьте его в alphabet."
            )
    return seq

def k_sequence_to_text(seq, alphabet):
    text = ''
    for k in seq:
        if 1 <= k <= len(alphabet):
            text += alphabet[k-1]
        else:
            text += '?'
    return text

def reverse_n(n, module):
    n = n % module
    for i in range(1, module):
        if (n * i) % module == 1:
            return i
    raise ValueError(f"Нет обратного элемента для {n} по модулю {module}")

def double(G, a, p, step):
    x = G[0]
    y = G[1]
    # Подробный вывод можно отключить, если не нужен
    numerator = 3 * x ** 2 + a
    denominator = 2 * y
    inv = reverse_n(denominator, p)
    lamb = (numerator * inv) % p
    new_x = (lamb ** 2 - 2 * x) % p
    new_y = (lamb * (x - new_x) - y) % p
    return [new_x, new_y]

def plus(G1, G2, p, step):
    x1, y1 = G1
    x2, y2 = G2
    numerator = y2 - y1
    denominator = x2 - x1
    inv = reverse_n(denominator, p)
    lamb = (numerator * inv) % p
    new_x = (lamb ** 2 - x1 - x2) % p
    new_y = (lamb * (x1 - new_x) - y1) % p
    return [new_x, new_y]

def multiply(k, G, a, p):
    Q = G
    if k == 1:
        return G
    elif k == 2:
        Q = double(G, a, p, 2)
    else:
        Q = double(G, a, p, 2)
        for i in range(3, k+1):
            Q = plus(Q, G, p, i)
    return Q

def enc(a, b, p, G, Cb, k, m):
    Db = multiply(Cb, G, a, p)
    R = multiply(k, G, a, p)
    P = multiply(k, Db, a, p)
    e = (m * P[0]) % p
    return (R, e)

def dec(a, b, p, Cb, R, e):
    Q = multiply(Cb, R, a, p)
    inv = reverse_n(Q[0], p)
    m_dec = (e * inv) % p
    return m_dec


def encrypt_text_ecc(text, a, b, p, G, Cb, k):
    """Текст → k-последовательность → шифрование каждого m; результат — одна строка для decrypt_text_ecc."""
    k_seq = text_to_k_sequence(text, alphabet)
    results = []
    for m in k_seq:
        R, e = enc(a, b, p, G, Cb, k, m)
        results.append((R, e))
    return ";".join(f"{R[0]},{R[1]},{e}" for R, e in results)


def decrypt_text_ecc(cipher_line, a, b, p, Cb):
    """Строка шифртекста (блоки x,y,e через ;) → восстановленный текст."""
    blocks = [x.strip() for x in cipher_line.split(";") if x.strip()]
    m_dec_list = []
    for block in blocks:
        parts = block.split(",")
        if len(parts) != 3:
            raise ValueError(f"Неверный блок шифртекста: {block!r}")
        R_dec = [int(parts[0]), int(parts[1])]
        e_dec = int(parts[2])
        m_dec = dec(a, b, p, Cb, R_dec, e_dec)
        m_dec_list.append(m_dec)
    return k_sequence_to_text(m_dec_list, alphabet)


def main():
    print("ECC: 1 — текст → k-последовательность, 2 — k-последовательность → текст, 3 — ECC-шифрование/расшифрование")
    mode = input("Выберите режим (1/2/3): ").strip()
    if mode == '1':
        text = input("Введите текст для ECC-шифрования:\n")
        k_seq = text_to_k_sequence(text, alphabet)
        print("\nK-последовательность (индексы символов):")
        print(k_seq)
        with open("ecc_k_sequence.txt", "w", encoding="utf-8") as f:
            f.write(" ".join(str(x) for x in k_seq))
        print("K-последовательность сохранена в ecc_k_sequence.txt")
    elif mode == '2':
        seq_str = input("Введите k-последовательность (через пробел или запятую):\n")
        seq = [int(x) for x in seq_str.replace(',', ' ').split()]
        text = k_sequence_to_text(seq, alphabet)
        print("\nВосстановленный текст:")
        print(text)
        with open("ecc_restored_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Восстановленный текст сохранён в ecc_restored_text.txt")
    elif mode == '3':
        print("Эллиптическая кривая (ECC) — шифрование/расшифрование")
        print("1. Шифрование")
        print("2. Расшифрование")
        submode = input("Выберите режим (1-2): ").strip()
        a = int(input('Введите a: '))
        b = int(input('Введите b: '))
        p = int(input('Введите p (простое число): '))
        G = input('Введите G в формате x,y: ').split(',')
        G = [int(G[0]), int(G[1])]
        if submode == '1':
            Cb = int(input('Введите Cb (закрытый ключ получателя): '))
            k = int(input('Введите k (секретный ключ для шифрования): '))
            m_input = input('Введите m (сообщение для шифрования, через запятую): ')
            m_list = [int(x.strip()) for x in m_input.split(',')]
            results = []
            for m in m_list:
                R, e = enc(a, b, p, G, Cb, k, m)
                results.append((R, e))
            # Сохраняем результат в файл
            with open("ecc_cipher.txt", "w", encoding="utf-8") as f:
                for R, e in results:
                    f.write(f"{R[0]},{R[1]},{e}\n")
            print("Результаты шифрования (для каждого m):")
            for R, e in results:
                print(f"{R[0]},{R[1]},{e}")
            print("\nГотовый шифртекст (одна строка, для расшифровки):")
            ready_cipher = ";".join(f"{R[0]},{R[1]},{e}" for R, e in results)
            print(ready_cipher)
            print("\nШифртекст сохранён в ecc_cipher.txt")
        elif submode == '2':
            Cb = int(input('Введите Cb (закрытый ключ получателя): '))
            print('Выберите источник шифртекста:')
            print('1. Ввести вручную')
            print('2. Прочитать из файла ecc_cipher.txt')
            source = input('Ваш выбор (1/2): ').strip()
            if source == '1':
                cipher_input = input("Введите шифртекст (каждый блок в формате x,y,e через запятую):\n")
            else:
                with open("ecc_cipher.txt", "r", encoding="utf-8") as f:
                    cipher_input = ";".join(line.strip() for line in f if line.strip())
                print("Считан шифртекст из ecc_cipher.txt")
            blocks = [x.strip() for x in cipher_input.split(';') if x.strip()]
            m_dec_list = []
            for block in blocks:
                parts = block.split(',')
                if len(parts) != 3:
                    print(f"Ошибка в блоке: {block}")
                    continue
                R_dec = [int(parts[0]), int(parts[1])]
                e_dec = int(parts[2])
                m_dec = dec(a, b, p, Cb, R_dec, e_dec)
                m_dec_list.append(m_dec)
            print("Расшифрованная последовательность m:")
            print(m_dec_list)
            # Сохраняем результат в файл
            with open("ecc_decoded_m.txt", "w", encoding="utf-8") as f:
                f.write(" ".join(str(x) for x in m_dec_list))
            print("Последовательность m сохранена в ecc_decoded_m.txt")
            # Восстановить текст
            text_restored = k_sequence_to_text(m_dec_list, alphabet)
            print("Восстановленный текст:")
            print(text_restored)
            with open("ecc_restored_text.txt", "w", encoding="utf-8") as f:
                f.write(text_restored)
            print("Восстановленный текст сохранён в ecc_restored_text.txt")
        else:
            print("Неверный выбор режима.")
    else:
        print("Неверный выбор режима.")

if __name__ == "__main__":
    main()
