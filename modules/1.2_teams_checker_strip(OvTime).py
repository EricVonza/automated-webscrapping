import requests
from bs4 import BeautifulSoup

# URL of the 1xbet live matches page (update the URL as necessary)
url = 'https://1xbet.co.ke/live/basketball'

# Fetch the content from the URL
response = requests.get(url)
html_content = response.content

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Assuming live match information is within a specific class or tag
# This example assumes 'live-match' class for demonstration purposes
live_matches = soup.find_all('span', class_='c-events__teams')

# Function to clean match details
def clean_match_details(details):
    return details.replace('Including Overtime', '').strip()

# Loop through the found elements and extract the match details
for match in live_matches:
    match_details = match.get_text(strip=True)
    clean_details = clean_match_details(match_details)
    
    # Print or process the cleaned match details
    print(clean_details)

# Note: Adjust the class_='live-match' to the actual class used by 1xbet for live matches
