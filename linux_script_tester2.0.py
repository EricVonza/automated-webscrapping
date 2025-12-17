import requests
from bs4 import BeautifulSoup
import time
import logging
import base64
import re

# -------------------------------------------
# Logging configuration
# -------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# -------------------------------------------
# Constants
# -------------------------------------------
URL = "https://1xbet.global/en/live/basketball"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

# -------------------------------------------
# Telegram Configuration (OBFUSCATED)
# -------------------------------------------
def _d(s: str) -> str:
    return base64.b64decode(s).decode()

T_URL = _d(
    "aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdDc2NzMwNzIyODc6QUFFOHp3VW96Ykcx"
    "b051UEM3OURTUl k5NGJfT1doaDJXcDgvc2VuZE1lc3NhZ2U=".replace(" ", "")
)

ROOM_ID = _d("LTEwMDIxNzAzNzczNjg=")

# -------------------------------------------
# Alert Tracking
# -------------------------------------------
low_quarter_alerts_sent = {}
MAX_LOW_QUARTER_ALERTS = 4

# -------------------------------------------
# Helpers
# -------------------------------------------
def format_match_vs(raw_text: str) -> str:
    cleaned = re.sub(r'\s+(Including Overtime).*$', '', raw_text.strip())
    for sep in [' - ', ' — ', ' – ', ' vs ', ' v ']:
        if sep in cleaned:
            t1, t2 = cleaned.split(sep, 1)
            return f"{t1.strip()} vs {t2.strip()}"
    return cleaned

def get_game_minute(timer: str) -> int:
    try:
        time_part = timer.split("|")[0].strip()
        minutes, _ = time_part.split(":")
        minutes = int(minutes)
        t = timer.lower()

        if "1st quarter" in t:
            return minutes
        if "2nd quarter" in t:
            return 12 + minutes
        if "3rd quarter" in t:
            return 24 + minutes
        if "4th quarter" in t:
            return 36 + minutes
    except:
        pass
    return -1

# -------------------------------------------
# Fetch HTML
# -------------------------------------------
def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return None

# -------------------------------------------
# Extract Matches
# -------------------------------------------
def extract_matches(html):
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    for m in soup.find_all(class_='c-events__name'):
        t = m.find('span', class_='c-events__teams')
        if t:
            matches.append(format_match_vs(" ".join(t.text.split())))
    return matches

# -------------------------------------------
# Extract Scores
# -------------------------------------------
def extract_scores_and_quarters(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('div', class_='c-events-scoreboard__line')
    games, i = [], 0

    while i < len(rows):
        try:
            s1 = [x.text.strip() for x in rows[i].find_all('span', class_='c-events-scoreboard__cell')]
            s2 = [x.text.strip() for x in rows[i+1].find_all('span', class_='c-events-scoreboard__cell')]
            games.append((
                {'total_score': s1[0] if s1 else "0", 'quarters': s1[1:] if len(s1) > 1 else ["0"]},
                {'total_score': s2[0] if s2 else "0", 'quarters': s2[1:] if len(s2) > 1 else ["0"]}
            ))
            i += 2
        except:
            i += 2
    return games

# -------------------------------------------
# Extract Timer
# -------------------------------------------
def extract_timer(html):
    soup = BeautifulSoup(html, 'html.parser')
    timers = []

    for t in soup.find_all(class_='c-events-scoreboard__subitem'):
        tm = t.find(class_='c-events__time')
        q = t.find(class_='c-events__overtime')
        timers.append(f"{tm.text.strip() if tm else '00:00'} | {q.text.strip() if q else 'No Quarter'}")

    return timers if timers else ["00:00 | No Quarter"]

# -------------------------------------------
# Telegram
# -------------------------------------------
def send_telegram_message(msg):
    try:
        requests.post(T_URL, data={'chat_id': ROOM_ID, 'text': msg}, timeout=10)
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# -------------------------------------------
# Main Loop
# -------------------------------------------
def main():
    while True:
        html = fetch_html(URL)
        if not html:
            time.sleep(10)
            continue

        matches = extract_matches(html)
        games = extract_scores_and_quarters(html)
        timers = extract_timer(html)

        max_len = max(len(matches), len(games), len(timers))
        matches += ["No Match"] * (max_len - len(matches))
        games += [({}, {})] * (max_len - len(games))
        timers += ["00:00 | No Quarter"] * (max_len - len(timers))

        for match, (t1, t2), timer in zip(matches, games, timers):
            if "women" in match.lower():
                continue

            timer_lower = timer.lower()

            # -------- LOW QUARTER ALERT --------
            prev_q = cutoff = None

            if "2nd quarter" in timer_lower:
                prev_q, cutoff = 0, 13
            elif "3rd quarter" in timer_lower:
                prev_q, cutoff = 1, 23
            elif "4th quarter" in timer_lower:
                prev_q, cutoff = 2, 33

            if prev_q is not None:
                if get_game_minute(timer) >= cutoff:
                    continue

                low_quarter_alerts_sent.setdefault(match, 0)

                if low_quarter_alerts_sent[match] < MAX_LOW_QUARTER_ALERTS:
                    try:
                        q1 = int(t1['quarters'][prev_q])
                        q2 = int(t2['quarters'][prev_q])
                    except:
                        q1 = q2 = 0

                    if q1 < 12 or q2 < 12:
                        send_telegram_message(
                            f"⚠️ Low Quarter Alert\n{match}\n{timer}\n"
                            f"Q{prev_q + 1}: T1={q1} vs T2={q2}"
                        )
                        low_quarter_alerts_sent[match] += 1

            # -------- 2Q UNDER LOGIC --------
            if "2nd quarter" in timer_lower:
                first_q_sum = sum(
                    int(x) for x in t1.get('quarters', ['0'])[:1] +
                    t2.get('quarters', ['0'])[:1] if x.isdigit()
                )

                if first_q_sum < 50 and any(x in timer for x in ["12:5", "13:0", "13:1", "16:5", "17:", "07:", "06:"]):
                    second_q_sum = sum(
                        int(x) for x in t1.get('quarters', ['0'])[1:2] +
                        t2.get('quarters', ['0'])[1:2] if x.isdigit()
                    )

                    est_2q = second_q_sum * 3

                    if est_2q <= 45:
                        send_telegram_message(
                            f"📉 2Q UNDER ALERT\n{match}\n{timer}\nEstimated 2Q pts: U{est_2q}"
                        )

        time.sleep(10)

# -------------------------------------------
# Entrypoint
# -------------------------------------------
if __name__ == "__main__":
    main()
