# Итоговая программа: меню выбора шифров.
# Импорты из lab_1 … lab_9 и единый терминальный сценарий (как при запуске исходных файлов).

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
from lab_6.A5 import encrypt_decrypt as a5_encrypt_decrypt
from lab_6.A52 import encrypt_decrypt as a52_encrypt_decrypt
from lab_7.AES import AES_decryption, AES_encryption
from lab_7.auxilary import split_by as lab7_split_by
from lab_7.kuznechik import kuznechik_decrypt, kuznechik_encrypt, on_bytes, split_key as kuz_split_key
from lab_7.MagmA import magma_decrypt as gost_magma_decrypt_block
from lab_7.MagmA import magma_encrypt as gost_magma_encrypt_block
from lab_7.MagmA import pkcs7_pad, pkcs7_unpad
from lab_8.ECC import decrypt_text_ecc, encrypt_text_ecc
from lab_8.ElGamal import decryption as elgamal_decrypt_raw, encrypt_elgamal, tchk_zpt_back
from lab_8.RSA import des as rsa_decrypt_text, encrypt as rsa_encrypt_text
from lab_8.ECC_codirovanie import main as ecc_codirovanie_main
from lab_9 import ElGamal_CP as elgamal_cp
from lab_9 import RSA_CP as rsa_cp


class _AlreadyPrinted:
    """Результат: весь вывод уже сделан внутри run_cipher (подписи, ГОСТ 34.13 и т.д.)."""


ALREADY_PRINTED = _AlreadyPrinted()


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


# Выводит в консоль главное меню программы: список доступных шифров и пункт «Выход».
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
    print("12. Сеть Фейстеля       26. RSA (цифровая подпись)")
    print("13. Одноразовый блокнот 27. ECC: кодирование текста")
    print("14. Гаммирование        28. ГОСТ 34.10-94")
    print("                        29. ГОСТ 34.10-2012")
    print("                        30. Диффи-Хеллман")
    print("                        31. Выход")
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
    cipher_id: 1-30 (и служебные сценарии), action: 1 или 2, text: строка для обработки.
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
        # Как в lab_6/A5.py: ключ — текст по алфавиту, кадр — десятичное 0..4194303.
        key = input(
            "Введите ключ (текст, буквы алфавита АБВ…Я; кодируется в 64 бита по 5 бит на букву): "
        ).strip()
        frame_raw = input(
            "Введите номер кадра (целое десятичное число 0..4194303, 22 бита): "
        ).strip()
        try:
            frame_num = int(frame_raw, 10)
        except ValueError:
            raise ValueError(
                "Ошибка: номер кадра должен быть целым числом в десятичной записи."
            ) from None
        try:
            lab6_utils.frame_decimal_to_bits(frame_num, 22)
        except ValueError as e:
            raise ValueError(str(e)) from None
        return a5_encrypt_decrypt(text, key, frame_num)
    if cipher_id == 16:
        key = input(
            "Введите ключ (текст, буквы алфавита АБВ…Я; кодируется в 64 бита по 5 бит на букву): "
        ).strip()
        if not lab6_utils.text_to_bits(key):
            raise ValueError(
                "Ошибка: в ключе нет букв из алфавита (32 буквы АБВ…Я)."
            )
        frame_raw = input(
            "Введите номер кадра (целое десятичное число 0..4194303, 22 бита): "
        ).strip()
        try:
            frame_num = int(frame_raw, 10)
        except ValueError:
            raise ValueError(
                "Ошибка: номер кадра должен быть целым числом в десятичной записи."
            ) from None
        try:
            lab6_utils.frame_decimal_to_bits(frame_num, 22)
        except ValueError as e:
            raise ValueError(str(e)) from None
        return a52_encrypt_decrypt(text, key, frame_num)
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

    if cipher_id == 25:
        # lab_9/ElGamal_CP.py — те же запросы, что в интерактивном main().
        if action == 1:
            P = int(input("Введите простое число P > 32: ").strip())
            if not elgamal_cp.is_prime(P):
                print("Ошибка: P должно быть простым числом!")
                return ALREADY_PRINTED
            G = int(input("Введите G (1 < G < P): ").strip())
            if G <= 1 or G >= P:
                print("Ошибка: G должно быть в диапазоне (1, P)")
                return ALREADY_PRINTED
            X = int(input(f"Введите секретный ключ X (1 < X < {P - 1}): ").strip())
            if not (1 < X < P - 1):
                print("Ошибка: X вне диапазона")
                return ALREADY_PRINTED
            plain = input("Введите текст для подписи: ")
            plain = elgamal_cp.tchk_zpt(plain)
            result = elgamal_cp.encryption(P, G, X, plain)
            if result:
                a, b, Y, G_ = result
                print(f"Подпись: ({a},{b})")
                print(f"Открытый ключ: Y = {Y}, G = {G_}, P = {P}")
            return ALREADY_PRINTED
        plain = input("Введите текст для проверки подписи: ")
        plain = elgamal_cp.tchk_zpt(plain)
        elgamal_cp.decryption(plain)
        return ALREADY_PRINTED

    if cipher_id == 26:
        if action == 1:
            rsa_cp.create_signature()
        else:
            rsa_cp.check_signature()
        return ALREADY_PRINTED

    return None


# Управляет диалогом с пользователем: показывает меню шифров, запрашивает выбор шифра и действие (шифрование/расшифрование), ввод текста, вызывает run_cipher и выводит результат; цикл повторяется до выбора «Выход».
def main():
    while True:
        show_main_menu()
        try:
            choice = input("Введите номер шифра (1-31): ").strip()
            n = int(choice)
        except ValueError:
            print("Введите число от 1 до 31.")
            print()
            continue

        if n == 31:
            print("Выход.")
            break

        if n < 1 or n > 30:
            print("Нет такого пункта. Введите 1-31.")
            print()
            continue

        # lab_8/ECC_codirovanie.py — один прогон, как при прямом запуске файла.
        if n == 27:
            try:
                ecc_codirovanie_main()
            except SystemExit:
                raise
            except Exception as e:
                print("Ошибка:", e)
            print()
            continue

        if n in (28, 29, 30):
            print(
                "В каталоге проекта нет отдельного скрипта для этого пункта "
                "(ожидаются лабораторные файлы ГОСТ 34.10 / Диффи-Хеллман)."
            )
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

            skip_global_text = n in (25, 26)
            # Для ГОСТ 34.13-2015 (пункт 19) текст вводится поблочно внутри gamma_magma.
            if n != 19 and not skip_global_text:
                text = input("Введите текст для обработки: ").strip()
                if not text:
                    print("Текст не введён.")
                    print()
                    continue
            else:
                text = ""

            try:
                result = run_cipher(n, action, text)
                if n == 19:
                    pass
                elif result is ALREADY_PRINTED:
                    pass
                elif n in (15, 16):
                    if action == 1:
                        print("Зашифрованный текст:", result)
                    else:
                        print("Расшифрованный текст:", result)
                elif n == 20:
                    if action == 1:
                        print("SHIFR =", result)
                    else:
                        print("DESHIFR =", result)
                elif result is not None:
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
