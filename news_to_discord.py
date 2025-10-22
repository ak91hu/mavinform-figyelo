import requests
from bs4 import BeautifulSoup
import time
import os
import json
from datetime import datetime

NEWS_SOURCES = [
    "https://www.mavcsoport.hu",
    "https://www.mavcsoport.hu/mavinform",
    "https://www.mavcsoport.hu/mavinform?field_mavinform_tags_target_id%5B%5D=10835&title=",
    "https://www.mavcsoport.hu/mavinform?field_mavinform_tags_target_id%5B%5D=10837&title=",
]

SEARCH_KEYWORDS = [
    "győri",
    "hegyeshalom",
    "S10",
    "G10",
    "kelenföldi",
    "tatabányai",
]

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXXXX/YYYYYY"
CHECK_INTERVAL_SECONDS = 30 * 60
SENT_LINKS_FILE_PATH = "/data/sent_links.json"

def select_emoji_for_news(text: str) -> str:
    lowercase_text = text.lower()
    if any(word in lowercase_text for word in ["késés", "várakozás"]):
        return "⏰"
    elif any(word in lowercase_text for word in ["pótlóbusz", "vágányzár", "lezárás", "átépítés"]):
        return "🚌"
    elif any(word in lowercase_text for word in ["műszaki", "hiba", "meghibásodás", "áramszünet"]):
        return "🔧"
    elif any(word in lowercase_text for word in ["karbantartás", "javítás"]):
        return "🧰"
    else:
        return "🚆"

def load_sent_links() -> set[str]:
    if os.path.exists(SENT_LINKS_FILE_PATH):
        with open(SENT_LINKS_FILE_PATH, "r", encoding="utf-8") as file:
            return set(json.load(file))
    return set()


def save_sent_links(sent_links: set[str]) -> None:
    with open(SENT_LINKS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(list(sent_links), file, ensure_ascii=False, indent=2)

def fetch_news_articles() -> list[tuple[str, str, str]]:
    """
    Visszaadja a talált híreket (URL, cím, forrás)
    """
    collected_articles = []
    for source_url in NEWS_SOURCES:
        try:
            response = requests.get(source_url, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")

            for link_tag in soup.find_all("a"):
                article_url = link_tag.get("href")
                article_title = link_tag.get_text().strip()

                if not article_url or not article_title:
                    continue

                if any(keyword in article_title.lower() for keyword in SEARCH_KEYWORDS):
                    if article_url.startswith("/"):
                        article_url = "https://www.mavcsoport.hu" + article_url

                    source_label = "MÁVINFORM" if "mavinform" in source_url else "MÁV hírek"
                    collected_articles.append((article_url, article_title, source_label))

        except Exception as error:
            print(f"⚠️ Hiba a lekérésnél: {source_url} → {error}")

    return collected_articles


def post_news_to_discord(article_url: str, article_title: str, source_label: str) -> bool:
    emoji = select_emoji_for_news(article_title)
    embed_title = f"{emoji} MÁV / Forgalmi információ"
    short_description = article_title if len(article_title) <= 150 else article_title[:147] + "..."

    embed_message = {
        "title": embed_title,
        "description": f"{short_description}\n\n🔗 [Részletek itt]({article_url})",
        "color": 0xE67E22, 
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": f"Forrás: {source_label} | MÁV hírek figyelő"},
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed_message]})
    return response.status_code in (200, 204)

def run_news_monitor() -> None:
    sent_links = load_sent_links()

    while True:
        try:
            fetched_articles = fetch_news_articles()

            for article_url, article_title, source_label in fetched_articles:
                if article_url not in sent_links:
                    success = post_news_to_discord(article_url, article_title, source_label)
                    if success:
                        print(f"✅ Küldve: {article_title} ({article_url})")
                        sent_links.add(article_url)

            save_sent_links(sent_links)

        except Exception as error:
            print(f"❌ Hiba a feldolgozás során: {error}")

        print(f"⏳ Következő ellenőrzés {CHECK_INTERVAL_SECONDS // 60} perc múlva...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_news_monitor()
