import requests
from bs4 import BeautifulSoup
import time
import logging

# Set up logging
logging.basicConfig(handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants
URL = "https://1xbet.global/en/live/basketball"
TELEGRAM_API_URL = "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage"
CHAT_ID = "<YOUR_CHAT_ID>"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        logger.info("Fetched HTML content successfully.")
        return response.content
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

def extract_matches(soup):
    matches = soup.find_all(class_='c-events__name')
    teams_list = []
    for idx, match in enumerate(matches, start=1):
        teams = match.find('span', class_='c-events__teams')
        if teams:
            text = teams.get_text(strip=True).replace("Including Overtime", "")
            teams_list.append(f"Game {idx}: {text}")
    return teams_list

def extract_scores(soup):
    scoreboard_items = soup.find_all(class_='c-events-scoreboard__item')
    games = []
    for item in scoreboard_items:
        cells = item.find_all(class_='c-events-scoreboard__cell')
        scores = [cell.get_text(strip=True) for cell in cells]
        if scores:
            total = scores[0]
            quarters = scores[1:] if len(scores) > 1 else ["No data"]
            games.append({'total_score': total, 'quarters': quarters})
    return [(games[i], games[i + 1]) for i in range(0, len(games), 2)]

def extract_timers(soup):
    timers = []
    scoreboard_wrappers = soup.find_all('div', class_='c-events-scoreboard')
    for board in scoreboard_wrappers:
        time = board.find('span', class_='c-events__time')
        quarter = board.find('span', class_='c-events__overtime')
        t = time.get_text(strip=True) if time else "No time"
        q = quarter.get_text(strip=True) if quarter else "No quarter"
        timers.append(f"{q} - {t}")
    return timers

def send_telegram_message(message):
    try:
        response = requests.post(TELEGRAM_API_URL, data={
            'chat_id': CHAT_ID,
            'text': message
        })
        if response.ok:
            logger.info("Telegram message sent.")
        else:
            logger.error(f"Telegram error: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

def main():
    while True:
        html = fetch_html(URL)
        if not html:
            time.sleep(10)
            continue

        soup = BeautifulSoup(html, 'html.parser')
        matches = extract_matches(soup)
        scores = extract_scores(soup)
        timers = extract_timers(soup)

        # Normalize lengths
        max_len = max(len(matches), len(scores), len(timers))
        matches += ["No match data"] * (max_len - len(matches))
        scores += [({}, {})] * (max_len - len(scores))
        timers += ["No timer info"] * (max_len - len(timers))

        print("\n=== All Gathered Games ===")
        for match, (team1, team2), timer in zip(matches, scores, timers):
            logger.info(f"{match}")
            logger.info(f"Team 1: {team1}")
            logger.info(f"Team 2: {team2}")
            logger.info(f"{timer}")
            logger.info("-" * 60)

        print("\n=== Filtered Games Matching Criteria ===")
        for match, (team1, team2), timer in zip(matches, scores, timers):
            q1_sum = sum(int(q) for q in team1.get('quarters', ['0'])[:1] + team2.get('quarters', ['0'])[:1] if q.isdigit())
            if q1_sum < 34 and "2nd quarter" in timer.lower() and any(t in timer for t in ["12:", "13:"]):
                q2_pts = sum(int(q) for q in team1.get('quarters', ['0'])[1:2] + team2.get('quarters', ['0'])[1:2] if q.isdigit())
                est = q2_pts * 3.5
                if est < 33:
                    logger.info(f"{match} - 1Q: {q1_sum}, 2Q Est: {est}")
                    logger.info(f"{timer}")
                    logger.info("=" * 60)
                    send_telegram_message(f"{match} | 2Q pts: OV{est}")

        time.sleep(10)

if __name__ == "__main__":
    main()
