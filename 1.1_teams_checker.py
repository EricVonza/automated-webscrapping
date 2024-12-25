import requests
from bs4 import BeautifulSoup

def fetch_basketball_matches(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_matches(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    return matches

def extract_teams(matches):
    teams_list = []
    game_counter = 1
    for match in matches:
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "")
            teams_text = " ".join(teams_text.split())  # Remove extra whitespaces
            teams_list.append(f"Game {game_counter}:\n{teams_text}\n")
            game_counter += 1
    return teams_list

def main():
    url = "https://1xbet.com/en/live/basketball"
    html_content = fetch_basketball_matches(url)
    
    if html_content:
        matches = parse_matches(html_content)
        teams_list = extract_teams(matches)
        
        if teams_list:
            for teams in teams_list:
                print(teams)
        else:
            print("No matches found.")

if __name__ == "__main__":
    main()
