#!/usr/bin/env python3
"""
Script to improve short_effect descriptions in full_powers.json
Processes powers in batches with checkpointing support
"""

import json
import re
from pathlib import Path

CHECKPOINT_FILE = 'short_effect_progress.json'
POWERS_FILE = 'full_powers.json'
CATEGORIES_FILE = 'power_categories.json'

def load_checkpoint():
    """Load progress from checkpoint file"""
    if Path(CHECKPOINT_FILE).exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {
        'completed_powers': [],
        'current_category': 'combat_attacks',
        'current_batch': 0
    }

def save_checkpoint(checkpoint):
    """Save progress to checkpoint file"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def load_data():
    """Load powers database and categories"""
    with open(POWERS_FILE, 'r') as f:
        powers_data = json.load(f)
    with open(CATEGORIES_FILE, 'r') as f:
        categories = json.load(f)
    return powers_data, categories

def save_powers(powers_data):
    """Save updated powers database"""
    with open(POWERS_FILE, 'w') as f:
        json.dump(powers_data, f, indent=2)

def generate_short_effect(power_name, power_data):
    """
    Generate improved short_effect from full effect.
    Uses pattern matching and compression techniques.
    """
    effect = power_data.get('effect', '')

    # Start building the short effect
    parts = []

    # Check for attack patterns
    attack_match = re.search(r'(makes?|perform) (?:a|an) (close|ranged|melee|Agility|Ego|Melee|Logic) (attack|check)', effect, re.IGNORECASE)

    if attack_match:
        attack_type = attack_match.group(2)
        # Extract success and fantastic success effects
        success_effects = []

        # Look for "success" outcomes
        success_pattern = r'(?:If (?:it|the attack) (?:is a )?)?success(?:es)?, ([^.]+)'
        fantastic_pattern = r'(?:On a )?[Ff]antastic(?:al)? success, ([^.]+)'

        success_match = re.search(success_pattern, effect, re.IGNORECASE)
        fantastic_match = re.search(fantastic_pattern, effect, re.IGNORECASE)

        # Build attack description
        attack_desc = f"{attack_type.capitalize()} attack"

        if success_match:
            success_text = success_match.group(1).strip()
            success_text = success_text.replace('the enemy takes', '').replace('the target takes', '')
            success_text = success_text.replace('regular damage', 'damage')
            success_effects.append(f"• Success: {success_text}")

        if fantastic_match:
            fantastic_text = fantastic_match.group(1).strip()
            fantastic_text = fantastic_text.replace('the enemy takes', '').replace('the target takes', '')
            fantastic_text = fantastic_text.replace('double damage', '2× damage')
            success_effects.append(f"• Fantastic: {fantastic_text}")

        if success_effects:
            return attack_desc + '\n' + '\n'.join(success_effects)
        else:
            # Fallback: just use attack type + truncated effect
            return f"{attack_desc}: {effect[:100]}..."

    # For non-attack powers, use compression techniques
    # Remove "The character" from start
    short = effect
    short = re.sub(r'^The character ', '', short)

    # If it's too long, try to extract key mechanics
    if len(short) > 150:
        # Try to get first sentence
        first_sentence = short.split('.')[0]
        if len(first_sentence) < 150:
            return first_sentence
        else:
            # Just truncate intelligently at a word boundary
            return short[:147] + '...'

    return short

def get_next_batch(categories, checkpoint, batch_size=25):
    """Get the next batch of powers to process"""
    category_order = ['combat_attacks', 'movement', 'defensive_passive', 'utility_control', 'complex_unique']

    current_cat = checkpoint['current_category']
    if current_cat not in category_order:
        return None, None

    cat_index = category_order.index(current_cat)

    # Get powers in this category that haven't been completed
    cat_powers = categories[current_cat]
    remaining = [p for p in cat_powers if p not in checkpoint['completed_powers']]

    if not remaining:
        # Move to next category
        if cat_index + 1 < len(category_order):
            next_cat = category_order[cat_index + 1]
            checkpoint['current_category'] = next_cat
            checkpoint['current_batch'] = 0
            return get_next_batch(categories, checkpoint, batch_size)
        else:
            return None, None  # All done!

    # Get next batch
    batch = remaining[:batch_size]
    return current_cat, batch

def show_batch_preview(powers_data, batch_powers):
    """Show preview of proposed changes for a batch"""
    print("\n" + "=" * 80)
    print("PROPOSED CHANGES")
    print("=" * 80)

    for power_name in batch_powers:
        power = powers_data['powers'][power_name]
        old_short = power.get('short_effect', '')
        new_short = generate_short_effect(power_name, power)

        print(f"\n{power_name}")
        print(f"  Action: {power.get('action', 'N/A')} | Cost: {power.get('cost', 'N/A')}")
        print(f"\n  FULL EFFECT:")
        print(f"    {power.get('effect', '')[:200]}...")
        print(f"\n  OLD SHORT:")
        print(f"    {old_short}")
        print(f"\n  NEW SHORT:")
        for line in new_short.split('\n'):
            print(f"    {line}")
        print("-" * 80)

def apply_batch(powers_data, batch_powers):
    """Apply improved short_effect to a batch of powers"""
    for power_name in batch_powers:
        power = powers_data['powers'][power_name]
        new_short = generate_short_effect(power_name, power)
        power['short_effect'] = new_short

    save_powers(powers_data)

def main():
    """Main execution"""
    checkpoint = load_checkpoint()
    powers_data, categories = load_data()

    print("Short Effect Improvement Tool")
    print("=" * 80)
    print(f"Current progress: {len(checkpoint['completed_powers'])}/364 powers completed")
    print(f"Current category: {checkpoint['current_category']}")
    print(f"Current batch: {checkpoint['current_batch']}")

    # Get next batch
    category, batch = get_next_batch(categories, checkpoint)

    if not batch:
        print("\n✓ All powers completed!")
        return

    print(f"\nProcessing {len(batch)} powers from category: {category}")
    print(f"Batch #{checkpoint['current_batch'] + 1}")

    # Show preview
    show_batch_preview(powers_data, batch)

    # Ask for confirmation
    print("\n" + "=" * 80)
    print("Options:")
    print("  [a] - Apply these changes")
    print("  [s] - Skip this batch")
    print("  [q] - Quit")
    choice = input("Choice: ").strip().lower()

    if choice == 'a':
        apply_batch(powers_data, batch)
        checkpoint['completed_powers'].extend(batch)
        checkpoint['current_batch'] += 1
        save_checkpoint(checkpoint)
        print(f"\n✓ Applied changes to {len(batch)} powers")
        print(f"Progress: {len(checkpoint['completed_powers'])}/364")
    elif choice == 's':
        checkpoint['completed_powers'].extend(batch)
        checkpoint['current_batch'] += 1
        save_checkpoint(checkpoint)
        print(f"\n⊘ Skipped {len(batch)} powers")
    else:
        print("\nExiting. Progress saved. Run again to continue.")

if __name__ == '__main__':
    main()
