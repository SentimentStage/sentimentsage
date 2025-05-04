# Fully Automated SentimentSage Implementation Guide

This guide provides a step-by-step plan to build a zero-budget, zero-human-effort cryptocurrency sentiment analysis system. All components use free tiers of services and run completely automatically.

## Project Structure

```
sentimentsage/
├── .github/
│   └── workflows/
│       ├── data_collection.yml
│       ├── sentiment_analysis.yml
│       └── deploy.yml
├── src/
│   ├── collectors/
│   │   ├── twitter_collector.py
│   │   ├── reddit_collector.py
│   │   └── news_collector.py
│   ├── analysis/
│   │   ├── sentiment_analyzer.py
│   │   ├── trend_detector.py
│   │   └── report_generator.py
│   ├── web/
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   └── charts.js
│   │   └── css/
│   │       └── style.css
│   └── utils/
│       ├── database.py
│       ├── email_sender.py
│       └── config.py
├── data/
│   ├── collected/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── requirements.txt
└── README.md
```

## Step 1: Set Up GitHub Repository

1. Create a new GitHub repository named "sentimentsage"
2. Enable GitHub Pages in repository settings
3. Set up branch protection rules to prevent workflow disruption

## Step 2: Data Collection System

### Twitter Collector (twitter_collector.py)

```python
import os
import tweepy
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

def get_twitter_client():
    """Initialize Tweepy client with bearer token."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    return tweepy.Client(bearer_token=bearer_token)

def collect_bitcoin_tweets():
    """Collect recent tweets about Bitcoin."""
    client = get_twitter_client()
    
    # Use the free Twitter API v2 search endpoint
    query = "bitcoin lang:en -is:retweet -is:reply -has:links"
    
    # Get the current date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Search recent tweets (limited to ~7 days with free API)
        tweets = client.search_recent_tweets(
            query=query,
            max_results=100,  # Maximum allowed in free tier
            tweet_fields=["created_at", "public_metrics", "author_id"]
        )
        
        # Save tweets to JSON file
        if tweets.data:
            output_file = f"data/collected/twitter_{today}.json"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, "w") as f:
                json_data = [tweet.data for tweet in tweets.data]
                json.dump(json_data, f)
            
            print(f"Collected {len(tweets.data)} tweets about Bitcoin")
            return output_file
        else:
            print("No tweets found")
            return None
            
    except Exception as e:
        print(f"Error collecting tweets: {e}")
        return None

if __name__ == "__main__":
    collect_bitcoin_tweets()
```

### Reddit Collector (reddit_collector.py)

```python
import praw
import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

def get_reddit_client():
    """Initialize Reddit client."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="SentimentSage/0.1",
    )

def collect_bitcoin_posts():
    """Collect recent posts about Bitcoin from relevant subreddits."""
    reddit = get_reddit_client()
    subreddits = ["Bitcoin", "CryptoCurrency", "BitcoinMarkets"]
    
    # Get the current date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    all_posts = []
    
    try:
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for post in subreddit.hot(limit=25):
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "subreddit": subreddit_name,
                    "url": post.url
                }
                all_posts.append(post_data)
        
        # Save posts to JSON file
        if all_posts:
            output_file = f"data/collected/reddit_{today}.json"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, "w") as f:
                json.dump(all_posts, f)
            
            print(f"Collected {len(all_posts)} Reddit posts about Bitcoin")
            return output_file
        else:
            print("No Reddit posts found")
            return None
            
    except Exception as e:
        print(f"Error collecting Reddit posts: {e}")
        return None

if __name__ == "__main__":
    collect_bitcoin_posts()
```

### News Collector (news_collector.py)

```python
import feedparser
import json
import os
import datetime
from newspaper import Article
import time

def collect_crypto_news():
    """Collect news articles about Bitcoin from RSS feeds."""
    feeds = [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cryptonews.com/news/feed/"
    ]
    
    # Get the current date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    all_articles = []
    
    try:
        for feed_url in feeds:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Limit to first 10 articles per feed
                # Check if Bitcoin is mentioned in title or summary
                title = entry.title.lower()
                summary = entry.summary.lower() if hasattr(entry, 'summary') else ""
                
                if "bitcoin" in title or "btc" in title or "bitcoin" in summary or "btc" in summary:
                    article_data = {
                        "title": entry.title,
                        "summary": entry.summary if hasattr(entry, 'summary') else "",
                        "link": entry.link,
                        "published": entry.published if hasattr(entry, 'published') else "",
                        "source": feed.feed.title
                    }
                    
                    # Try to get full article text
                    try:
                        article = Article(entry.link)
                        article.download()
                        time.sleep(1)  # Be nice to the servers
                        article.parse()
                        article_data["full_text"] = article.text
                    except:
                        article_data["full_text"] = ""
                    
                    all_articles.append(article_data)
        
        # Save articles to JSON file
        if all_articles:
            output_file = f"data/collected/news_{today}.json"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, "w") as f:
                json.dump(all_articles, f)
            
            print(f"Collected {len(all_articles)} news articles about Bitcoin")
            return output_file
        else:
            print("No news articles found")
            return None
            
    except Exception as e:
        print(f"Error collecting news articles: {e}")
        return None

if __name__ == "__main__":
    collect_crypto_news()
```

