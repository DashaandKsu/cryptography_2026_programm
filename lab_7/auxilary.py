import math
from random import randint

char_sheet = {
    ' ': 'ПРБ',
    ',': 'ЗПТ',
    '.': 'ТЧК',
    '-': 'ДФС',
    chr(8211): 'ДФС',
    ';': 'ТЗП',
    '!': 'ВСЗ'
}

low_key_char_sheet = {
    ' ': 'прб',
    ',': 'зпт',
    '.': 'тчк',
    '-': 'дфс',
    chr(8211): 'дфс',
    ';': 'тзп',
    '!': 'всз'
}

CODECS = [
    'ansi',
    'utf-8',
    'cp866',
    'windows-1251'
]


def check_mutual_simplicity(int1, int2):
    if not isinstance(int1, int):
        raise TypeError("First arg is not int")
    if not isinstance(int2, int):
        raise TypeError("Second arg is not int")
    int1_s = [i for i in range(2, int1 + 1) if int1 % i == 0]
    int2_s = [i for i in range(2, int2 + 1) if int2 % i == 0]
    # print(f'{int1}:{int1_s}')
    # print(f'{int2}:{int2_s}')
    # print()
    return not set(int1_s) & set(int2_s)


def show_by(text, size):
    if len(text) % size != 0:
        raise ValueError(f'Text cannot be splitted by parts of {size}')
    else:
        splitted_text = split_by(text, size)
        for it in range(len(splitted_text)):
            print(it, '\t', splitted_text[it])
        print()


def get_devisors(int1, mode="normal"):
    if not isinstance(int1, int):
        raise TypeError("Given arg is not int")
    if mode == "simple":
        return [i for i in range(1, int1) if int1 % i == 0 and is_simple(i)]
    else:
        return [i for i in range(1, int1) if int1 % i == 0]


def is_simple(int1):
    if int1 == 1:
        return True
    return len([i for i in range(1, int1) if int1 % i == 0]) == 1


def split_by(text, size, mode='strict'):
    """ modes = ['strict', 'lazy']"""
    if mode == 'strict':
        return [text[i * size:(i + 1) * size] for i in range(len(text) // size)]
    elif mode == 'lazy':
        text_len = len(text)
        number_of_valid_blocks = text_len//size
        container = [text[i * size:(i + 1) * size] for i in range(number_of_valid_blocks)]
        container.append(text[number_of_valid_blocks*size:])
        return container
    else:
        raise ValueError('Wrong split mode')


def remove_char(target, char_set, mode, using_low_key):
    used_dict = low_key_char_sheet if using_low_key else char_sheet
    if mode == 'front':
        for char in char_set:
            target = target.replace(char, used_dict.get(char))
    elif mode == 'back':
        # print(used_dict)
        for char in char_set:
            target = target.replace(used_dict.get(char), char)
            # print(used_dict.get(char), char)
        target = target.capitalize()
    else:
        raise ValueError('Invalid work mode [front, back]')
    return target


def gen_char(n):
    return ''.join([chr(randint(1072, 1103)) for _ in range(n)])


def fix_to_len(_text, target_size):
    # print(f'\nauxilary.fix_to_len')
    len_text = len(_text)
    if len(_text) % target_size == 0:
        print(f'Length is okay')
        return _text
    to_fill = target_size * (len_text // target_size + 1) - len_text
    print(f'To fill till %{target_size}==0 generating {to_fill} characters. Total size: {len_text+to_fill}\n')
    _text += gen_char(to_fill)
    return _text


def text_wrapper(text, mode='front', no_replace=False, replace=True, low_key=False):
    # print(text_wrapper, text, mode)
    if not no_replace:
        text = text.replace('ё', 'е')
        if replace:
            text = text.replace('й', 'и')
    return remove_char(text, [' ', '.', ',', ';', '-'], mode, low_key)


big_simples = [i for i in range(100, 500) if is_simple(i)]


def euler(int1):
    return len([i for i in range(1, int1) if check_mutual_simplicity(i, int1)])


def solve_comparison(q_e, x1, mod):
    for i in range(mod ** 2):
        if (q_e * i) % mod == x1:
            return i


def solve_linear_congruence(a, b, m):
    g = math.gcd(a, m)
    if b % g:
        raise ValueError("No solutions")
    a, b, m = a // g, b // g, m // g
    return pow(a, -1, m) * b % m


def get_simples(int1):
    return [i for i in range(1, int1) if check_mutual_simplicity(i, int1)]


def block_zerofill_to(hex_block, length):
    if len(hex_block) == length:
        return hex_block
    # print('\n' + '-' * 14 + 'BLOCK ERROR START' + '-' * 14)
    # print(f"Block {hex_block} length is not {length}, filling")
    hex_block = hex_block.zfill(length)
    # print(f"Returning {hex_block}")
    # print('-' * 14 + 'BLOCK ERROR END' + '-' * 14 + '\n')
    return hex_block


testing_string = "самаясильнаяцепьслабеесвоегосамогослабогозвенатчк"
