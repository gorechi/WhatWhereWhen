# Импортируем библиотеку re, которая позволяет искать в тексте вопроса. Она будет использована для поиска
# изображений и звуковых файлов

import re
from typing import List

# Описание класс Вопрос

class Question():
    def __init__(self,
                 questionId,
                 question,
                 answer,
                 passCriteria,
                 source,
                 comments,
                 tourTitle,
                 tournamentTitle,
                 tourPlayedAt,
                 complexity,
                 morph):
        self.questionId = questionId
        self.question = question
        self.answer = answer
        self.passCriteria = passCriteria
        self.source = source
        self.comments = comments
        self.tourTitle = tourTitle
        self.tournamentTitle = tournamentTitle
        self.tourPlayedAt = tourPlayedAt
        self.picture = self.get_pic()
        self.sound = self.get_sound()
        self.complexity = complexity
        self.morph = morph

# Функция ищет в тексте вопроса приложенную картинку и если находит ее, возвращает ее в виде
# строки с адресом в интернете. Если не находит - возвращает False.

    def get_pic(self):
        s = re.search('\d{6,}.jpg', self.question)
        if s:
            pic_name = s.group(0)
            pic_path = 'https://db.chgk.info/images/db/' + pic_name
            return pic_path
        else:
            return False

# Функция ищет в тексте вопроса приложенный звуковой файл и если находит его, возвращает в виде
# строки с адресом в интернете. Если не находит - возвращает False.

    def get_sound(self):
        s = re.search('\d{6,}.mp3', self.question)
        if s:
            sound_name = s.group(0)
            sound_path = 'https://db.chgk.info/images/db/' + sound_name
            return sound_path
        else:
            return False

# Функция возвращает сформированный из нескольких строк ответ на вопрос

    def get_answer(self):
        answer_string = self.answer + '\n'
        answer_string += '=' * 30 + '\n'
        if self.comments:
            answer_string += self.comments + '\n'
        if self.complexity:
            answer_string += 'Сложность: ' + self.complexity + '\n'
        answer_string += f'Источник: {self.source}, {self.tournamentTitle}, {self.tourTitle}'
        return answer_string

# Функция проверяет правильность ответа, для чего ищет вхождение полученной от пользователя строки текста в строку
# ответа на вопрос + дополнительные варианты ответов (если они есть). Если в ответе на вотпрос содержится строка
# пользователя, возвращается True. Если нет - False.

    def check_answer(self, input_string):
        right_answer = self.answer.lower()
        answer_list = self.string_to_list(right_answer)
        print(answer_list)
        input_list = self.string_to_list(input_string)
        print(input_list)
        answer_list = self.normalize_list(answer_list)
        print(answer_list)
        input_list = self.normalize_list(input_list)
        print(input_list)
        for word in input_list:
            if not word in answer_list:
                return False
        return True
        
    def string_to_list(self, input_string:str) -> List:
        no_symbols_string = re.sub("[,|.|?|!]", "", input_string)
        no_symbols_string.replace('  ', ' ')
        word_list = no_symbols_string.split(' ')
        return word_list
    
    def normalize_list(self, input_list:List) -> List:
        result_list = []
        for word in input_list:
            result_word = self.morph.parse(word)[0].normal_form
            result_list.append(result_word)
        return result_list
