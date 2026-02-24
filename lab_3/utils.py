# Общие утилиты для шифров lab_3 (матричный шифр, Плэйфер)

import random
from fractions import Fraction

# =========================== UTILS ==========================
RUS_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def letter_to_index(letter: str) -> int:
    return RUS_ALPHABET.index(letter)


def index_to_letter(idx: int) -> str:
    return RUS_ALPHABET[idx % 32]


def prepare_text(text: str) -> str:
    text = text.upper().replace("Ё", "Е")
    return "".join(ch for ch in text if ch in RUS_ALPHABET)


def merge_similar_letters(text: str) -> str:
    text = text.replace("Й", "И").replace("Ё", "Е").replace("Ь", "Ъ")
    return text
