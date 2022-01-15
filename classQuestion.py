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

    #Функция ищет в тексте вопроса приложенную картинку и если находит ее, возвращает ее в виде
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
        answer_string += 'Источник: ' + self.source
        return answer_string

    # Функция проверяет правильность ответа, для чего ищет вхождение полученной от пользователя строки текста в строку
    # ответа на вопрос + дополнительные варианты ответов (если они есть). Если в ответе на вотпрос содержится строка
    # пользователя, возвращается True. Если нет - False.
    def check_answer(self, answer_string):
        right_answer = self.answer.lower()
        if self.passCriteria:
            right_answer += self.passCriteria.lower()
        answer = answer_string.lower()
        find_answer = right_answer.find(answer)
        if find_answer > -1:
            return True
        else:
            return False
