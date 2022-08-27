from classes.classQuestion import Question #Импортируется класс Вопрос
import random #Импортируется стандартная библиотека генерации случайных значений
from db.db_functions import get_chat
import requests
import untangle
import re


class Game():
 
    current_game={}
    
    def __init__(self, chat_id, is_full_game=False):
        self.chat_id = chat_id
        self.questions_list = []
        self.current_question = None
        self.current_question_number = 0
        self.is_full_game = is_full_game
        self.error = False
        self.setup_game()


    def setup_game(self) -> bool:
        chat = get_chat(self.chat_id)
        difficulty = chat.difficulty
        if difficulty == 0:
            request_string = 'https://db.chgk.info/xml/random/types1'
        else:
            request_string = f'https://db.chgk.info/xml/random/complexity{str(difficulty)}/types1'
        request = requests.get(request_string)
        if request.status_code == 200:
            request_text = request.text
            obj = untangle.parse(request_text)
            for q in obj.search.question:
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
            Game.current_game[self.chat_id] = self
        else:
            self.error = True
            return False
        return True
 
    
    def get_question(self):
        if not self.is_full_game:
            random.shuffle(self.questions_list)
            self.current_question = self.questions_list[0]
            return self.questions_list[0], False, self.number_of_questions
        if self.current_question_number < len(self.questions_list) - 1:
            self.current_question = self.questions_list[self.current_question_number]
            self.current_question_number += 1
            return self.current_question, self.current_question_number, self.number_of_questions
        self.end_game()
        return False, False, False


    def end_game(self):
        self.current_question = None
        self.is_full_game = False
        Game.current_game[self.chat_id] = None
        return True