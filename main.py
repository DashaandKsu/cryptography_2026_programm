# Итоговая программа: меню выбора шифров.
# Содержит только импорт функций из папок lab_1, lab_2, ... lab_8 и их использование.

# Импортируем функции шифрования и расшифрования Атбаш, Цезаря, Полибия, Тритемия, Белазо, Виженера, матричного шифра и Плэйфера
from lab_1.atbash import encrypt_text as atbash_encrypt, decrypt_text as atbash_decrypt
from lab_1.Cesar import encrypt_text as cesar_encrypt, decrypt_text as cesar_decrypt
from lab_1.Polibia import encrypt_text as polybius_encrypt, decrypt_text as polybius_decrypt
from lab_2.Tritemi import encrypt_tritemius as tritemi_encrypt, decrypt_tritemius as tritemi_decrypt
from lab_2.Belazo import encrypt_text as belazo_encrypt, decrypt_text as belazo_decrypt
from lab_2.Vizhenera import encrypt_text as vigenere_encrypt, decrypt_text as vigenere_decrypt
from lab_2.magma import encrypt_text as magma_encrypt, decrypt_text as magma_decrypt
from lab_3.matrix import (
    encrypt_text as matrix_encrypt_text,
    decrypt_text as matrix_decrypt_text,
)
from lab_3.playfer import (
    encrypt as playfair_encrypt,
    decrypt as playfair_decrypt,
    validate_key as playfair_validate_key,
    display_table as playfair_display_table,
)
from lab_4.vertical import encrypt as vertical_encrypt, decrypt as vertical_decrypt
from lab_4.feistel import encrypt as feistel_encrypt, split_key, check_params
from lab_4.cardano import encrypt_text as cardano_encrypt, decrypt_text as cardano_decrypt, run_cardano_gui
from lab_5.shenon import shenon, check_conditions
from lab_5.gost34_13_2015 import gamma_magma
from lab_6 import utils as lab6_utils
from lab_6.A5 import A5_1
from lab_6.A52 import A5_2
from lab_7.AES import AES_decryption, AES_encryption
from lab_7.auxilary import split_by as lab7_split_by
from lab_7.kuznechik import kuznechik_decrypt, kuznechik_encrypt, on_bytes, split_key as kuz_split_key
from lab_7.MagmA import magma_decrypt as gost_magma_decrypt_block
from lab_7.MagmA import magma_encrypt as gost_magma_encrypt_block
from lab_7.MagmA import pkcs7_pad, pkcs7_unpad
from lab_8.ECC import decrypt_text_ecc, encrypt_text_ecc
from lab_8.ElGamal import decryption as elgamal_decrypt_raw, encrypt_elgamal, tchk_zpt_back
from lab_8.RSA import des as rsa_decrypt_text, encrypt as rsa_encrypt_text


def _hex_only(s: str) -> str:
    return "".join(s.split()).lower()


def _validate_hex_key_len(key_hex: str, n: int, label: str) -> None:
    h = _hex_only(key_hex)
    if len(h) != n or any(c not in "0123456789abcdef" for c in h):
        raise ValueError(f"{label}: ровно {n} hex-символов (0–9, a–f).")


def _gost_magma_crypt(text: str, key_hex: str, encrypt: bool) -> str:
    """ГОСТ 28147-89 (Магма): блок 64 бит, ключ 256 бит, PKCS#7, UTF-8 для открытого текста."""
    _validate_hex_key_len(key_hex, 64, "Ключ")
    key_hex = _hex_only(key_hex)
    if encrypt:
        raw = text.encode("utf-8")
        raw_padded = pkcs7_pad(raw, 8)
        text_h = raw_padded.hex()
        block_list = lab7_split_by(text_h, 16)
        return "".join(
            hex(gost_magma_encrypt_block(b, key_hex))[2:].zfill(16) for b in block_list
        )
    ct = _hex_only(text)
    if len(ct) % 16 != 0:
        raise ValueError("Шифртекст: hex без пробелов, длина кратна 16 символам.")
    block_list = lab7_split_by(ct, 16)
    decoded_hex = "".join(
        hex(gost_magma_decrypt_block(b, key_hex))[2:].zfill(16) for b in block_list
    )
    plain = pkcs7_unpad(bytearray.fromhex(decoded_hex))
    return plain.decode("utf-8")


