#!/usr/bin/env python3
"""
Get the next batch of powers to work on and show their full details
"""

import json

def main():
    # Load checkpoint and categories
    with open('short_effect_progress.json') as f:
        checkpoint = json.load(f)
    with open('power_categories.json') as f:
        categories = json.load(f)
    with open('full_powers.json') as f:
        powers_data = json.load(f)

    # Get remaining powers in current category
    current_cat = checkpoint['current_category']
    completed = set(checkpoint['completed_powers'])
    remaining = [p for p in categories[current_cat] if p not in completed]

    if not remaining:
        print("✓ Current category complete! Moving to next category...")
        # Would need to implement category switching here
        return

    # Get next batch
    batch_size = 25
    next_batch = remaining[:batch_size]

    print('=' * 80)
    print(f'BATCH #{checkpoint["current_batch"] + 1} - {current_cat}')
    print('=' * 80)
    print(f'Progress: {len(checkpoint["completed_powers"])}/364 total')
    print(f'Remaining in category: {len(remaining)}')
    print(f'Next batch: {len(next_batch)} powers')
    print()

    # Show each power with full details for easy reference while writing short_effects
    for i, power_name in enumerate(next_batch, 1):
        power = powers_data['powers'][power_name]
        print(f'{i}. {power_name}')
        print(f'   Action: {power.get("action", "N/A")} | Cost: {power.get("cost", "N/A")} | Range: {power.get("range", "N/A")}')
        print(f'   Effect: {power.get("effect", "")[:150]}...')
        print(f'   Current short: {power.get("short_effect", "N/A")[:100]}...')
        print()

    # Show template for batch_improvements.json
    print('=' * 80)
    print('TEMPLATE for batch_improvements.json:')
    print('=' * 80)
    print('{')
    for power_name in next_batch[:3]:  # Show first 3 as examples
        print(f'  "{power_name}": {{')
        print(f'    "short_effect": "TODO: Write improved short_effect here"')
        print(f'  }},')
    print('  ...')
    print('}')

if __name__ == '__main__':
    main()
