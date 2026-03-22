"""
Реализация поточного шифра A5/2 (ослабленная версия GSM).
Использует 4 регистра, нелинейный выход и управление тактированием от R4.
"""

try:
    from . import utils
except ImportError:
    import utils


class LFSR:
    """Аналогично LFSR из A5/1 (то же представление)."""

    def __init__(self, length: int, taps: list[int], state: list[int] = None):
        self.length = length
        self.taps = taps
        if state is None:
            self.state = [0] * length
        else:
            self.state = state.copy()

    def clock(self, feedback_bit: int = None) -> int:
        fb = 0
        for t in self.taps:
            fb ^= self.state[t]
        if feedback_bit is not None:
            fb ^= feedback_bit
        out = self.state[-1]
        self.state = [fb] + self.state[:-1]
        return out

    def get_bit(self, index: int) -> int:
        return self.state[index]

    def set_state(self, new_state: list[int]):
        self.state = new_state.copy()


class A5_2:
    """Реализация A5/2."""

    # Параметры регистров (длина, отводы для обратной связи)
    REG_PARAMS = [
        (19, [18, 17, 16, 13]),  # R1
        (22, [21, 20, 16, 7]),  # R2
        (23, [22, 21, 20, 7]),  # R3
        (17, [16, 11, 4]),  # R4: полином x^17 + x^12 + x^5 + 1
    ]
    # Биты R4, управляющие тактированием R1,R2,R3 (индексы от 0 младший)
    CLOCK_CONTROL_BITS = [3, 7, 10]  # для R1, R2, R3 соответственно
    # Индексы битов, участвующих в формировании выходного бита (по описанию из википедии)
    # majority1: R1[12], R2[15], R3[16]
    # majority2: R1[9],  R2[13], R3[18]
    # majority3: R1[15], R2[10], R3[11]
    MAJ1 = (12, 15, 16)  # индексы для первой мажоритарной функции
    MAJ2 = (9, 13, 18)  # для второй
    MAJ3 = (15, 10, 11)  # для третьей

    def __init__(self, key_bits: list[int], frame_bits: list[int]):
        assert len(key_bits) == 64
        assert len(frame_bits) == 22

        self.regs = []
        for length, taps in self.REG_PARAMS:
            self.regs.append(LFSR(length, taps))

        # Инициализация ключом (все регистры тактируются принудительно)
        for i in range(64):
            bit = key_bits[i]
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # Инициализация номером кадра
        for i in range(22):
            bit = frame_bits[i]
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # 100 холостых тактов с нерегулярным тактированием (управление от R4)
        for _ in range(100):
            self._clock_controlled()

    def _clock_controlled(self) -> int:
        """
        Выполняет один такт с управлением от R4.
        R4 тактируется всегда.
        R1,R2,R3 тактируются, если соответствующий управляющий бит R4 равен 1.
        Возвращает выходной бит системы (до сдвига), вычисленный по нелинейной функции.
        """
        r1, r2, r3, r4 = self.regs

        # Сохраняем значения битов для выходной функции (до сдвига)
        # (используются текущие состояния, не учитывая будущий сдвиг R4)
        bits_r1 = [r1.get_bit(i) for i in range(r1.length)]
        bits_r2 = [r2.get_bit(i) for i in range(r2.length)]
        bits_r3 = [r3.get_bit(i) for i in range(r3.length)]
        bits_r4 = [r4.get_bit(i) for i in range(r4.length)]

        # Определяем, какие из R1,R2,R3 будут тактироваться (на основе текущих битов R4)
        clock_r1 = bits_r4[self.CLOCK_CONTROL_BITS[0]]
        clock_r2 = bits_r4[self.CLOCK_CONTROL_BITS[1]]
        clock_r3 = bits_r4[self.CLOCK_CONTROL_BITS[2]]

        # Тактируем R4 (всегда)
        r4.clock()

        # Тактируем R1,R2,R3 в соответствии с управляющими битами
        # Важно: при тактировании мы используем текущие состояния (до сдвига R4),
        # но R4 уже сдвинут? Порядок может влиять. В стандарте A5/2 сначала тактируют R4,
        # а затем, используя его СТАРЫЕ управляющие биты, тактируют остальные.
        # Мы уже сохранили старые биты R4 в clock_r1,... и сдвинули R4.
        # Теперь тактируем R1,R2,R3 с их собственными отводами, но без внешнего feedback.
        if clock_r1:
            r1.clock()
        if clock_r2:
            r2.clock()
        if clock_r3:
            r3.clock()

        # Вычисляем выходной бит по трём мажоритарным функциям (используем старые биты регистров)
        def majority(a, b, c):
            return (a & b) | (a & c) | (b & c)

        m1 = majority(
            bits_r1[self.MAJ1[0]], bits_r2[self.MAJ1[1]], bits_r3[self.MAJ1[2]]
        )
        m2 = majority(
            bits_r1[self.MAJ2[0]], bits_r2[self.MAJ2[1]], bits_r3[self.MAJ2[2]]
        )
        m3 = majority(
            bits_r1[self.MAJ3[0]], bits_r2[self.MAJ3[1]], bits_r3[self.MAJ3[2]]
        )

        return m1 ^ m2 ^ m3

    def generate_keystream(self, n_bits: int) -> list[int]:
        keystream = []
        for _ in range(n_bits):
            keystream.append(self._clock_controlled())
        return keystream


def encrypt_decrypt(text: str, key_str: str, frame_str: str) -> str:
    """Шифрование/расшифрование текста с A5/2."""
    key_bits = utils.str_to_bits(key_str)
    frame_bits = utils.str_to_bits(frame_str)
    text_bits = utils.text_to_bits(text)

    a5 = A5_2(key_bits, frame_bits)
    keystream = a5.generate_keystream(len(text_bits))

    cipher_bits = [text_bits[i] ^ keystream[i] for i in range(len(text_bits))]
    return utils.bits_to_text(cipher_bits)


def main():
    print("=== A5/2 Шифрование/расшифрование (русский текст, 32 буквы) ===")
    choice = input("Выберите действие (1 - зашифровать, 2 - расшифровать): ").strip()
    if choice not in ("1", "2"):
        print("Неверный выбор.")
        return

    text = input("Введите текст: ").strip()
    key = input("Введите 64-битный ключ (последовательность 0 и 1): ").strip()
    frame = input("Введите 22-битный номер кадра (последовательность 0 и 1): ").strip()

    if len(key) != 64 or not all(c in "01" for c in key):
        print("Ошибка: ключ должен быть ровно 64 бита.")
        return
    if len(frame) != 22 or not all(c in "01" for c in frame):
        print("Ошибка: номер кадра должен быть ровно 22 бита.")
        return

    result = encrypt_decrypt(text, key, frame)
    if choice == "1":
        print("Зашифрованный текст:", result)
    else:
        print("Расшифрованный текст:", result)


if __name__ == "__main__":
    main()
