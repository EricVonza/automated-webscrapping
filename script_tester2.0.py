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

# -------------------------------------------
# PER-GAME Low Quarter Alert Tracking
# -------------------------------------------
low_quarter_alerts_sent = {}  # key = match name, value = count
MAX_LOW_QUARTER_ALERTS = 4


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
            teams_list.append(teams_text)
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
                'quarters': team1_scores[1:] if len(team1_scores) > 1 else ["0"]
            }
            team2 = {
                'total_score': team2_scores[0],
                'quarters': team2_scores[1:] if len(team2_scores) > 1 else ["0"]
            }

            games.append((team1, team2))
            i += 2
        except IndexError:
            games.append((
                {'total_score': "0", 'quarters': ["0"]},
                {'total_score': "0", 'quarters': ["0"]}
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

        timers.append(f"{timer_text} | {quarter_text}")

    if not timers:
        timers = ["No timer info | No quarter info"]

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
            matches += ["No match"] * (max_len - len(matches))
            games += [({}, {})] * (max_len - len(games))
            timers += ["No timer info | No quarter info"] * (max_len - len(timers))

            # 🔍 Filter out women’s games
            filtered = [
                (m, g, t)
                for m, g, t in zip(matches, games, timers)
                if "women" not in m.lower()
            ]

            for match, (team1, team2), timer in filtered:

                # Extract timer/quarter parts
                timer_lower = timer.lower()

                # -------------------------------------------
                # PER-GAME LOW QUARTER RULE
                # -------------------------------------------
                match_key = match

                if match_key not in low_quarter_alerts_sent:
                    low_quarter_alerts_sent[match_key] = 0

                completed_quarters = []

                if "2nd quarter" in timer_lower:
                    completed_quarters = [0]
                elif "3rd quarter" in timer_lower:
                    completed_quarters = [0, 1]
                elif "4th quarter" in timer_lower:
                    completed_quarters = [0, 1, 2]
                elif "overtime" in timer_lower:
                    completed_quarters = [0, 1, 2, 3]

                # Only send if THIS match has not exceeded its limit
                if low_quarter_alerts_sent[match_key] < MAX_LOW_QUARTER_ALERTS:

                    for q in completed_quarters:
                        try:
                            t1_q = int(team1["quarters"][q]) if team1["quarters"][q].isdigit() else 0
                            t2_q = int(team2["quarters"][q]) if team2["quarters"][q].isdigit() else 0
                        except:
                            continue

                        if t1_q < 12 or t2_q < 12:
                            msg = (
                                f"⚠️ Low Quarter Alert\n"
                                f"{match}\n"
                                f"{timer}\n"
                                f"Quarter {q+1}: T1={t1_q}, T2={t2_q}"
                            )
                            send_telegram_message(msg)

                            low_quarter_alerts_sent[match_key] += 1

                            logger.info(f"{match_key} -> Alert {low_quarter_alerts_sent[match_key]}/4")

                            break
                else:
                    logger.info(f"{match_key}: low-quarter limit reached.")

        time.sleep(10)


# Script entrypoint
if __name__ == "__main__":
    main()
