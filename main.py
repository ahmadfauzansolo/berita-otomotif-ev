# --- Konfigurasi ---
import requests
import time
import random
import os
import tweepy
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel dari .env

# --- API Keys dari .env ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# --- Setup Auth Twitter (API v2) ---
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# --- Keyword Pencarian ---
keywords = [
    "motor listrik", "kendaraan listrik", "EV", "mobil listrik", "baterai mobil",
    "baterai motor", "konversi motor listrik", "charging station", "kendaraan listrik", "skutik listrik",
    "subsidi motor listrik", "sepeda listrik", "BLDC", "dinamo motor",
    "Baterai lithium-ion", "Electric Vehicle", "baterai SLA", "Elon Musk"
]

brands = [
    "Gesits", "Viar", "Selis", "Volta", "Alva", "Polytron", "Smoot", "Rakata", "Yadea", "United",
    "Honda EM1", "Yamaha E01", "NIU", "Treeletrik", "Uwinfly", "Italjet", "Sunra", "Evoseed",
    "BF Goodrich", "Elvindo", "U-Winfly", "Uwinfly"
]

all_keywords = keywords + brands

# --- File Penyimpan Link Yang Sudah Diposting ---
posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    with open(posted_links_file, "w") as f:
        pass

def sudah_diposting(link):
    with open(posted_links_file, "r") as f:
        return link.strip() in f.read()

def tandai_sudah_diposting(link):
    with open(posted_links_file, "a") as f:
        f.write(link.strip() + "\n")

# --- Fungsi Relevansi Berita ---
def is_relevant(text):
    text = (text or "").lower()
    return any(kw.lower() in text for kw in all_keywords)

# --- Ambil Berita dari NewsData.io ---
def ambil_berita(keyword):
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={keyword}&language=id&country=id&category=technology,business"
        response = requests.get(url)
        data = response.json()

        print("=== Keyword:", keyword, "===")
        print("Total Results:", data.get("totalResults"))

        results = data.get("results")
        if isinstance(results, list):
            return results
        else:
            print("❌ Format results tidak sesuai:", results)
            return []
    except Exception as e:
        print("❌ Gagal ambil berita:", e)
        return []

# --- Posting Berita ke Twitter ---
def post_berita_ke_twitter():
    random.shuffle(all_keywords)
    for keyword in all_keywords:
        berita_list = ambil_berita(keyword)
        for berita in berita_list:
            if isinstance(berita, dict):
                title = berita.get("title", "")
                content = berita.get("content", "") or berita.get("description", "")
                link = berita.get("link", "")

                # Filter relevansi
                if not (is_relevant(title) or is_relevant(content)):
                    print("Lewat: tidak relevan dengan keyword/brand")
                    continue

                if title and link and not sudah_diposting(link):
                    try:
                        status = f"{title}\n{link}"
                        if len(status) > 280:
                            status = status[:277] + "..."
                        client.create_tweet(text=status)
                        print(f"✅ Berhasil posting: {title}")
                        tandai_sudah_diposting(link)
                        return  # hanya satu posting per siklus
                    except Exception as e:
                        print(f"❌ Gagal posting: {e}")
                else:
                    print("Lewat: sudah pernah atau tidak lengkap")
            else:
                print("Lewat: format data tidak sesuai")

# --- Flask untuk Keep Alive ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/test-tweet')
def test_tweet():
    try:
        client.create_tweet(text="Tes posting dari bot di Render.com 🚀")
        return "✅ Tes tweet berhasil diposting!"
    except Exception as e:
        return f"❌ Gagal posting: {e}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Jalankan Bot ---
keep_alive()
print("🔁 Bot aktif... Posting setiap 1.5 jam sekali")
while True:
    post_berita_ke_twitter()
    time.sleep(5400)  # 1.5 jam
