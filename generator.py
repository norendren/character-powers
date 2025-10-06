#!/usr/bin/env python3
"""
Marvel Multiverse RPG - Power Reference Sheet Generator
Usage: python generate_power_sheet.py
"""

import json
import re
import sys
from difflib import get_close_matches

def load_powers_db(filepath='full_powers.json'):
    """Load the powers database from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please ensure it's in the same directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filepath} is not valid JSON.")
        exit(1)

def parse_power_list_robust(text, db):
    """
    Parse the power list by searching the input text for known power names,
    prioritizing longer names to prevent substring false positives.
    """
    
    # 1. Normalize the text (Eliminate all layout/whitespace issues)
    # This turns the messy block into one long, clean string.
    # Replace all whitespace/newlines/tabs with a single space
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove all bullet points for a cleaner search space
    text = text.replace('◆', '').replace('|', '').strip() 
    
    # 2. Prepare the database names (list of all keys, sorted by length descending)
    all_power_names = list(db['powers'].keys())
    all_power_names.sort(key=len, reverse=True)
    
    found_powers = []
    
    # Use a mutable copy of the text string
    search_text = text
    
    # 3. Search for the longest names first and remove them from the text
    for power_name in all_power_names:
        # We need an exact word boundary check to avoid false positives 
        # like matching "bolt" in "bolts" or a power name embedded in a header.
        # However, since the input is just one giant clean string, a simple 
        # 'in' check is often robust enough after the long-name sort.
        # Let's use a non-regex check first for speed.
        
        # Simple check for power name existence
        if power_name in search_text:
            found_powers.append({'name': power_name, 'power_set': None})
            
            # Remove the found name to prevent shorter names from matching a substring.
            # Example: If 'Slashing Fist' is found, remove it, so 'Slashing' isn't
            # found afterward.
            search_text = search_text.replace(power_name, ' ', 1)
            
    # The current robust method sacrifices Power Set tracking (which was brittle anyway).
    # If Power Set is critical, you'd need a second, much more complex regex pass
    # to extract text between known headers, but that reintroduces brittleness.
    # For a *reference sheet*, the action type (Permanent, Standard, etc.) from the DB
    # is usually more important than the source Power Set.
    
    # Deduplicate the list just in case of odd matches
    unique_powers = []
    seen_names = set()
    for power in found_powers:
        if power['name'] not in seen_names:
            unique_powers.append(power)
            seen_names.add(power['name'])
            
    return unique_powers

def parse_power_list(text):
    """
    Parse the power list from character sheet format.
    Focuses only on lines containing the bullet-point symbol (◆) and tracks headers.
    """
    # 1. Standardize and normalize the text
    text = re.sub(r'^POWERS\s*', '', text.strip(), flags=re.IGNORECASE)
    
    # FIX #1: Replace inline bullets with a newline and a bullet
    text = re.sub(r'\s*◆\s*', '\n◆', text)
    
    # 2. Split the text into lines
    lines = re.split(r'[\r\n]+', text)
    
    powers = []
    current_power_set = None
    last_power_index = -1 
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue

        # 1. Bullet-Point Item (New Power)
        if line.startswith('◆'):
            power_name = line.replace('◆', '', 1).strip()
            
            powers.append({
                'name': power_name,
                'power_set': current_power_set
            })
            last_power_index = len(powers) - 1
            
        # 2. Non-Bulleted Item (Header OR Continuation)
        else:
            # Check for standard header exclusion (e.g., '(Energy)')
            if line.startswith('(') and line.endswith(')'):
                continue
                
            # FIX #2: Determine if this is a CONTINUATION or a NEW HEADER
            
            # A line is a CONTINUATION if a power was just added (last_power_index != -1) 
            # AND the text looks like a power name continuation (e.g., contains only words, not multiple parentheses/special characters indicating a full header)
            
            # Use a strict check: If the previous line was a power, assume this non-bulleted line is a continuation.
            # Only reset if the text clearly looks like a header (e.g., ALL CAPS, or contains "Power" or "Weapons").
            is_new_header = any(keyword in line.upper() for keyword in ["POWERS", "WEAPONS", "BASIC"])
            
            if last_power_index != -1 and not is_new_header:
                # Treat as Continuation of the LAST power name (e.g., "Protection" for "Environmental")
                powers[last_power_index]['name'] += " " + line
                
            else:
                # Treat as New Header/Power Set
                current_power_set = line
                last_power_index = -1 # Stop merging lines until the next bullet point
                
    return powers

def find_power_in_db(power_name, db):
    """Find a power in the database with fuzzy matching."""
    powers = db['powers']
    
    # Try exact match first
    if power_name in powers:
        return powers[power_name]
    
    # Try case-insensitive match
    for key in powers:
        if key.lower() == power_name.lower():
            return powers[key]
    
    # Try removing spaces
    no_spaces = power_name.replace(' ', '')
    for key in powers:
        if key.replace(' ', '').lower() == no_spaces.lower():
            return powers[key]
    
    # Try fuzzy matching
    all_power_names = list(powers.keys())
    matches = get_close_matches(power_name, all_power_names, n=1, cutoff=0.8)
    if matches:
        return powers[matches[0]]
    
    return None

def categorize_powers(parsed_powers, db):
    """Categorize powers by action type."""
    categories = {
        'permanent': [],
        'standard': [],
        'reaction': [],
        'movement': [],
        'other': []
    }
    
    warnings = []
    errors = []
    
    for power in parsed_powers:
        db_power = find_power_in_db(power['name'], db)
        
        if not db_power:
            errors.append(f"Power not found: \"{power['name']}\"")
            # Try to find close matches
            matches = get_close_matches(power['name'], db['powers'].keys(), n=3, cutoff=0.6)
            if matches:
                errors.append(f"  Did you mean: {', '.join(matches)}?")
            continue
        
        action = db_power.get('action', '').lower() if db_power.get('action') else ''
        
        if not action or 'permanent' in action:
            categories['permanent'].append(db_power)
        elif 'reaction' in action:
            categories['reaction'].append(db_power)
        elif 'movement' in action:
            categories['movement'].append(db_power)
        elif 'standard' in action:
            categories['standard'].append(db_power)
        else:
            categories['other'].append(db_power)
    
    return categories, warnings, errors

def generate_power_html(power):
    """Generate HTML for a single power."""
    html = f'        <div class="power">\n'
    html += f'            <div class="power-name">{power["name"]}</div>\n'
    
    power_set = power.get('power_set') or 'None'
    html += f'            <div class="power-detail"><strong>Power Set:</strong> {power_set}</div>\n'
    
    prereqs = power.get('prerequisites', {})
    if prereqs and prereqs.get('powers'):
        html += f'            <div class="power-detail"><strong>Prerequisites:</strong> {", ".join(prereqs["powers"])}</div>\n'
    
    if prereqs and prereqs.get('rank'):
        html += f'            <div class="power-detail"><strong>Rank:</strong> {prereqs["rank"]}</div>\n'
    
    duration = power.get('duration')
    if duration and duration.lower() != 'permanent':
        html += f'            <div class="power-detail"><strong>Duration:</strong> {duration}</div>\n'
    
    action = power.get('action')
    if action and 'permanent' not in action.lower():
        html += f'            <div class="power-detail"><strong>Action:</strong> {action}</div>\n'
    
    trigger = power.get('trigger')
    if trigger:
        html += f'            <div class="power-detail"><strong>Trigger:</strong> {trigger}</div>\n'
    
    cost = power.get('cost')
    if cost:
        html += f'            <div class="power-detail"><strong>Cost:</strong> {cost}</div>\n'
    
    range_val = power.get('range')
    if range_val:
        html += f'            <div class="power-detail"><strong>Range:</strong> {range_val}</div>\n'
    
    effect = power.get('effect')
    if effect:
        html += f'            <div class="power-detail"><strong>Effect:</strong> {effect}</div>\n'
    
    html += '        </div>\n'
    return html

def generate_html_sheet(character_name, categories):
    """Generate the complete HTML reference sheet."""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{character_name} - Power Reference Sheet</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 10pt;
            margin: 0.5in;
            line-height: 1.3;
        }}
        h1 {{
            text-align: center;
            font-size: 16pt;
            margin-bottom: 0.2in;
            border-bottom: 2px solid black;
            padding-bottom: 5px;
        }}
        h2 {{
            font-size: 12pt;
            margin-top: 0.15in;
            margin-bottom: 0.1in;
            border-bottom: 1px solid black;
            padding-bottom: 2px;
        }}
        .columns {{
            column-count: 2;
            column-gap: 0.3in;
        }}
        .power {{
            break-inside: avoid;
            margin-bottom: 0.15in;
            page-break-inside: avoid;
        }}
        .power-name {{
            font-weight: bold;
            font-size: 11pt;
            margin-bottom: 3px;
        }}
        .power-detail {{
            margin-left: 0.1in;
            margin-bottom: 2px;
        }}
        @media print {{
            body {{
                margin: 0.5in;
            }}
        }}
    </style>
</head>
<body>
    <h1>{character_name.upper()} - Power Reference Sheet</h1>
'''
    
    # Permanent powers
    if categories['permanent']:
        html += '    <h2>PERMANENT POWERS</h2>\n    <div class="columns">\n'
        for power in categories['permanent']:
            html += generate_power_html(power)
        html += '    </div>\n\n'
    
    # Standard action powers
    if categories['standard']:
        html += '    <h2>STANDARD ACTION POWERS</h2>\n    <div class="columns">\n'
        for power in categories['standard']:
            html += generate_power_html(power)
        html += '    </div>\n\n'
    
    # Movement action powers
    if categories['movement']:
        html += '    <h2>MOVEMENT ACTION POWERS</h2>\n    <div class="columns">\n'
        for power in categories['movement']:
            html += generate_power_html(power)
        html += '    </div>\n\n'
    
    # Reaction powers
    if categories['reaction']:
        html += '    <h2>REACTION POWERS</h2>\n    <div class="columns">\n'
        for power in categories['reaction']:
            html += generate_power_html(power)
        html += '    </div>\n\n'
    
    # Other powers
    if categories['other']:
        html += '    <h2>OTHER POWERS</h2>\n    <div class="columns">\n'
        for power in categories['other']:
            html += generate_power_html(power)
        html += '    </div>\n\n'
    
    html += '</body>\n</html>'
    return html

def main():
    """Main function to run the generator."""
    print("Marvel Multiverse RPG - Power Reference Sheet Generator")
    print("=" * 60)
    
    # Load database
    db = load_powers_db()
    
    # Get character name
    character_name = input("\nCharacter Name: ").strip()
    if not character_name:
        character_name = "Character"
    
    # Get power list
    print("\nPaste your power list (press Ctrl+D when done):")
    try:
        # sys.stdin.read() reads the entire block of input until EOF
        # This is the most reliable way to handle multi-line terminal paste
        power_text = sys.stdin.read()
    except EOFError:
        power_text = ""
    
    if not power_text.strip():
        print("Error: No power list provided.")
        exit(1)
    
    # Parse powers
    #parsed_powers = parse_power_list(power_text)
    parsed_powers = parse_power_list_robust(power_text,db)
    
    # Show parsed powers as comma-separated list
    power_names = [p['name'] for p in parsed_powers]
    total_parsed = len(power_names)
    
    print("\n" + "=" * 60)
    print("PARSED POWERS:")
    print("=" * 60)
    comma_separated = ", ".join(power_names)
    print(comma_separated)
    
    # Preliminary DB check to provide confidence/warning
    found_count = 0
    missing_names = []
    
    for power in parsed_powers:
        if find_power_in_db(power['name'], db):
            found_count += 1
        else:
            missing_names.append(power['name'])
            
    print("-" * 60)
    
    if total_parsed == found_count:
        print(f"✅ Success: {found_count} out of {total_parsed} powers were found in the database.")
    elif found_count > 0:
        print(f"⚠️ Warning: {found_count} out of {total_parsed} powers found. Missing: {', '.join(missing_names)}")
    else:
        print(f"❌ Error: Found 0 powers out of {total_parsed} in the database. Please check your list.")
        
    print("=" * 60)
    
    # Ask if user wants to edit
    print("\nDoes this list look correct, or do you want to edit it?")
    print("  [Enter] - Continue with these powers (missing powers will be skipped)")
    print("  [e] - Edit the comma-separated list")
    choice = input("Choice: ").strip().lower()
    
    if choice == 'e':
        print("\nPaste your edited comma-separated list:")
        edited_text = input().strip()
        
        if edited_text:
            # Parse the comma-separated list
            power_names = [p.strip() for p in edited_text.split(',') if p.strip()]
            parsed_powers = [{'name': name, 'power_set': None} for name in power_names]
            
            print(f"\nUsing {len(parsed_powers)} powers from edited list.")
    
    # Categorize powers and check for errors
    categories, warnings, errors = categorize_powers(parsed_powers, db)
    
    # Display errors and warnings
    if errors:
        print("\n" + "!" * 60)
        print("ERRORS FOUND:")
        print("!" * 60)
        for error in errors:
            print(f"  {error}")
        print("!" * 60)
        
        print("\nDo you want to:")
        print("  [c] - Continue anyway (skip missing powers)")
        print("  [e] - Edit the power list again")
        print("  [q] - Quit")
        choice = input("Choice: ").strip().lower()
        
        if choice == 'q':
            print("Exiting.")
            exit(0)
        elif choice == 'e':
            print("\nPaste your corrected comma-separated list:")
            edited_text = input().strip()
            
            if edited_text:
                power_names = [p.strip() for p in edited_text.split(',') if p.strip()]
                parsed_powers = [{'name': name, 'power_set': None} for name in power_names]
                categories, warnings, errors = categorize_powers(parsed_powers, db)
                
                # Check again for errors
                if errors:
                    print("\nStill found errors:")
                    for error in errors:
                        print(f"  {error}")
                    print("\nContinuing anyway (skipping missing powers)...")
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    # Generate HTML
    html = generate_html_sheet(character_name, categories)
    
    # Save to file
    filename = f"powers/{character_name.lower().replace(' ', '_')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    total_powers = sum(len(cat) for cat in categories.values())
    print(f"\n" + "=" * 60)
    print(f"SUCCESS! Reference sheet generated: {filename}")
    print("=" * 60)
    print(f"  Permanent: {len(categories['permanent'])} powers")
    print(f"  Standard: {len(categories['standard'])} powers")
    print(f"  Movement: {len(categories['movement'])} powers")
    print(f"  Reaction: {len(categories['reaction'])} powers")
    if categories['other']:
        print(f"  Other: {len(categories['other'])} powers")
    print(f"  TOTAL: {total_powers} powers")
    print("=" * 60)
    print(f"\nOpen {filename} in your browser to view and print.")

if __name__ == '__main__':
    main()