## Step 3: Sentiment Analysis System

### Sentiment Analyzer (sentiment_analyzer.py)

```python
import os
import json
import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Download VADER lexicon (needed once)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def analyze_twitter_sentiment(date=None):
    """Analyze sentiment of collected tweets."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    input_file = f"data/collected/twitter_{date}.json"
    
    if not os.path.exists(input_file):
        print(f"No Twitter data found for {date}")
        return None
    
    try:
        # Load tweets
        with open(input_file, "r") as f:
            tweets = json.load(f)
        
        # Initialize sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        
        # Analyze sentiment for each tweet
        sentiments = []
        for tweet in tweets:
            text = tweet.get("text", "")
            sentiment = sid.polarity_scores(text)
            sentiments.append({
                "text": text,
                "compound": sentiment["compound"],
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"]
            })
        
        # Calculate average sentiment
        if sentiments:
            df = pd.DataFrame(sentiments)
            avg_sentiment = {
                "compound": df["compound"].mean(),
                "positive": df["positive"].mean(),
                "negative": df["negative"].mean(),
                "neutral": df["neutral"].mean(),
                "count": len(sentiments)
            }
            
            # Save results
            output_dir = f"data/processed/"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f"{output_dir}twitter_sentiment_{date}.json"
            with open(output_file, "w") as f:
                json.dump({
                    "average": avg_sentiment,
                    "details": sentiments
                }, f)
            
            print(f"Twitter sentiment analysis complete: {avg_sentiment['compound']}")
            return output_file
        else:
            print("No tweets to analyze")
            return None
            
    except Exception as e:
        print(f"Error analyzing Twitter sentiment: {e}")
        return None

def analyze_reddit_sentiment(date=None):
    """Analyze sentiment of collected Reddit posts."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    input_file = f"data/collected/reddit_{date}.json"
    
    if not os.path.exists(input_file):
        print(f"No Reddit data found for {date}")
        return None
    
    try:
        # Load posts
        with open(input_file, "r") as f:
            posts = json.load(f)
        
        # Initialize sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        
        # Analyze sentiment for each post
        sentiments = []
        for post in posts:
            # Combine title and text for analysis
            text = post.get("title", "") + " " + post.get("selftext", "")
            sentiment = sid.polarity_scores(text)
            sentiments.append({
                "title": post.get("title", ""),
                "compound": sentiment["compound"],
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"]
            })
        
        # Calculate average sentiment
        if sentiments:
            df = pd.DataFrame(sentiments)
            avg_sentiment = {
                "compound": df["compound"].mean(),
                "positive": df["positive"].mean(),
                "negative": df["negative"].mean(),
                "neutral": df["neutral"].mean(),
                "count": len(sentiments)
            }
            
            # Save results
            output_dir = f"data/processed/"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f"{output_dir}reddit_sentiment_{date}.json"
            with open(output_file, "w") as f:
                json.dump({
                    "average": avg_sentiment,
                    "details": sentiments
                }, f)
            
            print(f"Reddit sentiment analysis complete: {avg_sentiment['compound']}")
            return output_file
        else:
            print("No Reddit posts to analyze")
            return None
            
    except Exception as e:
        print(f"Error analyzing Reddit sentiment: {e}")
        return None

def analyze_news_sentiment(date=None):
    """Analyze sentiment of collected news articles."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    input_file = f"data/collected/news_{date}.json"
    
    if not os.path.exists(input_file):
        print(f"No news data found for {date}")
        return None
    
    try:
        # Load articles
        with open(input_file, "r") as f:
            articles = json.load(f)
        
        # Initialize sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        
        # Analyze sentiment for each article
        sentiments = []
        for article in articles:
            # Combine title and full text for analysis
            text = article.get("title", "") + " " + article.get("full_text", "")
            sentiment = sid.polarity_scores(text)
            sentiments.append({
                "title": article.get("title", ""),
                "compound": sentiment["compound"],
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"]
            })
        
        # Calculate average sentiment
        if sentiments:
            df = pd.DataFrame(sentiments)
            avg_sentiment = {
                "compound": df["compound"].mean(),
                "positive": df["positive"].mean(),
                "negative": df["negative"].mean(),
                "neutral": df["neutral"].mean(),
                "count": len(sentiments)
            }
            
            # Save results
            output_dir = f"data/processed/"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f"{output_dir}news_sentiment_{date}.json"
            with open(output_file, "w") as f:
                json.dump({
                    "average": avg_sentiment,
                    "details": sentiments
                }, f)
            
            print(f"News sentiment analysis complete: {avg_sentiment['compound']}")
            return output_file
        else:
            print("No news articles to analyze")
            return None
            
    except Exception as e:
        print(f"Error analyzing news sentiment: {e}")
        return None

def generate_combined_sentiment(date=None):
    """Combine all sentiment sources into an overall score."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Define weights for different sources
    weights = {
        "twitter": 0.4,
        "reddit": 0.4,
        "news": 0.2
    }
    
    combined_sentiment = {
        "date": date,
        "sources": {},
        "overall": None
    }
    
    try:
        # Load Twitter sentiment
        twitter_file = f"data/processed/twitter_sentiment_{date}.json"
        if os.path.exists(twitter_file):
            with open(twitter_file, "r") as f:
                twitter_data = json.load(f)
                combined_sentiment["sources"]["twitter"] = twitter_data["average"]
        
        # Load Reddit sentiment
        reddit_file = f"data/processed/reddit_sentiment_{date}.json"
        if os.path.exists(reddit_file):
            with open(reddit_file, "r") as f:
                reddit_data = json.load(f)
                combined_sentiment["sources"]["reddit"] = reddit_data["average"]
        
        # Load News sentiment
        news_file = f"data/processed/news_sentiment_{date}.json"
        if os.path.exists(news_file):
            with open(news_file, "r") as f:
                news_data = json.load(f)
                combined_sentiment["sources"]["news"] = news_data["average"]
        
        # Calculate weighted average
        if combined_sentiment["sources"]:
            weighted_sum = 0
            total_weight = 0
            
            for source, data in combined_sentiment["sources"].items():
                if source in weights:
                    weighted_sum += data["compound"] * weights[source]
                    total_weight += weights[source]
            
            if total_weight > 0:
                combined_sentiment["overall"] = weighted_sum / total_weight
        
        # Save combined sentiment
        output_dir = f"data/processed/"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}combined_sentiment_{date}.json"
        with open(output_file, "w") as f:
            json.dump(combined_sentiment, f)
        
        print(f"Combined sentiment: {combined_sentiment['overall']}")
        return output_file
    
    except Exception as e:
        print(f"Error generating combined sentiment: {e}")
        return None

if __name__ == "__main__":
    # Run all sentiment analysis
    analyze_twitter_sentiment()
    analyze_reddit_sentiment()
    analyze_news_sentiment()
    generate_combined_sentiment()
```

