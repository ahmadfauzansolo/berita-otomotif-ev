import os
import requests
import time
import random
import threading
from dotenv import load_dotenv
from flask import Flask
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

# Keyword list
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

# Posted link file
posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    open(posted_links_file, "w").close()

def sudah_diposting(link):
    with open(posted_links_file, "r") as f:
        return link.strip() in f.read()

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
            f"&q={keyword}&language=id&country=id&category=technology,business"
        )
        response = requests.get(url)
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
                    return
                except Exception as e:
                    print(f"❌ Gagal posting: {e}")

# === Loop otomatis posting setiap 1,5 jam dengan potongan 1 menit ===
def loop_otomatis():
    while True:
        print("🔄 Mengecek dan posting berita...")
        post_berita_ke_twitter()
        print("🕒 Menunggu 3 menit...")
for i in range(90):  # 90 menit
    print(f"⏳ Menit ke-{i+1} dari 90")
    time.sleep(60)


threading.Thread(target=loop_otomatis, daemon=True).start()

# === Web server untuk Render tetap aktif ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Twitter Bot Pak bNdotzz KLAYABAN Service is Running (Auto-post setiap 1,5 jam)"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
