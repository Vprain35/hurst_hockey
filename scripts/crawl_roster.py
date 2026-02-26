#!/usr/bin/env python3
"""Crawl the Mercyhurst men's hockey roster and append player bios to bio.csv

Usage:
  python3 scripts/crawl_roster.py --append
"""
import re
import csv
import os
import sys
import time
import argparse

try:
    import requests
except Exception:
    requests = None

BASE = 'https://hurstathletics.com'
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'bio.csv')
CSV_PATH = os.path.abspath(CSV_PATH)

FIELDNAMES = [
    'first_name','last_name','position','jersey_number','weight','height','class_year','home_town','highschool'
]


def fetch_url(url: str) -> str:
    if requests:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    # fallback to urllib
    from urllib.request import urlopen
    with urlopen(url, timeout=15) as fh:
        return fh.read().decode('utf-8', errors='ignore')


def parse_html(content: str) -> dict:
    data = dict.fromkeys(FIELDNAMES, '')

    m = re.search(r'<span class="sidearm-roster-player-name [^>]*>.*?<span>([^<]+)</span>\s*<span>([^<]+)</span>', content, re.S)
    if not m:
        m = re.search(r'sidearm-roster-player-name [^>]*>.*?<span>([^<]+)</span>.*?<span>([^<]+)</span>', content, re.S)
    if m:
        data['first_name'] = m.group(1).strip()
        data['last_name'] = m.group(2).strip()

    m = re.search(r'<span class="sidearm-roster-player-jersey-number">\s*(\d+)', content)
    if m:
        data['jersey_number'] = m.group(1).strip()

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


def read_existing(csv_path: str) -> set:
    seen = set()
    if not os.path.exists(csv_path):
        return seen
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            fn = r.get('first_name', '').strip()
            ln = r.get('last_name', '').strip()
            if fn or ln:
                seen.add((fn, ln))
    return seen


def append_row(row: dict, csv_path: str = CSV_PATH):
    exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, '') for k in FIELDNAMES})


def find_player_links(roster_html: str) -> list:
    # find hrefs that look like roster player pages
    hrefs = set()
    # relative links
    for m in re.findall(r'href="(/sports/mens-ice-hockey/roster/[^"]+)"', roster_html):
        hrefs.add(BASE + m)
    # absolute links
    for m in re.findall(r'href="(https?://[^"]*/sports/mens-ice-hockey/roster/[^"]+)"', roster_html):
        hrefs.add(m)
    return sorted(hrefs)


def crawl(roster_url: str, append: bool = True, limit: int | None = None):
    print('Fetching roster:', roster_url)
    html = fetch_url(roster_url)
    links = find_player_links(html)
    print(f'Found {len(links)} player links')

    seen = read_existing(CSV_PATH)
    print(f'Already have {len(seen)} players in {CSV_PATH}')

    added = 0
    for i, link in enumerate(links):
        if limit and i >= limit:
            break
        try:
            print('Fetching', link)
            phtml = fetch_url(link)
            row = parse_html(phtml)
            key = (row.get('first_name','').strip(), row.get('last_name','').strip())
            if not key[0] and not key[1]:
                print('  Skipped: no name parsed')
                continue
            if key in seen:
                print('  Skipped (exists):', key)
                continue
            if append:
                append_row(row)
                print('  Appended:', key)
            else:
                print('  Would append:', row)
            seen.add(key)
            added += 1
            time.sleep(0.3)
        except Exception as e:
            print('  Error fetching/parsing', link, e)

    print(f'Done. Added {added} new players.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--roster-url', default=BASE + '/sports/mens-ice-hockey/roster')
    parser.add_argument('--append', action='store_true', help='Append parsed players to bio.csv')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of players to fetch (0 = all)')
    args = parser.parse_args()

    lim = args.limit if args.limit and args.limit > 0 else None
    try:
        crawl(args.roster_url, append=args.append, limit=lim)
    except Exception as e:
        print('Fatal error:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
