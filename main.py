import os
import requests
import tweepy
import time
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
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

missing_keys = []
for name, val in [
    ("TWITTER_API_KEY", TWITTER_API_KEY),
    ("TWITTER_API_SECRET", TWITTER_API_SECRET),
    ("TWITTER_ACCESS_TOKEN", ACCESS_TOKEN),
    ("TWITTER_ACCESS_SECRET", ACCESS_SECRET)
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
# TELEGRAM BOT
# ==============================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # contoh: "@namachannel" atau chat_id numerik

def send_to_telegram(title, link):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return  # kalau env belum diset, abaikan saja

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": f"✅ Berhasil diposting ke Twitter:\n\n{title}\n{link}",
            "disable_web_page_preview": False
        }
        requests.post(url, data=payload, timeout=10)
        print(f"📩 [TELEGRAM] Terkirim: {title}")
    except Exception as e:
        print("⚠️ [TELEGRAM ERROR]", e)

# ==============================
# FILE UNTUK LINK SUDAH DIPOSTING
# ==============================
posted_links_file = "posted_links.txt"
if not os.path.exists(posted_links_file):
    open(posted_links_file, "w").close()

def normalize_link(link):
    """Samakan format link supaya tidak terdeteksi berbeda"""
    return (link or "").strip().split("?")[0].rstrip("/")

def sudah_diposting(link):
    link = normalize_link(link)
    with open(posted_links_file, "r") as f:
        posted = [normalize_link(l) for l in f.readlines()]
    return link in posted

def tandai_sudah_diposting(link):
    link = normalize_link(link)
    with open(posted_links_file, "a") as f:
        f.write(link + "\n")

# ==============================
# LOGGING FILES
# ==============================
quota_log_file = "quota_errors.log"
posted_log_file = "posted_log.log"
duplicate_log_file = "duplicate_errors.log"
rate_limit_log_file = "rate_limit_errors.log"

def log_quota_exceeded(keyword):
    with open(quota_log_file, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - Quota exceeded untuk keyword '{keyword}'\n")
    print(f"⚠️ [QUOTA] Limit NewsData untuk '{keyword}'")

def log_posted_news(title, link):
    with open(posted_log_file, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - {title} | {link}\n")

def log_duplicate_error(title, link):
    with open(duplicate_log_file, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - DUPLICATE: {title} | {link}\n")
    print(f"⚠️ [DUPLICATE] {title}")

def log_rate_limit_error(title, link):
    with open(rate_limit_log_file, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - RATE LIMIT: {title} | {link}\n")
    print(f"⚠️ [RATE LIMIT] {title}")

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
        print("❌ [FETCH ERROR]", e)
        return []

    if isinstance(data, dict) and data.get("status") == "error":
        if "quota" in str(data).lower() or "exceeded" in str(data).lower():
            log_quota_exceeded(keyword)
        else:
            print(f"⚠️ [INVALID] Data berita '{keyword}': {data.get('message', 'unknown error')}")
        return []

    results = data.get("results", [])
    if not isinstance(results, list):
        print(f"⚠️ [INVALID] Hasil bukan list: {results}")
        return []

    return results

# ==============================
# POST BERITA KE TWITTER
# ==============================
MAX_POSTS_PER_RUN = 5       # batasi posting per eksekusi cron
DELAY_BETWEEN_POSTS = 30    # delay antar posting (detik)

def post_berita_ke_twitter():
    total_posted = 0
    print(f"\n🚀 Script dijalankan - {datetime.now():%Y-%m-%d %H:%M:%S}")
    for kw in keywords:
        if total_posted >= MAX_POSTS_PER_RUN:
            break
        berita_list = ambil_berita(kw)
        print(f"🔎 {kw}: {len(berita_list)} berita ditemukan")
        for berita in berita_list:
            if total_posted >= MAX_POSTS_PER_RUN:
                break

            title = berita.get("title")
            link = berita.get("link")
            content = berita.get("description") or berita.get("content")

            if not title or not link:
                print("⚠️ [SKIP] Data berita tidak valid")
                continue

            if sudah_diposting(link):
                print(f"⏭️ [SKIP] Sudah pernah diposting: {title}")
                continue

            if not is_relevant(title, content):
                print(f"⏭️ [SKIP] Tidak relevan: {title}")
                continue

            if can_post:
                try:
                    twitter_client.create_tweet(text=f"{title}\n{link}")
                    total_posted += 1
                    tandai_sudah_diposting(link)
                    log_posted_news(title, link)
                    print(f"✅ [POSTED] {title}")

                    # Kirim ke Telegram setelah sukses ke Twitter
                    send_to_telegram(title, link)

                    time.sleep(DELAY_BETWEEN_POSTS)
                except Exception as e:
                    err_str = str(e)
                    print("⚠️ [ERROR]", err_str)
                    if "duplicate" in err_str.lower():
                        log_duplicate_error(title, link)
                        tandai_sudah_diposting(link)  # supaya tidak diulang lagi
                    elif "429" in err_str or "Too Many Requests" in err_str:
                        log_rate_limit_error(title, link)
            else:
                print(f"ℹ️ [SKIP] Twitter API key hilang: {title}")

    print(f"📢 Total {total_posted} berita diposting kali ini\n")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    post_berita_ke_twitter()
