from classQuestion import Question
import random

class Game():
    def __init__(self, obj, chat_id):
        self.obj = obj
        self.chat_id = chat_id
        self.questions_list = []
        self.current_question = None
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
        print(self.questions_list)

    def get_random_question(self):
        random.shuffle(self.questions_list)
        self.current_question = self.questions_list[0]
        return self.questions_list[0]

    def reset_question(self):
        self.current_question = None
        print(self.current_question)
