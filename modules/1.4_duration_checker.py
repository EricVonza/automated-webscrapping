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
    # This will depend on the structure of the website, which you need to inspect
    timer = soup.find_all(class_='c-events-scoreboard__subitem')

    # Loop through each match and extract the current quarter information
    for duration in timer:
        # Find the specific element that contains the current quarter info
        # Example: (adjust based on the actual structure)
        current_timer = duration.find(class_='c-events__time')
        
        # Check if the current_quarter element exists
        if "2 Quarter 14:" in current_timer or "2 Quarter 15:" in current_timer or "3 Quarter 24:" in current_timer or "3 Quarter 25:" in current_timer:
            # Extract and print the current quarter information
            print(current_timer.text.strip())
