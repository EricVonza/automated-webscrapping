import requests
from bs4 import BeautifulSoup

URL = "https://1xbet.co.ke/live/basketball"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

# Fetch HTML Content
def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Extract Basketball Matches (Teams)
def extract_matches(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    teams_list = []
    for idx, match in enumerate(matches, start=1):
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "")
            teams_list.append(f"Game {idx}: {teams_text}")
        else:
            teams_list.append(f"Game {idx}: No team info")
    return teams_list

# Extract Scores and Quarters
def extract_scores_and_quarters(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_elements = soup.find_all('div', class_='c-events-scoreboard__line')
    
    games = []
    for i in range(0, len(target_elements), 2):
        try:
            team1_scores = [span.get_text(strip=True) for span in target_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.get_text(strip=True) for span in target_elements[i + 1].find_all('span', class_='c-events-scoreboard__cell')]
            
            # Default to 0 if no score
            if not team1_scores:
                team1_scores = ["0"]
            if not team2_scores:
                team2_scores = ["0"]

            team1 = {
                'total_score': team1_scores[0],
                'quarters': team1_scores[1:] if len(team1_scores) > 1 else ["No data"]
            }
            team2 = {
                'total_score': team2_scores[0],
                'quarters': team2_scores[1:] if len(team2_scores) > 1 else ["No data"]
            }

            games.append((team1, team2))
        except IndexError:
            games.append((
                {'total_score': "0", 'quarters': ["No data"]},
                {'total_score': "0", 'quarters': ["No data"]}
            ))

    return games

# Extract Timer and Quarter Info
def extract_timer(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    timer_elements = soup.find_all(class_='c-events-scoreboard__subitem')
    
    timers = []
    for timer in timer_elements:
        time_element = timer.find(class_='c-events__time')
        quarter_element = timer.find(class_='c-events__overtime')
        
        timer_text = time_element.get_text(strip=True) if time_element else "No timer info"
        quarter_text = quarter_element.get_text(strip=True) if quarter_element else "No quarter info"
        
        timers.append(f"Timer: {timer_text} | Quarter: {quarter_text}")
    
    return timers or ["Timer: No timer info | Quarter: No quarter info"]

# Main Function to Merge, Filter (2nd Quarter), and Print Output
def main():
    html_content = fetch_html(URL)
    
    if html_content:
        matches = extract_matches(html_content)
        games = extract_scores_and_quarters(html_content)
        timers = extract_timer(html_content)

        # Ensure all lists align in length
        max_len = max(len(matches), len(games), len(timers))
        matches += ["No match data"] * (max_len - len(matches))
        games += [({'total_score': "0"}, {'total_score': "0"})] * (max_len - len(games))
        timers += ["Timer: No timer info | Quarter: No quarter info"] * (max_len - len(timers))

        for match, (team1, team2), timer in zip(matches, games, timers):
            if "2nd quarter" in timer.lower():
                print(f"{match} -")
                print(f"  First Team Total: {team1.get('total_score', '0')}, Quarters: {', '.join(team1.get('quarters', ['No data']))}")
                print(f"  Second Team Total: {team2.get('total_score', '0')}, Quarters: {', '.join(team2.get('quarters', ['No data']))}")
                print(f"  {timer}")
                print("-" * 40)

if __name__ == "__main__":
    main()
