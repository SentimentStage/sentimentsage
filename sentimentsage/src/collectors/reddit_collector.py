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