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

        # Combine both teams and quarter as a unique match identifier
        match_identifier = (teams_text, quarter_text)

        # Print only if this match has not been printed before
        if match_identifier not in printed_matches:
            printed_matches.add(match_identifier)

            # Print teams and current quarter (if available)
            if teams_text:
                print(f"Teams: {teams_text}")

            # Print current quarter with an extra line before the next teams
            if quarter_text:
                print(f"Current Quarter: {quarter_text}\n")  # Add a newline here
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
