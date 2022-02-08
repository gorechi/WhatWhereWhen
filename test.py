import re

a = '!сложность 1'
b = '!сложность 6'
c = '!сложность'
d = '!сложность 12'
l = [a, b, c, d]
for i in l:
    if re.match('!сложность [1-5]', i):
        print (i[11])