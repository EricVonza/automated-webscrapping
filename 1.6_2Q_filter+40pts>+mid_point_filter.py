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

# Parse and Extract Basketball Matches (Teams)
def extract_matches(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    teams_list = []
    for idx, match in enumerate(matches, start=1):
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "")
            teams_text = " ".join(teams_text.split())
            teams_list.append(f"Game {idx}: {teams_text}")
    return teams_list

# Parse and Extract Scores and Quarters
def extract_scores_and_quarters(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_elements = soup.find_all('div', class_='c-events-scoreboard__line')
    
    games = []
    i = 0
    while i < len(target_elements):
        try:
            team1_scores = [span.get_text(strip=True) for span in target_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.get_text(strip=True) for span in target_elements[i + 1].find_all('span', class_='c-events-scoreboard__cell')]
            
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
            i += 2
        except IndexError:
            games.append((
                {'total_score': "0", 'quarters': ["No data"]},
                {'total_score': "0", 'quarters': ["No data"]}
            ))
            i += 2

    return games

# Parse and Extract Timer Information
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
    
    if not timers:
        timers = ["Timer: No timer info | Quarter: No quarter info"]
    
    return timers

# Main Function to Merge, Filter (2nd Quarter and 14th or 15th Minute), and Print Output
def main():
    html_content = fetch_html(URL)
    
    if html_content:
        matches = extract_matches(html_content)
        games = extract_scores_and_quarters(html_content)
        timers = extract_timer(html_content)

        max_len = max(len(matches), len(games), len(timers))
        matches += ["No match data"] * (max_len - len(matches))
        games += [({}, {})] * (max_len - len(games))
        timers += ["Timer: No timer info | Quarter: No quarter info"] * (max_len - len(timers))

        for match, (team1, team2), timer in zip(matches, games, timers):
            if "2nd quarter" in timer.lower() and ("14:5" in timer or "15:0" in timer or "15:1" in timer):
                print(f"{match} -")
                print(f"  First Team Total: {team1.get('total_score', 'No data')}, Quarters: {', '.join(team1.get('quarters', ['No data']))}")
                print(f"  Second Team Total: {team2.get('total_score', 'No data')}, Quarters: {', '.join(team2.get('quarters', ['No data']))}")
                print(f"  {timer}")
                print("-" * 40)

if __name__ == "__main__":
    main()
