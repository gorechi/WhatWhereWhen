from db.db import DBMyGame, DBPlayer, DBQuestion, DBScore, DBTheme, DBCurrentTheme, DBCurrentQuestion
from db.db import new_session as session
from db.db_functions import get_chat, get_player
from options import question_answered
from sqlalchemy import desc


def db_mg_get_scores(game:DBMyGame) -> list:
    scores = session.query(DBScore).filter(DBScore.game == game).order_by(desc(DBScore.score)).all()
    print(scores)
    return scores
    

def db_mg_skip_question(question:DBQuestion) -> question_answered:
    theme = question.theme
    question.is_answered = True
    session.commit()
    theme_is_played = db_mg_check_theme_is_played(theme)
    if theme_is_played:
        return question_answered.THEME
    return question_answered.ONLY_QUESTION


def db_mg_question_answered(question:DBQuestion, player_id:str) -> question_answered:
    theme = question.theme
    game = theme.game
    score = get_score(player_id=player_id, game=game)
    db_mg_update_score(score=score, value=question.price)
    question.is_answered = True
    session.commit()
    theme_is_played = db_mg_check_theme_is_played(theme)
    if theme_is_played:
        return question_answered.THEME
    return question_answered.ONLY_QUESTION

    
def db_mg_wrong_answer(question:DBQuestion, player_id:str):
    theme = question.theme
    game = theme.game
    score = get_score(player_id=player_id, game=game)
    db_mg_update_score(score=score, value=(0-question.price))


def db_mg_update_score(score:DBScore, value:int):
    score.score += value
    session.add(score)
    session.commit()


def db_mg_check_theme_is_played(theme:DBTheme) -> bool:
    unanswered_question = session.query(DBQuestion).filter(
                            DBQuestion.theme == theme,
                            DBQuestion.is_answered == False
                            ).first()
    if not theme.is_played and not unanswered_question:
        theme.is_played = True
        db_mg_delete_current_theme(theme.game)
    if theme.is_played:
        return True
    return False

def db_mg_end_game(game:DBMyGame) -> list:
    db_mg_delete_game(game=game)
    return

def db_mg_delete_game(game:DBMyGame):
    session.delete(game)
    session.commit()


def db_mg_delete_current_theme(game: DBMyGame):
    current_theme = session.query(DBCurrentTheme).filter(DBCurrentTheme.game == game).first()
    if current_theme:
        session.delete(current_theme)
        session.commit()


def db_mg_set_current_theme(game: DBMyGame, theme: DBTheme) -> DBCurrentTheme:
    current_theme = session.query(DBCurrentTheme).filter(DBCurrentTheme.game == game).first()
    if current_theme:
        if current_theme.theme == theme:
            return current_theme
        else:
            current_theme.theme = theme
    else:    
        current_theme = DBCurrentTheme(game=game, theme=theme)
    session.add(current_theme)
    session.commit()
    return current_theme


def db_mg_set_current_question(theme: DBTheme, question: DBQuestion) -> DBCurrentQuestion:
    current_question = session.query(DBCurrentQuestion).filter(
        DBCurrentQuestion.theme == theme, 
        DBCurrentQuestion.question == question).first()
    if current_question:
        if current_question.question == question:
            return current_question
        else:
            current_question.question = question
    else:
        current_question = DBCurrentQuestion(theme=theme, question=question)
    session.add(current_question)
    session.commit()
    return current_question


def db_mg_update_game(game: DBMyGame):
    session.add(game)
    session.commit()


def get_game_themes(game: DBMyGame) -> list:
    result_game = session.query(DBMyGame).filter(
        DBMyGame.id == game.id).first()
    themes = result_game.themes
    return themes


def get_game_by_chat(chat_id: str) -> DBMyGame:
    chat = get_chat(chat_id=chat_id)
    game = session.query(DBMyGame).filter(DBMyGame.chat == chat).first()
    return game


def get_score(player_id: str, game: DBMyGame) -> DBScore:
    player = get_player(player_id)
    if not game:
        return False
    score = session.query(DBScore).filter(
        DBScore.player == player, 
        DBScore.game == game).first()
    if not score:
        score = DBScore(game=game, player=player)
        session.add(score)
        session.commit()
    return score


def change_score(player_id: str, game_id: str, value: int):
    score = get_score(player_id=player_id, game_id=game_id)
    if not score:
        return False
    score.score += value
    session.add(score)
    session.commit()


def create_game_from_list(chat_id: str, host_id: str, themes_list: list) -> DBMyGame:
    chat = get_chat(chat_id)
    host = get_player(host_id)
    game = DBMyGame(chat=chat, host=host)
    session.add(game)
    for theme_index, theme in enumerate(themes_list):
        new_theme = DBTheme(
            name=theme['theme'],
            game=game,
            theme_index=theme_index+1
        )
        session.add(new_theme)
        for i, question in enumerate(theme['questions']):
            new_question = DBQuestion(
                text=question['question'],
                answer=question['answer'],
                price=(i + 1)*10,
                theme=new_theme
            )
            session.add(new_question)
    session.commit()
    return game
