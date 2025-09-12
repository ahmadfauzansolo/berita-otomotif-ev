import os
import requests
import time
import random
from dotenv import load_dotenv
import tweepy

# Load .env
load_dotenv()

# Twitter API Keys
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Twitter Auth
twitter_client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Keyword list (sama seperti sebelumnya)
keywords = [
    "motor listrik", "kendaraan listrik", "EV", "mobil listrik", "baterai mobil",
    "baterai motor", "konversi motor listrik", "charging station", "skutik listrik",
    "subsidi motor listrik", "sepeda listrik", "BLDC", "dinamo motor",
    "baterai lithium-ion", "Electric Vehicle", "baterai SLA", "Elon Musk"
]

brands = [
    "Gesits", "Viar", "Selis", "Volta", "Alva", "Polytron", "Smoot", "Rakata", "Yadea", "United",
    "Honda EM1", "Yamaha E01", "NIU", "Treeletrik", "Uwinfly", "Italjet", "Sunra", "Evoseed",
    "BF Goodrich", "Elvindo", "U-Winfly"
]

all_keywords = keywords + brands

posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    open(posted_links_file, "w").close()

def sudah_diposting(link):
    try:
        with open(posted_links_file, "r") as f:
            posted = set(line.strip() for line in f if line.strip())
            return link.strip() in posted
    except FileNotFoundError:
        return False

def tandai_sudah_diposting(link):
    with open(posted_links_file, "a") as f:
        f.write(link.strip() + "\n")

def is_relevant(title, content):
    combined = (title or "") + " " + (content or "")
    combined = combined.lower()
    return any(kw.lower() in combined for kw in all_keywords)

def ambil_berita(keyword):
    try:
        url = (
            f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}"
            f"&q={keyword}&language=id&country=id"
        )
        response = requests.get(url, timeout=20)
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print("❌ Gagal ambil berita:", e)
        return []

def post_berita_ke_twitter():
    random.shuffle(all_keywords)
    for keyword in all_keywords:
        print(f"🔎 Mencari berita untuk keyword: {keyword}")
        berita_list = ambil_berita(keyword)
        for berita in berita_list:
            if isinstance(berita, dict):
                title = berita.get("title", "")
                content = berita.get("content", "") or berita.get("description", "")
                link = berita.get("link", "")

                print(f"📰 Cek berita: {title}")
                if not (title and link):
                    print("⚠️ Lewat: Tidak ada judul atau link")
                    continue
                if not is_relevant(title, content):
                    print("⛔ Lewat: Tidak relevan")
                    continue
                if sudah_diposting(link):
                    print("⏭️ Lewat: Sudah pernah diposting")
                    continue

                try:
                    status = f"{title}\n{link}"
                    if len(status) > 280:
                        status = status[:277] + "..."
                    twitter_client.create_tweet(text=status)
                    print(f"✅ Berhasil posting: {title}")
                    tandai_sudah_diposting(link)
                    return  # STOP setelah berhasil posting 1 berita
                except Exception as e:
                    print(f"❌ Gagal posting: {e}")
                    return
    print("❌ Tidak ada berita relevan yang bisa diposting kali ini.")

if __name__ == "__main__":
    print("🔄 Menjalankan 1x job posting...")
    post_berita_ke_twitter()