### Trend Detector (trend_detector.py)

```python
import os
import json
import datetime
import pandas as pd
import numpy as np

def detect_sentiment_trends(days=7):
    """Detect trends in sentiment data over the specified number of days."""
    today = datetime.datetime.now()
    dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    
    sentiment_data = []
    
    try:
        # Load sentiment data for each date
        for date in dates:
            file_path = f"data/processed/combined_sentiment_{date}.json"
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if data["overall"] is not None:
                        sentiment_data.append({
                            "date": date,
                            "sentiment": data["overall"]
                        })
        
        if not sentiment_data:
            print("No sentiment data available for trend analysis")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(sentiment_data)
        df = df.sort_values("date")
        
        # Calculate basic trend metrics
        trends = {
            "dates": df["date"].tolist(),
            "sentiment_values": df["sentiment"].tolist(),
            "average": df["sentiment"].mean(),
            "std_dev": df["sentiment"].std(),
            "min": df["sentiment"].min(),
            "max": df["sentiment"].max()
        }
        
        # Calculate day-to-day changes
        if len(df) > 1:
            df["change"] = df["sentiment"].diff()
            trends["daily_changes"] = df["change"].dropna().tolist()
            
            # Calculate trend direction (positive or negative)
            if len(df) >= 3:
                x = np.arange(len(df))
                y = df["sentiment"].values
                slope, _ = np.polyfit(x, y, 1)
                trends["trend_direction"] = "positive" if slope > 0 else "negative"
                trends["trend_strength"] = abs(slope)
        
        # Save trend data
        output_dir = "data/processed/"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}sentiment_trends.json"
        with open(output_file, "w") as f:
            json.dump(trends, f)
        
        print(f"Trend analysis complete: {trends.get('trend_direction', 'insufficient data')}")
        return output_file
    
    except Exception as e:
        print(f"Error detecting sentiment trends: {e}")
        return None

if __name__ == "__main__":
    detect_sentiment_trends()
```

