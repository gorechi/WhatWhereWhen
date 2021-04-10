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
        self.complexity = complexity

    def get_pic(self):
        text = self.question
        s = re.search('\d{6,}.jpg', text)
        if s:
            pic_name = s.group(0)
            pic_path = 'https://db.chgk.info/images/db/' + pic_name
            return pic_path
        else:
            return False

    def get_sound(self):
        text = self.question
        s = re.search('\d{6,}.mp3', text)
        if s:
            sound_name = s.group(0)
            sound_path = 'https://db.chgk.info/images/db/' + sound_name
            return sound_path
        else:
            return False

