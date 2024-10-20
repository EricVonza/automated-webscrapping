import requests
from bs4 import BeautifulSoup
import time  # Import the time module to introduce delays

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Set headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

# Function to check if the timer is between 24:00 and 26:00
def is_timer_in_range(timer_text):
    try:
        minutes, seconds = map(int, timer_text.split(":"))
        # Ensure the time is within 24:00 and 26:00
        return 24 <= minutes <= 26
    except ValueError:
        return False

# Introduce a 2-minute delay before execution
print("Waiting for 2 minutes before executing the script...")
time.sleep(120)  # Wait for 2 minutes (120 seconds)

# Send a GET request to the website with headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the sections that contain the basketball match information
    matches = soup.find_all(class_='c-events__item')

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

        # Only print if this match has not been printed before, is in the 3rd quarter, and the timer is between 24:00 and 26:00
        if match_identifier not in printed_matches and quarter_text == "3rd quarter" and timer_text and is_timer_in_range(timer_text):
            printed_matches.add(match_identifier)

            # Print the relevant information for the 3rd quarter match with timer in range
            if teams_text:
                print(f"Teams: {teams_text}")
            if quarter_text:
                print(f"Current Quarter: {quarter_text}")
            if timer_text:
                print(f"Timer: {timer_text}\n")  # Print the timer for the match
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
