

CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
NUMBERS_BY_CHAR = {c: i for i, c in enumerate(CHARS)}


def encode(number, padding):
    encoded = []
    while number:
        encoded.append(char_from_num(number % 62))
        number //= 62

    return ''.join(reversed(encoded)).rjust(padding, '0')


def decode(encoded):
    number = 0
    pow = 62**(len(encoded)-1)
    for char in encoded:
        number += num_from_char(char) * pow
        pow //= 62

    return number


def char_from_num(digit):
    return CHARS[digit]


def num_from_char(char):
    return NUMBERS_BY_CHAR[char]
