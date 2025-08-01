import os
import time
import random
import threading
from dotenv import load_dotenv
from flask import Flask
import tweepy
import feedparser

# Load .env
load_dotenv()

# Twitter API Keys
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Twitter Auth
twitter_client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Keywords utama
keywords = ["mobil listrik", "motor listrik", "sepeda listrik"]

# File penanda berita yang sudah diposting
posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    open(posted_links_file, "w").close()

def sudah_diposting(link):
    with open(posted_links_file, "r") as f:
        return link.strip() in f.read()

def tandai_sudah_diposting(link):
    with open(posted_links_file, "a") as f:
        f.write(link.strip() + "\n")

def is_relevant(title, summary):
    combined = (title or "") + " " + (summary or "")
    combined = combined.lower()
    return any(kw.lower() in combined for kw in keywords)

def ambil_berita_rss():
    berita_semua = []
    for keyword in keywords:
        query = keyword.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=id&gl=ID&ceid=ID:id"
        print(f"🔎 Ambil RSS untuk: {keyword}")
        feed = feedparser.parse(url)
        berita_semua.extend(feed.entries)
    return berita_semua

def post_berita_ke_twitter():
    berita_list = ambil_berita_rss()
    random.shuffle(berita_list)
    for berita in berita_list:
        title = berita.get("title", "")
        link = berita.get("link", "")
        summary = berita.get("summary", "")
        if not (title and link):
            continue
        print(f"📰 Cek: {title}")
        if not is_relevant(title, summary):
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
            return
    print("❌ Tidak ada berita relevan yang bisa diposting kali ini.")

# === Loop otomatis posting setiap 90 menit ===
def loop_otomatis():
    while True:
        print("🔄 Mengecek dan posting berita...")
        post_berita_ke_twitter()
        print("🕒 Menunggu 90 menit...")
        for i in range(90):
            print(f"⏳ Menit ke-{i+1} dari 90")
            time.sleep(60)

threading.Thread(target=loop_otomatis, daemon=True).start()

# === Web server ===
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>Twitter Bot Status</title>
            <style>
                body {
                    background-color: #f0f4f8;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding-top: 100px;
                    color: #333;
                }
                .container {
                    background: white;
                    display: inline-block;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #2c3e50;
                }
                p {
                    font-size: 18px;
                }
                .emoji {
                    font-size: 50px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🤖⚡</div>
                <h1>Twitter Bot: Pak bNdotzz KLAYABAN</h1>
                <p>Status: <strong style="color:green;">Online & Berjalan</strong></p>
                <p>Auto-post berita motor listrik setiap 1,5 jam</p>
                <p>⏰ Terakhir update: <span id="waktu"></span></p>
            </div>
            <script>
                const waktu = new Date().toLocaleString("id-ID", { timeZone: "Asia/Jakarta" });
                document.getElementById("waktu").innerText = waktu;
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
