# How to Resume Short Effect Improvements

## For the User

When you want to continue, just say to Claude Code:

```
Continue improving short_effects for the next batch
```

Claude Code will:
1. Check `short_effect_progress.json` to see where you left off
2. Load the next 20-25 powers from the current category
3. Read each power's full effect and craft improved short_effect descriptions
4. Show you the proposed changes
5. Ask for approval
6. Apply the changes and update the checkpoint

## Current Status

**Progress: 25/364 powers (6.9%)**

Last completed: Batch 1 (Combat Attacks)
- 25 powers completed
- See `short_effect_progress.json` for full list

## Files Used by Claude Code

- `short_effect_progress.json` - Checkpoint (which powers are done)
- `power_categories.json` - Powers grouped by category
- `full_powers.json` - Main database (gets updated)

## Style Guidelines for Claude Code

When crafting short_effects:
- Use bullet points (`•`) for attack outcomes (Success/Fantastic)
- Use newlines (`\n`) to break up complex mechanics
- Keep concise but complete (all mechanical details)
- Use symbols: `×` for times, `vs.` for versus, `2×` for double
- Target 50-200 chars (flexible)

### Examples

**Attack Power:**
```
Melee check vs. target within reach
• Success: Target takes damage
• Fantastic: 2× damage and stunned
```

**Passive Power:**
```
+2 Agility damage multiplier; +2 to non-attack Agility checks
```

**Complex Power:**
```
Powers boosted/dampened by criterion
• Boosted: 2× range/duration, +1 damage multiplier
• Dampened: ½ range/duration, -1 damage multiplier
```

## Next Batch

Next up: Batch 2 (Combat Attacks)
- 175 powers remaining in this category
- Run `python3 get_next_batch.py` to preview
