from chgksettings import TOKEN
import requests #Импортируем библиотеку HTTP запросов
import untangle #Импортируем библиотеку обработки XML
from classGame import Game #Импортируем класс Game
import discord #Импортируем официальную библиотеку Discord
from random import randint as r #Импортируем библиотеку random
from bs4 import BeautifulSoup


# Хэш-таблицы (словари), в которых хранятся данные о текущих играх и отгаданных вопросах для разных чатов
current_game = {}
streak = {}

# Функция создания новой игры. Данные берутся с сайта db.chgk.info
def get_game(chat_id, is_full_game):
    global current_game
    have_question = False
    if current_game.get(chat_id):
        if current_game[chat_id].is_current_question() or current_game[chat_id].is_full_game:
            have_question = True
    if not have_question:
        request = requests.get('https://db.chgk.info/xml/random/types1').text
        obj = untangle.parse(request)
        new_game = Game(obj, chat_id, is_full_game)
        current_game[chat_id] = new_game
        return True
    else:
        return False

# Класс клиента для Discord. В нем хранятся обработчики различных событий, которые приходят из чатов.
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        global currentQuestion
        global streak
        chat_id = message.channel.id
        # Не нужно, чтобы бот отвечал самому себе
        if message.author.id == self.user.id:
            return

        # Ветка, в которой бот реагирует на команду !Факт и присылает случайный интересный факт
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

        # Ветка, в которой бот реагирует на команду !Вопрос и присылает следующий вопрос ЧГК.
        if message.content.startswith('!вопрос'):
            full_game = False
            current_question = None
            if current_game.get(chat_id):
                full_game = current_game[chat_id].is_full_game
                current_question = current_game[chat_id].current_question
            if not current_question:
                if not full_game:
                    new_game = get_game(chat_id, False)
                question, number = current_game[chat_id].get_question()
                if number:
                    number_string = f'Номер вопроса: {str(number)}'
                else:
                    number_string = 'Случайный вопрос'
                if question.picture:
                    embed = discord.Embed(color=0xff9900)  # Создание Embed'a
                    embed.set_image(url=question.picture)  # Устанавливаем картинку Embed'a
                    await message.channel.send(embed=embed)  # Отправляем Embed
                await message.channel.send(f'{number_string}\n{question.question}')
            else:
                await message.channel.send('Не торопись-ка! Сначала ответьте на предыдущий вопрос.',
                                               mention_author=True)

        # Ветка, в которой бот реагирует на команду !Игра и начинает новую игру ЧГК
        if message.content.startswith('!игра'):
            if get_game(chat_id, True): # Создаем игру и проверяем, все ли прошло хорошо.
                question, number = current_game[chat_id].get_question() # Просим игру дать нам вопрос и его номер
                number_string = f'Номер вопроса: {str(number)}'
                if question.picture: # Проверка на то, что в вопросе есть картинка
                    embed = discord.Embed(color=0xff9900)  # Создание Embed'a
                    embed.set_image(url=question.picture)  # Устанавливаем картинку Embed'a
                    await message.channel.send(embed=embed)  # Отправляем Embed
                await message.channel.send(f'{number_string}\n{question.question}') # Отправляем вопрос в чат
            else: # Если игра уже существует, выдаем предупреждение в чат
                await message.channel.send('Прекратите хулиганить! У вас уже есть запущенная игра.',
                                           mention_author=True)

        # Ветка, в которой бот реагирует на команду !Ответ и выдает ответ на вопрос ЧГК
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
                current_game[chat_id].current_question = None
                streak[chat_id] = 0

        # Ветка, в которой бот реагирует на обычный текст и, если задан вопрос ЧГК, пытается сравнить этот текст
        # с ответом на этот вопрос. Если ответ содержит присланный текст, вопрос считается отвеченным.
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
                    if streak[chat_id] >= 5:
                        await message.channel.send(f'{streak[chat_id]} вопросов подряд!')
                    current_game[chat_id].current_question = None

client = MyClient()
client.run(TOKEN)