def _validate_binary_key_frame(key_str: str, frame_str: str) -> None:
    if len(key_str) != 64 or not all(c in "01" for c in key_str):
        raise ValueError("Ключ: ровно 64 символа 0 или 1.")
    if len(frame_str) != 22 or not all(c in "01" for c in frame_str):
        raise ValueError("Номер кадра: ровно 22 символа 0 или 1.")


def _a5_1_crypt(text: str, key_str: str, frame_str: str, encrypt: bool) -> str:
    """Шифртекст при encrypt=True — одна строка из 0/1 (bits_to_str), без правок lab_6/A5.py."""
    _validate_binary_key_frame(key_str, frame_str)
    key_bits = lab6_utils.str_to_bits(key_str)
    frame_bits = lab6_utils.str_to_bits(frame_str)
    if encrypt:
        text_bits = lab6_utils.text_to_bits(text)
        if not text_bits:
            raise ValueError("Нет допустимых букв (алфавит 32 буквы А–Я без Ё, без пробелов).")
        a5 = A5_1(key_bits, frame_bits)
        ks = a5.generate_keystream(len(text_bits))
        cipher_bits = [text_bits[i] ^ ks[i] for i in range(len(text_bits))]
        return lab6_utils.bits_to_str(cipher_bits)
    cipher_bits = lab6_utils.str_to_bits(text)
    if not cipher_bits:
        raise ValueError("Введите шифртекст как цепочку из 0 и 1 (пробелы можно).")
    if len(cipher_bits) % 5 != 0:
        raise ValueError("Длина шифртекста в битах должна быть кратна 5 (5 бит на букву).")
    a5 = A5_1(key_bits, frame_bits)
    ks = a5.generate_keystream(len(cipher_bits))
    plain_bits = [cipher_bits[i] ^ ks[i] for i in range(len(cipher_bits))]
    return lab6_utils.bits_to_text(plain_bits)


def _a5_2_crypt(text: str, key_str: str, frame_str: str, encrypt: bool) -> str:
    _validate_binary_key_frame(key_str, frame_str)
    key_bits = lab6_utils.str_to_bits(key_str)
    frame_bits = lab6_utils.str_to_bits(frame_str)
    if encrypt:
        text_bits = lab6_utils.text_to_bits(text)
        if not text_bits:
            raise ValueError("Нет допустимых букв (алфавит 32 буквы А–Я без Ё, без пробелов).")
        a52 = A5_2(key_bits, frame_bits)
        ks = a52.generate_keystream(len(text_bits))
        cipher_bits = [text_bits[i] ^ ks[i] for i in range(len(text_bits))]
        return lab6_utils.bits_to_str(cipher_bits)
    cipher_bits = lab6_utils.str_to_bits(text)
    if not cipher_bits:
        raise ValueError("Введите шифртекст как цепочку из 0 и 1 (пробелы можно).")
    if len(cipher_bits) % 5 != 0:
        raise ValueError("Длина шифртекста в битах должна быть кратна 5 (5 бит на букву).")
    a52 = A5_2(key_bits, frame_bits)
    ks = a52.generate_keystream(len(cipher_bits))
    plain_bits = [cipher_bits[i] ^ ks[i] for i in range(len(cipher_bits))]
    return lab6_utils.bits_to_text(plain_bits)


