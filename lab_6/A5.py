import random

def generate_random_binary_string(length=64):
    return ''.join(random.choice('01') for _ in range(length))

def get_r1():
    """Функция принимает пользовательский ввод и генерирует 
    три регистра для последующего использования в генерации ключей."""
    while True:
        rstr = input("Введите ключ (64 символа 0 и 1, либо оставьте пустым для случайного): ")
        if not rstr:
            rstr = generate_random_binary_string()
            print(f"Случайный ключ: {rstr}")
        if len(rstr) != 64:
            print("Ключ должен быть 64 символа")
            continue
        if not all(char in '01' for char in rstr):
            print("Ключ должен состоять только из 1 и 0")
            continue
        r1 = [0]*19
        r2 = [0]*22
        r3 = [0]*23
        for i in range(64):
            r1t = r1[18]^r1[17]^r1[16]^r1[13]^int(rstr[i])
            r1.insert(0, r1t)
            r1.pop()
            r2t = r2[21]^r2[20]^int(rstr[i])
            r2.insert(0, r2t)
            r2.pop()
            r3t = r3[22]^r3[21]^r3[20]^r3[7]^int(rstr[i])
            r3.insert(0, r3t)
            r3.pop()
        return r1, r2, r3

def gamma(r1, r2, r3):
    """Генерация гаммы на основе регистров."""
    # Инициализация
    for _ in range(100):
        F = (r1[8] and r2[10]) or (r1[8] and r3[10]) or (r2[10] and r3[10])
        if r1[8] == F:
            r1t = r1[18]^r1[17]^r1[16]^r1[13]
            r1.insert(0, r1t)
            r1.pop()
        if r2[10] == F:
            r2t = r2[21]^r2[20]
            r2.insert(0, r2t)
            r2.pop()
        if r3[10] == F:
            r3t = r3[22]^r3[21]^r3[20]^r3[7]
            r3.insert(0, r3t)
            r3.pop()
    gam = []
    for _ in range(512):  # Делаем длинную гамму, чтобы хватило на длинные сообщения
        F = (r1[8] and r2[10]) or (r1[8] and r3[10]) or (r2[10] and r3[10])
        if r1[8] == F:
            r1t = r1[18]^r1[17]^r1[16]^r1[13]
            r1.insert(0, r1t)
            r1.pop()
        if r2[10] == F:
            r2t = r2[21]^r2[20]
            r2.insert(0, r2t)
            r2.pop()
        if r3[10] == F:
            r3t = r3[22]^r3[21]^r3[20]^r3[7]
            r3.insert(0, r3t)
            r3.pop()
        # Для гаммы используем по 8 бит подряд, чтобы шифровать по байтам
        gam.append(r1[18]^r2[21]^r3[22])
    return gam

def encrypt_message_bytes(message, gamma_bits):
    encrypted_array = []
    message_bytes = message.encode('utf-8')  # строка в байты
    for i, byte in enumerate(message_bytes):
        gamma_byte = 0
        for j in range(8):
            gamma_byte = (gamma_byte << 1) | gamma_bits[i*8 + j]
        xor_result = byte ^ gamma_byte
        encrypted_array.append(format(xor_result, '08b'))
    return encrypted_array

def decrypt_message_bytes(encrypted_array, gamma_bits):
    decrypted_bytes = bytearray()
    for i, binary_str in enumerate(encrypted_array):
        xor_result = int(binary_str, 2)
        gamma_byte = 0
        for j in range(8):
            gamma_byte = (gamma_byte << 1) | gamma_bits[i*8 + j]
        byte = xor_result ^ gamma_byte
        decrypted_bytes.append(byte)
    return decrypted_bytes.decode('utf-8')


def main():
    print("Выберите режим:")
    print("1 — Шифрование")
    print("2 — Расшифровка")
    mode = input("Ваш выбор (1/2): ").strip()
    if mode not in ('1', '2'):
        print("Некорректный выбор!")
        return
    r1, r2, r3 = get_r1()
    gamma_bits = gamma(r1[:], r2[:], r3[:])  # Передаем копии, чтобы сохранить состояние
    if mode == '1':
        message = input("Введите сообщение для шифрования: ")
        encrypted = encrypt_message_bytes(message, gamma_bits)
        print("Зашифрованное сообщение :")
        print(' '.join(encrypted))
    else:
        encrypted_input = input("Введите зашифрованное сообщение через пробел: ")
        encrypted_array = encrypted_input.strip().split()
        decrypted = decrypt_message_bytes(encrypted_array, gamma_bits)
        print("Расшифрованное сообщение:", decrypted)

if __name__ == "__main__":
    main()

#1011111010010100010110101010101110100100101001010101101010101101