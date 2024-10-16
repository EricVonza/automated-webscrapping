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
    matches = soup.find_all(class_='c-events__name')

    # Loop through each match and extract the current teams information
    for match in matches:
        # Find the specific element that contains the teams info
        teams = match.find('span', class_='c-events__teams')
        
        # Check if the teams element exists
        if teams:
            # Extract the text and remove "Including Overtime" if present
            teams_text = teams.text.strip().replace("Including Overtime", "")
            
            # Print the cleaned text
            print(teams_text)
