from bs4 import BeautifulSoup
import requests

# URL of the page to scrape
url = 'https://1xbet.co.ke/live/basketball'  # Replace with the actual URL

# Send a GET request to the URL
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with the target class
    target_elements = soup.find_all('div', class_='c-events-scoreboard__line')

    # Extract and organize data
    games = []
    for i in range(0, len(target_elements), 2):  # Loop in steps of 2 to get pairs of teams
        # Ensure there are enough score elements for both teams
        try:
            team1_scores = [span.text.strip() for span in target_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.text.strip() for span in target_elements[i+1].find_all('span', class_='c-events-scoreboard__cell')]

            if len(team1_scores) < 2 or len(team2_scores) < 2:
                continue  # Skip this game if there are not enough scores

            team1 = {
                'total_score': team1_scores[0], 
                'quarters': team1_scores[1:]
            }

            team2 = {
                'total_score': team2_scores[0], 
                'quarters': team2_scores[1:]
            }

            # Check if the sum of first quarter scores is greater than 40
            first_quarter_sum = int(team1_scores[1]) + int(team2_scores[1])
            if first_quarter_sum > 40:
                games.append((team1, team2))  # Store both teams as a tuple if condition is met

        except IndexError:
            continue  # Skip this iteration if an index error occurs

    # Print all filtered games
    if games:
        for idx, (team1, team2) in enumerate(games, start=1):
            print(f"Game {idx}:")
            print(f"  First Team Scores: {team1['total_score']}, Quarter Scores: {team1['quarters']}")
            print(f"  Second Team Scores: {team2['total_score']}, Quarter Scores: {team2['quarters']}")
            print("-" * 40)
    else:
        print("No games with first quarter scores summing above 40.")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
