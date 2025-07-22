import requests
from bs4 import BeautifulSoup
import time
import re
import logging


URL = "https://1xbet.global/en/live/basketball"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Windows 11 x86_64 Bit; rv:109.0) Gecko/20100101 Firefox/115.0'
}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_console_status():
    logger.info("Script is running and monitoring basketball matches...")

# Fetch HTML Content
def fetch_html(url):
    #logger.info("Fetching HTML content...")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        #logger.info("HTML fetched successfully.")
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

# Parse and Extract Basketball Matches (Teams)
def extract_matches(html_content):
    #logger.info("Extracting match data...")
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    teams_list = []
    for idx, match in enumerate(matches, start=1):
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "")
            teams_text = " ".join(teams_text.split())
            teams_list.append(f"Game {idx}: {teams_text}")
    #logger.info(f"Found {len(teams_list)} matches.")
    return teams_list

# Parse and Extract Scores and Quarters
def extract_scores_and_quarters(html_content):
    #logger.info("Extracting scores and quarters...")
    soup = BeautifulSoup(html_content, 'html.parser')
    target_elements = soup.find_all('div', class_='c-events-scoreboard__line')

    games = []
    i = 0
    while i < len(target_elements):
        try:
            team1_scores = [span.get_text(strip=True) for span in target_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.get_text(strip=True) for span in target_elements[i + 1].find_all('span', class_='c-events-scoreboard__cell')]

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

    #logger.info(f"Extracted data for {len(games)} games.")
    return games

# Parse and Extract Timer Information
def extract_timer(html_content):
    #logger.info("Extracting timer information...")
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

    #logger.info(f"Found {len(timers)} timers.")
    return timers

# Send Telegram Message
def send_telegram_message(message):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            data={'chat_id': CHAT_ID, 'text': message}
        )
        if response.status_code == 200:
            logger.info("Telegram message sent successfully.")
        else:
            logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

# Main Function
def main():
    while True:
        print_console_status()
        #logger.info("Starting new data fetch cycle...")
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
                first_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[:1] + team2.get('quarters', ['0'])[:1] if q.isdigit())
                if first_quarter_sum < 34 and "2nd quarter" in timer.lower() and re.search(r"1[2-3]:\d+", timer):
                    second_quarter_sum = sum(int(q) for q in team1.get('quarters', ['0'])[1:2] + team2.get('quarters', ['0'])[1:2] if q.isdigit())
                    estimated_2q_points = second_quarter_sum * 3.5
                    if estimated_2q_points < 33:
                        logger.info(f"{match} | 2Q pts: OV{estimated_2q_points}")
                        send_telegram_message(f"{match} | 2Q pts: OV{estimated_2q_points}")
        else:
            logger.error("Failed to fetch HTML content.")

        #logger.info("Sleeping for 10 seconds...")
        time.sleep(10)

if __name__ == "__main__":
    main()
