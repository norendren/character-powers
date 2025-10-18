#!/usr/bin/env python3
"""
Apply manually-crafted short_effect improvements from batch_improvements.json
"""

import json

def main():
    # Load the improvements
    with open('batch_improvements.json', 'r') as f:
        improvements = json.load(f)

    # Load the powers database
    with open('full_powers.json', 'r') as f:
        powers_data = json.load(f)

    # Load or create checkpoint
    try:
        with open('short_effect_progress.json', 'r') as f:
            checkpoint = json.load(f)
    except FileNotFoundError:
        checkpoint = {
            'completed_powers': [],
            'current_category': 'combat_attacks',
            'current_batch': 0
        }

    print(f"Applying {len(improvements)} improvements...")
    print("=" * 80)

    # Apply each improvement
    for power_name, data in improvements.items():
        if power_name in powers_data['powers']:
            old_short = powers_data['powers'][power_name].get('short_effect', '')
            new_short = data['short_effect']

            powers_data['powers'][power_name]['short_effect'] = new_short

            print(f"\n✓ {power_name}")
            print(f"  OLD: {old_short[:60]}...")
            print(f"  NEW: {new_short[:60]}...")

            # Add to completed list if not already there
            if power_name not in checkpoint['completed_powers']:
                checkpoint['completed_powers'].append(power_name)
        else:
            print(f"\n✗ {power_name} - NOT FOUND IN DATABASE")

    # Save updated database
    with open('full_powers.json', 'w') as f:
        json.dump(powers_data, f, indent=2)

    # Update checkpoint
    checkpoint['current_batch'] = 1
    with open('short_effect_progress.json', 'w') as f:
        json.dump(checkpoint, f, indent=2)

    print("\n" + "=" * 80)
    print(f"✓ Applied {len(improvements)} improvements")
    print(f"✓ Progress: {len(checkpoint['completed_powers'])}/364 powers")
    print(f"✓ Checkpoint saved to short_effect_progress.json")
    print("\nTo resume later, run improve_short_effects.py - it will continue from where you left off")

if __name__ == '__main__':
    main()
