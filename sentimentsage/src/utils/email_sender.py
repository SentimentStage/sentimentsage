import os
import json
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

def get_sentiment_color(sentiment):
    color_map = {
        "positive": "#27ae60",
        "neutral": "#f1c40f",
        "negative": "#e74c3c"
    }
    return color_map.get(sentiment.lower(), "#2980b9")

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
        
        # Enhanced HTML body with color coding and insights
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f8f9fa; }}
                .container {{ background: #fff; border-radius: 8px; padding: 2em; max-width: 600px; margin: auto; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #2c3e50; }}
                .sentiment-label {{ font-size: 1.2em; font-weight: bold; }}
                .sentiment-score {{ font-size: 2em; font-weight: bold; color: {get_sentiment_color(sentiment)}; }}
                .insights ul {{ margin: 0; padding-left: 1.2em; }}
                .footer {{ margin-top: 2em; font-size: 0.9em; color: #888; }}
            </style>
        </head>
        <body>
            <div class=\"container\">
                <h1>SentimentSage Daily Report</h1>
                <h2>Bitcoin Sentiment: <span style=\"color: {get_sentiment_color(sentiment)}\">{sentiment.capitalize()}</span></h2>
                <div class=\"sentiment-score\">{report.get('sentiment_score', 'N/A')}</div>
                <p>Date: {today}</p>
                <p>Summary: {report.get('summary', 'No summary available.')}</p>
                <h3>Key Insights:</h3>
                <div class=\"insights\">
                    <ul>
        """
        # Add insights
        for insight in report.get("insights", []):
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
                <p>Volatility: <strong>{report.get('volatility', 'N/A')}</strong></p>
                <p>Premium Insights: {report.get('premium_insights', 'No additional insights.')}</p>
            """
        body += """
                <p>For more details, visit your dashboard.</p>
            </div>
            <div class=\"footer\">&copy; 2025 SentimentSage. All rights reserved.</div>
        </body>
        </html>
        """
        return subject, body
    except Exception as e:
        print(f"Error creating email content: {e}")
        return None, None

def send_email(recipient, subject, body, image_path=None):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_SENDER", smtp_username)

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', '<report_image>')
            msg.attach(mime_img)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Example usage: send daily report to a list of recipients
    recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
    subject, body = create_email_content()
    if subject and body:
        for recipient in recipients:
            if recipient.strip():
                send_email(recipient.strip(), subject, body)