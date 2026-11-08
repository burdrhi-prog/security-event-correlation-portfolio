#!/usr/bin/env python3
"""Correlate synthetic authentication events without attributing an operator.

Usage: python scripts/correlate_events.py examples/synthetic_events.csv
Python 3.10+, standard library only.
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {"event_id", "timestamp", "account", "event_type", "client_id", "source"}
WINDOW_SECONDS = 15 * 60


def parse_time(value):
    """Return UTC-aware datetime; reject timestamps without a timezone."""
    stamp = value.strip()
    if stamp.endswith("Z"):
        stamp = stamp[:-1] + "+00:00"
    parsed = datetime.fromisoformat(stamp)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def load_events(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        events = []
        seen = set()
        for line, row in enumerate(reader, start=2):
            if not any(row.values()):
                continue
            if any(not (row.get(key) or "").strip() for key in REQUIRED):
                raise ValueError(f"line {line}: required field empty")
            event_id = row["event_id"].strip()
            if event_id in seen:
                raise ValueError(f"line {line}: duplicate event_id {event_id}")
            seen.add(event_id)
            events.append({
                "event_id": event_id,
                "timestamp_utc": parse_time(row["timestamp"]).isoformat().replace("+00:00", "Z"),
                "_dt": parse_time(row["timestamp"]),
                "account": row["account"].strip(),
                "event_type": row["event_type"].strip(),
                "client_id": row["client_id"].strip(),
                "source": row["source"].strip(),
            })
    return events


def correlate(events):
    """Flag different client IDs near each other on one account; no actor inference."""
    by_account = defaultdict(list)
    for event in events:
        by_account[event["account"]].append(event)
    findings = []
    for account, rows in by_account.items():
        rows.sort(key=lambda item: item["_dt"])
        for i, first in enumerate(rows):
            for second in rows[i + 1:]:
                gap = int((second["_dt"] - first["_dt"]).total_seconds())
                if gap > WINDOW_SECONDS:
                    break
                if first["client_id"] == second["client_id"]:
                    continue
                findings.append({
                    "rule": "distinct_client_ids_within_15_minutes",
                    "account": account,
                    "event_ids": [first["event_id"], second["event_id"]],
                    "gap_seconds": gap,
                    "classification": "review_required",
                    "interpretation": "Two logical client identifiers appeared close in time. This does not establish distinct physical devices, people, or unauthorized access.",
                })
    return findings


def run(path):
    events = load_events(path)
    findings = correlate(events)
    return {
        "dataset": Path(path).name,
        "event_count": len(events),
        "finding_count": len(findings),
        "findings": findings,
        "limitations": [
            "Synthetic demonstration; not evidence of a real incident.",
            "Client identifiers do not uniquely identify physical devices or operators.",
            "Temporal proximity is a review signal, not proof of compromise.",
            "Missing records and provider clock differences can affect conclusions.",
        ],
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/correlate_events.py examples/synthetic_events.csv")
    try:
        print(json.dumps(run(sys.argv[1]), indent=2))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc
