
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
            
EMAIL_ADDRESS = "giovannibwayo@gmail.com"
EMAIL_PASSWORD = "xfgy cnrd suva raxv"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
            
def send_test_email():
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Test Email from News Scrapers"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    
    content = """
    This is a test email from News Scrapers Dashboard.
    
    Sent at: 2025-08-20 16:56:05
    
    If you received this email, your configuration is working correctly!
    """
    
    msg.attach(MIMEText(content, "plain"))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    
    print("Test email sent successfully!")
            
if __name__ == "__main__":
    send_test_email()
