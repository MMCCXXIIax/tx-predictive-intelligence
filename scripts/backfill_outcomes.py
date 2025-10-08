#!/usr/bin/env python3
"""
Backfill realized trade outcomes into the TX backend using /api/outcomes/log.

Usage:
  python scripts/backfill_outcomes.py --csv data/outcomes.csv --base-url http://localhost:5000

CSV columns (header required):
  symbol,pattern,entry_price,exit_price,pnl,quantity,timeframe,opened_at,closed_at,metadata

- metadata is optional JSON string (e.g. {"notes":"TP hit"})
- timestamps should be ISO-8601 (e.g. 2025-01-01T09:00:00Z)
- base-url points to your deployed backend (Render URL or local)
"""
import csv
import json
import argparse
import sys
from typing import Any, Dict
import requests


def post_outcome(base_url: str, row: Dict[str, Any]) -> Dict[str, Any]:
    url = base_url.rstrip('/') + '/api/outcomes/log'
    payload = {
        'symbol': (row.get('symbol') or '').upper(),
        'pattern': row.get('pattern'),
        'entry_price': float(row.get('entry_price') or 0),
        'exit_price': float(row.get('exit_price') or 0),
        'pnl': float(row.get('pnl') or 0),
        'quantity': float(row.get('quantity') or 0),
        'timeframe': row.get('timeframe') or '1h',
        'opened_at': row.get('opened_at'),
        'closed_at': row.get('closed_at'),
        'metadata': json.loads(row['metadata']) if row.get('metadata') else {}
    }
    r = requests.post(url, json=payload, timeout=15)
    try:
        j = r.json()
    except Exception:
        j = {'success': False, 'status_code': r.status_code, 'text': r.text[:300]}
    return j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True, help='Path to CSV file with outcomes')
    ap.add_argument('--base-url', required=True, help='Base URL of TX backend (e.g. https://service.onrender.com)')
    args = ap.parse_args()

    ok = 0
    fail = 0
    with open(args.csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            res = post_outcome(args.base_url, row)
            if res.get('success'):
                ok += 1
                print(f"[{i}] OK: {row.get('symbol')} {row.get('pattern')} pnl={row.get('pnl')}")
            else:
                fail += 1
                print(f"[{i}] FAIL: {row.get('symbol')} {row.get('pattern')} -> {res}")
    print(f"Done. success={ok} fail={fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()
