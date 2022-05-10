
"""Вспомогательные функции для Своей игры"""

import re
import requests
import untangle
from discord import Message
from db.db import DBMyGame, DBQuestion, DBScore, DBTheme
from db.db_functions_mg import create_game_from_list, db_mg_end_game, db_mg_get_scores, db_mg_set_winner_score


def split_questions(text: str) -> list:
    
    """Функция делит вопросы, пришедшие с сервера в виде одной строки."""
    
    result = re.split('\n   \d+. ', text)
    return result


def setup_game(chat_id:str, host_id:str) -> dict:
    
    """Функция запрашивает с сайта вопросы игры и формирует из них объект игры"""
    
    request_string = 'https://db.chgk.info/xml/random/types5/limit15'
    request = requests.get(request_string)
    if request.status_code != 200:
        return False
    request_text = request.text
    obj = untangle.parse(request_text)
    themes = []
    for theme in obj.search.question:
        questions = split_questions(theme.Question.cdata)
        answers = split_questions(theme.Answer.cdata)
        parsed_theme = {}
        parsed_theme['theme'] = re.sub('\n', ' ', questions[0])
        questions.pop(0)
        parsed_theme['questions'] = []
        for index, question in enumerate(questions):
            question_dict = {}
            if index < 5:
                question = re.sub('\n', ' ', question)
                answer = re.sub('   1. ', '', answers[index])
                question_dict['question'] = question            
                question_dict['answer'] = answer
                parsed_theme['questions'].append(question_dict)
        themes.append(parsed_theme)
    game = create_game_from_list(chat_id=chat_id, host_id=host_id, themes_list=themes)
    return game


def get_themes_text(game:DBMyGame) -> str:
    
    """Функция формирует список тем Своей игры. Сыгранные темы перечеркиваются."""
    
    themes = game.themes
    themes_text = 'Темы игры:\n'
    for theme in themes:
        tildas = ''
        if theme.is_played:
            tildas = '~~'
        themes_text += f'{tildas}{theme.theme_index}. {theme.name}{tildas}\n'
    return themes_text


def get_current_theme(game:DBMyGame) -> DBTheme:
    
    """Функция возвращает текущую тему для игры."""
    
    game_current_theme = game.current_theme
    if game_current_theme:
        current_theme = game_current_theme.theme
        return current_theme
    return None


def get_current_question(theme:DBTheme) -> DBQuestion:
    
    """Функция возвращает текущий вопрос для темы."""
    
    theme_current_question = theme.current_question
    if theme_current_question:
        current_question = theme_current_question.question
        return current_question
    return None 
    
    
def get_mg_question(game:DBMyGame) -> DBQuestion:
    
    """Функция возвращает текущий вопрос для игры."""
    
    current_theme = get_current_theme(game=game)
    if not current_theme:
        return False
    current_question = get_current_question(theme=current_theme)
    if current_question:
        return current_question
    return None


def get_theme_by_index(game:DBMyGame, theme_index:int) -> DBTheme:
    
    """Функция возвращает тему игры по ее порядковому номеру."""
    
    theme = game.themes[theme_index-1]
    if theme.is_played:
        return None, None
    question = get_theme_next_question(theme)
    if not question:
        theme.is_played = True
        return None, None
    return theme, question


def get_theme_next_question(theme:DBTheme) -> DBQuestion:
    
    """Функция возвращает следующий вопрос из указанной темы."""
    
    questions = [q for q in theme.questions if not q.is_answered]
    if questions:
        return questions[0]
    else:
        return None


def get_question_text(question:DBQuestion) -> str:
    
    """Функция формирует текст вопроса для его вывода в чат."""
    
    question_text = f'Тема: {question.theme.name}\n'
    question_text += f'Вопрос за {question.price}:\n'
    question_text += '=' * 30 + '\n'
    question_text += f'{question.text}'
    return question_text


def get_scores_table(game:DBMyGame) -> str:
    
    """Функция формирует строку для вывода в чат таблицы результатов Своей игры."""
    
    scores = db_mg_get_scores(game=game)
    reply = '```Текущие результаты таковы:\n'
    for score in scores:
        reply += '{:4} - {}\n'.format(score.score, score.player.real_name)
    reply += '```'
    return reply        