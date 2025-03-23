import requests
from bs4 import BeautifulSoup
import time

# Telegram Configuration
TELEGRAM_API_URL = "https://api.telegram.org/bot7673072287:AAE8zwUozbG1oNuPC79DSRY94b_OWhh2Wp8/sendMessage"
CHAT_ID = "-1002170377368"

URL = "https://1xbet.global/en/live/basketball"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
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

# Send Telegram Message
def send_telegram_message(message):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            data={'chat_id': CHAT_ID, 'text': message}
        )
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send Telegram message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# Main Function to Merge, Filter, and Print Output
def main():
    while True:
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
                is_women_game = "(Women)" in match
                first_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[:1] + team2.get('quarters', ['0'])[:1] if q.isdigit())
                
                if ((is_women_game and first_quarter_sum < 25) or (not is_women_game and first_quarter_sum < 32)) and "2nd quarter" in timer.lower() and ("11:5" in timer or "12:0" in timer or "12:1" in timer or "08:0" in timer or "07:5" in timer):
                    second_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[1:2] + team2.get('quarters', ['0'])[1:2] if q.isdigit())
                    estimated_2q_points = second_quarter_sum * 4
                    if estimated_2q_points < 27 :
                        print(f"{match} - First Team Total: {team1.get('total_score', 'No data')}, Quarters: {', '.join(team1.get('quarters', ['No data']))}")
                        print(f"Second Team Total: {team2.get('total_score', 'No data')}, Quarters: {', '.join(team2.get('quarters', ['No data']))}")
                        print(f"{timer}")
                        print(f"Estimated midpoint pts: {second_quarter_sum}")
                        print(f"Estimated 2Q pts: {estimated_2q_points}")
                        print("-" * 40)

                        message = f"{match} | 2Q pts: OV{estimated_2q_points} "

                        send_telegram_message(message)

        time.sleep(10)

if __name__ == "__main__":
    main()
