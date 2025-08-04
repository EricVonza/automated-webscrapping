import requests
from bs4 import BeautifulSoup

# Target URL
URL = "https://1xbet.global/en/live/basketball"

# HTTP headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def extract_scoreboard_items(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    scoreboard_items = soup.find_all(class_='c-events-scoreboard__item')

    print(f"\n=== Found {len(scoreboard_items)} scoreboard items ===")
    for i, item in enumerate(scoreboard_items, start=1):
        print(f"\nItem {i}:")
        print(item.prettify())  # Pretty-print full HTML
        print("Text Only:", item.get_text(strip=True))
        print("-" * 60)

def main():
    html_content = fetch_html(URL)
    if html_content:
        extract_scoreboard_items(html_content)

if __name__ == "__main__":
    main()