### Report Generator (report_generator.py)

```python
import os
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt

def generate_daily_report():
    """Generate a daily sentiment report."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Load today's combined sentiment
    combined_file = f"data/processed/combined_sentiment_{today}.json"
    if not os.path.exists(combined_file):
        print(f"No combined sentiment data found for {today}")
        return None
    
    # Load trend data
    trend_file = "data/processed/sentiment_trends.json"
    if not os.path.exists(trend_file):
        print("No trend data found")
        return None
    
    try:
        # Load data
        with open(combined_file, "r") as f:
            combined_data = json.load(f)
        
        with open(trend_file, "r") as f:
            trend_data = json.load(f)
        
        # Create report data
        report = {
            "date": today,
            "current_sentiment": combined_data["overall"],
            "sentiment_category": categorize_sentiment(combined_data["overall"]),
            "sources": combined_data["sources"],
            "trend_direction": trend_data.get("trend_direction", "neutral"),
            "trend_strength": trend_data.get("trend_strength", 0),
            "historical_data": {
                "dates": trend_data["dates"],
                "values": trend_data["sentiment_values"]
            }
        }
        
        # Generate insights
        report["insights"] = generate_insights(report)
        
        # Create visualization
        create_sentiment_chart(trend_data["dates"], trend_data["sentiment_values"], today)
        
        # Save report
        output_dir = "data/processed/"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}daily_report_{today}.json"
        with open(output_file, "w") as f:
            json.dump(report, f)
        
        print(f"Daily report generated for {today}")
        return output_file
    
    except Exception as e:
        print(f"Error generating daily report: {e}")
        return None

def categorize_sentiment(sentiment_value):
    """Categorize sentiment into human-readable format."""
    if sentiment_value >= 0.5:
        return "very positive"
    elif sentiment_value >= 0.2:
        return "positive"
    elif sentiment_value >= -0.2:
        return "neutral"
    elif sentiment_value >= -0.5:
        return "negative"
    else:
        return "very negative"

def generate_insights(report_data):
    """Generate automatic insights based on sentiment data."""
    insights = []
    
    # Current sentiment insight
    sentiment_category = report_data["sentiment_category"]
    insights.append(f"Current Bitcoin sentiment is {sentiment_category} with a score of {report_data['current_sentiment']:.2f}")
    
    # Trend insight
    if "trend_direction" in report_data:
        direction = report_data["trend_direction"]
        strength = report_data["trend_strength"]
        
        if direction == "positive":
            insights.append(f"Sentiment is trending upward with strength {strength:.4f}")
        elif direction == "negative":
            insights.append(f"Sentiment is trending downward with strength {strength:.4f}")
    
    # Source comparison
    sources = report_data.get("sources", {})
    if sources:
        source_values = {}
        for source, data in sources.items():
            source_values[source] = data["compound"]
        
        if source_values:
            max_source = max(source_values, key=source_values.get)
            min_source = min(source_values, key=source_values.get)
            
            insights.append(f"Most positive source: {max_source} ({source_values[max_source]:.2f})")
            insights.append(f"Most negative source: {min_source} ({source_values[min_source]:.2f})")
    
    return insights

def create_sentiment_chart(dates, values, today):
    """Create a visualization of sentiment trends."""
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker='o', linestyle='-', color='blue')
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
        plt.title(f"Bitcoin Sentiment Trend - {today}")
        plt.xlabel("Date")
        plt.ylabel("Sentiment Score")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        output_dir = "src/web/images/"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}sentiment_trend.png")
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating sentiment chart: {e}")
        return False

if __name__ == "__main__":
    generate_daily_report()
```

## Step 4: Email Notification System

### Email Sender (email_sender.py)

