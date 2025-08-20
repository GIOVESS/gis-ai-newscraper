## GIS & AI Newscraper

Automated daily and weekly email digests for GIS and AI, plus a Streamlit dashboard to preview and send.

### Overview

This repository contains:
- **Daily AI & GIS Digest** (`ai_gis_digest.py`) – fetches and emails top AI/GIS articles
- **Weekly Trends Digest** (`weekly_trends_digest.py`) – compiles notable weekly trends
- **Streamlit Dashboard** (`app.py`) – preview results and send emails interactively

### Prerequisites
- Python 3.9+
- Gmail account with an App Password

### Install
```bash
git clone https://github.com/GIOVESS/gis-ai-newscraper.git
cd gis-ai-newscraper
python -m venv .venv
.venv\Scripts\activate  # PowerShell on Windows
pip install -r requirements.txt
```

### Configure email
You can configure credentials in two ways:
- Via the Streamlit dashboard sidebar (recommended): run the app and enter your Gmail and App Password; it updates `ai_gis_digest.py` and `weekly_trends_digest.py` automatically.
- Manually edit both files and set:
```python
EMAIL_ADDRESS = "your.email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

Gmail App Password steps:
1) Enable 2-Step Verification  2) Open `https://myaccount.google.com/apppasswords`  3) Create an App Password for Mail  4) Use the 16-character password above

### Run
```bash
# Streamlit dashboard (preview + send)
streamlit run app.py

# Daily digest (one-off)
python ai_gis_digest.py

# Weekly trends (one-off)
python weekly_trends_digest.py
```

### Windows Task Scheduler
- Daily task
  - Program: `python`
  - Arguments: `E:\PROJECT\daily-digest\ai_gis_digest.py`
  - Start in: `E:\PROJECT\daily-digest`
- Weekly task (Monday 08:00)
  - Program: `python`
  - Arguments: `E:\PROJECT\daily-digest\weekly_trends_digest.py`
  - Start in: `E:\PROJECT\daily-digest`

### Testing
```bash
# Send a simple test email from within the app (Tab: "Test Email")
# or run the helper script directly:
python test_email.py
```

### Project structure
```
daily-digest/
├── ai_gis_digest.py          # Daily article digest
├── weekly_trends_digest.py   # Weekly trends digest
├── app.py                    # Streamlit dashboard
├── requirements.txt          # Dependencies
├── test_digest.py            # Helpers/tests
├── test_email.py             # Test email sender
└── README.md
```

### Troubleshooting
- **SMTP auth error**: verify App Password and that 2FA is enabled
- **Empty results**: try again later; sources can fluctuate
- **Firewall/Network**: ensure Python has outbound internet access

### License
MIT

### Maintainer
Giovanni Bwayo • giovannibwayo@gmail.com • giovannibwayo.site

### Git push (this repo)
```bash
git init
git add .
git commit -m "Initial commit: GIS & AI newscraper"
git branch -M main
git remote add origin https://github.com/GIOVESS/gis-ai-newscraper.git
git push -u origin main
```


