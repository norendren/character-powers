# Short Effect Improvement Workflow

This document explains how to continue improving the `short_effect` descriptions across all 364 powers in `full_powers.json`.

## Current Progress

**Completed: 25/364 powers (6.9%)**

### Batches Completed:
1. ✓ Combat Attacks - Batch 1 (25 powers)

### Remaining Categories:
- Combat Attacks: ~175 powers remaining
- Movement: 29 powers
- Defensive/Passive: 36 powers
- Utility/Control: 30 powers
- Complex/Unique: 69 powers

## Files Involved

- `full_powers.json` - Main powers database (gets updated)
- `power_categories.json` - Powers grouped by category
- `short_effect_progress.json` - **Checkpoint file** tracking completed powers
- `batch_improvements.json` - Staging file for next batch improvements
- `apply_batch.py` - Script to apply staged improvements

## Workflow for Each Batch

### 1. Create Manual Improvements

Edit `batch_improvements.json` with the next 20-30 powers. Format:

```json
{
  "Power Name": {
    "short_effect": "Concise description\n• Success: effect\n• Fantastic: effect"
  }
}
```

**Style Guidelines:**
- Use bullet points (`•`) for attack success/fantastic effects
- Use semicolons to separate multiple mechanics
- Use newlines (`\n`) to break up complex powers
- Keep abbreviations: `×` for times, `vs.` for versus, `2×` for double
- Target 50-200 characters (flexible based on complexity)
- Include all mechanical details (costs, durations, ranges)
- Drop filler words ("The character", "If it succeeds")

### 2. Apply the Batch

```bash
python3 apply_batch.py
```

This will:
- Apply all improvements in `batch_improvements.json`
- Update `full_powers.json`
- Add completed powers to `short_effect_progress.json`
- Increment the batch counter

### 3. Verify Updates

Check that the changes look good in the generated HTML:

```bash
# Generate a test character sheet to see the new short_effects in action
python3 generator.py
```

## How to Resume After Usage Limits

The checkpoint system (`short_effect_progress.json`) tracks:
- Which powers have been completed
- Current category being worked on
- Current batch number

**To resume:**

1. Check current progress:
```bash
cat short_effect_progress.json
```

2. See which category/batch you're on:
```bash
python3 -c "
import json
with open('short_effect_progress.json') as f:
    cp = json.load(f)
print(f'Progress: {len(cp[\"completed_powers\"])}/364')
print(f'Category: {cp[\"current_category\"]}')
print(f'Batch: {cp[\"current_batch\"]}')
"
```

3. Get next batch of powers to work on:
```bash
python3 -c "
import json

# Load checkpoint and categories
with open('short_effect_progress.json') as f:
    checkpoint = json.load(f)
with open('power_categories.json') as f:
    categories = json.load(f)

# Get remaining powers in current category
current_cat = checkpoint['current_category']
completed = set(checkpoint['completed_powers'])
remaining = [p for p in categories[current_cat] if p not in completed]

# Show next 25
next_batch = remaining[:25]
print(f'Next {len(next_batch)} powers from {current_cat}:')
print(', '.join(next_batch))
"
```

4. Create improvements for those powers in `batch_improvements.json`

5. Apply with `python3 apply_batch.py`

## Tips for Creating Good Short Effects

### Attack Powers
```
Attack type check vs. defense
• Success: main effect
• Fantastic: enhanced effect
```

Example:
```
Melee check vs. two enemies within reach (fails if either defense beats it)
• Success: Both take full damage
• Fantastic: Both take full damage and knocked prone
```

### Passive/Permanent Powers
Keep it simple and mechanical:
```
+X to stat; effect description
```

Example:
```
+2 Agility damage multiplier; +2 to non-attack Agility checks
```

### Complex Powers
Use newlines and bullets to organize:
```
Main effect description
• Condition 1: effect
• Condition 2: effect
• Duration/Cost: details
```

Example:
```
Powers boosted or dampened based on criterion (Confidence/Faith/Media Popularity)
• Boosted: 2× range/duration, +1 damage multiplier, auto-Fantastic effects
• Dampened: ½ range/duration, -1 damage multiplier, no Fantastic success
• Lasts: 1 combat or 1 day
```

## Automation Note

The `improve_short_effects.py` script was created for automated generation but produces lower quality results. **Manual curation is recommended** for best quality. The `apply_batch.py` workflow with manual `batch_improvements.json` editing produces much better results.

## Estimated Time

- ~25 powers per batch
- ~15-20 batches total
- 10-15 minutes per batch (reading full effects, crafting short versions)
- **Total: ~3-5 hours of work** spread across multiple sessions