```python
import os
import json
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

def create_email_content(is_premium=False):
    """Create email content based on the latest sentiment data."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_file = f"data/processed/daily_report_{today}.json"
    
    if not os.path.exists(report_file):
        print(f"No daily report found for {today}")
        return None, None
    
    try:
        # Load report data
        with open(report_file, "r") as f:
            report = json.load(f)
        
        # Create email subject
        sentiment = report["sentiment_category"]
        subject = f"Bitcoin Sentiment Alert: {sentiment.capitalize()} on {today}"
        
        # Create email body
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ font-size: 12px; color: #666; padding-top: 20px; }}
                .sentiment-score {{ font-size: 24px; font-weight: bold; }}
                .insights {{ background-color: #f5f5f5; padding: 15px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SentimentSage Daily Report</h1>
                </div>
                <div class="content">
                    <h2>Bitcoin Sentiment: <span style="color: {get_sentiment_color(report['current_sentiment'])}">{sentiment.capitalize()}</span></h2>
                    <p class="sentiment-score">{report['current_sentiment']:.2f}</p>
                    
                    <h3>Key Insights:</h3>
                    <div class="insights">
                        <ul>
        """
        
        # Add insights
        for insight in report["insights"]:
            body += f"<li>{insight}</li>\n"
        
        body += """
                        </ul>
                    </div>
        """
        
        # Add premium content if applicable
        if is_premium:
            body += f"""
                    <h3>Detailed Analysis:</h3>
                    <p>Trend Direction: <strong>{report.get('trend_direction', 'neutral')}</strong></p>
                    <p>Trend Strength: <strong>{report.get('trend_strength', 0):.4f}</strong></p>
                    
                    <h3>Source Breakdown:</h3>
                    <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                        <tr>
                            <th>Source</th>
                            <th>Sentiment</th>
                        </tr>
            """
            
            # Add source breakdown
            for source, data in report.get("sources", {}).items():
                body += f"""
                        <tr>
                            <td>{source.capitalize()}</td>
                            <td style="color: {get_sentiment_color(data['compound'])}">{data['compound']:.2f}</td>
                        </tr>
                """
            
            body += """
                    </table>
                    <p><img src="cid:sentiment_chart" alt="Sentiment Trend Chart" style="width: 100%; max-width: 600px;"></p>
            """
        else:
            # Add upgrade prompt for free users
            body += """
                    <div style="background-color: #fffae6; padding: 15px; margin: 15px 0; border-left: 4px solid #ffd700;">
                        <h3>Upgrade to Premium</h3>
                        <p>For detailed source breakdown, trend analysis, and more insights, upgrade to our premium plan.</p>
                        <p><a href="https://github.com/yourusername/sentimentsage" style="background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Upgrade Now</a></p>
                    </div>
            """
        
        # Add footer
        body += """
                </div>
                <div class="footer">
                    <p>This is an automated message from SentimentSage. <a href="https://github.com/yourusername/sentimentsage">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, body
    
    except Exception as e:
        print(f"Error creating email content: {e}")
        return None, None

def get_sentiment_color(sentiment_value):
    """Get color based on sentiment value."""
    if sentiment_value >= 0.5:
        return "#006600"  # dark green
    elif sentiment_value >= 0.2:
        return "#00cc00"  # light green
    elif sentiment_value >= -0.2:
        return "#666666"  # gray
    elif sentiment_value >= -0.5:
        return "#cc0000"  # light red
    else:
        return "#660000"  # dark red

def send_email_notifications(recipients, is_premium=False):
    """Send sentiment report emails to subscribers."""
    subject, body = create_email_content(is_premium)
    
    if not subject or not body:
        print("Failed to create email content")
        return False
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_username or not smtp_password:
        print("SMTP credentials not configured")
        return False
    
    sender_email = smtp_username
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["Subject"] = subject
        
        # Attach HTML content
        message.attach(MIMEText(body, "html"))
        
        # Attach image for premium users
        if is_premium:
            image_path = "src/web/images/sentiment_trend.png"
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', '<sentiment_chart>')
                    message.attach(img)
        
        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send emails
        for recipient in recipients:
            message["To"] = recipient
            server.sendmail(sender_email, recipient, message.as_string())
            print(f"Email sent to {recipient}")
        
        server.quit()
        return True
    
    except Exception as e:
        print(f"Error sending emails: {e}")
        return False

def load_subscribers():
    """Load subscribers from JSON file."""
    subscribers_file = "data/subscribers.json"
    
    if not os.path.exists(subscribers_file):
        return {"free": [], "premium": []}
    
    try:
        with open(subscribers_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading subscribers: {e}")
        return {"free": [], "premium": []}

def send_all_notifications():
    """Send notifications to all subscribers."""
    subscribers = load_subscribers()
    
    # Send to premium subscribers
    if subscribers.get("premium"):
        send_email_notifications(subscribers["premium"], is_premium=True)
    
    # Send to free subscribers
    if subscribers.get("free"):
        send_email_notifications(subscribers["free"], is_premium=False)

if __name__ == "__main__":
    send_all_notifications()

## Step 5: Website Creation

### Main Page (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentimentSage - AI-Powered Crypto Sentiment Analysis</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <div class="container">
            <h1>SentimentSage</h1>
            <p class="tagline">AI-Powered Crypto Market Intelligence</p>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <div class="hero-content">
                <h2>Trade with confidence, powered by AI insights</h2>
                <p>SentimentSage helps crypto traders make more informed decisions by analyzing social sentiment, news, and on-chain data.</p>
                <a href="#subscribe" class="cta-button">Get Free Insights</a>
            </div>
        </section>

        <section id="current-sentiment">
            <h2>Today's Bitcoin Sentiment</h2>
            <div class="sentiment-card" id="sentiment-display">
                <div class="sentiment-score">Loading...</div>
                <div class="sentiment-label">Calculating sentiment...</div>
                <div class="sentiment-date"></div>
            </div>
            <div class="chart-container">
                <canvas id="sentimentChart"></canvas>
            </div>
        </section>

        <section id="subscribe">
            <h2>Get Daily Sentiment Alerts</h2>
            <div class="plans">
                <div class="plan">
                    <h3>Free Insights</h3>
                    <p class="price">$0/month</p>
                    <ul>
                        <li>Daily sentiment score</li>
                        <li>Basic trend information</li>
                        <li>Weekly email summary</li>
                    </ul>
                    <form id="free-signup-form" class="signup-form">
                        <input type="email" name="email" placeholder="Your email address" required>
                        <button type="submit" class="cta-button">Subscribe Free</button>
                    </form>
                </div>
                <div class="plan featured">
                    <h3>Premium Insights</h3>
                    <p class="price">$29/month</p>
                    <ul>
                        <li>Detailed sentiment analysis</li>
                        <li>Source breakdown</li>
                        <li>Daily alerts</li>
                        <li>Trend predictions</li>
                    </ul>
                    <a href="https://buy.stripe.com/your_payment_link" class="cta-button premium-button">Upgrade to Premium</a>
                </div>
            </div>
        </section>

        <section id="how-it-works">
            <h2>How SentimentSage Works</h2>
            <div class="steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <h3>Data Collection</h3>
                    <p>Our AI scans millions of data points from Twitter, Reddit, and crypto news sources.</p>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <h3>Sentiment Analysis</h3>
                    <p>Advanced algorithms analyze the emotional tone and context of discussions.</p>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <h3>Trend Detection</h3>
                    <p>Patterns and emerging narratives are identified before they impact markets.</p>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <h3>Actionable Insights</h3>
                    <p>You receive clear, actionable information to support your trading decisions.</p>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 SentimentSage. All rights reserved.</p>
            <div class="footer-links">
                <a href="#">Terms of Service</a>
                <a href="#">Privacy Policy</a>
                <a href="#">Contact</a>
            </div>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>
```

