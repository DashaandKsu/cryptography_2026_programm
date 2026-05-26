"""
Реализация поточного шифра A5/1 (GSM).
Основан на трёх регистрах сдвига с нерегулярным тактированием.
"""

try:
    from . import utils
except ImportError:
    import utils


class LFSR:
    """Регистр сдвига с линейной обратной связью (LFSR).

    Состояние хранится как список битов от младшего (индекс 0)
    к старшему (индекс length-1). При сдвиге:
      - старший бит (последний) выдаётся как выходной
      - новый бит (результат XOR по отводам) становится младшим (индекс 0)
    """

    def __init__(self, length: int, taps: list[int], state: list[int] = None):
        self.length = length
        self.taps = taps
        if state is None:
            self.state = [0] * length
        else:
            assert len(state) == length, "Неверная длина состояния"
            self.state = state.copy()

    def clock(self, feedback_bit: int = None) -> int:
        """
        Выполняет один такт регистра.
        Если feedback_bit задан, он XOR-ится с обратной связью по отводам
        и записывается в младший разряд.
        Возвращает выходной бит (старший бит ДО сдвига).
        """
        fb = 0
        for t in self.taps:
            fb ^= self.state[t]
        if feedback_bit is not None:
            fb ^= feedback_bit
        out = self.state[-1]
        self.state = [fb] + self.state[:-1]
        return out

    def get_bit(self, index: int) -> int:
        """Возвращает значение бита по индексу (0 = младший)."""
        return self.state[index]

    def set_state(self, new_state: list[int]):
        """Устанавливает новое состояние."""
        assert len(new_state) == self.length
        self.state = new_state.copy()


class A5_1:
    """Реализация шифра A5/1."""

    # Параметры регистров (длина, отводы для обратной связи)
    # Многочлены согласно методичке:
    REG_PARAMS = [
        (19, [18, 17, 16, 13]),   # R1: x^19 + x^18 + x^17 + x^14 + 1
        (22, [21, 20]),           # R2: x^22 + x^21 + 1
        (23, [22, 21, 20, 7]),    # R3: x^23 + x^22 + x^21 + x^8 + 1
    ]
    # Индексы битов, управляющих тактированием
    CLOCK_BITS = [8, 10, 10]  # для R1, R2, R3 (0 = младший)

    def __init__(self, key_bits: list[int], frame_bits: list[int]):
        """
        key_bits   : 64 бита ключа (первый элемент = старший бит ключа)
        frame_bits : 22 бита номера кадра (первый = старший бит)

        ВАЖНО: в A5/1 биты ключа и кадра подаются в регистры
        от младшего к старшему (LSB first). Поэтому мы итерируем
        списки в обратном порядке.
        """
        assert len(key_bits) == 64, "Ключ должен быть 64 бита"
        assert len(frame_bits) == 22, "Номер кадра должен быть 22 бита"

        # Создаём три регистра, начальное состояние - все нули
        self.regs = []
        for length, taps in self.REG_PARAMS:
            self.regs.append(LFSR(length, taps))

        # Фаза 1: инициализация ключом (64 такта, все регистры тактируются)
        # Биты подаются от младшего к старшему (LSB first).
        for i in range(63, -1, -1):
            bit = key_bits[i]
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # Фаза 2: инициализация номером кадра (22 такта, все регистры тактируются)
        # Биты подаются от младшего к старшему.
        for i in range(21, -1, -1):
            bit = frame_bits[i]
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # Фаза 3: 100 холостых тактов с мажоритарным тактированием
        for _ in range(100):
            self._clock_majority()

    def _majority(self) -> int:
        """Возвращает мажоритарное значение трёх тактовых битов."""
        bits = [reg.get_bit(self.CLOCK_BITS[i]) for i, reg in enumerate(self.regs)]
        return 1 if sum(bits) >= 2 else 0

    def _clock_majority(self) -> int:
        """
        Один такт с мажоритарным тактированием.
        Сначала выполняется сдвиг тех регистров, у которых тактовый бит
        совпал с мажоритарным значением. Затем выходной бит системы
        формируется как XOR старших битов всех трёх регистров ПОСЛЕ сдвига.
        """
        maj = self._majority()
        for i, reg in enumerate(self.regs):
            if reg.get_bit(self.CLOCK_BITS[i]) == maj:
                reg.clock()
        # Выход = XOR старших битов ПОСЛЕ сдвига
        return (self.regs[0].state[-1]
                ^ self.regs[1].state[-1]
                ^ self.regs[2].state[-1])

    def generate_keystream(self, n_bits: int) -> list[int]:
        """Генерирует n_bits бит ключевого потока."""
        return [self._clock_majority() for _ in range(n_bits)]


