from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref
from sqlalchemy import Column, String, Integer, Boolean
import os

basedir = os.path.dirname(os.path.realpath(__file__))
connection_string = 'sqlite:///' + os.path.join(basedir, 'db.db')

engine = create_engine(connection_string, echo=False, future=True)

Session = sessionmaker()
new_session = Session(bind=engine)

Base = declarative_base()

class DBResult(Base):
    
    """
    Класс статистики игрока в отдельном чате. 
    
    Содержит:
    - chat_id - идетификатор объекта DBChat
    - player_id - идентификатор объекта DBPlayer
    - answers - количество правильных ответов в Что? Где? Когда?
    - mg_wins - количество побед в Своей игре
    
    Дополнительные связи:
    - player
    - chat
    """
    
    __tablename__ = 'results'
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer(), ForeignKey('chats.id'))
    player_id = Column(Integer(), ForeignKey('players.id'))
    answers = Column(Integer(), default=0)
    mg_wins = Column(Integer(), default=0)

    player = relationship('DBPlayer', 
                          uselist=False, 
                          backref=backref('player_results', 
                                          order_by=id, 
                                          cascade="all, delete-orphan"))
    chat = relationship('DBChat', 
                          uselist=False, 
                          backref=backref('chat_results', 
                                          order_by=id, 
                                          cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Результат: chat = {self.chat}, player = {self.player}, answers = {self.answers}>'


class DBChat(Base):
    
    """
    Класс чата. 
    
    Содержит:
    - chat_discord_id - идетификатор чата Discord
    - difficulty - сложность игр Что? Где? Когда? в этом чате.
    
    Дополнительные связи:
    - chat_results
    """
    
    __tablename__ = 'chats'
    id = Column(Integer(), primary_key=True)
    chat_discord_id = Column(String(), nullable=False, unique=True)
    difficulty = Column(Integer(), nullable=True, default=0)

    def __repr__(self):
        return f'<Чат: id = {self.chat_id}, difficulty = {self.difficulty}>'


class DBPlayer(Base):
    
    """
    Класс игрока. 
    
    Содержит:
    - player_discord_id - идентификатор игрока в Discord
    - real_name - ник игрока в Discord
    
    Дополнительные связи:
    - scores
    """
    
    __tablename__ = 'players'
    id = Column(Integer(), primary_key=True)
    player_discord_id = Column(String(50), nullable=False, unique=True)
    real_name = Column(String(50), nullable=True, unique=False)

    def __repr__(self):
        return f'<Игрок: name = {self.real_name}>'


class DBMyGame(Base):
    
    """
    Класс Своей игры. 
    
    Содержит:
    - chat_id - идетификатор объекта DBChat
    - host_id - ведущий игры, идентификатор объекта DBPlayer
    - paused - признак того, что игра находится на паузе 
    
    Дополнительные связи:
    - current_theme - текущая тема игры
    - scores - баллы игроков в данной игре
    """
    
    __tablename__ = 'mygame'
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer(), ForeignKey('chats.id'))
    host_id = Column(Integer(), ForeignKey('players.id'))
    paused = Column(Boolean(), default=False)
    chat = relationship('DBChat')
    host = relationship('DBPlayer')
    
    def __repr__(self):
        return f'<Моя игра: id = {self.id}, host = {self.host}>'


class DBTheme(Base):
    
    """
    Класс темы Своей игры. 
    
    Содержит:
    - game_id - идетификатор объекта DBMyGame
    - name - название темы
    - theme_index - порядковый номер темы
    - is_played - признак того, что в теме сыграны все вопросы
    
    Дополнительные связи:
    - questions - список всех вопросов игры
    - current_question - текущий вопрос в теме
    """
    
    __tablename__ = 'themes'
    id = Column(Integer(), primary_key=True)
    game_id = Column(Integer(), ForeignKey('mygame.id'))
    name = Column(String(150), nullable=False, unique=False)
    theme_index = Column(Integer())
    is_played = Column(Boolean(), default=False)
    game = relationship('DBMyGame', 
                        backref=backref('themes', 
                                        order_by=id, 
                                        cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<Тема: index = {self.theme_index}, name = {self.name}>'
    

class DBCurrentTheme(Base):
    
    """
    Класс текущей темы Своей игры. Служит для связки между темами и Своей игрой.
    
    Содержит:
    - game_id - идетификатор объекта DBMyGame
    - theme_id - идентификатор объекта DBTheme
    
    Дополнительные связи:
    - theme
    - game
    """
    
    __tablename__ = 'current_themes'
    id = Column(Integer(), primary_key=True)
    game_id = Column(Integer(), ForeignKey('mygame.id'))
    theme_id = Column(Integer(), ForeignKey('themes.id'))
    game = relationship('DBMyGame', uselist=False, 
                        backref=backref('current_theme', 
                                        order_by=game_id, 
                                        cascade="all, delete-orphan", 
                                        uselist=False))
    theme = relationship('DBTheme', uselist=False)
    
    def __repr__(self):
        return f'<Текущая тема: game = {self.game}, theme = {self.theme}>'


class DBQuestion(Base):
    
    """
    Класс вопроса Своей игры. 
    
    Содержит:
    - theme_id - идентификатор объекта DBTheme
    - text - текст вопроса
    - price - стоимость вопроса в баллах
    - answer - текст ответа на вопрос
    - is_answered - признак того, что на вопрос уже ответили
    
    Дополнительные связи:
    - theme - объект темы игры
    """
    
    __tablename__ = 'questions'
    id = Column(Integer(), primary_key=True)
    theme_id = Column(Integer(), ForeignKey('themes.id'))
    text = Column(String(), nullable=False, unique=False)
    price = Column(Integer(), nullable=False)
    answer = Column(String(), nullable=False)
    is_answered = Column(Boolean(), default=False)
    theme = relationship('DBTheme', 
                         backref=backref('questions', 
                                         order_by=id, 
                                         cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<Вопрос: price = {self.price}, is_answered = {self.is_answered}>'


class DBCurrentQuestion(Base):
    
    """
    Класс текущего вопроса Своей игры. Служит для связки между темами и вопросами.
    
    Содержит:
    - theme_id - идентификатор объекта DBTheme
    - question_id - идентификатор объекта DBQuestion
    
    Дополнительные связи:
    - theme
    - question
    """
    
    __tablename__ = 'current_questions'
    id = Column(Integer(), primary_key=True)
    theme_id = Column(Integer(), ForeignKey('themes.id'))
    question_id = Column(Integer(), ForeignKey('questions.id'))
    theme = relationship('DBTheme', 
                         uselist=False, 
                         backref=backref('current_question', 
                                         order_by=question_id, 
                                         cascade="all, delete-orphan", 
                                         uselist=False))
    question = relationship('DBQuestion', 
                            uselist=False)
    
    def __repr__(self):
        return f'<Текущий вопрос: theme = {self.theme}, question = {self.question}>'    


class DBScore(Base):
    
    """
    Класс счета игроков в Своей игре.
    
    Содержит:
    - game_id - идетификатор объекта DBMyGame
    - player_id - идентификатор объекта DBPlayer
    - score - количество баллов, которое набрал игрок
    
    Дополнительные связи:
    - player
    - game
    """
    
    __tablename__ = 'mg_scores'
    id = Column(Integer(), primary_key=True)
    game_id = Column(Integer(), ForeignKey('mygame.id'))
    player_id = Column(Integer(), ForeignKey('players.id'))
    score = Column(Integer(), default=0)
    player = relationship('DBPlayer', 
                          uselist=False, 
                          backref=backref('scores', 
                                          order_by=player_id, 
                                          cascade="all, delete-orphan"))
    game = relationship('DBMyGame', 
                        uselist=False, 
                        backref=backref('scores', 
                                        order_by=game_id, 
                                        cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<Счет: player = {self.player}, score = {self.score}>'
                         
