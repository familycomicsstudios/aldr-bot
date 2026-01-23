import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord webhook URL
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN")

# Google Sheets TSV export URL (public sheet)
SHEET_TSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrZEUcAFIiGmzFAjjdUVKWhDSLue_SvTQIxT4ZbhlvBa6yc4l4juAZn3HREfvO0VIv2ms98453VItI/pub?gid=0&single=true&output=tsv"

# Check interval (in minutes)
CHECK_INTERVAL = float(os.getenv("CHECK_INTERVAL", "10"))
