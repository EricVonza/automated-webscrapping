import requests
from bs4 import BeautifulSoup
import logging
import time

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Target URL
URL = "https://1xbet.global/en/live/basketball"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Fetch HTML Content
def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        logger.info("Fetched HTML content successfully.")
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

# Extract Matches (Team Names)
def extract_matches(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = soup.find_all(class_='c-events__name')
    teams_list = []
    for idx, match in enumerate(matches, start=1):
        teams = match.find('span', class_='c-events__teams')
        if teams:
            teams_text = teams.text.strip().replace("Including Overtime", "").replace("  ", " ")
            teams_list.append(f"Game {idx}: {teams_text}")
    return teams_list

# Extract Scores and Quarters
def extract_scores(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    score_elements = soup.find_all('div', class_='c-events-scoreboard__line')
    
    games = []
    i = 0
    while i < len(score_elements):
        try:
            team1_scores = [span.get_text(strip=True) for span in score_elements[i].find_all('span', class_='c-events-scoreboard__cell')]
            team2_scores = [span.get_text(strip=True) for span in score_elements[i + 1].find_all('span', class_='c-events-scoreboard__cell')]
            
            games.append({
                'team1': {'total_score': team1_scores[0], 'quarters': team1_scores[1:] if len(team1_scores) > 1 else ['No data']},
                'team2': {'total_score': team2_scores[0], 'quarters': team2_scores[1:] if len(team2_scores) > 1 else ['No data']}
            })
            i += 2
        except IndexError:
            games.append({'team1': {'total_score': "0", 'quarters': ["No data"]}, 'team2': {'total_score': "0", 'quarters': ["No data"]}})
            i += 2
    
    return games

# Extract Timer and Quarter Info
def extract_timers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    timer_elements = soup.find_all(class_='c-events-scoreboard__subitem')
    
    timers = []
    for timer in timer_elements:
        time_element = timer.find(class_='c-events__time')
        quarter_element = timer.find(class_='c-events__overtime')
        
        timer_text = time_element.get_text(strip=True) if time_element else "No timer info"
        quarter_text = quarter_element.get_text(strip=True) if quarter_element else "No quarter info"
        
        timers.append(f"Timer: {timer_text} | Quarter: {quarter_text}")
    
    return timers if timers else ["Timer: No info | Quarter: No info"]

# Main function to scrape games
def main():
    html_content = fetch_html(URL)
    
    if html_content:
        matches = extract_matches(html_content)
        scores = extract_scores(html_content)
        timers = extract_timers(html_content)
        
        max_len = max(len(matches), len(scores), len(timers))
        matches += ["No match data"] * (max_len - len(matches))
        scores += [({'total_score': "0", 'quarters': ["No data"]}, {'total_score': "0", 'quarters': ["No data"]})] * (max_len - len(scores))
        timers += ["Timer: No info | Quarter: No info"] * (max_len - len(timers))
        
        for match, game, timer in zip(matches, scores, timers):
            logger.info("="*40)
            logger.info(match)
            logger.info(f"Team 1 - Total: {game['team1']['total_score']}, Quarters: {', '.join(game['team1']['quarters'])}")
            logger.info(f"Team 2 - Total: {game['team2']['total_score']}, Quarters: {', '.join(game['team2']['quarters'])}")
            logger.info(timer)
            logger.info("="*40)
    
if __name__ == "__main__":
    main()
