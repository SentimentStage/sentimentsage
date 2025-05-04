import os
import json
from textblob import TextBlob
import glob

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob (simple polarity)."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def process_twitter_data():
    input_files = glob.glob("data/collected/twitter_*.json")
    results = []
    for file in input_files:
        with open(file, "r") as f:
            tweets = json.load(f)
            for tweet in tweets:
                text = tweet.get("text", "")
                polarity = analyze_sentiment(text)
                results.append({
                    "source": "twitter",
                    "id": tweet.get("id"),
                    "text": text,
                    "sentiment": polarity
                })
    return results

def process_reddit_data():
    input_files = glob.glob("data/collected/reddit_*.json")
    results = []
    for file in input_files:
        with open(file, "r") as f:
            posts = json.load(f)
            for post in posts:
                text = post.get("title", "") + " " + post.get("selftext", "")
                polarity = analyze_sentiment(text)
                results.append({
                    "source": "reddit",
                    "id": post.get("id"),
                    "text": text,
                    "sentiment": polarity
                })
    return results

def process_news_data():
    input_files = glob.glob("data/collected/news_*.json")
    results = []
    for file in input_files:
        with open(file, "r") as f:
            articles = json.load(f)
            for article in articles:
                text = article.get("title", "") + " " + article.get("summary", "") + " " + article.get("full_text", "")
                polarity = analyze_sentiment(text)
                results.append({
                    "source": "news",
                    "title": article.get("title"),
                    "sentiment": polarity
                })
    return results

def main():
    twitter_results = process_twitter_data()
    reddit_results = process_reddit_data()
    news_results = process_news_data()
    all_results = twitter_results + reddit_results + news_results
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/sentiment_results.json", "w") as f:
        json.dump(all_results, f)
    print(f"Processed {len(all_results)} items for sentiment analysis.")

if __name__ == "__main__":
    main()