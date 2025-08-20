import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
import re
import sys
import os

# ===== CONFIGURATION =====
EMAIL_ADDRESS = os.getenv("NEWS_SENDER_EMAIL", "giovannibwayo@gmail.com")
EMAIL_PASSWORD = os.getenv("NEWS_EMAIL_PASSWORD", "xfgy cnrd suva raxv")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
RECIPIENT_EMAIL = os.getenv("NEWS_RECIPIENT_EMAIL", "giovannibwayo@gmail.com")
MAX_TRENDS = 10  # Limit to top 10 trends

# ===== INDUSTRY TRENDS SOURCES =====
TREND_SOURCES = [
    {
        "name": "Towards Data Science Trends",
        "url": "https://towardsdatascience.com/feed",
        "type": "blog"
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "type": "news"
    },
    {
        "name": "Google AI Blog",
        "url": "https://ai.googleblog.com/feeds/posts/default",
        "type": "corporate"
    },
    {
        "name": "AWS Machine Learning Blog",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "type": "corporate"
    },
    {
        "name": "Esri Insights Blog",
        "url": "https://www.esri.com/arcgis-blog/feed/",
        "type": "gis"
    },
    {
        "name": "Mapbox Blog",
        "url": "https://blog.mapbox.com/rss",
        "type": "gis"
    },
    {
        "name": "KDnuggets News",
        "url": "https://www.kdnuggets.com/feed",
        "type": "news"
    },
    {
        "name": "Analytics Vidhya",
        "url": "https://www.analyticsvidhya.com/blog/feed/",
        "type": "blog"
    },
    {
        "name": "GIS Lounge",
        "url": "https://www.gislounge.com/feed/",
        "type": "gis"
    },
    {
        "name": "Harvard Data Science Review",
        "url": "https://hdsr.mitpress.mit.edu/rss_2.0",
        "type": "academic"
    }
]

# ===== FUNCTIONS =====
def extract_trend_content(url):
    """Extract content from trend articles"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:350] + "..." if len(text) > 350 else text
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return "Content not available"

def is_trend_article(title, content):
    """Check if article is about trends/developments"""
    trend_keywords = [
        "trend", "development", "advance", "innovation", "emerging",
        "future", "2025", "2024", "outlook", "prediction",
        "breakthrough", "new", "latest", "update", "release",
        "survey", "report", "study", "analysis", "forecast"
    ]
    
    content = content.lower()
    title = title.lower()
    
    # Check for trend-related keywords
    trend_score = sum(1 for keyword in trend_keywords if keyword in title or keyword in content)
    
    return trend_score >= 2  # At least 2 trend keywords

def calculate_trend_score(article, source_type):
    """Calculate relevance score for trend articles"""
    title = article['title'].lower()
    content = article.get('content', '').lower()
    
    score = 0
    
    # Source type weighting
    source_weights = {
        "academic": 8,
        "corporate": 7, 
        "news": 6,
        "blog": 5,
        "gis": 6
    }
    score += source_weights.get(source_type, 5)
    
    # Trend keyword matches
    trend_keywords = [
        "trend", "development", "advance", "innovation", "emerging",
        "future", "2025", "2024", "outlook", "prediction"
    ]
    
    for keyword in trend_keywords:
        if keyword in title:
            score += 3
        if keyword in content:
            score += 2
    
    # Industry impact keywords
    impact_keywords = [
        "transform", "revolution", "disrupt", "change", "shift",
        "growth", "market", "industry", "adoption", "implementation"
    ]
    
    for keyword in impact_keywords:
        if keyword in title:
            score += 2
        if keyword in content:
            score += 1
    
    # Recency bonus (prefer articles from last 7 days)
    try:
        published_date = article.get('published', '')
        if 'hour' in published_date or 'day' in published_date:
            score += 5
        elif 'week' in published_date:
            score += 3
    except:
        pass
    
    # Length bonus (longer articles often have more substance)
    if len(content) > 500:
        score += 2
    
    return score

def get_industry_trends():
    """Fetch industry trends and developments"""
    trends = []
    
    print("Fetching industry trends...")
    
    for source in TREND_SOURCES:
        try:
            print(f"Checking {source['name']}...")
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                continue
                
            for entry in feed.entries[:15]:  # Check first 15 entries per source
                # Skip if too old (rough check)
                published = entry.get('published', '')
                if '2023' in published or '2022' in published:
                    continue
                
                # Get content
                content = entry.get('summary', '')
                if not content or len(content) < 100:
                    content = extract_trend_content(entry.link)
                
                # Check if this is a trend article
                if is_trend_article(entry.title, content):
                    trend_score = calculate_trend_score({
                        'title': entry.title,
                        'content': content,
                        'published': published
                    }, source['type'])
                    
                    trends.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': content[:300] + "..." if len(content) > 300 else content,
                        'source': source['name'],
                        'source_type': source['type'],
                        'published': published,
                        'score': trend_score
                    })
                    print(f"  ✓ Trend found: {entry.title} (Score: {trend_score})")
                    
        except Exception as e:
            print(f"Error processing {source['name']}: {e}")
    
    return trends

def select_top_trends(trends, max_trends=MAX_TRENDS):
    """Select the top N most relevant trends"""
    # Sort by trend score (descending)
    sorted_trends = sorted(trends, key=lambda x: x['score'], reverse=True)
    
    # Return top N trends
    return sorted_trends[:max_trends]

def generate_trends_email_content(trends):
    """Generate HTML email content for trends"""
    if not trends:
        return """
        <html>
        <body>
            <h2>🌐 GIS & AI Weekly Trends Digest</h2>
            <p>No significant trends identified this week. Check back next week!</p>
        </body>
        </html>
        """
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; text-align: center; }}
            .trend {{ margin-bottom: 30px; padding: 20px; border-radius: 8px; background-color: #f8f9fa; border-left: 5px solid #667eea; }}
            .trend h3 {{ margin-top: 0; color: #2c3e50; }}
            .trend a {{ color: #3498db; text-decoration: none; font-weight: bold; }}
            .trend a:hover {{ text-decoration: underline; }}
            .meta {{ font-size: 0.9em; color: #7f8c8d; margin-bottom: 12px; }}
            .score {{ float: right; background-color: #667eea; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.85em; }}
            .source-badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 0.8em; margin-right: 10px; }}
            .source-academic {{ background-color: #8e44ad; color: white; }}
            .source-corporate {{ background-color: #3498db; color: white; }}
            .source-news {{ background-color: #e74c3c; color: white; }}
            .source-blog {{ background-color: #2ecc71; color: white; }}
            .source-gis {{ background-color: #f39c12; color: white; }}
            .footer {{ margin-top: 40px; padding: 20px; text-align: center; font-size: 0.9em; color: #7f8c8d; border-top: 1px solid #eee; }}
            .insight {{ background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌐 GIS & AI Weekly Trends Digest</h1>
            <p>Week of {datetime.now().strftime('%B %d, %Y')}</p>
            <p>Top {len(trends)} industry developments and emerging trends</p>
        </div>
        
        <div class="insight">
            <strong>📈 This Week's Focus:</strong> The most significant developments in geospatial AI, 
            machine learning applications, and data science innovations that are shaping the industry.
        </div>
    """
    
    for i, trend in enumerate(trends, 1):
        # Determine source type for styling
        source_class = f"source-{trend['source_type']}"
        source_name = trend['source_type'].capitalize()
        
        html_content += f"""
        <div class="trend">
            <span class="score">Impact: {trend['score']}</span>
            <h3>{i}. {trend['title']}</h3>
            <div class="meta">
                <span class="source-badge {source_class}">{source_name}</span>
                <strong>Source:</strong> {trend['source']} | 
                <strong>Published:</strong> {trend['published']}
            </div>
            <p>{trend['summary']}</p>
            <p><a href="{trend['link']}">🔗 Read detailed analysis</a></p>
        </div>
        """
    
    html_content += f"""
        <div class="footer">
            <p>Curated from leading industry sources • {datetime.now().strftime('%Y-%m-%d')}</p>
            <p>This weekly digest was created for Giovanni Bwayo</p>
        </div>
    </body>
    </html>
    """
    return html_content

