import requests
from bs4 import BeautifulSoup
import time
import logging

#  Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output
    ]
)

logger = logging.getLogger(__name__)

# Constants
URL = "https://1xbet.global/en/live/basketball"

# Telegram Configuration
T_URL = "https://api.telegram.org/bot7673072287:AAE8zwUozbG1oNuPC79DSRY94b_OWhh2Wp8/sendMessage"
ROOM_ID = "-1002170377368"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

# 🔍 Fetch HTML
def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        logger.info("Fetched HTML content successfully.")
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

#  Extract Match Info
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

#  Extract Scores and Quarters
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

#  Extract Timer Info
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
            T_URL,
            data={'chat_id': ROOM_ID, 'text': message}
        )
        if response.status_code == 200:
            logger.info("Telegram message sent successfully.")
        else:
            logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

#  Main Logic
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

            # 🔍 Filter out women’s games
            filtered_data = [
                (m, g, t)
                for m, g, t in zip(matches, games, timers)
                if "women" not in m.lower()
            ]

            for match, (team1, team2), timer in filtered_data:

                # ---------------- Existing Rule ---------------- #
                first_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[:1] + team2.get('quarters', ['0'])[:1] if q.isdigit())
                if first_quarter_sum < 50 and "2nd quarter" in timer.lower() and ("12:5" in timer or "13:0" in timer or "13:1" in timer):
                    second_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[1:2] + team2.get('quarters', ['0'])[1:2] if q.isdigit())
                    estimated_2q_points = second_quarter_sum * 3.1
                    if estimated_2q_points < 33:
                        message = f"{match} | 2Q pts: OV{estimated_2q_points} "
                        send_telegram_message(message)

                # ---------------- Low Score + Previous Quarter Rule ---------------- #
                if ("2nd quarter" in timer.lower() and "13:" in timer) or ("4th quarter" in timer.lower() and "33:" in timer):
                    if "2nd quarter" in timer.lower():
                        q_index = 1  # 2Q
                        prev_index = 0  # Q1
                    else:
                        q_index = 3  # 4Q
                        prev_index = 2  # Q3

                    team1_q_points = int(team1.get('quarters', ['0'])[q_index]) if team1.get('quarters', ['0'])[q_index].isdigit() else 0
                    team2_q_points = int(team2.get('quarters', ['0'])[q_index]) if team2.get('quarters', ['0'])[q_index].isdigit() else 0

                    # Previous quarter totals
                    try:
                        team1_prev = int(team1.get('quarters', ['0'])[prev_index]) if team1.get('quarters', ['0'])[prev_index].isdigit() else 0
                        team2_prev = int(team2.get('quarters', ['0'])[prev_index]) if team2.get('quarters', ['0'])[prev_index].isdigit() else 0
                    except IndexError:
                        team1_prev, team2_prev = 0, 0

                    prev_total = team1_prev + team2_prev

                    # Rule: low score this quarter AND previous quarter total < 36
                    if ((team1_q_points < 6 and team2_q_points <= 9) or (team2_q_points < 6 and team1_q_points <= 9)) and prev_total < 36:
                        message = (
                            f" {match} | {timer} | Quarter {q_index+1}: Low score alert!\n"
                            f"T1={team1_q_points}, T2={team2_q_points} | Previous Quarter total={prev_total}"
                        )
                        send_telegram_message(message)

        time.sleep(10)

# Script entrypoint
if __name__ == "__main__":
    main()
