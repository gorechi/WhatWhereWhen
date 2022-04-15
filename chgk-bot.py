from settings import TOKEN
import requests 
import untangle 
from classGame import Game
from discord import Message, Client, Embed
from random import randint as r
from bs4 import BeautifulSoup 
import re
from pymorphy2 import MorphAnalyzer


# Хэш-таблицы (словари), в которых хранятся данные о текущих играх и отгаданных вопросах для разных чатов
current_game = {}
streak = {}
difficulty_dict = {}

morph = MorphAnalyzer()

def get_game(chat_id: str, is_full_game: bool) -> bool:
    global difficulty_dict
    global current_game
    have_question = False
    if current_game.get(chat_id):
        if current_game[chat_id].is_current_question() or current_game[chat_id].is_full_game:
            have_question = True
    if not have_question:
        if difficulty_dict.get(chat_id, 0) == 0:
            request_string = 'https://db.chgk.info/xml/random/types1'
        else:
            request_string = f'https://db.chgk.info/xml/random/complexity{str(difficulty_dict[chat_id])}/types1'
        request = requests.get(request_string).text
        obj = untangle.parse(request)
        new_game = Game(obj, chat_id, is_full_game, morph = morph)
        current_game[chat_id] = new_game
        return True
    else:
        return False

class MyClient(Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message:Message) -> None:
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!факт'):
            await fact_answer(message)

        if message.content.startswith('!вопрос'):
            await question_answer(message)

        if message.content.startswith('!игра'):
            await gama_answer(message)

        if message.content.startswith('!ответ'):
            await answer_answer(message)
            
        if message.content.startswith('!повтор'):
            await repeat_answer(message)

        if message.content.startswith('!закончить'):
            await finish_answer(message)
        
        if re.match('!сложность [0-5]', message.content):
            await difficulty_answer(message)
            
        if not message.content.startswith('!'):
            await plain_text_answer(message)

async def fact_answer(message: Message) -> None:
    fact_text = None
    while not fact_text:
        r_number = r(1, 7495)
        fact_link = 'https://facts.museum/' + str(r_number)
        fact_img = 'https://facts.museum/img/facts/' + str(r_number) + '.jpg'
        fact = requests.get(fact_link)
        soup = BeautifulSoup(fact.text, 'lxml')
        if soup.find('p', class_='content'):
            fact_text = soup.find('p', class_='content').text
    fact_text += '\n' + fact_link
    embed = Embed(color=0x07c610, title='Случайный факт', description=fact_text)
    embed.set_image(url = fact_img)
    await message.channel.send(embed=embed)
    
async def question_answer(message: Message) -> None:
    global current_game
    chat_id = message.channel.id
    full_game = False
    current_question = None
    if current_game.get(chat_id):
        full_game = current_game[chat_id].is_full_game
        current_question = current_game[chat_id].current_question
    if not current_question:
        if not full_game:
            new_game = get_game(chat_id, False)
        question, number, number_of_questions = current_game[chat_id].get_question()
        if number:
            number_string = f'Номер вопроса: {str(number)} из {str(number_of_questions)}'
        else:
            number_string = 'Случайный вопрос'
        if question.picture:
            embed = Embed(color=0xff9900)
            embed.set_image(url=question.picture)
            await message.channel.send(embed=embed)
        await message.channel.send(f'{number_string}\n{question.question}')
    else:
        await message.channel.send('Не торопись-ка! Сначала ответьте на предыдущий вопрос.',
                                    mention_author=True)

async def repeat_answer(message: Message) -> None:
    global current_game
    chat_id = message.channel.id
    current_question = None
    if current_game.get(chat_id):
        current_question = current_game[chat_id].current_question
    if current_question:
        question, number, number_of_questions = current_game[chat_id].get_question()
        if number:
            number_string = f'Номер вопроса: {str(number)} из {str(number_of_questions)}'
        else:
            number_string = 'Случайный вопрос'
        if current_question.picture:
            embed = Embed(color=0xff9900)
            embed.set_image(url=current_question.picture)
            await message.channel.send(embed=embed)
        await message.channel.send(f'{number_string}\n{current_question.question}')
    else:
        await message.channel.send('Нечего повторять - вопрос-то не задали еще.',
                                    mention_author=True)

async def gama_answer(message: Message) -> None:
    global current_game
    chat_id = message.channel.id
    if get_game(chat_id, True):
        question, number, number_of_questions = current_game[chat_id].get_question()
        number_string = f'Номер вопроса: {str(number)} из {str(number_of_questions)}'
        if question.picture:
            embed = Embed(color=0xff9900)
            embed.set_image(url=question.picture)
            await message.channel.send(embed=embed)
        await message.channel.send(f'{number_string}\n{question.question}')
    else:
        await message.channel.send('Прекратите хулиганить! У вас уже есть запущенная игра.',
                                        mention_author=True)

async def answer_answer(message: Message) -> None:
    global streak
    global current_game
    chat_id = message.channel.id
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

async def finish_answer(message: Message) -> None:
    global current_game
    chat_id = message.channel.id
    if not current_game.get(chat_id):
        await message.channel.send('Вы еще не начали игру, а уже хотите ее закончить.')
    else:
        await message.channel.send('Игра закончена.')
        current_game.get(chat_id).end_game()
        current_game.pop(chat_id, False)

async def difficulty_answer(message: Message) -> None:
    global difficulty_dict
    chat_id = message.channel.id
    difficulty = int(message.content[11])
    difficulty_list = ['любые', 'очень простые', 'простые', 'средние', 'сложные', 'очень сложные']
    difficulty_dict[chat_id] = difficulty
    if difficulty == 0:
        await message.channel.send('В этот чат будут приходить игры и вопросы любой сложности.')
    else:
        await message.channel.send(f'В этот чат будут приходить {difficulty_list[difficulty]} игры и вопросы.')

async def plain_text_answer(message: Message) -> None:
    global current_game
    global streak
    chat_id = message.channel.id
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


# Запускаем бота
client = MyClient()
client.run(TOKEN)
