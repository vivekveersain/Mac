import random
from pandas.io.clipboard import clipboard_get, clipboard_set

maps = {'a': ['a', 'A', '@']
        , 'b': ['b', 'B', 'ℬ']
        , 'c': ['c', 'C', '¢', '©']
        , 'd': ['d', 'D', 'ꝺ', 'Ɖ', 'ɖ']
        , 'e': ['e', 'E', '£', '€']
        , 'f': ['f', 'F']
        , 'g': ['g', 'G']
        , 'h': ['h', 'H', '#', "¦¬¦"]
        , 'i': ['i', 'I', '!', "¡"]
        , 'j': ['j', 'J']
        , 'k': ['k', 'K', "|<", "¦<"]
        , 'l': ['l', 'L']
        , 'm': ['m', 'M', '|\/|']
        , 'n': ['n', 'N', "|\|", "¦\¦"]
        , 'o': ['o', 'O', "0"]
        , 'p': ['p', 'P', "¶"]
        , 'q': ['q', 'Q']
        , 'r': ['r', 'R', "®"]
        , 's': ['s', 'S', "$", "&"]
        , 't': ['t', 'T', "¿"]
        , 'u': ['u', 'U', "|_|"]
        , 'v': ['v', 'V', "\/"]
        , 'w': ['w', 'W', "|/\|"]
        , 'x': ['x', 'X', "×"]
        , 'y': ['y', 'Y', "¥"]
        , 'z': ['z', 'Z']}

try:
	inp = clipboard_get().lower()[::-1]
	out = "".join([random.choice(maps.get(r, r)) for r in inp])
	clipboard_set(out)
except: print("ERROR!")
