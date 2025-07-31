import os
import requests
import time
import random
import threading
from dotenv import load_dotenv
from flask import Flask, render_template_string
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
            f"&q={keyword}&language=id&country=id"
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

# === Loop otomatis posting setiap 90 menit ===
def loop_otomatis():
    while True:
        print("🔄 Mengecek dan posting berita...")
        post_berita_ke_twitter()
        print("🕒 Menunggu 90 menit...")
        for i in range(90):  # 90 menit
            print(f"⏳ Menit ke-{i+1} dari 90")
            time.sleep(60)

threading.Thread(target=loop_otomatis, daemon=True).start()

# === Web server ===
app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
        <html>
        <head>
            <title>Twitter Bot Status</title>
            <style>
                body { font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding-top: 50px; }
                .card { background: #1f1f1f; border-radius: 10px; padding: 20px; display: inline-block; box-shadow: 0 0 10px #0f0; }
                h1 { color: #0f0; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>✅ Bot KLAYABAN Aktif</h1>
                <p>Twitter Bot Pak <b>bNdotzz</b> sedang berjalan.</p>
                <p>Memposting berita otomotif listrik setiap 1,5 jam.</p>
            </div>
        </body>
        </html>
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
