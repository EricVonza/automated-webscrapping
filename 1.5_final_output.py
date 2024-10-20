import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Set headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

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

        # Extract timer information
        timer = match.find_all(class_='c-events-scoreboard__subitem')  # Find the timers within the match

        # Check if any timers are found
        if timer:
            for duration in timer:
                # Find the specific element that contains the current quarter info
                current_timer = duration.find(class_='c-events__time')  # Check this class name
                current_quarter = duration.find(class_='c-events__overtime')  # Find the quarter info
                
                # Check if the timer element exists
                if current_timer:
                    # Extract text from the timer element and strip whitespace
                    timer_text = current_timer.get_text(strip=True)

                    # Extract text from the quarter element (if it exists)
                    quarter_text = current_quarter.get_text(strip=True) if current_quarter else "No quarter info"

                    # Combine both teams and quarter as a unique match identifier
                    match_identifier = (teams_text, quarter_text)

                    # Print only if this match has not been printed before
                    if match_identifier not in printed_matches:
                        printed_matches.add(match_identifier)

                        # Print teams, current quarter, and timer information
                        if teams_text:
                            print(f"Teams: {teams_text}")
                        print(f"Timer: {timer_text} | Quarter Status: {quarter_text}\n")  # Add a newline here
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
