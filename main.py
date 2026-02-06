# Итоговая программа: меню выбора шифров.
# Содержит только импорт функций из папок lab_1, lab_2, ... и их использование.

from lab_1.atbash import encrypt_text as atbash_encrypt, decrypt_text as atbash_decrypt


def show_main_menu():
    """Вывод главного меню выбора шифра (два столбца)."""
    print("Выберите шифр:")
    print(" 1. Шифр Атбаш          15. A5/1")
    print(" 2. Шифр Цезаря         16. A5/2")
    print(" 3. Квадрат Полибия     17. МАГМА")
    print(" 4. Шифр Тритемия       19. AES")
    print(" 5. Шифр Белазо         20. Кузнечик")
    print(" 6. Шифр Виженера       21. RSA")
    print(" 7. Магма               22. ElGamal")
    print(" 8. Матричный шифр      23. ECC")
    print(" 9. Шифр Плейфера       24. RSA (подпись)")
    print("10. Вертикальная перест. 25. ElGamal (подпись)")
    print("11. Решетка Кардано     26. ГОСТ 34.10-94")
    print("12. Сеть Фейстеля       27. ГОСТ 34.10-2012")
    print("13. Одноразовый блокнот 28. Диффи-Хеллман")
    print("14. Гаммирование        29. Выход")
    print()


def show_action_menu():
    """Подменю: зашифровать / расшифровать / выход."""
    print("Выберите действие:")
    print("1. Зашифровать текст")
    print("2. Расшифровать текст")
    print("3. Выход")
    print()

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
    # Остальные шифры пока не подключены
    return None


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

        # Подменю для выбранного шифра
        while True:
            show_action_menu()
            try:
                action_str = input("Введите номер действия (1-3): ").strip()
                action = int(action_str)
            except ValueError:
                print("Введите число 1, 2 или 3.")
                print()
                continue

            if action == 3:
                break

            if action != 1 and action != 2:
                print("Введите 1, 2 или 3.")
                print()
                continue

            text = input("Введите текст для обработки: ").strip()
            if not text:
                print("Текст не введён.")
                print()
                continue

            result = run_cipher(n, action, text)
            if result is not None:
                print("Результат:", result)
            else:
                print("Результат: Пока не реализовано.")

            print()

    return


if __name__ == "__main__":
    main()
