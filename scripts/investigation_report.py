#!/usr/bin/env python3
"""Generate a Markdown cross-provider review from synthetic SIM/auth CSV events."""
import argparse
from collections import Counter
from pathlib import Path
try:
    from scripts.sim_change_correlation import load_events, correlate
except ModuleNotFoundError:
    from sim_change_correlation import load_events, correlate

def safe(value):
    return str(value).replace('\\','\\\\').replace('|','\\|').replace('`','\\`').replace('\r',' ').replace('\n',' ')

def build_report(path, before_minutes=1440, after_minutes=1440):
    events, duplicates = load_events(path)
    findings = correlate(events, before_minutes, after_minutes)
    events = sorted(events, key=lambda e:(e['_dt'],e['source'],e['event_id']))
    counts = Counter(e['source'] for e in events)
    lines = ['# Cross-provider security event review — synthetic demonstration','',
        '**Scope:** illustrative event correlation, not a real incident determination.',
        f'**Input:** `{safe(Path(path).name)}`',
        f'**Window:** {before_minutes} minutes before / {after_minutes} minutes after each SIM anchor.',
        f'**Data quality:** {len(events)} unique source-scoped events; {len(duplicates)} duplicate row(s) excluded.',
        f'**Review groups:** {len(findings)} SIM-anchor groups containing related account-security activity.','',
        '## Provider/source coverage','','| Source | Unique events |','|---|---:|']
    for source,count in sorted(counts.items()):
        lines.append(f'| {safe(source)} | {count} |')
    lines += ['','## Chronological event timeline','','| UTC timestamp | Source | Source record | Event ID | Account | Event type | Authorization label |',
        '|---|---|---|---|---|---|---|']
    for e in events:
        vals=[e['timestamp_utc'],e['source'],e['source_record_id'],e['event_id'],e['account'],e['event_type'],e['authorization_status']]
        lines.append('| '+' | '.join(safe(v) for v in vals)+' |')
    lines += ['','## Grouped correlation findings','']
    if not findings:
        lines += ['No SIM-anchor groups met the selected time-window and event-type criteria.','']
    for i, finding in enumerate(findings,1):
        anchor=finding['sim_event']
        lines += [f'### Review group {i}: {safe(anchor["source_record_id"])}','',
            f'- **SIM anchor:** {safe(anchor["event_type"])} at {safe(anchor["timestamp_utc"])} (source: {safe(anchor["source"])}; event: {safe(anchor["event_id"])}).',
            f'- **Recorded authorization:** {safe(anchor["authorization_status"])}. This is a source label, not independently verified authorization.',
            f'- **Related events:** {finding["related_count"]}; **cross-provider:** {"yes" if finding["cross_provider"] else "no"}.','',
            '| Relative timing | Event | Source record | Type | UTC |','|---|---|---|---|---|']
        for e in finding['related_events']:
            seconds=e['seconds_from_sim_event']
            relative='at anchor' if seconds==0 else f'{abs(seconds)} sec {"before" if seconds<0 else "after"}'
            lines.append(f'| {relative} | {safe(e["event_id"])} | {safe(e["source_record_id"])} | {safe(e["event_type"])} | {safe(e["timestamp_utc"])} |')
        lines += ['','**Observation:** source-labelled events fall within the configured window.',
            '**Interpretation:** temporal proximity warrants review, not causation or attribution.','']
    lines += ['## Evidence gaps and follow-up questions','',
        '- Are carrier timestamps and time zones independently documented?',
        '- Is authorization status backed by source evidence?',
        '- Are authentication or recovery records missing?',
        '- Are source event identifiers distinct or duplicated across systems?','',
        '## Constraints and limitations','',
        '- All examples are fictional; no private workbook records were used.',
        '- Carrier-recorded SIM events do not identify the authorizing person.',
        '- Logical client identifiers do not prove physical device or operator identity.',
        '- Correlation windows are heuristics, not causal evidence.',
        '- One event may appear in overlapping SIM-anchor groups.',
        '- Record authenticity and clock accuracy are not established.','']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--output')
    parser.add_argument('--before-minutes',type=int,default=1440)
    parser.add_argument('--after-minutes',type=int,default=1440)
    args=parser.parse_args()
    try:
        result=build_report(args.input,args.before_minutes,args.after_minutes)
        if args.output:
            Path(args.output).write_text(result,encoding='utf-8')
            print(f'Wrote {args.output}')
        else:
            print(result)
    except (OSError,ValueError) as exc:
        parser.exit(2,f'Error: {exc}\n')
if __name__=='__main__':
    main()
