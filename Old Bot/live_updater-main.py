from cgitb import text
import requests
from bs4 import BeautifulSoup
from time import sleep

def stock_title():
    url ="https://1xbet.co.ke/live/basketball"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")
    home_away_teams =  soup.find_all(class_="c-events__teams")
    scores =  soup.find_all(class_="c-events-scoreboard__cell")

    return home_away_teams 
    

home_away_teams = stock_title()
scores = stock_title()
for t,div in enumerate(home_away_teams):
    text = div.get_text(separator=' \n     ', strip=True)
    cleaned_text = text.replace('Including Overtime', '').strip()
    print(f" {t}: {cleaned_text}" )

scores = stock_title()
for s, div in enumerate(scores):
    text = div.get_text(separator='', strip=True)
    cleaned_text = text.replace('', '').strip()
    print(f" {s}")

    #print(f" {t}: {cleaned_text} {s}")
#while True:
    #new_title = stock_title
    #if new_title != title:
        #title = stock_title()
        #print("\nOVER Game detected "+str(title)+"Total median points are" )
       #title = title.replace('Including Overtime','')
       #print('New Str:{title}')
        #sleep(60)






