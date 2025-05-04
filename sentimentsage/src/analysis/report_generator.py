import os
import json

def load_trend_summary():
    with open("data/processed/trend_summary.json", "r") as f:
        return json.load(f)

def generate_report(trends):
    report_lines = ["# SentimentSage Trend Report\n"]
    for source, stats in trends.items():
        report_lines.append(f"## {source.capitalize()}\n")
        report_lines.append(f"- Average Sentiment: {stats['average']:.3f}")
        report_lines.append(f"- Std Dev: {stats['stddev']:.3f}")
        report_lines.append(f"- Count: {stats['count']}")
        report_lines.append("")
    return "\n".join(report_lines)

def main():
    trends = load_trend_summary()
    report = generate_report(trends)
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/report.md", "w") as f:
        f.write(report)
    print("Report generated.")

if __name__ == "__main__":
    main()