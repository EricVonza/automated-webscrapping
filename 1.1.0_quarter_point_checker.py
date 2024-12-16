import requests
from bs4 import BeautifulSoup

def fetch_basketball_data():
    # URL of the website to scrape
    url = "https://1xbet.com/en/live/basketball"

    try:
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the span element containing the basketball match data
        span_element = soup.find('span', class_='c-events-scoreboard__cell')

        if span_element:
            # Extract the text content
            number = span_element.text.strip()
            print(f"Extracted number: {number}")  # Example: 19
        else:
            print("Element not found")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

# Run the function
fetch_basketball_data()
