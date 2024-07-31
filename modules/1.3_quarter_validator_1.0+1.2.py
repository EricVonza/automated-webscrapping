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

    matches = soup.find_all(class_='c-events-scoreboard__item')  # Replace with actual class

    for match in matches:
        # Find the specific element that contains the current quarter info
        # Example: (adjust based on the actual structure)
        teams = match.find(class_='c-events__teams')
        
        if teams:
            # Extract and print the current quarter information
            
            all_teams = teams.get_text(strip=True)

        quarter = match.find(class_='c-events__overtime')  # Replace with actual class
        if quarter:
            current_quarter = quarter.get_text(strip=True)
        else:
            current_quarter = 'N/A'

        if "3 Quarter" == current_quarter:

        # Print the extracted information
            print(f" Match {all_teams} Current Quarter: {current_quarter} ")

       

        # Print the extracted information
    
