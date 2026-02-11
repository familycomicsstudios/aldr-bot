"""
Manual message sender for ALDR Bot
Allows sending a Discord notification for a specific level row
"""

import requests
from io import StringIO
import csv
import sys
from config import DISCORD_WEBHOOK_URL, SHEET_TSV_URL

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

# Difficulty emoji mapping
DIFFICULTY_EMOJI_MAP = {
    'effortless': '<:effortless:1470940267782869188>',
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
        if difficulty < 1.0:
            return '<:effortless:1470940267782869188>'
        elif difficulty < 2.0:
            return '<:easy:1464320027963424912>'
        elif difficulty < 3.0:
            return '<:medium:1464320095034802289>'
        elif difficulty < 4.0:
            return '<:hard:1464320167571095766>'
        elif difficulty < 5.0:
            return '<:harder:1464320225075007632>'
        elif difficulty < 6.0:
            return '<:insane:1464320293622386812>'
        elif difficulty < 7.0:
            return '<:expert:1464320350237102337>'
        elif difficulty < 8.0:
            return '<:extreme:1464320430658551838>'
        elif difficulty < 9.0:
            return '<:madness:1464320499600462119>'
        elif difficulty < 10.0:
            return '<:master:1464320549600755937>'
        elif difficulty < 11.0:
            return '<:grandmaster:1464320611038924874>'
        elif difficulty < 12.0:
            return '<:gm1:1464320687953940543>'
        elif difficulty < 13.0:
            return '<:gm2:1464320747613978748>'
        elif difficulty < 14.0:
            return '<:tas:1464320806162268222>'
        elif difficulty < 15.0:
            return '<:tas1:1464320856275550414>'
        else:
            return '<:tas2:1464320904061518007>'
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
            print(f"✓ Discord message sent successfully!")
            print(f"  {message}")
            return True
        else:
            print(f"✗ Failed to send Discord message. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error sending Discord message: {e}")
        return False


def main():
    print("=" * 60)
    print("ALDR Bot - Manual Message Sender")
    print("=" * 60)
    
    # Fetch sheet data
    print("\nFetching sheet data...")
    data = fetch_sheet_data()
    
    if not data or len(data) < 2:
        print("✗ No data found in sheet")
        return
    
    print(f"✓ Loaded {len(data) - 1} levels")
    
    # Build username to Discord ID mapping
    username_to_id_map = {}
    for row in data[1:]:
        while len(row) < len(COLUMN_MAP):
            row.append('')
        
        username = row[COLUMN_MAP['TRACKER_USERNAME']].strip() if COLUMN_MAP['TRACKER_USERNAME'] < len(row) else ''
        discord_id = row[COLUMN_MAP['DISCORD_ID']].strip() if COLUMN_MAP['DISCORD_ID'] < len(row) else ''
        
        if username and discord_id:
            username_to_id_map[username] = discord_id
    
    print(f"✓ Found {len(username_to_id_map)} Discord user mappings\n")
    
    # Get row number from user
    if len(sys.argv) > 1:
        try:
            row_num = int(sys.argv[1])
        except ValueError:
            print("✗ Invalid row number. Usage: python send_manual.py <row_number>")
            return
    else:
        # Interactive mode
        print("Available levels:")
        for idx, row in enumerate(data[1:], start=1):
            if len(row) > COLUMN_MAP['LEVEL_NAME']:
                level_name = row[COLUMN_MAP['LEVEL_NAME']].strip()
                level_id = row[COLUMN_MAP['ALDR_ID']].strip() if len(row) > COLUMN_MAP['ALDR_ID'] else ''
                if level_id:
                    print(f"  {idx}. {level_name} (ID: {level_id})")
        
        print()
        try:
            row_num = int(input("Enter row number to send: "))
        except (ValueError, KeyboardInterrupt):
            print("\n✗ Cancelled")
            return
    
    # Validate row number
    if row_num < 1 or row_num > len(data) - 1:
        print(f"✗ Invalid row number. Must be between 1 and {len(data) - 1}")
        return
    
    # Get the row (add 1 because data[0] is header)
    row = data[row_num]
    
    # Ensure row has enough columns
    while len(row) < len(COLUMN_MAP):
        row.append('')
    
    level_id = row[COLUMN_MAP['ALDR_ID']].strip()
    level_name = row[COLUMN_MAP['LEVEL_NAME']].strip()
    creators = row[COLUMN_MAP['CREATOR']].strip()
    difficulty = row[COLUMN_MAP['DIFFICULTY']].strip()
    victors_str = row[COLUMN_MAP['VICTORS']].strip()
    
    if not level_id:
        print("✗ This row has no level ID (empty row)")
        return
    
    if not victors_str:
        print("✗ This level has no victors yet")
        return
    
    # Get the newest (last) victor from the comma-separated list
    victors_list = [v.strip() for v in victors_str.split(',') if v.strip()]
    newest_victor = victors_list[-1] if victors_list else None
    
    if not newest_victor:
        print("✗ Could not find a victor in the victors list")
        return
    
    print(f"\nLevel: {level_name}")
    print(f"Creator(s): {creators}")
    print(f"Difficulty: {difficulty}")
    print(f"All victors: {victors_str}")
    print(f"Newest victor: {newest_victor}")
    print()
    
    # Send the message
    send_discord_message(newest_victor, level_name, creators, difficulty, username_to_id_map)


if __name__ == '__main__':
    main()
