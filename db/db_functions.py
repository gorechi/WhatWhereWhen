from db.db import new_session as session, DBChat, DBPlayer, DBResult
from sqlalchemy import select, desc

def update_player_name(player_id:str, real_name:str) -> str:
    player = get_player(player_id=player_id)
    if player.real_name != real_name:
        player.real_name = real_name
        session.add(player)
        session.commit()
    return player.real_name


def get_chat(chat_id: str) -> bool:
    chat = session.query(DBChat).filter(DBChat.chat_id == str(chat_id)).first()
    if not chat:
        chat = DBChat(chat_id=chat_id)
        session.add(chat)
        session.commit()
    return chat


def set_chat_difficulty(chat_id: str, dif: int) -> bool:
    chat = get_chat(chat_id)
    chat.difficulty = dif
    session.add(chat)
    session.commit()
    return True


def set_player_name(player_id: str, player_name: str) -> bool:
    player = get_player(player_id)
    player.real_name = player_name
    session.add(player)
    session.commit()
    return True


def get_player(player_id: str) -> DBPlayer:
    player = session.query(DBPlayer).filter(
        DBPlayer.player_id == player_id).first()
    if not player:
        player = DBPlayer(player_id=player_id)
        session.add(player)
        session.commit()
    return player


def get_player_name(player_id: str) -> str:
    player = get_player(player_id)
    if player.real_name == None:
        return player.player_id
    else:
        return player.real_name


def player_add_answer(player_id: str, chat_id: str) -> int:
    result = get_result(player_id, chat_id)
    result.answers += 1
    session.add(result)
    session.commit()
    return result.answers


def get_result(player_id: str, chat_id: str) -> DBResult:
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
    chat = get_chat(chat_id)
    data = session.execute(select(DBResult.answers, DBPlayer.real_name).join(
            DBResult.player).where(DBResult.chat == chat).order_by(desc(DBResult.answers)))
    return data
    