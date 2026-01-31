"""
ALDR Bot - Monitors Google Sheet for changes and sends Discord notifications
"""

import time
import schedule
import requests
from datetime import datetime
from io import StringIO
import csv
from config import DISCORD_WEBHOOK_URL, SHEET_TSV_URL, CHECK_INTERVAL

# Sheet columns mapping
COLUMN_MAP = {
    'ALDR_ID': 0,
    'LEVEL_NAME': 1,
    'CREATOR': 2,
    'DIFFICULTY': 3,
    'SKILLS_BALANCE': 4,
    'LIST_POINTS': 5,
    'PROJECT': 6,
    'VIDEO': 7,
    'NOTES': 8,
    'LEVEL_CODE': 9,
    'VICTORS': 10,
    'IMPOSSIBLE': 11,
    'CHALLENGE': 12,
    'TRACKER_USERNAME': 22,
    'DISCORD_ID': 24,
}

# Store previous victors state (dict of level_id -> set of victors)
previous_victors = {}
first_check_done = False

# Difficulty emoji mapping
DIFFICULTY_EMOJI_MAP = {
    'easy': '<:easy:1464320027963424912>',
    'medium': '<:medium:1464320095034802289>',
    'hard': '<:hard:1464320167571095766>',
    'harder': '<:harder:1464320225075007632>',
    'insane': '<:insane:1464320293622386812>',
    'expert': '<:expert:1464320350237102337>',
    'extreme': '<:extreme:1464320430658551838>',
    'madness': '<:madness:1464320499600462119>',
    'master': '<:master:1464320549600755937>',
    'grandmaster': '<:grandmaster:1464320611038924874>',
    'gm1': '<:gm1:1464320687953940543>',
    'gm2': '<:gm2:1464320747613978748>',
    'tas': '<:tas:1464320806162268222>',
    'tas1': '<:tas1:1464320856275550414>',
    'tas2': '<:tas2:1464320904061518007>',
}


def get_difficulty_emoji(difficulty_str):
    """Get emoji for difficulty, mapping numeric ranges and names"""
    difficulty_str = difficulty_str.strip().lower()
    
    # Check if it's a named difficulty
    if difficulty_str in DIFFICULTY_EMOJI_MAP:
        return DIFFICULTY_EMOJI_MAP[difficulty_str]
    
    # Try to parse as numeric difficulty
    try:
        difficulty = float(difficulty_str)
        if difficulty < 1.5:
            return '<:easy:1464320027963424912>'
        elif difficulty < 2.5:
            return '<:medium:1464320095034802289>'
        elif difficulty < 3.5:
            return '<:hard:1464320167571095766>'
        elif difficulty < 4.5:
            return '<:harder:1464320225075007632>'
        elif difficulty < 5.5:
            return '<:insane:1464320293622386812>'
        elif difficulty < 6.5:
            return '<:expert:1464320350237102337>'
        elif difficulty < 7.5:
            return '<:extreme:1464320430658551838>'
        elif difficulty < 8.5:
            return '<:madness:1464320499600462119>'
        elif difficulty < 9.5:
            return '<:master:1464320549600755937>'
        else:
            return '<:grandmaster:1464320611038924874>'
    except ValueError:
        # If can't parse, return the original difficulty
        return difficulty_str


def fetch_sheet_data():
    """Fetch TSV data from Google Sheet"""
    try:
        response = requests.get(SHEET_TSV_URL, timeout=10)
        response.raise_for_status()
        
        # Parse TSV
        tsv_reader = csv.reader(StringIO(response.text), delimiter='\t')
        data = list(tsv_reader)
        
        return data
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return None


