# python3 -m venv telegram-bot-env
# source telegram-bot-env/bin/activate
# sudo apt install python3-requests
# pip install requests beautifulsoup4
# pip install python-telegram-bot
import requests
from bs4 import BeautifulSoup
import time
# import urllib.parse

BOT_TOKEN = ''
CHAT_ID = ''


def check_website_for_changes(url, selector):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    current_content = soup.select_one(selector).text.strip()


def send_telegram_notification(message):
    """
    Sends a notification message to your Telegram chat.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Error sending notification: {response.text}")


while True:
    check_website_for_changes('https://example.com', '#some-element')
    time.sleep(60)

if __name__ == "__main__":

    event_happened = True  # e.g., if some_condition_detected()
    if event_happened:
        send_telegram_notification(
            "🚨 External event detected! Something happened outside Telegram.")
