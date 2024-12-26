import requests
from bs4 import BeautifulSoup

URL = "https://1xbet.co.ke/live/basketball"  # or "https://1xbet.com/en/live/basketball"
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

# Parse and Extract Scores and Quarters (Script 2 Logic)
def extract_scores_and_quarters(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_elements = soup.find_all('div', class_='c-events-scoreboard__line')
    
    games = []
    for i in range(0, len(target_elements), 2):  # Loop in steps of 2 to get pairs of teams
        try:
            team1_scores = [span.get_text(strip=True) for span in target_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.get_text(strip=True) for span in target_elements[i+1].find_all('span', class_='c-events-scoreboard__cell')]

            # Ensure that both teams have at least one score
            if len(team1_scores) < 2 or len(team2_scores) < 2:
                continue  # Skip this game if there are no scores

            team1 = {
                'total_score': team1_scores[0],  # The first score is the total score
                'quarters': team1_scores[1:] if len(team1_scores) > 1 else ["No data"]
            }

            team2 = {
                'total_score': team2_scores[0],  # The first score is the total score
                'quarters': team2_scores[1:] if len(team2_scores) > 1 else ["No data"]
            }

            games.append((team1, team2))

        except IndexError:
            continue  # Skip this iteration if an index error occurs

    return games

# Parse and Extract Timer Information (For Game Timer and Quarter Status)
def extract_timer(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    timer_elements = soup.find_all(class_='c-events-scoreboard__subitem')
    
    timers = []
    for timer in timer_elements:
        time_element = timer.find(class_='c-events__time')
        quarter_element = timer.find(class_='c-events__overtime')
        
        # Handle cases where timer or quarter info may be missing
        if time_element:
            timer_text = time_element.get_text(strip=True)
            quarter_text = quarter_element.get_text(strip=True) if quarter_element else "No quarter info"
            # Add "No timer info" if timer_text is missing
            if not timer_text:
                timer_text = "No timer info"
            timers.append(f"Timer: {timer_text} | Quarter: {quarter_text}")
        else:
            # If there's no timer info, mark it as "No timer info"
            timers.append("Timer: No timer info | Quarter: No quarter info")
    
    return timers

# Main Function to Merge and Print Output
def main():
    html_content = fetch_html(URL)
    
    if html_content:
        # Extract teams and scores
        matches = extract_matches(html_content)
        games = extract_scores_and_quarters(html_content)
        timers = extract_timer(html_content)

        # Handle mismatched lengths
        max_len = max(len(matches), len(games), len(timers))
        matches += ["No match data"] * (max_len - len(matches))
        games += [({}, {})] * (max_len - len(games))  # Ensure games is a list of tuples, even if empty
        timers += ["No timer data"] * (max_len - len(timers))  # Add missing timer data

        # Merge and clean output
        for match, (team1, team2), timer in zip(matches, games, timers):
            # Include all games (including those with score 0, 0)
            print(f"{match} -")
            print(f"  First Team Total: {team1.get('total_score', 'No data')}, Quarters: {', '.join(team1.get('quarters', ['No data']))}")
            print(f"  Second Team Total: {team2.get('total_score', 'No data')}, Quarters: {', '.join(team2.get('quarters', ['No data']))}")
            print(f"  {timer}")
            print("-" * 40)

if __name__ == "__main__":
    main()
