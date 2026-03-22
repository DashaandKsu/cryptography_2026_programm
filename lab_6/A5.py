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
    к старшему (индекс length-1). При сдвиге влево:
      - старший бит (последний) выдаётся как выходной
      - новый бит (результат XOR по отводам) становится младшим (индекс 0)
    """

    def __init__(self, length: int, taps: list[int], state: list[int] = None):
        """
        length   : длина регистра (количество битов)
        taps     : список индексов битов (0 = младший), участвующих в обратной связи
        state    : начальное состояние (список 0/1) или None (заполнить нулями)
        """
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
        Если feedback_bit задан, он используется как новый бит (XOR с обратной связью).
        Иначе новый бит вычисляется только по отводам.
        Возвращает выходной бит (старший бит ДО сдвига).
        """
        # вычисляем бит обратной связи по отводам
        fb = 0
        for t in self.taps:
            fb ^= self.state[t]

        # если подан внешний бит, добавляем его
        if feedback_bit is not None:
            fb ^= feedback_bit

        # запоминаем выходной бит (старший)
        out = self.state[-1]

        # сдвиг: все биты смещаются в сторону старших, младшим становится fb
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
    REG_PARAMS = [
        (19, [18, 17, 16, 13]),  # R1: полином x^19 + x^18 + x^17 + x^14 + 1
        (22, [21, 20, 16, 7]),  # R2: полином x^22 + x^21 + x^17 + x^8 + 1
        (23, [22, 21, 20, 7]),  # R3: полином x^23 + x^22 + x^21 + x^8 + 1
    ]
    # Индексы битов, управляющих тактированием (clocking bits)
    CLOCK_BITS = [8, 10, 10]  # для R1, R2, R3 (0 = младший)

    def __init__(self, key_bits: list[int], frame_bits: list[int]):
        """
        key_bits   : 64 бита ключа (список 0/1, первый элемент = старший бит ключа)
        frame_bits : 22 бита номера кадра (список 0/1, первый = старший)
        """
        assert len(key_bits) == 64, "Ключ должен быть 64 бита"
        assert len(frame_bits) == 22, "Номер кадра должен быть 22 бита"

        # Создаём три регистра, начальное состояние – все нули
        self.regs = []
        for length, taps in self.REG_PARAMS:
            self.regs.append(LFSR(length, taps))

        # Инициализация ключом
        for i in range(64):
            bit = key_bits[i]  # здесь i идёт по порядку (0 = старший бит ключа)
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # Инициализация номером кадра
        for i in range(22):
            bit = frame_bits[i]
            for reg in self.regs:
                reg.clock(feedback_bit=bit)

        # 100 холостых тактов с мажоритарным тактированием (без выхода)
        for _ in range(100):
            self._clock_majority()

    def _majority(self) -> int:
        """Возвращает мажоритарное значение трёх тактовых битов."""
        bits = [reg.get_bit(self.CLOCK_BITS[i]) for i, reg in enumerate(self.regs)]
        return 1 if sum(bits) >= 2 else 0

    def _clock_majority(self) -> int:
        """
        Выполняет один такт с мажоритарным тактированием.
        Возвращает выходной бит (XOR старших битов всех регистров после сдвига? нет,
        стандарт A5/1 выдаёт бит ДО сдвига. Здесь будем возвращать выходной бит ДО сдвига.)
        """
        maj = self._majority()
        out_bits = []
        for i, reg in enumerate(self.regs):
            # регистр тактируется, если его тактовый бит совпадает с мажоритарным
            if reg.get_bit(self.CLOCK_BITS[i]) == maj:
                out_bits.append(reg.clock())  # clock() возвращает выходной бит
            else:
                # если не тактируется, просто запоминаем текущий старший бит (он останется)
                out_bits.append(reg.get_bit(reg.length - 1))
        # Выходной бит системы = XOR старших битов всех трёх регистров (после тактирования? нет, стандарт: XOR битов, которые были старшими ДО такта? Обычно выход формируется из старших битов ПОСЛЕ сдвига? В литературе: берутся старшие биты регистров, затем выполняется такт, затем выход = XOR этих трёх битов? Разные источники дают разную последовательность. Проверим по известной реализации: обычно сначала снимают выходной бит (XOR старших битов текущего состояния), потом выполняют тактирование. В спецификации GSM 03.20 сказано: на каждом шаге, когда генерируется ключевой поток, выходной бит равен XOR трёх старших битов регистров (до сдвига). Примем этот вариант.)
        # Однако в нашем методе clock() возвращает выходной бит (старший до сдвига) для каждого регистра.
        # Если регистр не тактировался, его старший бит остался тем же, что и до такта.
        # Поэтому мы можем просто взять out_bits (которые мы собрали) и сложить их по XOR.
        # Но out_bits[i] – это старший бит i-го регистра именно до выполнения такта (для тактировавшихся это бит, который ушёл, для не тактировавшихся – тот же бит).
        # Таким образом, XOR этих трёх значений даст выходной бит системы.
        return out_bits[0] ^ out_bits[1] ^ out_bits[2]

    def generate_keystream(self, n_bits: int) -> list[int]:
        """Генерирует n_bits бит ключевого потока."""
        keystream = []
        for _ in range(n_bits):
            keystream.append(self._clock_majority())
        return keystream


def encrypt_decrypt(text: str, key_str: str, frame_str: str) -> str:
    """
    Шифрование (и расшифрование) русского текста с помощью A5/1.
    key_str   : строка из 64 символов '0'/'1' (старший бит первый)
    frame_str : строка из 22 символов '0'/'1' (старший бит первый)
    """
    # Преобразуем входные данные в биты
    key_bits = utils.str_to_bits(key_str)
    frame_bits = utils.str_to_bits(frame_str)
    text_bits = utils.text_to_bits(text)

    # Создаём экземпляр шифра и генерируем ключевой поток
    a5 = A5_1(key_bits, frame_bits)
    keystream = a5.generate_keystream(len(text_bits))

    # XOR
    cipher_bits = [text_bits[i] ^ keystream[i] for i in range(len(text_bits))]

    # Обратно в текст
    return utils.bits_to_text(cipher_bits)


def main():
    print("=== A5/1 Шифрование/расшифрование (русский текст, 32 буквы) ===")
    choice = input("Выберите действие (1 - зашифровать, 2 - расшифровать): ").strip()
    if choice not in ("1", "2"):
        print("Неверный выбор.")
        return

    text = input("Введите текст: ").strip()
    key = input("Введите 64-битный ключ (последовательность 0 и 1): ").strip()
    frame = input("Введите 22-битный номер кадра (последовательность 0 и 1): ").strip()

    if len(key) != 64 or not all(c in "01" for c in key):
        print("Ошибка: ключ должен быть ровно 64 бита и состоять из 0 и 1.")
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

#Реализован тот же принцип (гаммирование по A5), но выбрана 
# другая оцифровка текста и формат вывода