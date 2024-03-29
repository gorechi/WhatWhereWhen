# Бот для проведения "Что? Где? Когда?" и Своей игры в Discord

Бот подключается к серверу Discord и в полуавтоматическом режиме проводит тренировки по "Что? Где? Когда?" и Своей игре.

Данные для проведения игр берутся с сайта https://db.chgk.info.

# Установка

После регистрации бота на сервере Discord (https://discord.com/developers/docs/getting-started#creating-an-app) необходимо создать в корневой папке бота файл settings.py и записать в него строку:

TOKEN = 'my_token'

где my_token - это токен бота, выданный ему при создании.

# Управление

Управление ботом осуществляется через команды:

## **Команды для Что? Где? Когда?**

## **!игра** 

Бот создает новую игру и выдает в чат первый вопрос из нее. При этом происходит проверка на то, что в чате уже запущена другая игра. Если это так, то новая игра не создается. 

Под игрой подразумевается последовательность из вопросов, которые задаются один за другим. Как только будут получены ответы на все вопросы игры, она заканчивается.

## **!вопрос**

Бот выдает в чат вопрос. При этом реализована дополнительная логика:

•	если в чате есть вопрос, на который не получен ответ, то новый вопрос не задается;

•	если в чате нет созданной игры, то по этой команде бот задает один случайный вопрос с сайта (запрашивает случайную игру и берет из нее случайный вопрос). При этом он не начинает новую игру;

•	если в чате ведется игра, то бот выдает из нее следующий по порядку вопрос.

## **!повторить**

По этой команде бот повторяет текущий вопрос.

## **!ответ**

Бот дает ответ на текущий вопрос. В текст входит сам ответ, комментарии и пояснения, если они есть, а также информация об игре, из которой был взят вопрос. При этом, если не был задан вопрос, бот должен об этом сообщить.

## **!закончить**

По этой команде бот досрочно заканчивает игру.

## **!сложность N**

При помощи этой команды игроки могут установить уровень сложности вопросов, которые бот будет присылать им в чат. N – это число в интервале от 0 до 5. Если выбрана сложность 0, то будут приходить вопросы любой сложности, сложность 1 означает очень легкие вопросы, а сложность 5 – только самые сложные.

Также бот реагирует на любой текст, который ввел пользователь. Если был задан вопрос, бот берет текст поступающих в чат сообщений и ищет этот текст в ответе на вопрос. Если текст найден, то вопрос считается отвеченным и бот сообщает об этом игрокам.

## **Команды для Своей игры**

## **!своя игра**

Бот начинает новую Свою игру. Если в этот момент уже запущена игра в Что? Где? Когда? или Своя игра, то новая игра создана не будет. 

Игрок, отдавший команду становится владельцем игры, только он может отдавать команды боту и выбирать темы. Остальные игроки могут только отвечать на вопросы.

Индикатором успешно запущенной игры является то, что бот выводит в чат список тем игры. С этого момента владелец игры может выбирать темы.

## **!1**

Команда выбора темы. После ! может стоять число от 1 до 15.

Получив такую команду бот выводит в чат текст следующего вопроса выбранной темы. После этого бот делает паузу, длительность котрой зависит от длины текста вопроса. Подразумевается, что за это время все игроки должны прочитать вопрос. Выждав паузу бот выводит в чат "БИП!", что означает, что игроки могут наживать на кнопку. 

Нажатием на кнопку считается любое сообщение, отправленное в чат. Игрок, который прислал первое после БИПа сообщение, получает право ответить на вопрос.

На ответ на вопрос дается 30 секунд. В ответе не важен регистр букв. Если игрок отвечает правильно, бот начисляет ему победные очки. Если игрок отвечает неправильно, то бот еще раз выводит в чат вопрос и ожидает до БИПа. После повторного БИПа ранее неправильно ответивший игрок не может нажимать на кнопку.

Если после БИПа никто из игроков не нажал на кнопку в течение 20 секунд, бот снимает вопрос и ожидает от владельца игры нового выбора темы.

## **!!**

Команда ставит игру на паузу. Когда игра на паузе, в чате можно, например, запустить игру Что? Где? Когда?

Снять игру с паузы можно командой !своя игра, при этом игрок, отдавший эту команду станет новым владельцем игры. Это полезно в ситуациях, когда владелец игры неожиданно покидает чат. В этом случае достаточно поставить игру на паузу и снять ее с паузы - у игры будет новый владелец.

## **!таблица**

По этой команде бот выводит в чат таблицу результатов игроков.