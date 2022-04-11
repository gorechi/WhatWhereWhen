import re
import re
from pymorphy2 import MorphAnalyzer

test_string = 'бить'

morph = MorphAnalyzer()

result = morph.parse(test_string)[0]
print(result)
lexemes = result.lexeme
for lexeme in lexemes:
    print(lexeme.word)

def normalize_string(input_string:str):
    no_symbols_string = re.sub("[,|.|?|!]", "", input_string)
    no_symbols_string.replace('  ', ' ')
    word_list = no_symbols_string.split(' ')
    return(word_list)

s = 'Вы готовы, дети!?'
print(normalize_string(s))

