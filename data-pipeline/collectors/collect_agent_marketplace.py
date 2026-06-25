#!/usr/bin/env python3
"""Collector: Agent Marketplace Monitor — query DB and write data JSON."""

import sqlite3, json, os, sys
from datetime import datetime, timezone

DB = "/opt/data/elko-skills/extension-marketplace.db"
OUTPUT_DIR = "/opt/data/repos/elko-reports-community/data-pipeline/output"

now = datetime.now(timezone.utc)
date_str = now.strftime("%Y-%m-%d")
time_str = now.strftime("%H%M")

print(f"\U0001f50d Agent Marketplace Collector \u2014 {date_str} {time_str} UTC")
print(f"  DB: {DB}")
print()

# Connect to DB
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get latest snapshot
cur.execute("SELECT * FROM daily_snapshots ORDER BY id DESC LIMIT 1")
snap = cur.fetchone()
if not snap:
    print("\u274c No snapshots found in DB!")
    sys.exit(1)

snapshot_id = snap["id"]
snap_date = snap["snapshot_date"]
total_entries = snap["total_entries"]
new_entries = snap["new_entries"]
top_tools = json.loads(snap["top_tools"]) if isinstance(snap["top_tools"], str) else snap["top_tools"]
trending = json.loads(snap["trending_categories"]) if isinstance(snap["trending_categories"], str) else snap["trending_categories"]
overlaps = json.loads(snap["overlaps_with_us"]) if isinstance(snap["overlaps_with_us"], str) else snap["overlaps_with_us"]
hot_topics = json.loads(snap["community_hot_topics"]) if isinstance(snap["community_hot_topics"], str) else snap["community_hot_topics"]
suggestions = json.loads(snap["suggestions"]) if isinstance(snap["suggestions"], str) else snap["suggestions"]

print(f"Snapshot ID {snapshot_id}: {total_entries} total, {new_entries} new, {len(overlaps)} overlaps")
print()

# Get entries count by platform
cur.execute("SELECT platform, COUNT(*) as cnt, COALESCE(SUM(downloads),0) as tot_dl FROM marketplace_entries GROUP BY platform ORDER BY cnt DESC")
sources_data = {}
for row in cur.fetchall():
    sources_data[row["platform"]] = {"count": row["cnt"], "total_downloads": row["tot_dl"]}

print(f"Sources: {json.dumps(sources_data, indent=2)}")

# Build output
output = {
    "type": "agent-marketplace",
    "generated_at": now.isoformat(),
    "date": date_str,
    "snapshot_id": snapshot_id,
    "total_entries": total_entries,
    "new_entries": new_entries,
    "top_tools": top_tools[:10],
    "overlaps": overlaps,
    "overlaps_count": len(overlaps),
    "community_hot_topics": hot_topics[:10],
    "sources": sources_data,
    "trending": trending,
    "suggestions": suggestions,
}

# Verify data
if total_entries == 0:
    print("\u274c Total entries is 0 — data looks wrong!")
    sys.exit(1)

if not top_tools:
    print("\u274c No top tools found!")
    sys.exit(1)

print(f"\nData valid: {total_entries} total entries, {len(top_tools)} top tools, {len(overlaps)} overlaps")

# Write JSON
os.makedirs(OUTPUT_DIR, exist_ok=True)
filename = f"agent-marketplace-{date_str}-{time_str}.json"
path = os.path.join(OUTPUT_DIR, filename)
with open(path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nWritten: {path}")
print(f"\U0001f517 {len(overlaps)} overlap entries")
print(path)