### CSS Styles (style.css)

```css
/* Base styles */
:root {
    --primary-color: #2563eb;
    --secondary-color: #1e40af;
    --accent-color: #60a5fa;
    --text-color: #333;
    --light-bg: #f3f4f6;
    --dark-bg: #1f2937;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: #fff;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* Header */
header {
    background-color: var(--dark-bg);
    color: white;
    padding: 1.5rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
    font-size: 2rem;
    font-weight: 700;
}

.tagline {
    font-size: 1rem;
    opacity: 0.8;
}

/* Hero section */
.hero {
    padding: 4rem 0;
    background: linear-gradient(to right, #2563eb, #4f46e5);
    color: white;
    text-align: center;
    border-radius: 0 0 10px 10px;
    margin-bottom: 3rem;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 700;
}

.hero p {
    font-size: 1.2rem;
    max-width: 800px;
    margin: 0 auto 2rem;
    opacity: 0.9;
}

.cta-button {
    display: inline-block;
    background-color: white;
    color: var(--primary-color);
    padding: 0.8rem 1.8rem;
    border-radius: 50px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    font-size: 1.1rem;
}

.cta-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Sections */
section {
    padding: 3rem 0;
}

section h2 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: var(--dark-bg);
}

/* Sentiment display */
.sentiment-card {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    padding: 2rem;
    text-align: center;
    max-width: 500px;
    margin: 0 auto 2rem;
}

.sentiment-score {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.sentiment-label {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.sentiment-date {
    font-size: 1rem;
    color: #666;
}

.chart-container {
    height: 300px;
    max-width: 800px;
    margin: 0 auto;
}

/* Pricing plans */
.plans {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2rem;
    margin-top: 2rem;
}

.plan {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    padding: 2rem;
    width: 100%;
    max-width: 380px;
}

.plan.featured {
    border: 2px solid var(--primary-color);
    transform: scale(1.05);
}

.plan h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
}

.price {
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1.5rem;
}

.plan ul {
    margin-bottom: 1.5rem;
    list-style-type: none;
}

.plan li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
}

.plan li:before {
    content: "✓";
    color: var(--success-color);
    margin-right: 0.5rem;
}

.premium-button {
    background-color: var(--primary-color);
    color: white;
    width: 100%;
    text-align: center;
}

/* Signup form */
.signup-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.signup-form input {
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.signup-form button {
    cursor: pointer;
    border: none;
}

/* How it works */
.steps {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2rem;
    margin-top: 2rem;
}

.step {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    padding: 2rem;
    width: 100%;
    max-width: 280px;
    text-align: center;
}

.step-number {
    background-color: var(--primary-color);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-weight: 700;
}

.step h3 {
    margin-bottom: 1rem;
}

/* Footer */
footer {
    background-color: var(--dark-bg);
    color: white;
    padding: 2rem 0;
    margin-top: 4rem;
}

footer .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.footer-links a {
    color: white;
    margin-left: 1rem;
    text-decoration: none;
    opacity: 0.8;
    transition: opacity 0.3s;
}

.footer-links a:hover {
    opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
    .hero h2 {
        font-size: 2rem;
    }
    
    .plan.featured {
        transform: scale(1);
    }
    
    footer .container {
        flex-direction: column;
        text-align: center;
    }
    
    .footer-links a {
        margin: 0 0.5rem;
    }
}
```

