import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import time

# URL of the website to scrape
url = "https://1xbet.com/en/live/basketball"

# Set headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

# Function to check if the timer is between 14:00 and 16:00
def is_timer_in_range(timer_text):
    try:
        minutes, seconds = map(int, timer_text.split(":"))
        # Ensure the time is within 14:00 and 16:00
        return 14 <= minutes <= 16
    except ValueError:
        return False

# Function to send WhatsApp message via Twilio
def send_whatsapp_message(message):
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,
            to=recipient_whatsapp_number
        )
        print(f"WhatsApp message sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

# Infinite loop to continuously check and send messages every 2 minutes
while True:
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the sections that contain the basketball match information
        matches = soup.find_all(class_='c-events__item')

        # Track previously printed matches to avoid repetition
        printed_matches = set()

        # Prepare the message content
        message_content = ""

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

            # Combine both teams, quarter, and timer as a unique match identifier
            match_identifier = (teams_text, quarter_text, timer_text)

            # Only add to message if this match is in the 2nd quarter and the timer is between 14:00 and 16:00
            if match_identifier not in printed_matches and quarter_text == "2nd quarter" and timer_text and is_timer_in_range(timer_text):
                printed_matches.add(match_identifier)

                # Append the relevant information to the message content
                message_content += f"Teams: {teams_text}\nCurrent Quarter: {quarter_text}\nTimer: {timer_text}\n\n"

        # If matches are found, send a WhatsApp message; otherwise, don't send anything
        if printed_matches:
            send_whatsapp_message(message_content)
        else:
            print("No matches found within the 2nd quarter and the time range.")

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    # Wait for 2 minutes before executing the script again
    print("Waiting for 2 minutes before the next check...\n")
    time.sleep(120)  # Wait for 2 minutes (120 seconds)