def send_discord_message(victor_name, level_name, creators, difficulty, username_to_id_map=None):
    """Send message to Discord webhook"""
    difficulty_emoji = get_difficulty_emoji(difficulty)
    
    # Format victor mention if Discord ID is available
    if username_to_id_map and victor_name in username_to_id_map:
        discord_id = username_to_id_map[victor_name]
        victor_display = f"<@{discord_id}> ({victor_name})"
    else:
        victor_display = victor_name
    
    message = f"**{victor_display}** has beaten **{level_name}** by {creators} - Difficulty: {difficulty} [{difficulty_emoji}]"
    
    payload = {
        "content": message
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print("[OK] Discord message sent: {}".format(message))
        else:
            print("[ERR] Failed to send Discord message. Status: {}".format(response.status_code))
    except Exception as e:
        print("[ERR] Error sending Discord message: {}".format(e))


def check_for_changes():
    """Check for changes in the spreadsheet"""
    global previous_victors, first_check_done
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for changes...")
    
    try:
        data = fetch_sheet_data()
        
        if not data or len(data) < 2:
            print("No data found in sheet")
            return
        
        # Build username to Discord ID mapping
        username_to_id_map = {}
        for row in data[1:]:
            while len(row) < len(COLUMN_MAP):
                row.append('')
            
            username = row[COLUMN_MAP['TRACKER_USERNAME']].strip() if COLUMN_MAP['TRACKER_USERNAME'] < len(row) else ''
            discord_id = row[COLUMN_MAP['DISCORD_ID']].strip() if COLUMN_MAP['DISCORD_ID'] < len(row) else ''
            
            if username and discord_id:
                username_to_id_map[username] = discord_id
        
        # Build current victors dict
        current_victors_dict = {}
        
        # Skip header row and process data
        for row_idx, row in enumerate(data[1:], start=1):
            # Ensure row has enough columns
            while len(row) < len(COLUMN_MAP):
                row.append('')
            
            level_id = row[COLUMN_MAP['ALDR_ID']].strip() if COLUMN_MAP['ALDR_ID'] < len(row) else ''
            level_name = row[COLUMN_MAP['LEVEL_NAME']].strip() if COLUMN_MAP['LEVEL_NAME'] < len(row) else ''
            creators = row[COLUMN_MAP['CREATOR']].strip() if COLUMN_MAP['CREATOR'] < len(row) else ''
            difficulty = row[COLUMN_MAP['DIFFICULTY']].strip() if COLUMN_MAP['DIFFICULTY'] < len(row) else ''
            victors_str = row[COLUMN_MAP['VICTORS']].strip() if COLUMN_MAP['VICTORS'] < len(row) else ''
            
            # Skip if no level ID (empty row)
            if not level_id:
                continue
            
            # Parse victors list (comma-separated) as a set
            current_victors = set(v.strip() for v in victors_str.split(',') if v.strip())
            current_victors_dict[level_id] = {
                'victors': current_victors,
                'level_name': level_name,
                'creators': creators,
                'difficulty': difficulty
            }
            
            # Get previously recorded victors for this level
            previous_victors_set = previous_victors.get(level_id, set())
            
            # Find new victors
            new_victors = current_victors - previous_victors_set
            
            # Only send notifications if this is not the first check
            if new_victors and first_check_done:
                # Send individual notification for each new victor
                print(f"Change detected for level: {level_name}")
                for victor in sorted(new_victors):
                    send_discord_message(victor, level_name, creators, difficulty, username_to_id_map)
        
        # Replace previous victors with current ones
        for level_id, data_dict in current_victors_dict.items():
            previous_victors[level_id] = data_dict['victors']
        
        # Mark first check as done
        if not first_check_done:
            first_check_done = True
            print("[OK] Initial check completed - baseline established")
        else:
            print("[OK] Check completed")
    
    except Exception as e:
        print("[ERR] Error during check: {}".format(e))


def main():
    """Main program loop"""
    print("=" * 60)
    print("ALDR Bot - Spreadsheet Monitor")
    print("=" * 60)
    print(f"Discord webhook: {DISCORD_WEBHOOK_URL[:50]}...")
    print(f"Check interval: {CHECK_INTERVAL} minutes")
    print("=" * 60)
    
    # Verify Discord webhook is configured
    if "YOUR_WEBHOOK" in DISCORD_WEBHOOK_URL:
        print("\n[WARN]  WARNING: Discord webhook URL not configured!")
        print("Please update DISCORD_WEBHOOK_URL in config.py")
        return
    
    # Initial check
    check_for_changes()
    
    # Schedule checks - convert to seconds if less than 1 minute
    if CHECK_INTERVAL < 1:
        interval_seconds = CHECK_INTERVAL * 60
        schedule.every(interval_seconds).seconds.do(check_for_changes)
    else:
        schedule.every(int(CHECK_INTERVAL)).minutes.do(check_for_changes)
    
    print(f"\n[OK] Monitoring started. Will check every {CHECK_INTERVAL} minutes.")
    print("Press Ctrl+C to stop.\n")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[OK] Monitoring stopped.")


if __name__ == '__main__':
    main()
