from db.db import new_session as session, DBChat, DBPlayer, DBResult
from sqlalchemy import select, desc

"""Функции базы данных, связанные с "Что? Где? Когда?" """

def update_player_name(player_id:str, real_name:str) -> str:
    
    """Функция записывает в базу имя игрока."""
    
    player = get_player(player_id=player_id)
    if player.real_name != real_name:
        player.real_name = real_name
        session.add(player)
        session.commit()
    return player.real_name


def get_chat(chat_id: str) -> DBChat:
    
    """Функция возвращает объект чата DBChat по его идентификатору в Discord"""
    
    chat = session.query(DBChat).filter(DBChat.chat_discord_id == str(chat_id)).first()
    if not chat:
        chat = DBChat(chat_discord_id=chat_id)
        session.add(chat)
        session.commit()
    return chat


def set_chat_difficulty(chat_id: str, dif: int) -> bool:
    
    """Функция устанавливает сложность вопросов в чате."""
    
    chat = get_chat(chat_id)
    chat.difficulty = dif
    session.add(chat)
    session.commit()
    return True


def get_player(player_id: str) -> DBPlayer:
    
    """Функция возвращает объект игрока DBPlayer по его идентификатору в Discord."""
    
    player = session.query(DBPlayer).filter(
        DBPlayer.player_discord_id == player_id).first()
    if not player:
        player = DBPlayer(player_discord_id=player_id)
        session.add(player)
        session.commit()
    return player


def get_player_name(player_id: str) -> str:
    
    """Функция получения имени игрока."""
    
    player = get_player(player_id)
    if player.real_name == None:
        return player.player_id
    else:
        return player.real_name


def player_add_answer(player_id: str, chat_id: str) -> int:
    
    """Функция добавляет правильный ответ игрока в базу."""
    
    result = get_result(player_id, chat_id)
    result.answers += 1
    session.add(result)
    session.commit()
    return result.answers


def get_result(player_id: str, chat_id: str) -> DBResult:
    
    """Функция получения результатов игрока по идентификаторам игрока и чата."""
    
    chat = get_chat(chat_id)
    player = get_player(player_id)
    result = session.query(DBResult).filter(
        player == player,
        chat == chat).first()
    if not result:
        result = DBResult(player=player, chat=chat)
        session.add(result)
        session.commit()
    return result


def get_chat_answers_table(chat_id: str) -> list:
    
    """Функция получения таблицы результатов игроков в конкретном чате."""
    
    chat = get_chat(chat_id)
    data = session.execute(select(DBResult.answers, DBPlayer.real_name).join(
            DBResult.player).where(DBResult.chat == chat).order_by(desc(DBResult.answers)))
    return data
    