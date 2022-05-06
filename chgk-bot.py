from db.db_functions_mg import db_mg_end_game, db_mg_get_scores, db_mg_question_answered, db_mg_skip_question, db_mg_update_game, db_mg_wrong_answer
from db.db_functions_mg import get_game_by_chat, db_mg_set_current_theme, db_mg_set_current_question
from functions_mg import get_themes_text, setup_game, get_theme_by_index, get_mg_question, get_question_text
from db.db import DBQuestion
from options import game_state, emojis, timer_values
from settings import TOKEN
import requests
from pymorphy2 import MorphAnalyzer
from classes.classGame import Game
from discord import Message, Client, Embed
from random import randint as r, choice
from bs4 import BeautifulSoup
from time import sleep
from options import game_state, question_answered
from asyncio import sleep as async_sleep
import re
from db.db_functions import set_chat_difficulty, player_add_answer, get_chat_answers_table, update_player_name, get_player


class Bot(Client):
    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, options=options)
        self.morph = MorphAnalyzer()
        self.hosts = {}
        self.game_states = {}
        self.answering_player = {}
        self.played = {}

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: Message) -> None:
        
        """Метод обработки сообщения из чата. 
        Реагирует на определенный шаблоны текста сообщения и вызывает соответствующеие методы бота.
        Все методы бота, которые запускаются отсюда, должны принимать на вход один обязательный параметр - 
        объект сообщения чата Message. Дальнейшая логика обработки этого сообщения должна быть реализована уже
        в запускаемом методе."""
        
        chat_id = message.channel.id

        if message.author.id == self.user.id or self.game_states.get(chat_id) == game_state.PAUSE:
            return

        content = message.content

        commands = {
            content.startswith('!факт'): self.fact,
            content.startswith('!вопрос'): self.question,
            content.startswith('!игра'): self.game,
            content.startswith('!ответ'): self.answer,
            content.startswith('!повтор'): self.repeat,
            content.startswith('!рекорды'): self.answers_table,
            content.startswith('!закончить'): self.finish,
            content.startswith('!своя игра'): self.my_game,
            content.startswith('!темы'): self.themes,
            content.startswith('!таблица'): self.table,
            content == '!!': self.pause,
            re.fullmatch('!([1-9]|1[0-5])', content.lower()) and self.check_host(message): self.theme,
            re.fullmatch('!сложность [0-5]', content.lower()): self.difficulty,
            not content.startswith('!'): self.plain_text
        }

        function = commands.get(True)
        if function:
            await function(message)


    async def pause(self, message:Message) -> None:
        
        """Метод ставит текущую Свою игру на паузу"""
        
        game, question, game_type = self.get_current_game_and_question(
            message=message)
        if game and game_type == 2 and not game.paused and self.check_host(message=message):
            chat_id = message.channel.id
            game.paused = True
            game.host = None
            self.hosts.pop(chat_id)
            if self.game_states.get(chat_id):
                self.game_states.pop(chat_id)
            if self.answering_player.get(chat_id):
                self.answering_player.pop(chat_id)
            if self.played.get(chat_id):
                self.played.pop(chat_id)
            db_mg_update_game(game)
            reply = 'Игра поставлена на паузу. Чтобы возобновить игру используйте команду "!своя игра". '
            reply += 'Игра возобновится с того места, на котором вы закончили.'
            await message.channel.send(reply)
        
    
    async def table(self, message: Message) -> None:
        
        """Метод выводит в чат таблицу результатов в Своей игре."""
        
        game, question, game_type = self.get_current_game_and_question(
            message=message)
        if game and game_type == 2 and not game.paused:
            scores = db_mg_get_scores(game=game)
            reply = '```Текущие результаты таковы:\n'
            for score in scores:
                reply += '{:3} - {}\n'.format(score.score, score.player.real_name)
            reply += '```'
            await message.channel.send(reply)
    
    
    async def themes(self, message: Message) -> None:
        
        """Метод выводит в чат список тем запущенной игры."""
        
        game, question, game_type = self.get_current_game_and_question(
            message=message)
        if game and game_type == 2 and not game.paused:
            themes_text = get_themes_text(game)
            await message.channel.send(themes_text)
        else:
            await message.channel.send('Своя игра еще не начата, так что и тем вам не будет.',
                                       mention_author=True)
    
    
    async def theme(self, message: Message) -> None:
        
        """Метод запроса темы в Своей игре. Запускается по команде типа "!3", которая соответствует теме №3. 
        Запрашивает текущую игру и проверяет тему на предмет того, что она уже сыграна. 
        Выдает в чат следующий вопрос запрошенной темы. """
        
        chat_id = message.channel.id
        game, question, game_type = self.get_current_game_and_question(
            message=message)
        if game and game_type == 2 and not game.paused and self.check_host(message=message):
            theme_index = int(message.content.split('!')[1])
            theme, question = get_theme_by_index(game=game, theme_index=theme_index)
            if question:
                db_mg_set_current_theme(game=game, theme=theme)
                db_mg_set_current_question(theme=theme, question=question)
                self.game_states[chat_id] = game_state.PAUSE
                await self.ask_mg_question(message=message, question=question)
            else:
                await message.channel.send('В этой теме уже сыграны все вопросы. Нужно выбрать другую.',
                                           mention_author=True)
        else:
            await message.channel.send('Надо сначала начать Свою игру, а уж только после этого просить тему.',
                                       mention_author=True)

    
    async def my_game(self, message: Message) -> None:
        
        """Метод запуска Своей игры. Проверяет, есть ли в чате запущенная Своя игра. 
        Если запущенной игры нет, создает новую игру, делает отправившего команду игрока ведущим."""
        
        chat_id = message.channel.id
        player_id = message.author.id
        game = get_game_by_chat(chat_id=chat_id)
        if not game:
            game = setup_game(chat_id=chat_id, host_id=player_id)
        elif game.paused:
            game.paused = False
            game.host = get_player(player_id)
            db_mg_update_game(game)
        if game.host.real_name:
            host_name = game.host.real_name
        else:
            host_name = update_player_name(
                player_id=player_id, real_name=message.author.name)
        themes_text = get_themes_text(game)
        themes_text += f'Ведуйщий: {host_name}'
        self.hosts[chat_id] = player_id
        await message.channel.send(themes_text)

    
    async def fact(self, message: Message) -> None:
        
        """Метод запрашивает случайный факт на сайте "Музей фактов" и выдает его в чат. 
        Сейчас не работает так как сайт переехал и сменил верстку."""
        
        fact_text = None
        while not fact_text:
            r_number = r(1, 7495)
            fact_link = 'https://facts.museum/' + str(r_number)
            fact_img = 'https://facts.museum/img/facts/' + \
                str(r_number) + '.jpg'
            fact = requests.get(fact_link)
            soup = BeautifulSoup(fact.text, 'lxml')
            if soup.find('p', class_='content'):
                fact_text = soup.find('p', class_='content').text
        fact_text += '\n' + fact_link
        embed = Embed(color=0x07c610, title='Случайный факт',
                      description=fact_text)
        embed.set_image(url=fact_img)
        await message.channel.send(embed=embed)

    
    async def question(self, message: Message) -> None:
        
        """Метод выдает в чат вопрос "Что? Где? Когда?". Метод проверяет на наличие запущенной полноценной игры.
        Если игра есть, то задается следующий вопрос из этой игры. Если игры нет, то на сате базы вопросов запрашивается
        случайный вопрос и отправляется в чат."""
        
        chat_id = message.channel.id
        current_game = Game.current_game.get(chat_id)
        full_game = False
        current_question = None
        if current_game:
            full_game = current_game.is_full_game
            current_question = current_game.current_question
        if current_question:
            await message.channel.send('Не торопись-ка! Сначала ответьте на предыдущий вопрос.',
                                       mention_author=True)
        else:
            if not full_game:
                current_game = Game(chat_id, False)
                if current_game.error:
                    await message.channel.send('Похоже, что база вопросов сейчас недоступна. Попробуйте позже.',
                                               mention_author=True)
                    return
            question, number, number_of_questions = current_game.get_question()
            if number:
                number_string = f'Номер вопроса: {str(number)} из {str(number_of_questions)}'
            else:
                number_string = 'Случайный вопрос'
            if question.picture:
                embed = Embed(color=0xff9900)
                embed.set_image(url=question.picture)
                await message.channel.send(embed=embed)
            await message.channel.send(f'{number_string}\n{question.question}')

    
    async def repeat(self, message: Message) -> None:
        current_game = Game.current_game
        chat_id = message.channel.id
        current_question = None
        if current_game.get(chat_id):
            current_question = current_game[chat_id].current_question
        if current_question:
            question, number, number_of_questions = current_game[chat_id].get_question(
            )
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

    
    async def game(self, message: Message) -> None:
        chat_id = message.channel.id
        current_game, current_question, game_type = self.get_current_game_and_question(
            message=message)
        if game_type == 1:
            await message.channel.send('Прекратите хулиганить! У вас уже есть запущенная игра.',
                                       mention_author=True)
        elif game_type == 2:
            await message.channel.send('Сначала доиграйте в Свою игру',
                                       mention_author=True)
        else:
            game = Game(chat_id, True)
            if game.error:
                await message.channel.send('Похоже, что база вопросов сейчас недоступна. Попробуйте позже.',
                                           mention_author=True)
                return
            question, number, number_of_questions = game.get_question()
            number_string = f'Номер вопроса: {str(number)} из {str(number_of_questions)}'
            if question.picture:
                embed = Embed(color=0xff9900)
                embed.set_image(url=question.picture)
                await message.channel.send(embed=embed)
            await message.channel.send(f'{number_string}\n{question.question}')

    
    async def answer(self, message: Message) -> None:
        chat_id = message.channel.id
        current_game = Game.current_game.get(chat_id)
        if current_game:
            current_question = current_game.current_question
        else:
            current_question = None
        if not current_question:
            await message.channel.send('Вам еще не задали вопрос, а вы уже хотите ответ.')
        else:
            answer_string = current_question.get_answer()
            await message.channel.send(answer_string)
            if current_game.is_full_game:
                current_game.current_question = None
            else:
                Game.current_game[chat_id] = None

    
    async def finish(self, message: Message) -> None:
        current_game, question, game_type = self.get_current_game_and_question(
            message=message)
        chat_id = message.channel.id
        if game_type == 0:
            await message.channel.send('Вы еще не начали игру, а уже хотите ее закончить.')
        elif game_type == 1:
            await message.channel.send('Игра закончена.')
            current_game.get(chat_id).end_game()
            current_game.pop(chat_id, False)
        elif game_type == 2: 
            if self.check_host(message):
                results = db_mg_end_game(current_game)
                await message.channel.send('Игра закончена.')
                self.hosts.pop[chat_id]
            else:
                await message.channel.send('Чтобы закончить игру нужно быть ее ведущим',
                                       mention_author=True)

    
    async def difficulty(self, message: Message) -> None:
        
        """Метод вызывается по команде '!сложность n' 
        и устанавливает для чата сложность вопросов "Что? Где? Когда?" """
        
        chat_id = message.channel.id
        difficulty = int(message.content[11])
        difficulty_list = ['любые', 'очень простые',
                           'простые', 'средние', 'сложные', 'очень сложные']
        set_chat_difficulty(chat_id, difficulty)
        if difficulty == 0:
            await message.channel.send('В этот чат будут приходить игры и вопросы любой сложности.')
        else:
            await message.channel.send(f'В этот чат будут приходить {difficulty_list[difficulty]} игры и вопросы.')

    
    async def answers_table(self, message: Message) -> None:
        
        """Метод вызывается по команде '!рекорды' 
        и выводит в чат таблицу результатов по игре "Что? Где? Когда?" """
        
        chat_id = message.channel.id
        data = get_chat_answers_table(chat_id)
        table = '**Количество правильных ответов по игрокам:**\n'
        for item in data.all():
            table += '{:3} - {}\n'.format(item[0], item[1])
        await message.channel.send(table)

    
    async def plain_text(self, message: Message) -> None:
        
        """Метод вызывается если в чат пришел простой текст, без '!' в начале.
        Реализованы три ветки логики:
        
        - Ответ на вопрос "Что? Где? Когда?"
        
        - Нажатие кнопки в Своей игре
        
        - Ответ на вопрос в Своей игре"""
        
        chat_id = message.channel.id
        player_id = message.author.id
        player_name = message.author.name
        game, current_question, game_type = self.get_current_game_and_question(
            message=message)
        if current_question and game_type == 1:
            right_answer = current_question.answer
            if self.check_answer(message.content, right_answer):
                answer_string = current_question.get_answer()
                player_answers = player_add_answer(player_id, chat_id)
                answer_string = f'Правильно!\n{answer_string}\n**{player_name}**, это твой **{player_answers}** правильный ответ.'
                await message.channel.send(answer_string)
                game.current_question = None
        elif game_type == 2 and self.game_states.get(chat_id) == game_state.WAITING_FOR_BUTTON:
            await self.mg_button_pressed(message=message, question=current_question)
        elif game_type == 2 and self.game_states.get(chat_id) == game_state.ANSWERING and self.check_answering_player(message):
            await self.check_mg_answer(message=message, question=current_question)

    
    async def check_mg_answer(self, message: Message, question: DBQuestion) -> bool:
        
        """Метод проверяет ответ на вопрос Своей игры."""
        
        chat_id = message.channel.id
        player_id = message.author.id
        player_name = message.author.display_name
        right_answer = question.answer
        answer_checked = self.check_answer(
            input_string=message.content, answer_string=right_answer)
        if answer_checked:
            answer_status = db_mg_question_answered(
                question=question, player_id=player_id)
            self.game_states.pop(chat_id)
            self.answering_player.pop(chat_id)
            self.clear_played(chat_id=chat_id)
            reply = f'{choice(emojis.get("right"))} Правильно! {player_name} зарабатывает {question.price} баллов.\n'
            reply += f'Правильный ответ: {question.answer}\n'
            if answer_status == question_answered.THEME:
                reply += f'Тема "{question.theme.name}" закончена. Нужно выбрать другую тему.\n'
            await message.channel.send(reply)
            return True
        else:
            db_mg_wrong_answer(question=question, player_id=player_id)
            reply = f'{choice(emojis.get("wrong"))} Не-а! {player_name} теряет {question.price} баллов.\n'
            reply += f'Оставшиеся игроки могут нажать на кнопку после БИПа.'
            self.add_played(chat_id=chat_id, player_id=player_id)
            await message.channel.send(reply)
            await self.beep(question=question, message=message)
            return False

    
    async def ask_mg_question(self, message: Message, question: DBQuestion):
        
        """Метод задает новый вопрос и запускает БИП."""
        
        chat_id = message.channel.id
        reply = get_question_text(question)
        self.answering_player[chat_id] = None
        await message.channel.send(reply)
        await self.beep(question=question, message=message)

    
    async def mg_button_pressed(self, message: Message, question:DBQuestion):
        
        """Метод срабатывает когда один из игроков нажал кнопку. 
        При этом происходит проверка на то, что игрок уже пытался ответить на этот вопрос."""
        
        chat_id = message.channel.id
        player_id = message.author.id
        if self.check_played(chat_id=chat_id, player_id=player_id):
            return
        display_name = message.author.display_name
        self.answering_player[chat_id] = {
            'id': player_id, 'name': display_name}
        sleep(1)
        final_player = self.answering_player.get(chat_id)
        if final_player and self.game_states[chat_id] != game_state.ANSWERING:
            self.game_states[chat_id] = game_state.ANSWERING
            await message.channel.send(f':thumbsup: Отвечает {final_player["name"]}')
            await self.beep_timer(question=question, message=message, state=game_state.ANSWERING)

    
    async def beep(self, question: DBQuestion, message: Message):
        
        """Метод выдерживает паузу и делает БИП, который означает, что игроки могут нажимать на кнопку.
        Пауза зависит от длины вопроса (количество символов в вопросе делится на 13)."""
        
        chat_id = message.channel.id
        pause = len(question.text)//13
        self.game_states[chat_id] = game_state.PAUSE
        sleep(pause)
        await message.channel.send('БИП!!!💡')
        self.game_states[chat_id] = game_state.WAITING_FOR_BUTTON
        await self.beep_timer(question=question, message=message, state=game_state.WAITING_FOR_BUTTON)

    
    async def beep_timer(self, question:DBQuestion, message:Message, state:game_state):
        
        """Метод запускает дополнительный процесс таймера и отслеживает, 
        попытался ли кто-то из игроков ответить на вопрос. Если никто не хочет отвечать,
        вопрос снимается из игры, в чат отправляется сообщение с правильным ответом.
        Длительность таймера в секундах регулируется значением n в range(n)."""
        
        chat_id = message.channel.id
        player_id = message.author.id
        player_name = message.author.display_name
        for _ in range(timer_values[state]):
            if self.game_states.get(chat_id) != state:
                return
            await async_sleep(1)
        if state == game_state.WAITING_FOR_BUTTON:
            skipped_status = db_mg_skip_question(question=question)
            self.clear_played(chat_id=chat_id)
            self.game_states[chat_id] = None
            reply = f':stopwatch:  Время вышло.\n'
            reply += f'Правильный ответ: {question.answer}\n'
            if skipped_status == question_answered.THEME:
                reply += f'Тема "{question.theme.name}" закончена. Нужно выбрать другую тему.\n'
            await message.channel.send(reply)
        elif state == game_state.ANSWERING:
            db_mg_wrong_answer(question=question, player_id=player_id)
            reply = f'{choice(emojis.get("wrong"))} {player_name} слишком долго думал и потерял {question.price} баллов.\n'
            reply += f'Оставшиеся игроки могут нажать на кнопку после БИПа.'
            self.add_played(chat_id=chat_id, player_id=player_id)
            await message.channel.send(reply)
            await self.beep(question=question, message=message)
            
            return False

    
    def check_answering_player(self, message:Message) -> bool:
        chat_id = message.channel.id
        player_id = message.author.id
        answering_player = self.answering_player.get(chat_id)
        if answering_player:
            if answering_player['id'] == player_id:
                return True
        return False
    
    
    def add_played(self, chat_id: str, player_id: str):
        if not self.played.get(chat_id):
            self.played[chat_id] = []
        self.played[chat_id].append(player_id)

    
    def clear_played(self, chat_id: str):
        if self.played.get(chat_id):
            self.played.pop(chat_id)

    
    def check_played(self, chat_id: str, player_id: str) -> bool:
        played_list = self.played.get(chat_id)
        if played_list:
            if player_id in played_list:
                return True
        return False

    
    def get_current_game_and_question(self, message: Message) -> tuple:
        chat_id = message.channel.id
        chgk_game = Game.current_game.get(chat_id)
        my_game = get_game_by_chat(chat_id=chat_id)
        if chgk_game:
            return chgk_game, chgk_game.current_question, 1
        elif my_game:
            question = get_mg_question(my_game)
            return my_game, question, 2
        return None, None, 0

    
    def check_host(self, message: Message) -> bool:
        player_id = message.author.id
        chat_id = message.channel.id
        if self.hosts.get(chat_id) == player_id:
            return True
        return False

    
    def check_answer(self, input_string: str, answer_string: str) -> bool:
        answer_list = self.normalize_string(answer_string.lower())
        input_list = self.normalize_string(input_string.lower())
        if len(input_list) == 0:
            return False
        for word in input_list:
            if not word in answer_list:
                return False
        return True

    
    def normalize_string(self, input_string: str) -> list:
        word_list = re.split(r'\W+', input_string)
        clean_list = [word for word in word_list if word != '']
        result_list = []
        for word in clean_list:
            result_word = self.morph.parse(word)[0].normal_form
            result_list.append(result_word)
        return result_list


def main():
    # Запускаем бота
    bot = Bot()
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
