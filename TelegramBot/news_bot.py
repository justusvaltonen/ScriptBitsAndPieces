
from dotenv import load_dotenv
import os
import requests
import feedparser
import time
import json
from datetime import datetime

# === CONFIG ===
load_dotenv()
BOT_TOKEN = os.getenv('TORVI_BOT_TOKEN')
CHAT_ID = os.getenv('TORVI_CHAT_ID')
CHECK_INTERVAL = 8640  # Seconds (~2.4 hours for 10 checks/day) 3600 = Hour

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError(
        "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file!")

# RSS Feeds
FEEDS = {
    'Hackaday': 'https://hackaday.com/feed/',
    'The Hacker News': 'https://feeds.feedburner.com/TheHackersNews'
}

# File to store last seen article IDs (for "new" detection)
STATE_FILE = 'news_state.json'


def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def send_telegram_notification(title, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': f"{title}\n\n{message}\n\n🕐 {
            datetime.now().strftime('%Y-%m-%d %H:%M')}",
        'parse_mode': 'HTML',
        'disable_web_page_preview': False  # Shows link preview
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Send failed: {e}")


def check_feed(source, url):
    print(f"Checking {source}...")
    feed = feedparser.parse(url)

    state = load_state()
    seen_ids = set(state.get(source, []))
    new_articles = []

    for entry in feed.entries[:10]:  # Limit to newest 10
        article_id = entry.id or entry.link  # Use ID or link as unique key
        if article_id not in seen_ids:
            title = entry.title
            link = entry.link
            summary = (entry.summary or "")[:200] + "..."  # Teaser
            new_articles.append((title, link, summary))
            seen_ids.add(article_id)

    # Update state
    state[source] = list(seen_ids)
    save_state(state)

    # Send notifications
    for title, link, summary in new_articles:
        message = f"<b>{title}</b>\n\n{
            summary}\n\n<a href='{link}'>Read more</a>"
        send_telegram_notification(f"📰 New from {source}:", message)
        print(f"Sent: {title}")
        time.sleep(1)  # Rate limit Telegram

    if not new_articles:
        print(f"No new articles from {source}.")


# === MAIN LOOP ===
if __name__ == "__main__":
    print("News Bot Started! Monitoring Hackaday & The Hacker News.")
    send_telegram_notification(
        "🚀 News Bot Live", f"Checking <b>{
            ', '.join(FEEDS.keys())}</b> every {
                CHECK_INTERVAL//3600} hours for new articles.")

    while True:
        for source, url in FEEDS.items():
            try:
                check_feed(source, url)
            except Exception as e:
                print(f"Error checking {source}: {e}")
                send_telegram_notification(
                    "⚠️ Bot Error", f"Failed to check {source}: {e}")

        print(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)
