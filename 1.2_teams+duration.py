import requests
from bs4 import BeautifulSoup

url = "https://1xbet.com/en/live/basketball"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

def fetch_basketball_matches(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_matches(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    timers = soup.find_all(class_='c-events-scoreboard__subitem')  # Extract timer info
    print(f"Found {len(matches)} matches and {len(timers)} timers")  # Debugging line
    return matches, timers

def extract_teams_and_timers(matches, timers):
    game_counter = 1
    results = []

    # Ensure the number of timers and matches are correctly paired
    min_len = min(len(matches), len(timers))  # Ensure we don't exceed either list

    for i in range(min_len):
        match = matches[i]
        timer = timers[i]

        # Extract teams
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "")
            teams_text = " ".join(teams_text.split())
        else:
            teams_text = "Unknown Teams"
        
        # Extract timer and quarter info
        current_timer = timer.find(class_='c-events__time')
        current_quarter = timer.find(class_='c-events__overtime')
        timer_text = current_timer.get_text(strip=True) if current_timer else "No Timer"
        quarter_text = current_quarter.get_text(strip=True) if current_quarter else "No Quarter Info"
        
        # Store result
        results.append(f"Game {game_counter}:\n"
                       f"{teams_text} | Timer: {timer_text} | Quarter Status: {quarter_text}\n")
        game_counter += 1
    
    return results

def main():
    html_content = fetch_basketball_matches(url)
    
    if html_content:
        matches, timers = parse_matches(html_content)
        teams_and_timers = extract_teams_and_timers(matches, timers)
        
        if teams_and_timers:
            for result in teams_and_timers:
                print(result)
        else:
            print("No matches or timers found.")

if __name__ == "__main__":
    main()