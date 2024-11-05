import requests
from bs4 import BeautifulSoup
import time
from twilio.rest import Client

# Twilio credentials
acc_sid = 'ACd8936a014ab4a62d75ed47303cabbbb1'
au_token = '1bda572d605d3c2f8be4d2fb86622bc5'
twilio_whatsapp_number = 'whatsapp:+14155238886' 
my_whatsapp_number = 'whatsapp:+254712908889'


# Initialize the Twilio client
client = Client(acc_sid, au_token)

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Set headers to mimic a real browser request
headers = {
    'Request Line': 'GET/HTTP1.1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept-Language' : 'en-US,en;q=0.5',

}

# Function to check if the timer starts with 24 or 25 minutes
def timer_starts_with_11_19(timer_str):
    try:
        # Extract the minutes from the timer string
        minutes = int(timer_str.split(':')[0])
        return minutes in [24, 25]
    except (ValueError, IndexError):
        return False

while True:
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the sections that contain the basketball match information
        matches = soup.find_all(class_='c-events__item')

        if not matches:
            print("No matches found. Check the structure or class names of the page.")

        printed_matches = set()

        # Loop through each match and extract the relevant information
        for match in matches:
            # Extract team names
            teams = match.find('span', class_='c-events__teams')
            teams_text = teams.text.strip().replace("Including Overtime", "") if teams else None

            # Extract current quarter or overtime info
            current_quarter = match.find('span', class_='c-events__overtime')
            quarter_text = current_quarter.text.strip() if current_quarter else None

            # Extract timer info
            timer = match.find(class_='c-events__time')
            timer_text = timer.get_text(strip=True) if timer else None

            # Combine teams, quarter, and timer as a unique match identifier
            match_identifier = (teams_text, quarter_text, timer_text)

            # Only show 3rd quarter games with the specified timer range
            if match_identifier not in printed_matches and quarter_text == "3rd quarter" and timer_text:
                if timer_starts_with_11_19(timer_text):
                    printed_matches.add(match_identifier)

                    # Prepare the message to send via WhatsApp
                    message_body = ""
                    if teams_text:
                        message_body += f"Teams: {teams_text}\n"
                    if quarter_text:
                        message_body += f"Current Quarter: {quarter_text}\n"
                    if timer_text:
                        message_body += f"Timer: {timer_text}\n"

                    # Send message via Twilio WhatsApp with error handling
                    try:
                        message = client.messages.create(
                            body=message_body,
                            from_=twilio_whatsapp_number,
                            to=my_whatsapp_number
                        )
                        print(f"Message SID: {message.sid}, Status: {message.status}")
                    except Exception as e:
                        print(f"Failed to send message: {e}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    # Wait for 60 seconds before the next iteration
    time.sleep(60)
