# ALDR Bot Setup Guide

## Prerequisites
- Python 3.8+
- Discord server with a webhook

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Discord Webhook

1. Go to your Discord server settings
2. Create a webhook in the channel where you want notifications
3. Copy the webhook URL
4. Update `DISCORD_WEBHOOK_URL` in `config.py`

### 3. Run the Program

```bash
python monitor.py
```

The program will:
- Check the spreadsheet every 10 minutes (configurable in `config.py`)
- Send a Discord message whenever a new victor is recorded in column K

## Configuration

Edit `config.py` to customize:
- `DISCORD_WEBHOOK_URL` - Your Discord webhook URL
- `SHEET_TSV_URL` - Google Sheet TSV export URL (pre-configured for the public sheet)
- `CHECK_INTERVAL` - How often to check for changes in minutes

## Files

- `monitor.py` - Main program
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
