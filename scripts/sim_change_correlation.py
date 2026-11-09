#!/usr/bin/env python3
"""Correlate SIM events with nearby account-security activity. Synthetic data only."""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

SIM_TYPES = {'sim_change', 'sim_swap', 'sim_activation', 'sim_deactivation'}
SECURITY_TYPES = {'login', 'recovery', 'password_reset', 'mfa_change', 'device_registration', 'session_refresh', 'recovery_contact_change'}
REQUIRED = {'event_id', 'timestamp', 'account', 'event_type', 'source', 'source_record_id'}


def parse_timestamp(value):
    value = value.strip()
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timestamps must contain a UTC offset or Z')
    return parsed.astimezone(timezone.utc)


def load_events(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError('missing columns: ' + ', '.join(sorted(missing)))
        records = list(reader)
    events, duplicates, seen = [], [], set()
    for row_number, row in enumerate(records, 2):
        if not any((v or '').strip() for v in row.values() if isinstance(v, str)):
            continue
        if any(not (row.get(k) or '').strip() for k in REQUIRED):
            raise ValueError(f'row {row_number}: missing required value')
        key = (row['source'].strip(), row['event_id'].strip())
        if key in seen:
            duplicates.append({'source': key[0], 'event_id': key[1]})
            continue
        seen.add(key)
        dt = parse_timestamp(row['timestamp'])
        events.append({
            'event_id': row['event_id'].strip(),
            'timestamp_original': row['timestamp'].strip(),
            'timestamp_utc': dt.isoformat().replace('+00:00', 'Z'),
            '_dt': dt,
            'account': row['account'].strip(),
            'event_type': row['event_type'].strip().lower(),
            'source': row['source'].strip(),
            'source_record_id': row['source_record_id'].strip(),
            'client_id': (row.get('client_id') or '').strip(),
            'authorization_status': (row.get('authorization_status') or 'unknown').strip().lower(),
        })
    return events, duplicates


def public_event(event):
    return {k: event[k] for k in ('event_id', 'event_type', 'timestamp_original', 'timestamp_utc', 'source', 'source_record_id', 'client_id', 'authorization_status')}


def correlate(events, before_minutes=1440, after_minutes=1440):
    if not 0 <= before_minutes <= 10080 or not 0 <= after_minutes <= 10080:
        raise ValueError('window minutes must be between 0 and 10080')
    anchors = sorted((e for e in events if e['event_type'] in SIM_TYPES), key=lambda e: (e['_dt'], e['source'], e['event_id']))
    findings = []
    for anchor in anchors:
        related = []
        for event in events:
            if event['account'] != anchor['account'] or event['event_type'] not in SECURITY_TYPES:
                continue
            delta_seconds = int((event['_dt'] - anchor['_dt']).total_seconds())
            if -before_minutes * 60 <= delta_seconds <= after_minutes * 60:
                related.append((delta_seconds, event))
        related.sort(key=lambda item: (item[1]['_dt'], item[1]['source'], item[1]['event_id']))
        if not related:
            continue
        findings.append({
            'classification': 'review_required',
            'rule': 'account_security_activity_near_sim_event',
            'account': anchor['account'],
            'sim_event': public_event(anchor),
            'related_count': len(related),
            'related_events': [{**public_event(e), 'seconds_from_sim_event': delta} for delta, e in related],
            'cross_provider': any(e['source'] != anchor['source'] for _, e in related),
            'interpretation': 'Temporal correlation only. SIM change and account activity do not establish a causal link, unauthorized access, a physical device, or an operator.',
        })
    return findings


def run(path, before_minutes=1440, after_minutes=1440):
    events, duplicates = load_events(path)
    findings = correlate(events, before_minutes, after_minutes)
    return {
        'dataset': Path(path).name,
        'event_count': len(events),
        'duplicate_count': len(duplicates),
        'duplicate_records': duplicates,
        'window': {'before_minutes': before_minutes, 'after_minutes': after_minutes},
        'finding_count': len(findings),
        'findings': findings,
        'limitations': [
            'Synthetic demonstration; no real case evidence or personal identifiers.',
            'Events are grouped per SIM anchor; an account event may appear under multiple SIM anchors if windows overlap.',
            'Authorization status is recorded, not independently verified.',
            'Temporal correlation does not establish causation, device identity, operator identity, or compromise.',
            'Only events assigned to the same synthetic account are compared.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Synthetic CSV event dataset')
    parser.add_argument('--before-minutes', type=int, default=1440)
    parser.add_argument('--after-minutes', type=int, default=1440)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.input, args.before_minutes, args.after_minutes), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
