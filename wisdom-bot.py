import discord
from discord.ext import commands
from config import TOKEN, UNSPLASH_KEY
import json
import requests
from pogovorki_functions import *

# Читаем файл
pogovorki = readfile('pogovorki.txt', True, '|')
l = len(pogovorki)
print('Всего поговорок: ' + str(l))
print('Всего вариантов бреда: ' + str(l*l-l))


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)

        if message.content.startswith('!wisdom'):
            wisdom = trim(pogovorki[dice(0, len(pogovorki) - 1)][0] + pogovorki[dice(0, len(pogovorki) - 1)][1])
            await message.channel.send(wisdom, mention_author=True)

        if message.content.startswith('!лиса'):
            response = requests.get('https://some-random-api.ml/img/fox')  # Get-запрос
            json_data = json.loads(response.text)  # Извлекаем JSON
            embed = discord.Embed(color=0xff9900, title='Random Fox')  # Создание Embed'a
            embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
            await message.channel.send (embed=embed)  # Отправляем Embed
            await message.channel.send ('Fox!', mention_author=True)

        if message.content.startswith('!frog'):
            response = requests.get('https://api.unsplash.com/photos/random/?query=frog&client_id=' + UNSPLASH_KEY)
            print(response.status_code)
            if response.status_code == 200:
                json_data = json.loads(response.text)  # Извлекаем JSON
                embed = discord.Embed(color=0x07c610, title='Random Frog')  # Создание Embed'a
                embed.set_image(url=json_data['urls']['regular'])  # Устанавливаем картинку Embed'a
                await message.channel.send (embed=embed)  # Отправляем Embed
                await message.channel.send ('Frog!', mention_author=True)

client = MyClient()
client.run(TOKEN)