import re
from pymorphy2 import MorphAnalyzer

test_string = 'бить'

morph = MorphAnalyzer()

result = morph.parse(test_string)[0]
print(result)
lexemes = result.lexeme
for lexeme in lexemes:
    print(lexeme.word)

