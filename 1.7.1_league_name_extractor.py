import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "https://1xbet.co.ke/en/live/basketball"

# Browser-like headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Request the page
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all league name <span> elements
    league_spans = soup.find_all(
        "span",
        class_="ui-caption--size-m ui-caption--color-clr-strong-alt ui-caption--no-wrap ui-caption dashboard-champ-name__caption"
    )

    # Preserve order and avoid duplicates
    league_names = []
    seen = set()

    for span in league_spans:
        text = span.get_text(strip=True)
        if text and text not in seen:
            league_names.append(text)
            seen.add(text)

    # Print as-is in extracted order
    print("🏀 Ordered Live Basketball League Names:")
    for name in league_names:
        print("-", name)

else:
    print(f"❌ Failed to load page. Status code: {response.status_code}")
