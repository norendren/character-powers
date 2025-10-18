# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Marvel Multiverse RPG Power Reference Sheet Generator. It's a Python utility that creates formatted HTML reference sheets for RPG characters by parsing their power lists and looking them up in a comprehensive powers database.

## Key Components

### generator.py (Main Script)
The entry point for the generator. Run with:
```bash
python3 generator.py
```

The script workflow:
1. Loads the powers database from `full_powers.json`
2. Prompts for character name
3. Accepts multi-line power list input (paste text, then Ctrl+D to finish)
4. Parses the input using `parse_power_list_robust()` which:
   - Normalizes whitespace and removes formatting characters
   - Searches for known power names (longest names first to avoid substring false positives)
   - Removes found names from search text to prevent duplicate matches
5. Categorizes powers by action type (permanent, standard, reaction, movement, other)
6. Generates a two-column HTML sheet in the `powers/` directory

### full_powers.json (Powers Database)
Contains 321+ powers from the Marvel Multiverse RPG Core Rulebook. Structure:
- `metadata`: Source info, version, total_powers count
- `powers`: Dictionary of power objects with keys:
  - `name`, `description`, `power_set`
  - `prerequisites`: {powers: [], rank: int, other: str}
  - `duration`, `action`, `trigger`, `cost`, `range`
  - `effect`, `short_effect`

### powers/ (Output Directory)
Contains generated HTML reference sheets for characters (e.g., `agatha.html`, `bullseye.html`, `nimrod.html`). Each HTML file uses a compact two-column layout optimized for printing.

## Parsing Strategy

The codebase has two parsing methods:
1. **parse_power_list()** (lines 79-137): Original method that attempts to parse structured input with bullet points and headers. Prone to whitespace/formatting issues.
2. **parse_power_list_robust()** (lines 24-77): Current method (used in main). More reliable - normalizes all text first, then searches for known power names sorted by length. Sacrifices power set tracking for robustness.

Power lookup uses fuzzy matching via `find_power_in_db()` with fallbacks:
- Exact match
- Case-insensitive match
- Spaces-removed match
- Fuzzy match (difflib, 0.8 cutoff)

## HTML Generation

Powers are categorized by action type and rendered in sections:
- PERMANENT POWERS
- STANDARD ACTION POWERS
- MOVEMENT ACTION POWERS
- REACTION POWERS
- OTHER POWERS

Each power displays: name, power set, prerequisites, duration, action, trigger, cost, range, effect.

Layout uses CSS columns (2-column, 0.3in gap) with break-inside: avoid for clean printing.

## Development

**Python Version**: Python 3.13.7 (any Python 3.x should work)

**Dependencies**: Standard library only (json, re, sys, difflib)

**Testing workflow**: Run the script and paste sample power lists to test parsing accuracy. Check generated HTML in browser.
