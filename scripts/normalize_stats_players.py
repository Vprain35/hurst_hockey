#!/usr/bin/env python3
"""Normalize the Player column in stats.csv: Title-case names and remove duplicated text.

Usage:
  python3 scripts/normalize_stats_players.py stats.csv
This updates the file in-place and preserves other columns.
"""
import csv
import sys
import re


def normalize_player_field(s: str) -> str:
    # s may be like 'bartecko, dominik bartecko, dominik' or 'bartecko, dominik'
    s = s.strip()
    # remove surrounding quotes
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]

    # If the name repeats, keep only the first "last, first" occurrence
    parts = s.split()
    # Find the comma separating last and first
    if ',' in s:
        # take up to the first double occurrence
        # split on comma
        last, rest = s.split(',', 1)
        # rest may contain duplicated portion; keep first token sequence
        first = rest.strip().split()[0] if rest.strip() else ''
        last = last.strip()
        # Title-case each hyphenated/compound piece
        def tcase(name):
            return '-'.join([p.capitalize() for p in name.split('-')])
        last = ' '.join([tcase(p) for p in last.split()])
        first = ' '.join([tcase(p) for p in first.split()])
        out = f'{last}, {first}' if first else f'{last}'
        return out
    # fallback: title case whole
    s2 = ' '.join([w.capitalize() for w in re.split(r'\s+', s)])
    return s2


def main():
    if len(sys.argv) < 2:
        print('Usage: normalize_stats_players.py <stats.csv>')
        sys.exit(1)
    path = sys.argv[1]
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print('Empty file')
        return

    # normalize player column (assumed index 1)
    for i in range(1, len(rows)):
        if len(rows[i]) > 1:
            rows[i][1] = normalize_player_field(rows[i][1])

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print('Normalized Player column in', path)


if __name__ == '__main__':
    main()
