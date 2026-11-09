#!/usr/bin/env python3
"""Report evidence-quality gaps without making attribution claims."""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED=('event_id','timestamp','account','event_type','source','source_record_id')
def check(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError('missing CSV header')
        missing=sorted(set(REQUIRED)-set(reader.fieldnames))
        if missing:
            raise ValueError('missing required columns: '+', '.join(missing))
        rows=list(reader)
    issues=[]; seen={}; offsets={}
    for n,row in enumerate(rows,2):
        def issue(code,severity,detail):
            issues.append({'row':n,'code':code,'severity':severity,'detail':detail})
        for field in REQUIRED:
            if not (row.get(field) or '').strip():
                issue('missing_required_value','error',field)
        source=(row.get('source') or '').strip()
        event_id=(row.get('event_id') or '').strip()
        if source and event_id:
            key=(source,event_id)
            if key in seen:
                issue('duplicate_source_event_id','warning',f'first seen at row {seen[key]}')
            else:
                seen[key]=n
        stamp=(row.get('timestamp') or '').strip()
        if stamp:
            try:
                dt=datetime.fromisoformat(stamp.replace('Z','+00:00'))
                if dt.tzinfo is None or dt.utcoffset() is None:
                    issue('missing_timezone','error','timestamp has no UTC offset')
                elif source:
                    offsets.setdefault(source,set()).add(dt.utcoffset().total_seconds())
            except ValueError:
                issue('invalid_timestamp','error','not ISO-8601')
        status=(row.get('authorization_status') or '').strip().lower()
        if status in ('','unknown'):
            issue('authorization_unresolved','info','authorization not established')
    for source,values in sorted(offsets.items()):
        if len(values)>1:
            issues.append({'row':None,'code':'mixed_source_offsets','severity':'info','detail':f'{source}: {len(values)} UTC offsets; verify source conventions'})
    return {'dataset':Path(path).name,'input_rows':len(rows),'issue_count':len(issues),
        'counts_by_severity':dict(sorted(Counter(x['severity'] for x in issues).items())),
        'issues':issues,'note':'Quality issues are not evidence of unauthorized access or manipulation.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input');parser.add_argument('--output')
    args=parser.parse_args()
    try:
        result=json.dumps(check(args.input),indent=2)+'\n'
        if args.output:
            Path(args.output).write_text(result,encoding='utf-8')
        else:
            print(result,end='')
    except (OSError,ValueError) as exc:
        parser.exit(2,f'Error: {exc}\n')
