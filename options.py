from enum import Enum, auto

class game_state(Enum):
    
    """Энум состояний игры. 
    Используется для того, чтобы бот правильно реагировал на введенные команды.
    
    Значения:
    
    - PAUSE - игра находится на паузе и не реагирует на команды. Используется когда игра ожидает БИП.
    - ANSWERING - бот принимает ответ от игрока. В этом состоянии не принимаются никакие команды.
    Обрабатывается только сообщение от игрока, который нажал на кнопку, остальные сообщения игнорируются.
    - WAITING_FOR_BUTTON - бот ожидает нажания "кнопки". Команды управления ботом игнорируются."""
    
    PAUSE = auto()
    ANSWERING = auto()
    WAITING_FOR_BUTTON = auto()
    
class question_answered(Enum):
    
    """Энум проверки правильности ответа. 
    Используется для определения события, которое произошло в результате ответа игрока.
    
    Значения:
    
    - ONLY_QUESTION - игрок правильно ответил на вопрос, но это не последний вопрос в теме.
    - THEME - Игрок правильно ответил на вопрос и при этом закрылась тема. 
    Также используется если вопрос вообще не был отвечен, но в результате этого тема закрылась.
    - WRONG_ANSWER - Игрок неправильно ответил на вопрос."""
    
    ONLY_QUESTION = auto()
    THEME = auto()
    WRONG_ANSWER = auto()
    
"""Наборы эмодзи, которые бот использует для разных поводов"""

emojis = {
    'wrong': [
        ':rolling_eyes:',
        ':zany_face:',
        ':face_with_raised_eyebrow:',
        ':thinking:',
        ':thumbsdown:',
        ':man_gesturing_no:',
        ':man_facepalming:',
        ':hear_no_evil:',
        ':snowflake:',
        ':headstone:',
        ':toilet:',
        ':chart_with_downwards_trend:'
    ],
    'right': [
        ':grinning:',
        ':nerd:',
        ':hugging:',
        ':smile_cat:',
        ':clap:',
        ':thumbsup:',
        ':ok_hand:',
        ':muscle:',
        ':brain:',
        ':crown:',
        ':eagle:',
        ':star2:',
        ':fire:',
        ':trophy:',
        ':military_medal:',
        ':first_place:',
        ':rocket:',
        ':fireworks:',
        ':gem:',
        ':tada:',
        ':chart_with_upwards_trend:' 
    ]
}

"""Время в секундах, которое дается на действие игроков. По истечении этого времени бот сбрасывает вопрос.
Ключем является состояние, котором находится игра в момент запуска таймера."""

timer_values = {
    game_state.ANSWERING: 20,
    game_state.WAITING_FOR_BUTTON: 30
}