import re

string = '(pic: 20140081.jpg)' \
         'На розданной фотографии - предмет быта, используемый племенами' \
         'охотников и скотоводов Восточной Африки. Разновидность этого предмета,' \
         'которую вы видите, предназначена для мужчин. Она отличается узким' \
         'круглым основанием, которое не позволяет СДЕЛАТЬ ЭТО. Назовите' \
         'произведение, в котором ЭТО СДЕЛАЛИ в числе прочих вертел и огонь.'
s = re.search('\d{6,}.jpg', string)

print(s.group(0))