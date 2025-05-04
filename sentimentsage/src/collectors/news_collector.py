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