from chgksettings import TOKEN, UNSPLASH_KEY
import requests
import untangle
from classGame import Game
import discord
import json
from pogovorki_functions import *
from random import randint as r
from bs4 import BeautifulSoup

# Читаем файл
with open('pogovorki.json', encoding='utf-8') as read_data:
    parsed_data = json.load(read_data)
wisdom = parsed_data[0]['part1'][0] + parsed_data[3]['part2'][0]

#print(request)
currentQuestion = {}
current_game = {}
streak = {}

def get_game(chat_id):
    global current_game
    if not currentQuestion.get(chat_id):
        request = requests.get('https://db.chgk.info/xml/random/types1').text
        obj = untangle.parse(request)
        new_game = Game(obj, chat_id)
        current_game[chat_id] = new_game
        return True
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
            part1 = random.choice(random.choice(parsed_data)['part1'])
            part2 = random.choice(random.choice(parsed_data)['part2'])
            wisdom = trim(part1 + part2)
            await message.channel.send(wisdom, mention_author=True)

        if message.content.startswith('!факт'):
            fact_text = None
            while not fact_text:
                r_number = r(1, 7495)
                print('+' * 40)
                print('Номер факта:', r_number)
                print('+' * 40)
                fact_link = 'https://muzey-factov.ru/' + str(r_number)
                fact_img = 'https://muzey-factov.ru/img/facts/' + str(r_number) + '.png'
                fact = requests.get(fact_link)
                soup = BeautifulSoup(fact.text, 'lxml')
                if soup.find('p', class_='content'):
                    fact_text = soup.find('p', class_='content').text
            fact_text += '\n' + fact_link
            embed = discord.Embed(color=0x07c610, title='Случайный факт', description=fact_text)  # Создание Embed'a
            embed.set_image(url = fact_img)  # Устанавливаем картинку Embed'a
            await message.channel.send(embed=embed)  # Отправляем Embed

        if message.content.startswith('!вопрос'):
            if get_game(chat_id):
                question = current_game[chat_id].get_random_question()
                if question.picture:
                    embed = discord.Embed(color=0xff9900)  # Создание Embed'a
                    embed.set_image(url=question.picture)  # Устанавливаем картинку Embed'a
                    await message.channel.send(embed=embed)  # Отправляем Embed
                await message.channel.send(question.question)
            else:
                await message.channel.send('Не торопись-ка! С начала оветьте на предыдущий вопрос.',
                                           mention_author=True)

        if message.content.startswith('!ответ'):
            if current_game.get(chat_id):
                current_question = current_game[chat_id].current_question
            else:
                current_question = None
            if not current_question:
                await message.channel.send('Вам еще не задали вопрос, а вы уже хотите ответ.')
            else:
                answer_string = current_question.get_answer()
                await message.channel.send(answer_string)
                current_game[chat_id].reset_question()
                streak[chat_id] = 0

        if message.content.startswith('!лягу'):
            response = requests.get('https://api.unsplash.com/photos/random/?query=frog&client_id=' + UNSPLASH_KEY)
            if response.status_code == 200:
                json_data = json.loads(response.text)  # Извлекаем JSON
                embed = discord.Embed(color=0x07c610, title='Случайная лягуха')  # Создание Embed'a
                embed.set_image(url=json_data['urls']['regular'])  # Устанавливаем картинку Embed'a
                await message.channel.send (embed=embed)  # Отправляем Embed

        if not message.content.startswith('!'):
            if current_game.get(chat_id):
                current_question = current_game[chat_id].current_question
            else:
                current_question = None
            if current_question:
                if current_question.check_answer(message.content):
                    answer_string = 'Правильно! \n' + current_question.get_answer()
                    if not streak.get(chat_id):
                        streak[chat_id] = 0
                    streak[chat_id] += 1
                    await message.channel.send(answer_string)
                    if streak[chat_id] == 5:
                        await message.channel.send('Пять вопросов подряд!')
                    current_game[chat_id].reset_question()

client = MyClient()
client.run(TOKEN)