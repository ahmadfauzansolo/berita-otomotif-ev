from flask import Flask
from threading import Thread
import time
import requests
import tweepy
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/test-tweet')
def test_tweet():
    try:
        # Token dan kunci dari environment
        api_key = os.environ.get("API_KEY")
        api_secret = os.environ.get("API_SECRET")
        access_token = os.environ.get("ACCESS_TOKEN")
        access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

        # Autentikasi Twitter
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
        api = tweepy.API(auth)

        # Kirim tweet
        tweet_text = "Ini adalah tweet uji coba dari route /test-tweet 🚀"
        api.update_status(tweet_text)

        return f"Berhasil mengirim: {tweet_text}"
    except Exception as e:
        return f"Gagal kirim tweet: {str(e)}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Panggil fungsi keep_alive agar Flask aktif
keep_alive()

# Bot utama bisa diletakkan di bawah ini
# while True:
#     cek dan post berita...
#     time.sleep(5400)
