alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123'
ROWS = 6
COLS = 6
SEPARATOR = '0'  # служебный символ, не должен встречаться в исходном тексте

letter_alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

def generate_table(key):
    key = key.upper().replace('Ё', 'Е')
    used = set()
    key_chars = []
    for ch in key:
        if ch in letter_alphabet and ch not in used:
            used.add(ch)
            key_chars.append(ch)
    for ch in alphabet:
        if ch not in used:
            key_chars.append(ch)
    table = [key_chars[i*COLS:(i+1)*COLS] for i in range(ROWS)]
    return table

def display_table(key):
    table = generate_table(key)
    print("\nТаблица Плэйфера (6x6):")
    print("-" * 37)
    for row in table:
        print("| " + " | ".join(row) + " |")
        print("-" * 37)

def find_position(table, ch):
    for r in range(ROWS):
        for c in range(COLS):
            if table[r][c] == ch:
                return r, c
    raise ValueError(f"Символ {ch} не найден в таблице")

def preprocess_text(text):
    text = text.upper().replace('Ё', 'Е')
    text = ''.join(ch for ch in text if ch in alphabet)
    processed = []
    i = 0
    while i < len(text):
        processed.append(text[i])
        if i + 1 < len(text) and text[i] == text[i + 1]:
            processed.append(SEPARATOR)
        i += 1
    if len(processed) % 2 != 0:
        processed.append(SEPARATOR)
    return ''.join(processed)

def encrypt_pair(table, a, b):
    r1, c1 = find_position(table, a)
    r2, c2 = find_position(table, b)
    if r1 == r2:
        return table[r1][(c1+1) % COLS], table[r2][(c2+1) % COLS]
    elif c1 == c2:
        return table[(r1+1) % ROWS][c1], table[(r2+1) % ROWS][c2]
    else:
        return table[r1][c2], table[r2][c1]

def decrypt_pair(table, a, b):
    r1, c1 = find_position(table, a)
    r2, c2 = find_position(table, b)
    if r1 == r2:
        return table[r1][(c1-1) % COLS], table[r2][(c2-1) % COLS]
    elif c1 == c2:
        return table[(r1-1) % ROWS][c1], table[(r2-1) % ROWS][c2]
    else:
        return table[r1][c2], table[r2][c1]

def encrypt(text, key):
    """Шифрование текста с использованием ключевого слова."""
    table = generate_table(key)
    prepared = preprocess_text(text)
    result = []
    for i in range(0, len(prepared), 2):
        a, b = prepared[i], prepared[i+1]
        enc_a, enc_b = encrypt_pair(table, a, b)
        result.append(enc_a)
        result.append(enc_b)
    return ''.join(result)

def decrypt(text, key):
    table = generate_table(key)
    result = []
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        dec_a, dec_b = decrypt_pair(table, a, b)
        result.append(dec_a)
        result.append(dec_b)
    decrypted = ''.join(result)
    decrypted = decrypted.replace(SEPARATOR, '') #
    return decrypted

def validate_key(key):
    if not key:
        return False, "Ключ не может быть пустым"
    key = key.upper().replace('Ё', 'Е')
    for ch in key:
        if ch not in letter_alphabet:
            return False, f"Ключ содержит недопустимый символ: {ch}"
    if len(set(key)) != len(key):
        return False, "Ключ не должен содержать повторяющихся букв"
    return True, "Ключ корректен"