#!/usr/bin/env python3
import re
import csv
import argparse
import os
import sys

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'bio.csv')
CSV_PATH = os.path.abspath(CSV_PATH)

FIELDNAMES = [
    'first_name','last_name','position','jersey_number','weight','height','class_year','home_town','highschool'
]

def parse_html(content: str) -> dict:
    data = dict.fromkeys(FIELDNAMES, '')

    # name
    m = re.search(r'<span class="sidearm-roster-player-name [^"]*">.*?<span>([^<]+)</span>\s*<span>([^<]+)</span>', content, re.S)
    if not m:
        # try a more permissive pattern
        m = re.search(r'sidearm-roster-player-name [^>]*>.*?<span>([^<]+)</span>.*?<span>([^<]+)</span>', content, re.S)
    if m:
        data['first_name'] = m.group(1).strip()
        data['last_name'] = m.group(2).strip()

    # jersey
    m = re.search(r'<span class="sidearm-roster-player-jersey-number">\s*(\d+)', content)
    if m:
        data['jersey_number'] = m.group(1).strip()

    # dt/dd pairs
    pairs = re.findall(r'<dt>([^<:]+):</dt>\s*<dd>(.*?)</dd>', content, re.S)
    for k, v in pairs:
        key = k.strip().lower()
        val = re.sub(r'\s+', ' ', v.strip())
        if key.startswith('position'):
            data['position'] = val
        elif key.startswith('height'):
            data['height'] = val
        elif key.startswith('weight'):
            data['weight'] = val
        elif key.startswith('class'):
            data['class_year'] = val
        elif key.startswith('hometown'):
            data['home_town'] = val
        elif key.startswith('high school') or key.startswith('highschool'):
            data['highschool'] = val

    return data


def append_to_csv(row: dict, csv_path: str = CSV_PATH):
    # ensure CSV exists and has header
    exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        # ensure we only write the expected fields
        writer.writerow({k: row.get(k, '') for k in FIELDNAMES})


def main():
    parser = argparse.ArgumentParser(description='Parse a saved player HTML snippet and append to bio.csv')
    parser.add_argument('--input', '-i', required=True, help='Path to local HTML file to parse')
    parser.add_argument('--append', action='store_true', help='Append parsed row to bio.csv')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print('Input file not found:', args.input, file=sys.stderr)
        sys.exit(2)

    with open(args.input, 'r', encoding='utf-8') as fh:
        content = fh.read()

    row = parse_html(content)
    print('Parsed:', row)

    if args.append:
        append_to_csv(row)
        print('Appended to', CSV_PATH)


if __name__ == '__main__':
    main()
