from classQuestion import Question
import random

class Game():
    def __init__(self, obj, chat_id, is_full_game=False):
        self.obj = obj
        self.chat_id = chat_id
        self.questions_list = []
        self.current_question = None
        self.current_question_number = 0
        self.is_full_game = is_full_game
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
        print(self.questions_list[0].question)

    def is_current_question(self):
        if self.current_question:
            return True
        else:
            return False

    def get_question(self):
        if not self.is_full_game:
            print('--11--')
            random.shuffle(self.questions_list)
            self.current_question = self.questions_list[0]
            print('random question')
            return self.questions_list[0]
        else:
            if self.current_question_number < len(self.questions_list) - 1:
                self.current_question = self.questions_list[self.current_question_number]
                self.current_question_number += 1
                print(self.current_question_number)
                return self.current_question
            else:
                self.end_game()
                return False

    def end_game(self):
        print('-----Игра закончена-----')
        self.current_question = None
        self.is_full_game = False
        return True