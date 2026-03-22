from pathlib import Path

try:
    from lab_7.auxilary import split_by, show_by, CODECS
    from lab_7.TaskMenu import getline
except ModuleNotFoundError:
    from auxilary import split_by, show_by, CODECS
    from TaskMenu import getline

# Путь к sample_text.txt рядом с этим скриптом (работает при запуске из любой папки)
_LAB_DIR = Path(__file__).resolve().parent
SAMPLE_TEXT_FILE = _LAB_DIR / 'sample_text.txt'

body = [['c', '4', '6', '2', 'a', '5', 'b', '9', 'e', '8', 'd', '7', '0', '3', 'f', '1'],
    ['6', '8', '2', '3', '9', 'a', '5', 'c', '1', 'e', '4', '7', 'b', 'd', '0', 'f'],
    ['b', '3', '5', '8', '2', 'f', 'a', 'd', 'e', '1', '7', '4', 'c', '9', '6', '0'],
    ['c', '8', '2', '1', 'd', '4', 'f', '6', '7', '0', 'a', '5', '3', 'e', '9', 'b'],
    ['7', 'f', '5', 'a', '8', '1', '6', 'd', '0', '9', '3', 'e', 'b', '4', '2', 'c'],
    ['5', 'd', 'f', '6', '9', '2', 'c', 'a', 'b', '7', '8', '1', '4', '3', 'e', '0'],
    ['8', 'e', '2', '5', '6', '9', '1', 'c', 'f', '4', 'b', '0', 'd', 'a', '3', '7'],
    ['1', '7', 'e', 'd', '0', '5', '8', '3', '4', 'f', 'a', '6', '9', 'c', 'b', '2']]

key = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
mask32 = 2 ** 32 - 1
selected_codec = CODECS[2]

def keys(int256):
    int256 = to_int(int256)
    container = []
    for i in reversed(range(8)):
        container.append((int256 >> (32 * i)) & mask32)
    container += container * 2 + list(reversed(container))
    return container

"""Разбивает 256-битный ключ на восемь 32-битных подклёчей и создаёт расширенную последовательность подклёчей."""

def to_int(x):
    if isinstance(x, int):
        return x
    return int(x, 16)

def t(int32):
    y = 0
    for i in reversed(range(8)):
        j = (int32 >> 4 * i) & 0xf
        y <<= 4
        y ^= int(body[i][j], 16)
    return y

"""Реализует подстановку по таблице S-блока"""

def shift11(int32):
    return ((int32 << 11) ^ (int32 >> (32 - 11))) & mask32

"""Выполняет циклический сдвиг на 11 бит влево XOR операцией"""

def g(i32, k32):
    i32, k32 = to_int(i32), to_int(k32)
    return shift11(t(i32 + k32) % 2 ** 32)

"""Комбинация подстановки"""

def split_by_32(int64):
    int64 = to_int(int64)
    left = int64 >> 32
    right = int64 & mask32
    return left, right

def join_32(left, right):
    left = to_int(left)
    right = to_int(right)
    return (left << 32) ^ right

"""Управляют разделением и объединением 64-битных блоков на две 32-битные части"""

def magma_encrypt(plaintext, source_key):
    container = keys(source_key)
    (left, right) = split_by_32(plaintext)
    for i in range(31):
        (left, right) = (right, left ^ g(right, container[i]))
    return join_32(left ^ g(right, hex(container[-1])), right)

"""Реализует сам процесс шифрования через 31 раунд операций XOR и замены"""

def magma_decrypt(plaintext, source_key):
    container = keys(source_key)
    container.reverse()
    (left, right) = split_by_32(plaintext)
    for i in range(31):
        (left, right) = (right, left ^ g(right, container[i]))
    return join_32(left ^ g(right, hex(container[-1])), right)

"""Осуществляет обратный процесс дешифрования, используя подключи в обратном порядке"""

def _magma(block, s_key, mode='enc', verbose=True):
    if mode == 'enc':
        if verbose:
            print(f"In:  {block}, len_block={len(block)}")
        res = hex(magma_encrypt(block, s_key))[2:]
        res = res.zfill(16)
        if verbose:
            print(f"Out: {res}, len_block={len(res)}\n")
        return res

    """Обрабатывает отдельные блоки данных и обеспечивает корректную длину выходных данных"""

    if mode == 'dec':
        res = hex(magma_decrypt(block, s_key))[2:].zfill(16)
        return res
    else:
        raise ValueError("Wrong work mode ['enc', 'dec']")

text = 'Я пишу к тебе в полной уверенности, что мы никогда более не увидимся. Несколько лет тому назад, расставаясь с тобою, я думала то же самое; но небу было угодно испытать меня втор...'


def pkcs7_pad(data: bytes, block_size: int = 8) -> bytes:
    p = block_size - (len(data) % block_size)
    if p == 0:
        p = block_size
    return data + bytes([p] * p)


def pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        return data
    p = data[-1]
    if p < 1 or p > 8:
        raise ValueError('Некорректное дополнение PKCS7')
    return data[:-p]


def _read_long_plaintext() -> str:
    print('Введите открытый текст (несколько строк). Завершите ввод строкой, содержащей только ***')
    lines = []
    while True:
        line = input()
        if line.strip() == '***':
            break
        lines.append(line)
    return '\n'.join(lines)


def _preview_hex(s: str, head: int = 80, tail: int = 40) -> str:
    if len(s) <= head + tail + 3:
        return s
    return f'{s[:head]}... ({len(s)} символов) ...{s[-tail:]}'


def main():
    print('Магма')
    print('Выбери опцию:')
    print('1) Демо: зашифровать (эталонный блок)')
    print('2) Демо: расшифровать (эталонный блок)')
    print('3) Длинный открытый текст (ввод с консоли, ~1000+ символов и др.)')
    print('4) Проверка из файла sample_text.txt (как раньше)')
    opt = int(input())
    if opt == 1:
        text_h = bytearray(text, selected_codec).hex()
        text_h = "fedcba9876543210"
        print(f'Текст переведенный в hex: {text_h}')
        if len(text_h) % 16 != 0:
            block_list = split_by(text_h, 16, 'lazy')
        else:
            block_list = split_by(text_h, 16)
        encoded = ''.join([_magma(block, key) for block in block_list])
        print(f'Расшифрованный текст: {encoded}')
    elif opt == 2:
        text_h = bytearray(text, selected_codec).hex()
        text_h = "4ee901e5c2d8ca3d"
        if len(text_h) % 16 != 0:
            block_list = split_by(text_h, 16, 'lazy')
        else:
            block_list = split_by(text_h, 16)
        decoded = ''.join([_magma(block, key, mode='dec') for block in block_list])
        print(f'Расшифрованный текст: {decoded}')
    elif opt == 3:
        open_plain = _read_long_plaintext()
        raw = open_plain.encode(selected_codec)
        raw_padded = pkcs7_pad(raw, 8)
        text_h = raw_padded.hex()
        print(f'\nСимволов в открытом тексте: {len(open_plain)}')
        print(f'Байт после кодировки: {len(raw)}, байт с PKCS#7: {len(raw_padded)}')
        print(f'Hex (превью): {_preview_hex(text_h)}')
        block_list = split_by(text_h, 16)
        encoded = ''.join([_magma(block, key, verbose=False) for block in block_list])
        print(f'\nШифртекст (hex, превью): {_preview_hex(encoded)}')
        decoded_hex = ''.join(
            [_magma(piece, key, mode='dec', verbose=False) for piece in split_by(encoded, 16)]
        )
        recovered = pkcs7_unpad(bytearray.fromhex(decoded_hex))
        recovered_text = recovered.decode(selected_codec)
        print('\nПроверка: расшифрованный текст совпадает с исходным —',
              'да' if recovered_text == open_plain else 'НЕТ (ошибка)')
        if len(recovered_text) <= 500:
            print(f'\nОткрытый текст после расшифровки:\n{recovered_text}')
        else:
            print(f'\nОткрытый текст после расшифровки (первые 400 символов):\n{recovered_text[:400]}...')
    elif opt == 4:
        # Файл сохраняют в UTF-8; шифруем байты UTF-8 (как в консоли Cursor/VS Code)
        if not SAMPLE_TEXT_FILE.is_file():
            print(f'Файл не найден: {SAMPLE_TEXT_FILE}')
            print('Положите sample_text.txt в папку lab_7 рядом с MagmA.py')
            return
        raw_text = getline(str(SAMPLE_TEXT_FILE), False, 'utf-8')
        raw_padded = pkcs7_pad(raw_text.encode('utf-8'), 8)
        text_h = raw_padded.hex()
        print(f'Файл sample_text.txt: символов {len(raw_text)}, байт с PKCS#7: {len(raw_padded)}')
        print(f'Hex (превью): {_preview_hex(text_h)}')
        block_list = split_by(text_h, 16)
        encoded = ''.join([_magma(block, key, verbose=False) for block in block_list])
        print('\nШифртекст (hex, превью):')
        print(_preview_hex(encoded))
        decoded = ''.join([_magma(piece, key, mode='dec', verbose=False) for piece in split_by(encoded, 16)])
        print(f'\nПосле расшифровки (hex, превью):')
        print(_preview_hex(decoded))
        open_recovered = pkcs7_unpad(bytearray.fromhex(decoded)).decode('utf-8')
        print(f'\nОткрытый текст из файла (восстановленный):\n{open_recovered}')
    else:
        return print('Bad option')

if __name__ == '__main__':
    main()