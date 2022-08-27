# Импортируем библиотеку re, которая позволяет искать в тексте вопроса. Она будет использована для поиска
# изображений и звуковых файлов

import re


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
                 complexity):
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


    def get_pic(self) -> str:
        s = re.search('\d{6,}.jpg', self.question)
        if s:
            pic_name = s.group(0)
            pic_path = 'https://db.chgk.info/images/db/' + pic_name
            return pic_path
        return False


    def get_sound(self) -> str:
        s = re.search('\d{6,}.mp3', self.question)
        if s:
            sound_name = s.group(0)
            sound_path = 'https://db.chgk.info/images/db/' + sound_name
            return sound_path
        return False


    def get_answer(self) -> str:
        answer_string = self.answer + '\n'
        answer_string += '=' * 30 + '\n'
        if self.comments:
            answer_string += self.comments + '\n'
        if self.complexity:
            answer_string += 'Сложность: ' + self.complexity + '\n'
        answer_string += f'Источник: {self.source}, {self.tournamentTitle}, {self.tourTitle} \n'
        answer_string += '=' * 30
        return answer_string
           