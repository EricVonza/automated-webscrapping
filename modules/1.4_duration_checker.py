import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section that contains the basketball match information
    timer = soup.find_all(class_='c-events-scoreboard__subitem')

    # Loop through each match and extract the current quarter information
    for duration in timer:
        # Find the specific element that contains the current quarter info
        current_timer = duration.find(class_='c-events__time')
        
        # Check if the element exists
        if current_timer:
            # Extract text from the element and check the conditions
            timer_text = current_timer.text.strip()
            if "2 Quarter 14:" in timer_text or "2 Quarter 15:" in timer_text or "3 Quarter 24:" in timer_text or "3 Quarter 25:" in timer_text:
                # Print the current quarter information
                print(timer_text)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
