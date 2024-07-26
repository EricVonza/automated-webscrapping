import requests
from bs4 import BeautifulSoup

def get_basketball_scores():
    url = "https://1xbet.co.ke/en/live/Basketball/"  # URL for 1xbet Kenya live basketball scores
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    games = soup.find_all('div', class_='c-events__item c-events__item_game')

    scores = []

    for game in games:
        teams = game.find_all('span', class_='c-events__team')
        scores_data = game.find_all('span', class_='c-events-scoreboard__cell')
        quarter_time = game.find('span', class_='c-events__overtime')

        if len(teams) == 2 and len(scores_data) == 2:
            home_team = teams[1].text.strip()
            away_team = teams[0].text.strip()
            home_score = scores_data[1].text.strip()
            away_score = scores_data[0].text.strip()

            # Get current quarter and time
            current_status = quarter_time.text.strip() if quarter_time else "Unknown"

            game_info = {
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "status": current_status
            }

            scores.append(game_info)

    return scores

if __name__ == "__main__":
    scores = get_basketball_scores()
    for score in scores:
        print(f"{score['away_team']} {score['away_score']} - {score['home_team']} {score['home_score']} ({score['status']})")
