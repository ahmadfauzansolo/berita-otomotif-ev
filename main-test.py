from flask import Flask
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Token dari .env
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Autentikasi Twitter
twitter_client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

@app.route("/")
def index():
    return "✅ Twitter Bot Test Service is Running"

@app.route("/test-tweet")
def test_tweet():
    try:
        tweet = twitter_client.create_tweet(text="✅ Test tweet from Render at /test-tweet")
        return f"Berhasil: {tweet.data}"
    except Exception as e:
        return f"Gagal kirim tweet: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
