#pip install bs4
#pip install requests

import requests
from bs4 import BeautifulSoup

URL = 'https://1xbet.co.ke/live/basketball'

page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

post = soup.find("div", class_="c-events-scoreboard__item")

title = post.find("span", class_="c-events__teams").text.strip()

print(title)




