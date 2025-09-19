import os
import requests
import tweepy
import logging
from datetime import datetime

# === Logging Setup ===
logging.basicConfig(
    filename="quota_errors.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Ambil variabel dari environment ===
API_KEY = os.getenv("NEWSDATA_API_KEY")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# === Twitter client ===
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# === Fungsi ambil berita ===
def get_berita(keyword):
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={keyword}&language=id,en"
    resp = requests.get(url)
    try:
        data = resp.json()
    except Exception:
        print(f"⚠️ Gagal parse JSON: {resp.text}")
        return []

    # Cek quota exceeded
    if "status" in data and data["status"] == "error":
        if "quota" in str(data).lower() or "exceeded" in str(data).lower():
            logging.info(f"Quota exceeded untuk keyword '{keyword}'")
            print(f"❌ Quota exceeded tercatat untuk '{keyword}'")
        return []

    return data.get("results", [])

# === Posting ke Twitter ===
def post_berita_ke_twitter():
    keywords = ["mobil listrik", "motor listrik", "kendaraan listrik"]
    total_posted = 0

    print("🚀 Script dijalankan")
    for kw in keywords:
        berita_list = get_berita(kw)
        print(f"🔎 {kw}: {len(berita_list)} berita ditemukan")

        for berita in berita_list:
            title = berita.get("title")
            link = berita.get("link")
            if not title or not link:
                print("⚠️ Data berita tidak valid")
                continue

            tweet_text = f"{title}\n{link}"
            try:
                client.create_tweet(text=tweet_text)
                total_posted += 1
            except Exception as e:
                print(f"⚠️ Gagal posting: {e}")

    print(f"📢 Total {total_posted} berita diposting kali ini")


if __name__ == "__main__":
    post_berita_ke_twitter()