### JavaScript Functionality (main.js)

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Load latest sentiment data
    loadSentimentData();
    
    // Set up form submission
    setupForms();
    
    // Update date
    updateDate();
});

function loadSentimentData() {
    // In a real implementation, this would fetch from your API
    // For now, we'll fetch from the JSON file directly
    fetch('/data/processed/combined_sentiment_latest.json')
        .then(response => {
            // If file doesn't exist yet, use sample data
            if (!response.ok) {
                return useSampleData();
            }
            return response.json();
        })
        .then(data => {
            updateSentimentDisplay(data);
        })
        .catch(error => {
            console.error('Error loading sentiment data:', error);
            useSampleData();
        });
    
    // Also load trend data for chart
    fetch('/data/processed/sentiment_trends.json')
        .then(response => {
            if (!response.ok) {
                return useSampleTrendData();
            }
            return response.json();
        })
        .then(data => {
            createSentimentChart(data);
        })
        .catch(error => {
            console.error('Error loading trend data:', error);
            useSampleTrendData();
        });
}

function updateSentimentDisplay(data) {
    const sentimentScore = document.querySelector('.sentiment-score');
    const sentimentLabel = document.querySelector('.sentiment-label');
    
    if (data && data.overall !== null) {
        // Format the sentiment score
        sentimentScore.textContent = data.overall.toFixed(2);
        
        // Determine sentiment category and color
        let category, color;
        
        if (data.overall >= 0.5) {
            category = 'Very Positive';
            color = '#10b981'; // Green
        } else if (data.overall >= 0.2) {
            category = 'Positive';
            color = '#34d399';
        } else if (data.overall >= -0.2) {
            category = 'Neutral';
            color = '#9ca3af';
        } else if (data.overall >= -0.5) {
            category = 'Negative';
            color = '#f87171';
        } else {
            category = 'Very Negative';
            color = '#ef4444'; // Red
        }
        
        sentimentLabel.textContent = category;
        sentimentScore.style.color = color;
    } else {
        sentimentScore.textContent = '0.00';
        sentimentLabel.textContent = 'No data available';
    }
}

function createSentimentChart(data) {
    if (!data || !data.dates || !data.sentiment_values) {
        return useSampleTrendData();
    }
    
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Bitcoin Sentiment',
                data: data.sentiment_values,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: -1,
                    suggestedMax: 1
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.parsed.y;
                            let sentiment = '';
                            
                            if (value >= 0.5) sentiment = 'Very Positive';
                            else if (value >= 0.2) sentiment = 'Positive';
                            else if (value >= -0.2) sentiment = 'Neutral';
                            else if (value >= -0.5) sentiment = 'Negative';
                            else sentiment = 'Very Negative';
                            
                            return `Sentiment: ${value.toFixed(2)} (${sentiment})`;
                        }
                    }
                }
            }
        }
    });
}

function useSampleData() {
    return {
        date: new Date().toISOString().split('T')[0],
        overall: 0.27,
        sources: {
            twitter: { compound: 0.31 },
            reddit: { compound: 0.25 },
            news: { compound: 0.18 }
        }
    };
}

