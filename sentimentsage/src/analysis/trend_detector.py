import os
import json
import glob
import numpy as np

def load_sentiment_results():
    files = glob.glob("data/processed/sentiment_results.json")
    all_results = []
    for file in files:
        with open(file, "r") as f:
            results = json.load(f)
            all_results.extend(results)
    return all_results

def compute_trends(results):
    # Group by source
    sources = {"twitter": [], "reddit": [], "news": []}
    for item in results:
        source = item.get("source")
        sentiment = item.get("sentiment")
        if source in sources and isinstance(sentiment, (int, float)):
            sources[source].append(sentiment)
    trends = {}
    for source, sentiments in sources.items():
        if sentiments:
            avg = float(np.mean(sentiments))
            std = float(np.std(sentiments))
            trends[source] = {"average": avg, "stddev": std, "count": len(sentiments)}
        else:
            trends[source] = {"average": 0, "stddev": 0, "count": 0}
    return trends

def main():
    results = load_sentiment_results()
    trends = compute_trends(results)
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/trend_summary.json", "w") as f:
        json.dump(trends, f)
    print("Trend summary saved.")

if __name__ == "__main__":
    main()