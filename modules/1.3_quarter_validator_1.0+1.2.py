import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = "https://1xbet.co.ke/en/live/basketball"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section that contains the basketball match information
    # This will depend on the structure of the website, which you need to inspect
    timeline = soup.find_all('div', class_='c-events__time')
    live_matches = soup.find_all('span', class_='c-events__teams')
    
        
    def clean_match_details(details):
        return details.replace('Including Overtime', '').strip()
    
    for match in live_matches:
        match_details = match.get_text(strip=True)
        clean_details = clean_match_details(match_details)
    
    # Loop through each match and extract the current quarter information
        for time_line in timeline:
        # Find the specific element that contains the current quarter info
        # Example: (adjust based on the actual structure)
            current_quarter = time_line.find('span', class_='c-events__overtime')
        
        # Check if the current_quarter element exists
            if current_quarter:
            # Extract and print the current quarter information
                print(clean_details + " " + current_quarter.text.strip())
        #else:
            #print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