function useSampleTrendData() {
    const today = new Date();
    const dates = [];
    const values = [];
    
    // Generate 7 days of sample data
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(today.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
        
        // Generate a random sentiment between -0.6 and 0.6
        const randomSentiment = (Math.random() * 1.2) - 0.6;
        values.push(randomSentiment);
    }
    
    return {
        dates: dates,
        sentiment_values: values
    };
}

function setupForms() {
    const freeSignupForm = document.getElementById('free-signup-form');
    
    if (freeSignupForm) {
        freeSignupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[name="email"]').value;
            
            // In a real implementation, this would send to your server
            // For now, just store in localStorage
            const subscribers = JSON.parse(localStorage.getItem('subscribers') || '{"free":[],"premium":[]}');
            if (!subscribers.free.includes(email)) {
                subscribers.free.push(email);
                localStorage.setItem('subscribers', JSON.stringify(subscribers));
            }
            
            // Show success message
            this.innerHTML = '<p class="success-message">Thank you! Check your email for confirmation.</p>';
        });
    }
}

function updateDate() {
    const sentimentDate = document.querySelector('.sentiment-date');
    if (sentimentDate) {
        const today = new Date();
        sentimentDate.textContent = today.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
}
```

## Step 6: GitHub Actions Automation

### Data Collection Workflow (.github/workflows/data_collection.yml)

```yaml
name: Data Collection

on:
  schedule:
    # Run daily at 00:00 UTC
    - cron: '0 0 * * *'
  # Allow manual triggering
  workflow_dispatch:

jobs:
  collect_data:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Collect Twitter data
        run: python src/collectors/twitter_collector.py
        env:
          TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
          
      - name: Collect Reddit data
        run: python src/collectors/reddit_collector.py
        env:
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          
      - name: Collect News data
        run: python src/collectors/news_collector.py
        
      - name: Commit and push if data changed
        run: |
          git config --global user.name 'GitHub Actions Bot'
          git config --global user.email 'actions@github.com'
          git add data/collected/
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto data collection update: $(date)"
          git push
```

### Sentiment Analysis Workflow (.github/workflows/sentiment_analysis.yml)

```yaml
name: Sentiment Analysis

on:
  # Run after data collection completes
  workflow_run:
    workflows: ["Data Collection"]
    types:
      - completed
  # Allow manual triggering
  workflow_dispatch:

jobs:
  analyze_sentiment:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run sentiment analysis
        run: python src/analysis/sentiment_analyzer.py
          
      - name: Detect trends
        run: python src/analysis/trend_detector.py
          
      - name: Generate daily report
        run: python src/analysis/report_generator.py
        
      - name: Create symlink to latest sentiment data
        run: |
          TODAY=$(date +"%Y-%m-%d")
          ln -sf "combined_sentiment_${TODAY}.json" data/processed/combined_sentiment_latest.json
        
      - name: Commit and push processed data
        run: |
          git config --global user.name 'GitHub Actions Bot'
          git config --global user.email 'actions@github.com'
          git add data/processed/
          git add src/web/images/
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto sentiment analysis update: $(date)"
          git push
```

### Notification Workflow (.github/workflows/send_notifications.yml)

```yaml
name: Send Notifications

on:
  # Run after sentiment analysis completes
  workflow_run:
    workflows: ["Sentiment Analysis"]
    types:
      - completed
  # Allow manual triggering
  workflow_dispatch:

jobs:
  send_emails:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Send email notifications
        run: python src/utils/email_sender.py
        env:
          SMTP_SERVER: ${{ secrets.SMTP_SERVER }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USERNAME: ${{ secrets.SMTP_USERNAME }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
```

### Deployment Workflow (.github/workflows/deploy.yml)

```yaml
name: Deploy Website

on:
  # Run after all other workflows complete
  workflow_run:
    workflows: ["Send Notifications"]
    types:
      - completed
  # Also run on pushes to main branch
  push:
    branches: [ main ]
  # Allow manual triggering
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@4.1.5
        with:
          branch: gh-pages
          folder: src/web
          # Include the latest processed data
          token: ${{ secrets.GITHUB_TOKEN }}
```

## Step 7: Requirements File

### requirements.txt

```
# Data Collection
tweepy==4.10.1
praw==7.6.0
feedparser==6.0.10
newspaper3k==0.2.8
python-dotenv==0.20.0

# Data Processing
pandas==1.4.2
numpy==1.22.3
nltk==3.7
matplotlib==3.5.2

# Email
```

## Step 8: Setup Instructions

### 1. Repository Setup

1. Create a new GitHub repository named "sentimentsage"
2. Clone

Let me know if you need the full content continued!