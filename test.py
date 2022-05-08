import re

s = '!сложность 4'

print(re.fullmatch('!сложность [0-5]', s.lower()))
print(re.fullmatch('!([1-9]|1[0-5])', s.lower()))