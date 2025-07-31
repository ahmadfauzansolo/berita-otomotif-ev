import os
import time
import requests
import tweepy
from flask import Flask
from threading import Thread

# === Konfigurasi API Keys ===
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

# === Inisialisasi Flask ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/test-tweet")
def test_tweet():
    tweet("🚀 Ini adalah tweet percobaan dari bot!")
    return "Test tweet berhasil dikirim!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Keyword Pencarian ===
keywords = [
    "motor listrik", "kendaraan listrik", "EV", "sepeda motor listrik", "motor ramah lingkungan",
    "baterai motor", "motor listrik Indonesia", "motor listrik terbaru", "motor listrik murah",
    "konversi motor listrik", "charging station", "kendaraan listrik roda dua", "motor listrik buatan lokal",
    "subsidi motor listrik", "motor listrik tanpa suara", "motor listrik hemat", "motor listrik irit energi",
    "spesifikasi motor listrik", "daya motor listrik", "pengisian baterai motor"
]

brands = [
    "Gesits", "Viar", "Selis", "Volta", "Alva", "Polytron", "Smoot", "Rakata", "Yadea", "United",
    "Honda EM1", "Yamaha E01", "NIU", "Treeletrik", "Uwinfly", "Italjet", "Sunra", "Evoseed",
    "BF Goodrich", "Elvindo"
]

# === Inisialisasi Twitter API ===
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
twitter_api = tweepy.API(auth)

# === Cek apakah berita sudah pernah diposting ===
POSTED_FILE = "posted_links.txt"

def sudah_dipost(link):
    if not os.path.exists(POSTED_FILE):
        return False
    with open(POSTED_FILE, "r") as f:
        return link in f.read()

def tandai_sudah_dipost(link):
    with open(POSTED_FILE, "a") as f:
        f.write(link + "\n")

# === Fungsi Posting ke Twitter ===
def tweet(teks):
    try:
        twitter_api.update_status(teks)
        print("Tweet dipost:", teks)
    except Exception as e:
        print("Gagal posting tweet:", e)

# === Cek dan Posting Berita ===
def cek_berita():
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&language=id&country=id&category=technology,business"
    try:
        response = requests.get(url)
        data = response.json()

        for artikel in data.get("results", []):
            title = artikel.get("title", "")
            content = artikel.get("content", "") or ""
            link = artikel.get("link", "")

            if not link or sudah_dipost(link):
                continue

            teks_lengkap = f"{title} {content}".lower()
            if any(k.lower() in teks_lengkap for k in keywords + brands):
                teks_tweet = f"{title}\n{link}"
                tweet(teks_tweet)
                tandai_sudah_dipost(link)
                break  # Post hanya satu artikel setiap siklus

    except Exception as e:
        print("Gagal mengambil atau memproses berita:", e)

# === Main Loop Bot ===
def start_bot():
    while True:
        print("🔄 Memeriksa berita...")
        cek_berita()
        print("⏳ Menunggu 5 menit...")
        time.sleep(5 * 60)

# === Jalankan Semuanya ===
keep_alive()
start_bot()
