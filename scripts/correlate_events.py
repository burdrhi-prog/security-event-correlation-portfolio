#!/usr/bin/env python3
"""Privacy-safe, evidence-linked correlation of synthetic security events.

Python 3.10+, standard library only. No operator/device attribution.
"""
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ('event_id', 'timestamp', 'account', 'event_type', 'client_id', 'source')
OPTIONAL = ('source_record_id', 'device_id', 'ip_address')


def parse_time(value):
    stamp = value.strip()
    if stamp.endswith('Z'):
        stamp = stamp[:-1] + '+00:00'
    parsed = datetime.fromisoformat(stamp)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f'timestamp must include timezone: {value!r}')
    return parsed.astimezone(timezone.utc)


def load_events(path):
    path = Path(path)
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            missing = set(REQUIRED) - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f'missing columns: {", ".join(sorted(missing))}')
            rows = list(reader)
    elif path.suffix.lower() == '.json':
        with path.open(encoding='utf-8-sig') as handle:
            rows = json.load(handle)
        if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
            raise ValueError('JSON input must be an array of event objects')
    else:
        raise ValueError('input must be .csv or .json')
    events, seen, duplicates = [], set(), []
    for line, row in enumerate(rows, start=2):
        if not any(str(v or '').strip() for v in row.values()):
            continue
        if any(not str(row.get(key) or '').strip() for key in REQUIRED):
            raise ValueError(f'record {line}: required field missing or empty')
        event_id = str(row['event_id']).strip()
        if event_id in seen:
            duplicates.append(event_id)
            continue
        seen.add(event_id)
        dt = parse_time(str(row['timestamp']))
        event = {key: str(row.get(key) or '').strip() for key in REQUIRED + OPTIONAL}
        event['timestamp_utc'] = dt.isoformat().replace('+00:00', 'Z')
        event['_dt'] = dt
        events.append(event)
    return events, duplicates


def correlate(events, window_minutes=15):
    if not 1 <= window_minutes <= 1440:
        raise ValueError('window_minutes must be between 1 and 1440')
    by_account = defaultdict(list)
    for event in events:
        by_account[event['account']].append(event)
    findings = []
    for account in sorted(by_account):
        rows = sorted(by_account[account], key=lambda e: (e['_dt'], e['event_id']))
        for index, first in enumerate(rows):
            for second in rows[index + 1:]:
                gap = int((second['_dt'] - first['_dt']).total_seconds())
                if gap > window_minutes * 60:
                    break
                if first['client_id'] == second['client_id']:
                    continue
                findings.append({
                    'rule': 'distinct_logical_clients_near_in_time',
                    'classification': 'review_required',
                    'account': account,
                    'event_ids': [first['event_id'], second['event_id']],
                    'sources': [first['source'], second['source']],
                    'source_record_ids': [first['source_record_id'], second['source_record_id']],
                    'timestamps_utc': [first['timestamp_utc'], second['timestamp_utc']],
                    'gap_seconds': gap,
                    'cross_provider': first['source'] != second['source'],
                    'interpretation': 'Temporal overlap of different logical client IDs; no inference of physical devices, actors, or compromise.',
                })
    return findings


def run(path, window_minutes=15):
    events, duplicates = load_events(path)
    findings = correlate(events, window_minutes)
    return {
        'dataset': Path(path).name,
        'event_count': len(events),
        'duplicate_event_id_count': len(duplicates),
        'duplicate_event_ids': sorted(set(duplicates)),
        'window_minutes': window_minutes,
        'finding_count': len(findings),
        'findings': findings,
        'limitations': [
            'Synthetic demonstration only; not evidence of a real incident.',
            'Event IDs are deduplicated within this input; same ID across providers may require a compound key.',
            'Different logical clients do not establish distinct physical devices, people, or unauthorized access.',
            'Time proximity is a review signal; source clocks and missing records may change interpretation.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='CSV or JSON event file')
    parser.add_argument('--window-minutes', type=int, default=15)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.input, args.window_minutes), indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