# Выводит в консоль главное меню программы: список доступных шифров (1–28) и пункт «Выход» (29), чтобы пользователь выбрал, каким алгоритмом шифровать или расшифровывать текст.
def show_main_menu():
    """Вывод главного меню выбора шифра (два столбца)."""
    print("Выберите шифр:")
    print(" 1. Шифр Атбаш          15. A5/1")
    print(" 2. Шифр Цезаря         16. A5/2")
    print(" 3. Квадрат Полибия     17. МАГМА")
    print(" 4. Шифр Тритемия       18. Шифр Шеннона")
    print(" 5. Шифр Белазо         19. ГОСТ 34.13-2015")
    print(" 6. Шифр Виженера       20. Кузнечик")
    print(" 7. Магма               21. AES")
    print(" 8. Матричный шифр      22. ElGamal")
    print(" 9. Шифр Плейфера       23. ECC")
    print("10. Вертикальная перест. 24. RSA")
    print("11. Решетка Кардано     25. ElGamal (подпись)")
    print("12. Сеть Фейстеля       26. ГОСТ 34.10-94")
    print("13. Одноразовый блокнот 27. ГОСТ 34.10-2012")
    print("14. Гаммирование        28. Диффи-Хеллман")
    print("                        29. Выход")
    print()


# Выводит подменю для выбранного шифра: зашифровать введённый текст, расшифровать введённый текст или вернуться к выбору другого шифра.
def show_action_menu(cipher_id=None):
    """Подменю: зашифровать / расшифровать / выход. Для шифра 11 (Кардано) добавлен пункт 4 — окно с решёткой."""
    print("Выберите действие:")
    print("1. Зашифровать текст")
    print("2. Расшифровать текст")
    if cipher_id == 11:
        print("4. Открыть окно с решёткой Кардано")
    print("3. Выход")
    print()

