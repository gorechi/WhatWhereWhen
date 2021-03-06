# Бот "Что? Где? Когда?" для Discord

Бот подключается к серверу Discord и в полуавтоматическом режиме проводит тренировки по "Что? Где? Когда?".

Данные для проведения игр берутся с сайта https://db.chgk.info.

# Установка

После регистрации бота на сервере Discord (https://discord.com/developers/docs/getting-started#creating-an-app) необходимо создать в корневой папке бота файл settings.py и записать в него строку:

TOKEN = 'my_token'

где my_token - это токен бота, выданный ему при создании.

# Управление

Управление ботом осуществляется через команды:

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

