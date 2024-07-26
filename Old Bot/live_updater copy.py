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
    divs =  soup.find_all('span' , class_="n")


    return divs

divs = stock_title()
for i, div in enumerate(divs):
    text = div.get_text(separator=' ', strip=True)
    cleaned_text = text.replace('Including Overtime', '').strip()
    print(f" {i}: {cleaned_text}")

#while True:
    #new_title = stock_title
    #if new_title != title:
        #title = stock_title()
        #print("\nOVER Game detected "+str(title)+"Total median points are" )
       #title = title.replace('Including Overtime','')
       #print('New Str:{title}')
        #sleep(60)