# По номеру шифра (cipher_id) и действию (1 — зашифровать, 2 — расшифровать) вызывает соответствующую функцию шифрования или расшифрования и передаёт ей текст; для нереализованных шифров возвращает None.
def run_cipher(cipher_id, action, text):
    """
    Вызов нужной функции шифрования или расшифрования по номеру шифра.
    cipher_id: 1-28, action: 1 или 2, text: строка для обработки.
    """
    if cipher_id == 1:
        if action == 1:
            return atbash_encrypt(text)
        else:
            return atbash_decrypt(text)
    if cipher_id == 2:
        if action == 1:
            return cesar_encrypt(text)
        else:
            return cesar_decrypt(text)
    if cipher_id == 3:
        if action == 1:
            return polybius_encrypt(text)
        else:
            return polybius_decrypt(text)
    if cipher_id == 4:
        if action == 1:
            return tritemi_encrypt(text)
        else:
            return tritemi_decrypt(text)
    if cipher_id == 5:
        if action == 1:
            return belazo_encrypt(text)
        else:
            return belazo_decrypt(text)
    if cipher_id == 6:
        if action == 1:
            return vigenere_encrypt(text)
        else:
            return vigenere_decrypt(text)
    if cipher_id == 7:
        if action == 1:
            return magma_encrypt(text)
        else:
            return magma_decrypt(text)
    if cipher_id == 8:
        if action == 1:
            return matrix_encrypt_text(text)
        else:
            return matrix_decrypt_text(text)
    if cipher_id == 9:
        key = input("Введите ключ Плэйфера: ").strip()
        valid, msg = playfair_validate_key(key)
        if not valid:
            raise ValueError(msg)
        playfair_display_table(key)
        if action == 1:
            return playfair_encrypt(text, key)
        else:
            return playfair_decrypt(text, key)
    if cipher_id == 10:
        key = input("Введите ключ: ").strip()
        if not key:
            raise ValueError("Ключ не может быть пустым")
        if action == 1:
            prepared = text.replace(" ", "прб").replace(",", "зпт").replace(".", "тчк").replace(":", "").replace(";", "").replace("!", "").replace("?", "").lower()
            return vertical_encrypt(prepared, key)
        else:
            return vertical_decrypt(text, key)
    if cipher_id == 11:
        if action == 1:
            cipher, orig_len = cardano_encrypt(text)
            print("Длина исходного текста (для расшифровки):", orig_len)
            return cipher
        else:
            try:
                orig_len_str = input("Введите длину исходного текста (после подготовки): ").strip()
                orig_len = int(orig_len_str) if orig_len_str else None
            except ValueError:
                orig_len = None
            return cardano_decrypt(text, orig_len)
    if cipher_id == 12:
        key = input("Введите ключ (64 hex-символа): ").strip()
        check_params(text, key)
        keys = split_key(key)
        if action == 1:
            return feistel_encrypt(text, keys)
        else:
            keys = list(keys)
            keys.reverse()
            return feistel_encrypt(text, keys)
    if cipher_id == 15:
        key = input("Введите 64-битный ключ (64 символа 0 и 1): ").strip()
        frame = input("Введите 22-битный номер кадра (22 символа 0 и 1): ").strip()
        return _a5_1_crypt(text, key, frame, encrypt=(action == 1))
    if cipher_id == 16:
        key = input("Введите 64-битный ключ (64 символа 0 и 1): ").strip()
        frame = input("Введите 22-битный номер кадра (22 символа 0 и 1): ").strip()
        return _a5_2_crypt(text, key, frame, encrypt=(action == 1))
    if cipher_id == 19:
        # Интерактивный режим ГОСТ 34.13-2015 (гаммирование Магма):
        # все параметры и вывод берутся из gamma_magma, текст здесь не используется.
        mode = "enc" if action == 1 else "dec"
        gamma_magma(mode)
        return None
    if cipher_id == 18:
        t0 = int(input("T0: ").strip())
        a = int(input("a: ").strip())
        c = int(input("c: ").strip())
        m = int(input("m: ").strip())
        if not check_conditions(a, c, m, t0):
            raise ValueError("не выполнены условия для генератора!")
        if action == 1:
            encrypted = shenon(text, t0, a, c, m)
            return ' '.join(encrypted)
        else:
            text_clean = text.replace(' ', '')
            decrypted = shenon(text_clean, t0, a, c, m, k=1)
            if decrypted and len(decrypted) == 1 and decrypted[0].startswith("Ошибка:"):
                raise ValueError(decrypted[0])
            return ''.join(decrypted) if decrypted else ''
    if cipher_id == 17:
        key = input("Введите 256-битный ключ (64 hex-символа): ").strip()
        return _gost_magma_crypt(text, key, encrypt=(action == 1))
    if cipher_id == 20:
        key_input = input("Введите ключ (64 hex-символа): ").strip()
        key = kuz_split_key(key_input, 32)
        msg = _hex_only(text)
        if action == 1:
            if len(msg) != 32:
                raise ValueError("Сообщение: ровно 32 hex-символа (128 бит блока).")
            shifr = kuznechik_encrypt(msg, key)
            return "".join(x[2:] for x in shifr)
        if len(msg) != 32:
            raise ValueError("Шифртекст: ровно 32 hex-символа.")
        shifr_bytes = on_bytes("0x" + msg)
        deshifr = kuznechik_decrypt(shifr_bytes, key)
        return "".join(x[2:] for x in deshifr)
    if cipher_id == 21:
        key_aes = input("Введите ключ AES (32 hex-символа, 128 бит): ").strip()
        th = _hex_only(text)
        if action == 1:
            if len(th) % 32 != 0:
                raise ValueError(
                    "Открытый текст: hex, длина кратна 32 символам (AES-128 по блокам)."
                )
            out = AES_encryption(th, key_aes, "Да")
        else:
            if len(th) % 32 != 0:
                raise ValueError("Шифртекст: hex, длина кратна 32 символам.")
            out = AES_decryption(th, key_aes, "Да")
        if isinstance(out, str) and out.startswith("Неверный"):
            raise ValueError(out)
        return out
    if cipher_id == 22:
        if action == 1:
            p = int(input("Введите p (простое число > 32): ").strip())
            g = int(input("Введите g (основание): ").strip())
            x = int(input("Введите секретный ключ x: ").strip())
            cipher, p_, g_, y = encrypt_elgamal(text, p, g, x)
            print(f"Открытый ключ: p={p_}, g={g_}, y={y}")
            return cipher
        p = int(input("Введите модуль p: ").strip())
        x = int(input("Введите секретный ключ x: ").strip())
        plain = elgamal_decrypt_raw(p, x, text)
        return tchk_zpt_back(plain)
    if cipher_id == 23:
        a = int(input("Введите параметр кривой a: ").strip())
        b = int(input("Введите параметр кривой b: ").strip())
        p_mod = int(input("Введите модуль p (простое): ").strip())
        if action == 1:
            g_line = input("Введите точку G как x,y: ").strip()
            gx, gy = [int(t.strip()) for t in g_line.split(",")]
            G = [gx, gy]
            cb = int(input("Введите закрытый ключ Cb: ").strip())
            k = int(input("Введите одноразовый ключ k: ").strip())
            return encrypt_text_ecc(text, a, b, p_mod, G, cb, k)
        cb = int(input("Введите закрытый ключ Cb: ").strip())
        return decrypt_text_ecc(text, a, b, p_mod, cb)
    if cipher_id == 24:
        if action == 1:
            n = int(input("Введите модуль n: ").strip())
            e = int(input("Введите открытую экспоненту e: ").strip())
            return rsa_encrypt_text(text, n, e)
        n = int(input("Введите модуль n: ").strip())
        d = int(input("Введите секретную экспоненту d: ").strip())
        return rsa_decrypt_text(text, n, d)

    return None


