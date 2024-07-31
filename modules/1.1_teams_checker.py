import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = "https://1xbet.co.ke/en/live/basketball"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section that contains the basketball match information
    # This will depend on the structure of the website, which you need to inspect
    matches = soup.find_all(class_='c-events__name')

    # Loop through each match and extract the current quarter information
    for match in matches:
        # Find the specific element that contains the current quarter info
        # Example: (adjust based on the actual structure)
        teams = match.find('span', class_='c-events__teams')
        
        # Check if the current_quarter element exists
        if teams:
            # Extract and print the current quarter information
            print(teams.text.strip())
