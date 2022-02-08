from classQuestion import Question #Импортируется класс Вопрос
import random #Импортируется стандартная библиотека генерации случайных значений

# Описание класса Игра
class Game():

# Функция инициации объекта класса, которая срабатывает когда программа создает новую игру.
# На вход передается прочитанный с сервера объект игры, идентификатор чата, в котором запущена игра, и признак,
# хочет ли пользователь играть полную игру.
# По умолчанию принимается, что новая игра не является полной, то есть пользователь хочет просто получить
# один вопрос из этой игры.

    def __init__(self, obj, chat_id, is_full_game=False):
        self.obj = obj
        self.chat_id = chat_id
        self.questions_list = []
        self.current_question = None
        self.current_question_number = 0
        self.is_full_game = is_full_game
# Пробегаем по вопросам, которые содержатся в объекте игры и из каждого вопроса создаем объект класса Вопрос.
# Все созданные объекты записываются в список вопросов игры.
        for q in self.obj.search.question:
            vopr = Question(q.QuestionId.cdata,
                            q.Question.cdata,
                            q.Answer.cdata,
                            q.PassCriteria.cdata,
                            q.Sources.cdata,
                            q.Comments.cdata,
                            q.tourTitle.cdata,
                            q.tournamentTitle.cdata,
                            q.tourPlayedAt.cdata,
                            q.Complexity.cdata)
            self.questions_list.append(vopr)
        self.number_of_questions = len(self.questions_list)

# Функция проверяет, есть ли у игры текущий вопрос

    def is_current_question(self):
        if self.current_question:
            return True
        else:
            return False

# Функция возвращает один из вопросов из игры

    def get_question(self):
# Если игра неполная, то возвращается случайный вопрос из списка вопросов игры
        if not self.is_full_game:
            random.shuffle(self.questions_list)
            self.current_question = self.questions_list[0]
            return self.questions_list[0], False, self.number_of_questions

# Если пользователь хочет играть полную игру, то вопросы возвращаются по порядку пока все не закончатся.
# Если вопросов не осталось, вызывается функция окончания игры.
        else:
            if self.current_question_number < len(self.questions_list) - 1:
                self.current_question = self.questions_list[self.current_question_number]
                self.current_question_number += 1
                return self.current_question, self.current_question_number, self.number_of_questions
            else:
                self.end_game()
                return False, False, False

# Функция окончания игры.

    def end_game(self):
        self.current_question = None
        self.is_full_game = False
        return True
