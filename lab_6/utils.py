"""Вспомогательные функции для работы с русским текстом и 5-битным кодированием"""

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
# 32 буквы, индекс от 0 до 31, кодируется 5 битами


def text_to_bits(text: str) -> list[int]:
    """
    Преобразует русский текст в список битов (длина кратна 5).
    Пробелы удаляются, буква 'Ё' не поддерживается (будет пропущена).
    """
    # Удаляем пробелы и переводим в верхний регистр
    clean = "".join(text.split()).upper()
    bits = []
    for ch in clean:
        if ch in ALPHABET:
            idx = ALPHABET.index(ch)  # число от 0 до 31
            # Превращаем число в 5 бит (старший бит первый)
            for i in range(4, -1, -1):
                bits.append((idx >> i) & 1)
    return bits


def bits_to_text(bits: list[int]) -> str:
    """
    Преобразует список битов (длина кратна 5) обратно в русский текст.
    Если в конце есть неполный блок, он игнорируется.
    """
    chars = []
    for i in range(0, len(bits), 5):
        if i + 5 > len(bits):
            break
        # Собираем 5 бит в число (старший бит первый)
        idx = 0
        for j in range(5):
            idx = (idx << 1) | bits[i + j]
        if idx < len(ALPHABET):
            chars.append(ALPHABET[idx])
    return "".join(chars)


def str_to_bits(s: str) -> list[int]:
    """Преобразует строку из '0' и '1' в список целых 0/1."""
    return [int(c) for c in s if c in "01"]


def bits_to_str(bits: list[int]) -> str:
    """Преобразует список битов в строку вида '0101'."""
    return "".join(str(b) for b in bits)
