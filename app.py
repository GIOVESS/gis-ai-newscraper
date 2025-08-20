import streamlit as st
import subprocess
import sys
import os
from datetime import datetime
import ai_gis_digest as daily
import weekly_trends_digest as weekly
from streamlit.components.v1 import html as st_html

# Page configuration
st.set_page_config(
    page_title="News Scrapers Dashboard",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success { color: green; }
    .error { color: red; }
    .warning { color: orange; }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">📰 GIS & AI News Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Configuration")
email_address = st.sidebar.text_input("Sender Email", os.getenv("NEWS_SENDER_EMAIL", "giovannibwayo@gmail.com"))
app_password = st.sidebar.text_input("Gmail App Password", os.getenv("NEWS_EMAIL_PASSWORD", "xfgy cnrd suva raxv"))
recipient_email = st.sidebar.text_input("Recipient Email", os.getenv("NEWS_RECIPIENT_EMAIL", email_address))

# Session state for run results and email status
if "daily_html" not in st.session_state:
    st.session_state.daily_html = ""
if "daily_results" not in st.session_state:
    st.session_state.daily_results = []
if "daily_sent" not in st.session_state:
    st.session_state.daily_sent = False
if "daily_sent_at" not in st.session_state:
    st.session_state.daily_sent_at = None

if "weekly_html" not in st.session_state:
    st.session_state.weekly_html = ""
if "weekly_results" not in st.session_state:
    st.session_state.weekly_results = []
if "weekly_sent" not in st.session_state:
    st.session_state.weekly_sent = False
if "weekly_sent_at" not in st.session_state:
    st.session_state.weekly_sent_at = None

# Save configuration
if st.sidebar.button("Save Configuration"):
    # Update the scripts with the provided email and password
    try:
        for script_file in ["ai_gis_digest.py", "weekly_trends_digest.py"]:
            if os.path.exists(script_file):
                with open(script_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Update email and password
                content = content.replace('"your.email@gmail.com"', f'"{email_address}"')
                content = content.replace('"your-app-password"', f'"{app_password}"')
                
                with open(script_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                st.sidebar.success(f"Updated {script_file}")
    except Exception as e:
        st.sidebar.error(f"Error updating configuration: {e}")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["Daily Digest", "Weekly Trends", "Test Email"])

with tab1:
    st.header("📅 My Daily AI & GIS Digest")
    
    # Status banner
    if st.session_state.daily_sent:
        sent_time = st.session_state.daily_sent_at.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.daily_sent_at else ""
        st.success(f"Email already sent{f' at {sent_time}' if sent_time else ''}.")

    st.subheader("Run Once")
    cols = st.columns(3)
    with cols[0]:
        if st.button("🔎 Fetch Daily Digest"):
            with st.spinner("Fetching latest AI & GIS articles..."):
                try:
                    # Configure module credentials dynamically
                    daily.EMAIL_ADDRESS = email_address
                    daily.EMAIL_PASSWORD = app_password
                    daily.RECIPIENT_EMAIL = recipient_email

                    articles = daily.get_news()
                    top_articles = daily.select_top_articles(articles)
                    email_html = daily.generate_email_content(top_articles)

                    st.session_state.daily_results = top_articles
                    st.session_state.daily_html = email_html
                    st.info(f"Prepared {len(top_articles)} articles.")
                except Exception as e:
                    st.error(f"Error preparing digest: {e}")
    with cols[1]:
        if st.button("✉️ Send Daily Email", disabled=st.session_state.daily_sent or not st.session_state.daily_html):
            try:
                # Use prepared HTML; if missing, prepare now
                if not st.session_state.daily_html:
                    daily.EMAIL_ADDRESS = email_address
                    daily.EMAIL_PASSWORD = app_password
                    daily.RECIPIENT_EMAIL = recipient_email
                    articles = daily.get_news()
                    top_articles = daily.select_top_articles(articles)
                    st.session_state.daily_html = daily.generate_email_content(top_articles)
                    st.session_state.daily_results = top_articles

                with st.spinner("Sending daily email..."):
                    sent = daily.send_email_smtp(st.session_state.daily_html, recipient_email=recipient_email)

                if sent:
                    st.session_state.daily_sent = True
                    st.session_state.daily_sent_at = datetime.now()
                    st.success("✅ Daily email sent successfully.")
                    st.rerun()
                else:
                    st.error("❌ Failed to send daily email.")
            except Exception as e:
                st.error(f"Error sending email: {e}")
    with cols[2]:
        if st.button("🗑️ Clear Daily Results", disabled=not (st.session_state.daily_html or st.session_state.daily_results)):
            st.session_state.daily_results = []
            st.session_state.daily_html = ""
            st.session_state.daily_sent = False
            st.session_state.daily_sent_at = None
            st.info("Cleared daily digest state.")

    # Render email-style HTML preview
    if st.session_state.daily_html:
        st.divider()
        st.subheader("Preview")
        st_html(st.session_state.daily_html, height=1000, scrolling=True)

with tab2:
    st.header("📈 My Weekly GIS & AI Trends")
    
    # Status banner
    if st.session_state.weekly_sent:
        sent_time = st.session_state.weekly_sent_at.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.weekly_sent_at else ""
        st.success(f"Email already sent{f' at {sent_time}' if sent_time else ''}.")

    st.subheader("Run Once")
    cols = st.columns(3)
    with cols[0]:
        if st.button("🔎 Fetch Weekly Trends"):
            with st.spinner("Fetching industry trends..."):
                try:
                    # Configure module credentials dynamically
                    weekly.EMAIL_ADDRESS = email_address
                    weekly.EMAIL_PASSWORD = app_password
                    weekly.RECIPIENT_EMAIL = recipient_email

                    trends = weekly.get_industry_trends()
                    top_trends = weekly.select_top_trends(trends)
                    email_html = weekly.generate_trends_email_content(top_trends)

                    st.session_state.weekly_results = top_trends
                    st.session_state.weekly_html = email_html
                    st.info(f"Prepared {len(top_trends)} trends.")
                except Exception as e:
                    st.error(f"Error preparing weekly trends: {e}")
    with cols[1]:
        if st.button("✉️ Send Weekly Email", disabled=st.session_state.weekly_sent or not st.session_state.weekly_html):
            try:
                if not st.session_state.weekly_html:
                    weekly.EMAIL_ADDRESS = email_address
                    weekly.EMAIL_PASSWORD = app_password
                    weekly.RECIPIENT_EMAIL = email_address
                    trends = weekly.get_industry_trends()
                    top_trends = weekly.select_top_trends(trends)
                    st.session_state.weekly_html = weekly.generate_trends_email_content(top_trends)
                    st.session_state.weekly_results = top_trends

                with st.spinner("Sending weekly email..."):
                    sent = weekly.send_trends_email(st.session_state.weekly_html, recipient_email=recipient_email)

                if sent:
                    st.session_state.weekly_sent = True
                    st.session_state.weekly_sent_at = datetime.now()
                    st.success("✅ Weekly trends email sent successfully.")
                    st.rerun()
                else:
                    st.error("❌ Failed to send weekly trends email.")
            except Exception as e:
                st.error(f"Error sending email: {e}")
    with cols[2]:
        if st.button("🗑️ Clear Weekly Results", disabled=not (st.session_state.weekly_html or st.session_state.weekly_results)):
            st.session_state.weekly_results = []
            st.session_state.weekly_html = ""
            st.session_state.weekly_sent = False
            st.session_state.weekly_sent_at = None
            st.info("Cleared weekly trends state.")

    # Render email-style HTML preview
    if st.session_state.weekly_html:
        st.divider()
        st.subheader("Preview")
        st_html(st.session_state.weekly_html, height=1000, scrolling=True)

with tab3:
    st.header("✉️ Test Email Configuration")
    
    st.info("Send a test email to verify your configuration is working correctly")
    
    test_email_content = f"""
    This is a test email from News Scrapers Dashboard.
    
    Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    If you received this email, your configuration is working correctly!
    """
    
    if st.button("Send Test Email"):
        try:
            # Create a simple test script
            test_script = """
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
            
EMAIL_ADDRESS = "{email}"
EMAIL_PASSWORD = "{password}"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
            
def send_test_email():
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Test Email from News Scrapers"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    
    content = \"\"\"{content}\"\"\"
    
    msg.attach(MIMEText(content, "plain"))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    
    print("Test email sent successfully!")
            
if __name__ == "__main__":
    send_test_email()
""".format(email=email_address, password=app_password, content=test_email_content)
            
            with open("test_email.py", "w", encoding='utf-8') as f:
                f.write(test_script)
            
            result = subprocess.run([sys.executable, "test_email.py"], 
                                  capture_output=True, text=True, timeout=60, encoding='utf-8')
            
            if result.returncode == 0:
                st.success("✅ Test email sent successfully!")
                st.info("Please check your inbox (and spam folder) for the test email")
            else:
                st.error("❌ Failed to send test email")
                st.text_area("Error Details", result.stderr, height=100)
                
        except Exception as e:
            st.error(f"Error: {e}")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>News Scrapers Dashboard • Built with Streamlit</p>
    <p>Maintainer: Giovanni Bwayo • giovannibwayo@gmail.com</p>
</div>
""", unsafe_allow_html=True)