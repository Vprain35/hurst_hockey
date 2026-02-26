#!/usr/bin/env python3
"""Fetch the target stats table and populate stats.csv with its rows.

By default this targets the table identified by the phrase
"Individual, Overall, Skaters" on the 2025-26 stats page. Use
`--input` to parse a saved HTML file instead (recommended if the page
requires JavaScript to render).

Usage:
  python3 scripts/populate_stats.py --out ../stats.csv --raw
"""
import re
import os
import sys
import csv
import argparse

try:
    import requests
except Exception:
    requests = None

BASE_URL = 'https://hurstathletics.com'
DEFAULT_URL = BASE_URL + '/sports/mens-ice-hockey/stats/2025-26'
DEFAULT_OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stats.csv'))


def fetch(url: str) -> str:
    if requests:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    from urllib.request import urlopen
    with urlopen(url, timeout=20) as fh:
        return fh.read().decode('utf-8', errors='ignore')


def extract_table_for_phrase(html: str, phrase: str) -> str | None:
    tables = re.findall(r'(<table[\s\S]*?</table>)', html, re.I)
    for t in tables:
        if phrase.lower() in t.lower():
            return t
    # fallback: find phrase and return first table after it
    idx = html.lower().find(phrase.lower())
    if idx == -1:
        # fuzzy: split phrase words and find nearby window
        words = [w.strip() for w in re.split(r'[^A-Za-z0-9]+', phrase) if w.strip()]
        if words:
            low = html.lower()
            for i in range(len(low)):
                window = low[i:i+1000]
                if all(w.lower() in window for w in words):
                    suffix = low[i:]
                    m = re.search(r'(<table[\s\S]*?</table>)', suffix, re.I)
                    if m:
                        return m.group(1)
        return None
    suffix = html[idx:]
    m = re.search(r'(<table[\s\S]*?</table>)', suffix, re.I)
    if m:
        return m.group(1)
    return None


def get_header_row_from_table(table_html: str) -> str | None:
    thead_m = re.search(r'<thead[\s\S]*?>([\s\S]*?)</thead>', table_html, re.I)
    block = thead_m.group(1) if thead_m else table_html
    trs = re.findall(r'(<tr[^>]*>[\s\S]*?</tr>)', block, re.I)
    if not trs:
        return None
    # if first has scope colgroup try second
    if re.search(r'scope\s*=\s*"colgroup"', trs[0], re.I) and len(trs) > 1:
        return trs[1]
    return trs[0]


def extract_cells_from_tr(tr_html: str) -> list:
    cells = re.findall(r'<t[dh][^>]*>([\s\S]*?)</t[dh]>', tr_html, re.I)
    cleaned = []
    for c in cells:
        txt = re.sub(r'<[^>]+>', '', c)
        txt = txt.replace('\n', ' ').replace('\r', ' ')
        txt = re.sub(r'\s+', ' ', txt).strip()
        cleaned.append(txt)
    return cleaned


def extract_body_rows(table_html: str) -> list:
    tbody_m = re.search(r'<tbody[\s\S]*?>([\s\S]*?)</tbody>', table_html, re.I)
    body = tbody_m.group(1) if tbody_m else table_html
    trs = re.findall(r'(<tr[^>]*>[\s\S]*?</tr>)', body, re.I)
    rows = [extract_cells_from_tr(tr) for tr in trs]
    # filter out empty rows
    return [r for r in rows if any(cell.strip() for cell in r)]


def read_existing_headers(path: str) -> list | None:
    if not os.path.exists(path):
        return None
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            hdr = next(reader)
            return hdr
        except StopIteration:
            return None


def write_rows(out_path: str, headers: list, rows: list):
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            # pad or truncate to match headers
            row = r[:len(headers)] + [''] * max(0, len(headers) - len(r))
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='Saved stats HTML file to parse (optional)')
    parser.add_argument('--url', default=DEFAULT_URL, help='Stats page URL')
    parser.add_argument('--phrase', default='Individual, Overall, Skaters', help='Phrase identifying the target table')
    parser.add_argument('--out', '-o', default=DEFAULT_OUT, help='Output CSV path')
    parser.add_argument('--raw', action='store_true', help='Use existing raw headers in stats.csv or generate raw headers before populating')
    args = parser.parse_args()

    # Load page
    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as fh:
                html = fh.read()
        else:
            html = fetch(args.url)
    except Exception as e:
        print('Failed to load page/input:', e, file=sys.stderr)
        sys.exit(2)

    table = extract_table_for_phrase(html, args.phrase)
    if not table:
        print('Could not find target table for phrase:', args.phrase, file=sys.stderr)
        sys.exit(3)

    # Determine headers: prefer existing file header, else extract from table
    existing = read_existing_headers(args.out)
    if existing:
        headers = existing
    else:
        tr = get_header_row_from_table(table)
        if not tr:
            print('Could not find header row in table', file=sys.stderr)
            sys.exit(4)
        headers = extract_cells_from_tr(tr)
        # If raw mode, keep as-is; otherwise sanitize similarly to generator
        if args.raw:
            headers = [h.strip() for h in headers]
            # ensure Player present and '#' and GP and BLK
            if not headers or not headers[0].lstrip().startswith('#'):
                headers.insert(0, '#')
            if len(headers) < 2:
                headers.insert(1, 'Player')
            elif headers[1] == '' or headers[1].lower() == 'name':
                headers[1] = 'Player'
            if not any(h.strip().lower() == 'gp' for h in headers):
                try:
                    idx = headers.index('Player')
                except ValueError:
                    idx = 1
                headers.insert(idx + 1, 'GP')
            if not any(h.strip().upper() == 'BLK' for h in headers):
                headers.append('BLK')
            # uppercase letters except 'Player'
            for i, lab in enumerate(headers):
                if lab == 'Player':
                    continue
                headers[i] = ''.join(ch.upper() if ch.isalpha() else ch for ch in lab)
        else:
            # basic sanitize: collapse whitespace and replace tags removed
            headers = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h)).strip() for h in headers]

    # Extract rows
    rows = extract_body_rows(table)
    if not rows:
        print('No data rows found in table', file=sys.stderr)
        sys.exit(5)

    # Write out CSV with header then rows
    write_rows(args.out, headers, rows)
    print(f'Wrote {len(rows)} rows to {args.out} with {len(headers)} columns.')


if __name__ == '__main__':
    main()
