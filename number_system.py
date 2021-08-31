dec_to_char = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    ",",
    ";",
]

char_to_dec = {
    "0": 0,  # 000000
    "1": 1,  # 000001
    "2": 2,  # 000010
    "3": 3,  # 000011
    "4": 4,  # 000100
    "5": 5,  # 000101
    "6": 6,  # 000110
    "7": 7,  # 000111
    "8": 8,  # 001000
    "9": 9,  # 001001
    "a": 10,  # 001010
    "b": 11,  # 001011
    "c": 12,  # 001100
    "d": 13,  # 001101
    "e": 14,  # 001110
    "f": 15,  # 001111
    "g": 16,  # 010000
    "h": 17,  # 010001
    "i": 18,  # 010010
    "j": 19,  # 010011
    "k": 20,  # 010100
    "l": 21,  # 010101
    "m": 22,  # 010110
    "n": 23,  # 010111
    "o": 24,  # 011000
    "p": 25,  # 011001
    "q": 26,  # 011010
    "r": 27,  # 011011
    "s": 28,  # 011100
    "t": 29,  # 011101
    "u": 30,  # 011110
    "v": 31,  # 011111
    "w": 32,  # 100000
    "x": 33,  # 100001
    "y": 34,  # 100010
    "z": 35,  # 100011
    "A": 36,  # 100100
    "B": 37,  # 100101
    "C": 38,  # 100110
    "D": 39,  # 100111
    "E": 40,  # 101000
    "F": 41,  # 101001
    "G": 42,  # 101010
    "H": 43,  # 101011
    "I": 44,  # 101100
    "J": 45,  # 101101
    "K": 46,  # 101110
    "L": 47,  # 101111
    "M": 48,  # 110000
    "N": 49,  # 110001
    "O": 50,  # 110010
    "P": 51,  # 110011
    "Q": 52,  # 110100
    "R": 53,  # 110101
    "S": 54,  # 110110
    "T": 55,  # 110111
    "U": 56,  # 111000
    "V": 57,  # 111001
    "W": 58,  # 111010
    "X": 59,  # 111011
    "Y": 60,  # 111100
    "Z": 61,  # 111101
    ",": 62,  # 111110
    ";": 63,  # 111111
}


class NumberSystem:
    def __init__(self):
        self._base = 64
        # encoding & decoding is in reverse order, i.e., least significant byte first
        # Example: A1 = 1 * val(A) + base * val(1)

    def encode(self, num):
        ans = []

        while num:
            ans.append(dec_to_char[num % self._base])
            num //= self._base

        return "".join(ans)

    def decode(self, num):
        ans = 0
        p = 1

        for i in num:
            ans += char_to_dec[i] * p
            p *= self._base

        return ans
