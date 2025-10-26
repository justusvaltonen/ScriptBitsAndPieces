# python3 -m venv telegram-bot-env
# source telegram-bot-env/bin/activate
# sudo apt install python3-requests
# pip install requests beautifulsoup4
# pip install python-telegram-bot
# source telegram-bot-env/bin/activate
# alias runbot='source ~/ScriptBitsAndPieces/TelegramBot/bin/activate && \
# python ~/ScriptBitsAndPieces/TelegramBot/bot.py'

import requests
from bs4 import BeautifulSoup
import time
import random
# import urllib.parse

# === CONFIGURE THESE ===
BOT_TOKEN = ''
CHAT_ID = ''
# ========================

# List of real browser User-Agents (rotate to avoid blocks)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36  \
    (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36  \
    (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) \
    Gecko/20100101 Firefox/130.0',
]


def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Failed to send: {e}")


previous_price = None


def check_bitcoin_price():
    global previous_price
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        data = response.json()
        current_price = data['bitcoin']['usd']

        if previous_price is None:
            send_telegram_notification(f"Bitcoin Bot (API) Live!\n<b>${current_price:,.0f}</b>")
        else:
            change = ((current_price - previous_price) / previous_price) * 100
            if abs(change) >= 1.0:
                arrow = "Up" if change > 0 else "Down"
                send_telegram_notification(
                    f"{arrow} <b>BTC ${current_price:,.0f}</b>\n"
                    f"<code>{change:+.2f}%</code>"
                )
        previous_price = current_price
        print(f"API: ${current_price:,.0f}")

    except Exception as e:
        send_telegram_notification(f"API Error: {e}")


# === MAIN LOOP ===
if __name__ == "__main__":
    print("Bitcoin Price Bot Starting...")
    send_telegram_notification("Bot is now monitoring Bitcoin price...")
    while True:
        check_bitcoin_price()
        time.sleep(65)  # 65s to avoid rate limits
