import re

content = '!сложность 4'

print(content.startswith('!факт'))
print(content.startswith('!вопрос'))
print(content.startswith('!игра'))
print(content.startswith('!ответ'))
print(content.startswith('!повтор'))
print(content.startswith('!рекорды'))
print(content.startswith('!закончить'))
print(content.startswith('!своя игра'))
print(content.startswith('!темы'))
print(content.startswith('!таблица'))
print(content == '!!')
print(re.fullmatch('!([1-9]|1[0-5])', content.lower()))
print(re.fullmatch('!сложность [0-5]', content.lower()))
print(not content.startswith('!'))