import os
import requests
import random
from dotenv import load_dotenv
import tweepy
import sys
import traceback

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ==============================
# TWITTER AUTH
# ==============================
twitter_client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

# ==============================
# KEYWORDS
# ==============================
keywords = [
    "mobil listrik",
    "motor listrik",
    "kendaraan listrik"
]

all_keywords = keywords

# ==============================
# FILE UNTUK LINK YANG SUDAH DIPOSTING
# ==============================
posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    open(posted_links_file, "w").close()

def sudah_diposting(link):
    with open(posted_links_file, "r") as f:
        return link.strip() in f.read()

def tandai_sudah_diposting(link):
    with open(posted_links_file, "a") as f:
        f.write(link.strip() + "\n")

# ==============================
# CEK RELEVANSI
# ==============================
def is_relevant(title, content):
    combined = (title or "") + " " + (content or "")
    combined = combined.lower()
    return any(kw.lower() in combined for kw in all_keywords)

# ==============================
# AMBIL BERITA DARI NEWSDATA.IO
# ==============================
def ambil_berita(keyword):
    try:
        url = (
            f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}"
            f"&q={keyword}&language=id&country=id"
        )
        response = requests.get(url)
        data = response.json()
        results = data.get("results", [])
        print(f"🔎 {keyword}: {len(results)} berita ditemukan")
        return results
    except Exception as e:
        print("❌ Gagal ambil berita:", e, file=sys.stderr)
        return []

# ==============================
# POST BERITA KE TWITTER
# ==============================
def post_berita_ke_twitter():
    random.shuffle(all_keywords)
    for kw in all_keywords:
        berita_list = ambil_berita(kw)
        if not berita_list:
            continue
        for berita in berita_list:
            link = berita.get("link")
            title = berita.get("title")
            content = berita.get("description") or berita.get("content")
            if not link or sudah_diposting(link):
                continue
            if is_relevant(title, content):
                try:
                    tweet_text = f"{title}\n{link}"
                    twitter_client.create_tweet(text=tweet_text)
                    tandai_sudah_diposting(link)
                    print("✅ Berhasil post:", title)
                    return  # hanya post 1 berita per run
                except Exception as e:
                    print("❌ Gagal post:", e, file=sys.stderr)
                    traceback.print_exc()

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    post_berita_ke_twitter()
