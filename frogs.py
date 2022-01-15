# Ветка, в которой бот реагирует на команду !лягушка или !лягуха и присылает случайную фотографию лягушки
if message.content.startswith('!лягу'):
    response = requests.get('https://api.unsplash.com/photos/random/?query=frog&client_id=' + UNSPLASH_KEY)
    if response.status_code == 200:
        json_data = json.loads(response.text)  # Извлекаем JSON
        embed = discord.Embed(color=0x07c610, title='Случайная лягуха')  # Создание Embed'a
        embed.set_image(url=json_data['urls']['regular'])  # Устанавливаем картинку Embed'a
        await message.channel.send(embed=embed)  # Отправляем Embed
