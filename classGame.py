from classQuestion import Question

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