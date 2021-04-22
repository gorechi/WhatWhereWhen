import requests
from bs4 import BeautifulSoup

fact = requests.get('https://muzey-factov.ru/7478')

soup = BeautifulSoup(fact.text, 'lxml')

print(soup)
print('+'*40)
print(soup.find('p', class_='content').text)
print(soup.find('img').find('src'))