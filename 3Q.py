import requests
from bs4 import BeautifulSoup
import time

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Set headers to mimic a real browser request
headers = {
    'Request Line': 'GET/HTTP1.1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept-Language' : 'en-US,en;q=0.5',
}

# Function to check if the timer starts with 11, 12, 13, 14, 15, 18, or 19
def timer_starts_with_11_19(timer_str):
    try:
        # Extract the minutes from the timer string
        minutes = int(timer_str.split(':')[0])
        # Check if the minutes are within the desired range
        return minutes in [24, 25]
    except (ValueError, IndexError):
        # Return False if the timer is not in the expected format or causes an error
        return False

while True:
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the sections that contain the basketball match information
        matches = soup.find_all(class_='c-events__item')

        if not matches:
            print("No matches found. Check the structure or class names of the page.")
        
        # Track previously printed matches to avoid repetition
        printed_matches = set()

        # Loop through each match and extract the relevant information
        for match in matches:
            # Extract team names
            teams = match.find('span', class_='c-events__teams')
            teams_text = teams.text.strip().replace("Including Overtime", "") if teams else None

            # Extract current quarter or overtime info
            current_quarter = match.find('span', class_='c-events__overtime')
            quarter_text = current_quarter.text.strip() if current_quarter else None

            # Extract timer info
            timer = match.find(class_='c-events__time')
            timer_text = timer.get_text(strip=True) if timer else None

            # Combine both teams, quarter, and timer as a unique match identifier
            match_identifier = (teams_text, quarter_text, timer_text)

            # Ensure only 3rd quarter games are displayed and the timer is within the desired range
            if match_identifier not in printed_matches and quarter_text == "3rd quarter" and timer_text:
                if timer_starts_with_11_19(timer_text):
                    printed_matches.add(match_identifier)

                    # Print the relevant information for the match
                    if teams_text:
                        print(f"Teams: {teams_text}")
                    if quarter_text:
                        print(f"Current Quarter: {quarter_text}")
                    if timer_text:
                        print(f"Timer: {timer_text}\n")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    # Wait for 60 seconds before running the next iteration
    time.sleep(60)
