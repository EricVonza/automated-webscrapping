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
    teams = []
    for element in target_elements:
        scores = [span.text.strip() for span in element.find_all('span', class_='c-events-scoreboard__cell')]
        total_score = scores[0]  # Total score is the first element
        team = {
            'total_score': total_score,
            'quarters': scores[1:]  # Remaining elements are quarter scores
        }
        teams.append(team)

    # Organize data for two teams
    print(f"First Team Scores: {teams[0]['total_score']}, Quarters Scores: {teams[0]['quarters']}")
    print(f"Second Team Scores: {teams[1]['total_score']}, Quarter Scores: {teams[1]['quarters']}")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