def send_trends_email(content, recipient_email: str = None, subject: str = None,
    sender_email: str = None, sender_password: str = None):
    """Send trends email using SMTP with optional overrides."""
    from_addr = sender_email or EMAIL_ADDRESS
    password = sender_password or EMAIL_PASSWORD
    to_addr = recipient_email or RECIPIENT_EMAIL
    email_subject = subject or f"🌐 GIS & AI Weekly Trends - {datetime.now().strftime('%Y-%m-%d')}"

    msg = MIMEMultipart("alternative")
    msg['Subject'] = email_subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    msg.attach(MIMEText(content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(from_addr, password)
            server.send_message(msg)
        print(f"{datetime.now()}: Trends email sent successfully to {to_addr}!")
        return True
    except Exception as e:
        print(f"{datetime.now()}: Error sending trends email: {e}")
        return False

def send_weekly_trends_digest(recipient_email: str = None):
    """Main function to fetch trends and send weekly email. Allows recipient override."""
    print(f"{datetime.now()}: Starting weekly trends collection...")
    
    # Get industry trends
    trends = get_industry_trends()
    print(f"{datetime.now()}: Found {len(trends)} potential trends")
    
    # Select top trends
    top_trends = select_top_trends(trends)
    print(f"{datetime.now()}: Selected top {len(top_trends)} trends")
    
    # Generate email content
    email_content = generate_trends_email_content(top_trends)
    
    # Send email
    success = send_trends_email(email_content, recipient_email=recipient_email)
    
    if success:
        print(f"{datetime.now()}: Weekly trends digest sent with {len(top_trends)} trends")
    else:
        print(f"{datetime.now()}: Failed to send trends digest")

# Add this function to check if running in Streamlit
def is_running_in_streamlit():
    return 'streamlit' in sys.modules

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    if is_running_in_streamlit():
        # When running in Streamlit, just define functions but don't auto-run
        print("Running in Streamlit mode - functions available but not auto-executing")
    else:
        print("GIS & AI Weekly Trends Digest System")
        print("====================================")
        
        # Run once immediately for testing
        print("Running initial trends test...")
        send_weekly_trends_digest()
        
        # Schedule weekly on Monday at 8:00 AM
        schedule.every().monday.at("08:00").do(send_weekly_trends_digest)
        
        print("Weekly trends scheduler started. Will run every Monday at 8:00 AM.")
        print("Press Ctrl+C to exit.")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour