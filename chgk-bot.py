from chgksettings import TOKEN, UNSPLASH_KEY
import requests
import untangle
from classQuestions import Question
import discord
from pogovorki_functions import *
import json

# Читаем файл
pogovorki = readfile('pogovorki.txt', True, '|')
l = len(pogovorki)
print('Всего поговорок: ' + str(l))
print('Всего вариантов бреда: ' + str(l*l-l))

#print(request)
currentQuestion = {}
streak = {}

def get_question(chat_id):
    global currentQuestion
    if not currentQuestion.get(chat_id):
        questionsList = []
        request = requests.get('https://db.chgk.info/xml/random/types1').text
        print(request)
        obj = untangle.parse(request)
        for q in obj.search.question:
            questionId = q.QuestionId.cdata
            question = q.Question.cdata
            answer = q.Answer.cdata
            passCriteria = q.PassCriteria.cdata
            source = q.Sources.cdata
            comments = q.Comments.cdata
            tourTitle = q.tourTitle.cdata
            tournamentTitle = q.tournamentTitle.cdata
            tourPlayedAt = q.tourPlayedAt.cdata
            complexity = q.Complexity.cdata
            vopr = Question(questionId,
                            question,
                            answer,
                            passCriteria,
                            source,
                            comments,
                            tourTitle,
                            tournamentTitle,
                            tourPlayedAt,
                            complexity)
            questionsList.append(vopr)
        random.shuffle(questionsList)
        currentQuestion[chat_id] = questionsList[0]
        return True
    else:
        return False

def get_answer(chat_id):
    global currentQuestion
    current_question = currentQuestion.get(chat_id)
    if current_question:
        answer_string = current_question.answer + '\n'
        answer_string += '=' * 30 + '\n'
        if current_question.comments:
            answer_string += current_question.comments + '\n'
        if current_question.complexity:
            answer_string += 'Сложность: ' + current_question.complexity + '\n'
        answer_string += 'Источник: ' + current_question.source
        return answer_string
    else:
        return False

def check_answer(chat_id, answer):
    global currentQuestion
    question = currentQuestion.get(chat_id)
    if question:
        right_answer = question.answer.lower()
        #if question.passCriteria:
        #    right_answer += question.passCriteria.lower()
        answer = answer.lower()
        find_answer = right_answer.find(answer)
        if find_answer > -1:
            return True
        else:
            return False
    else:
        return False

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        global currentQuestion
        global streak
        chat_id = message.channel.id
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)

        if message.content.startswith('!мудр'):
            wisdom = trim(pogovorki[dice(0, len(pogovorki) - 1)][0] + pogovorki[dice(0, len(pogovorki) - 1)][1])
            await message.channel.send(wisdom, mention_author=True)

        if message.content.startswith('!вопрос'):
            if get_question(chat_id):
                question = currentQuestion[chat_id]
                if question.picture:
                    embed = discord.Embed(color=0xff9900)  # Создание Embed'a
                    embed.set_image(url=question.picture)  # Устанавливаем картинку Embed'a
                    await message.channel.send(embed=embed)  # Отправляем Embed
                await message.channel.send(question.question)
            else:
                await message.channel.send('Не торопись-ка! С начала оветьте на предыдущий вопрос.',
                                           mention_author=True)

        if message.content.startswith('!ответ'):
            current_question = currentQuestion[chat_id]
            if not current_question:
                await message.channel.send('Вам еще не задали вопрос, а вы уже хотите ответ.')
            else:
                answer_string = get_answer(chat_id)
                await message.channel.send(answer_string)
                currentQuestion[chat_id] = None
                streak[chat_id] = 0

        if message.content.startswith('!лягу'):
            response = requests.get('https://api.unsplash.com/photos/random/?query=frog&client_id=' + UNSPLASH_KEY)
            if response.status_code == 200:
                json_data = json.loads(response.text)  # Извлекаем JSON
                embed = discord.Embed(color=0x07c610, title='Случайная лягуха')  # Создание Embed'a
                embed.set_image(url=json_data['urls']['regular'])  # Устанавливаем картинку Embed'a
                await message.channel.send (embed=embed)  # Отправляем Embed

        if not message.content.startswith('!'):
            if check_answer(chat_id, message.content):
                answer_string = 'Правильно! \n' + get_answer(chat_id)
                if not streak.get(chat_id):
                    streak[chat_id] = 0
                streak[chat_id] += 1
                if streak[chat_id] == 5:
                    await message.channel.send('Пять вопросов подряд!')
                await message.channel.send(answer_string)
                currentQuestion[chat_id] = None

client = MyClient()
client.run(TOKEN)