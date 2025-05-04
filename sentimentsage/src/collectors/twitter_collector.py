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