def encrypt_decrypt(text: str, key_text: str, frame_number: int) -> str:
    """
    Шифрование (и расшифрование) русского текста с помощью A5/1.
    key_text     : ключ как текст по алфавиту utils.ALPHABET → 64 бита
    frame_number : номер кадра 0..2^22-1
    """
    key_bits = utils.key_text_to_bits(key_text, 64)
    frame_bits = utils.frame_decimal_to_bits(frame_number, 22)
    text_bits = utils.text_to_bits(text)

    a5 = A5_1(key_bits, frame_bits)
    keystream = a5.generate_keystream(len(text_bits))

    cipher_bits = [text_bits[i] ^ keystream[i] for i in range(len(text_bits))]

    return utils.bits_to_text(cipher_bits)


def main():
    print("=== A5/1 Шифрование/расшифрование (русский текст, 32 буквы) ===")
    choice = input("Выберите действие (1 - зашифровать, 2 - расшифровать): ").strip()
    if choice not in ("1", "2"):
        print("Неверный выбор.")
        return

    text = input("Введите текст: ").strip()
    key = input(
        "Введите ключ (текст, буквы алфавита АБВ…Я; 5 бит на букву, до 13 букв): "
    ).strip()
    frame_raw = input(
        "Введите номер кадра (целое число 0..4194303, 22 бита): "
    ).strip()

    try:
        frame_num = int(frame_raw, 10)
    except ValueError:
        print("Ошибка: номер кадра должен быть целым числом в десятичной записи.")
        return
    try:
        utils.frame_decimal_to_bits(frame_num, 22)
    except ValueError as e:
        print("Ошибка:", e)
        return

    result = encrypt_decrypt(text, key, frame_num)
    if choice == "1":
        print("Зашифрованный текст:", result)
    else:
        print("Расшифрованный текст:", result)


#if __name__ == "__main__":
    #main()



def test_with_table():
    """Проверка совпадения с таблицей Excel. Ключ вводится в hex, кадр в десятичном."""
    print("\n=== Режим проверки с таблицей (ручной ввод) ===")
    key_hex = input("Введите ключ в hex (16 цифр, пример 123456789ABCDEF0): ").strip()
    frame_num = int(input("Введите номер кадра (десятичное, пример 0): ").strip())
    plain_text = input("Введите открытый текст (русские буквы, пример луч): ").strip()

    # Ключ hex → 64 бита MSB first
    key_int = int(key_hex, 16)
    key_bits = [(key_int >> (63 - i)) & 1 for i in range(64)]

    # Кадр → 22 бита
    frame_bits = utils.frame_decimal_to_bits(frame_num, 22)
ы
    # Открытый текст → биты
    text_bits = utils.text_to_bits(plain_text)

    # Шифруем
    a5 = A5_1(key_bits, frame_bits)
    gamma = a5.generate_keystream(len(text_bits))
    cipher_bits = [t ^ g for t, g in zip(text_bits, gamma)]

    # Выводим подробно
    print(f"\nКлюч в hex:        {key_hex.upper()}")
    print(f"Кадр (dec):        {frame_num}")
    print(f"Открытый текст:    {plain_text.upper()}")
    print(f"Текст в битах:     {''.join(map(str, text_bits))}")
    print(f"Гамма:             {''.join(map(str, gamma))}")
    print(f"Шифр в битах:      {''.join(map(str, cipher_bits))}")
    print(f"Шифр как текст:    {utils.bits_to_text(cipher_bits)}")


if __name__ == "__main__":
    test_with_table()