# Управляет диалогом с пользователем: показывает меню шифров, запрашивает выбор шифра и действие (шифрование/расшифрование), ввод текста, вызывает run_cipher и выводит результат; цикл повторяется до выбора «Выход».
def main():
    while True:
        show_main_menu()
        try:
            choice = input("Введите номер шифра (1-29): ").strip()
            n = int(choice)
        except ValueError:
            print("Введите число от 1 до 29.")
            print()
            continue

        if n == 29:
            print("Выход.")
            break

        if n < 1 or n > 28:
            print("Нет такого пункта. Введите 1-29.")
            print()
            continue

        while True:
            show_action_menu(n)
            try:
                action_str = input("Введите номер действия (1-3" + (", 4" if n == 11 else "") + "): ").strip()
                action = int(action_str)
            except ValueError:
                print("Введите число 1, 2 или 3" + (" или 4" if n == 11 else "") + ".")
                print()
                continue

            if action == 3:
                break

            if n == 11 and action == 4:
                run_cardano_gui()
                print()
                continue

            if action != 1 and action != 2:
                print("Введите 1, 2 или 3" + (" или 4" if n == 11 else "") + ".")
                print()
                continue
            
            # Для ГОСТ 34.13-2015 (пункт 19) текст вводится поблочно внутри gamma_magma,
            # поэтому здесь запрос не нужен.
            if n != 19:
                text = input("Введите текст для обработки: ").strip()
                if not text:
                    print("Текст не введён.")
                    print()
                    continue
            else:
                text = ""

            try:
                result = run_cipher(n, action, text)
                # Для ГОСТ 34.13-2015 вывод полностью делает gamma_magma.
                if n != 19:
                    if result is not None:
                        print("Результат:", result)
                    else:
                        print("Результат: Пока не реализовано.")
            except ValueError as e:
                print("Ошибка:", e)

            print()

    return


# Точка входа: при запуске файла как программы вызывается main() и запускается меню выбора шифров для шифрования и расшифрования текста.
if __name__ == "__main__":
    main()
