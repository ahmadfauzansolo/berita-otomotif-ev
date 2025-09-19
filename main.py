import os
import requests
import tweepy
from datetime import datetime

# ==============================
# KEYWORDS
# ==============================
keywords = ["mobil listrik", "motor listrik", "kendaraan listrik"]

# ==============================
# TWITTER ENV CHECK
# ==============================
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

missing_keys = []
for name, val in [
    ("TWITTER_API_KEY", TWITTER_API_KEY),
    ("TWITTER_API_SECRET", TWITTER_API_SECRET),
    ("ACCESS_TOKEN", ACCESS_TOKEN),
    ("ACCESS_SECRET", ACCESS_SECRET)
]:
    if not val:
        missing_keys.append(name)

if missing_keys:
    print(f"⚠️ Tidak bisa posting ke Twitter, environment variable hilang: {missing_keys}")
    can_post = False
else:
    can_post = True
    twitter_client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

# ==============================
# FILE UNTUK LINK SUDAH DIPOSTING
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
# LOG QUOTA EXCEEDED
# ==============================
quota_log_file = "quota_errors.log"

def log_quota_exceeded(keyword):
    with open(quota_log_file, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Quota exceeded untuk keyword '{keyword}'\n")
    print(f"⚠️ Quota exceeded tercatat untuk '{keyword}'")

# ==============================
# LOG POSTING BERITA
# ==============================
posted_log_file = "posted_log.log"

def log_posted_news(title, link):
    with open(posted_log_file, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {title} | {link}\n")

# ==============================
# CEK RELEVANSI
# ==============================
def is_relevant(title, content):
    combined = (title or "") + " " + (content or "")
    combined = combined.lower()
    return any(kw.lower() in combined for kw in keywords)

# ==============================
# AMBIL BERITA DARI NEWSDATA.IO
# ==============================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def ambil_berita(keyword):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={keyword}&language=id"
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        print("❌ Gagal ambil berita:", e)
        return []

    if isinstance(data, dict) and data.get("status") == "error":
        # Catat quota exceeded
        if "quota" in str(data).lower() or "exceeded" in str(data).lower():
            log_quota_exceeded(keyword)
        else:
            print(f"⚠️ Data berita tidak valid untuk keyword '{keyword}': {data.get('message', 'unknown error')}")
        return []

    results = data.get("results", [])
    if not isinstance(results, list):
        print(f"⚠️ Data berita tidak valid, results bukan list: {results}")
        return []

    return results

# ==============================
# POST BERITA KE TWITTER
# ==============================
def post_berita_ke_twitter():
    total_posted = 0
    print(f"🚀 Script dijalankan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for kw in keywords:
        berita_list = ambil_berita(kw)
        print(f"🔎 {kw}: {len(berita_list)} berita ditemukan")
        for berita in berita_list:
            title = berita.get("title")
            link = berita.get("link")
            content = berita.get("description") or berita.get("content")

            if not title or not link:
                print("⚠️ Data berita tidak valid")
                continue

            if sudah_diposting(link):
                continue

            if not is_relevant(title, content):
                continue

            if can_post:
                try:
                    twitter_client.create_tweet(text=f"{title}\n{link}")
                    total_posted += 1
                    tandai_sudah_diposting(link)
                    log_posted_news(title, link)
                    print(f"✅ Berhasil post: {title}")
                except Exception as e:
                    print("⚠️ Gagal posting:", e)
            else:
                print(f"ℹ️ Skip posting karena Twitter API key hilang: {title}")

    print(f"📢 Total {total_posted} berita diposting kali ini")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    post_berita_ke_twitter()
