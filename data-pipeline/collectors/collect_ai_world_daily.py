#!/usr/bin/env python3
"""
AI World Daily — Collector (Stage 1)
Gathers data from the ai_world.db SQLite DB and returns structured JSON.
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

import sqlite3

DB_PATH = "/opt/data/ai_world.db"
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

def collect():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Entity map for display names → slugs and wp
    entity_map = {
        "OpenAI": {"slug": "openai", "wp": "OpenAI", "db_slug": "openai"},
        "Anthropic": {"slug": "anthropic", "wp": "Anthropic", "db_slug": "anthropic"},
        "Google DeepMind": {"slug": "google", "wp": "Google_DeepMind", "db_slug": "google_deepmind"},
        "xAI": {"slug": "xai", "wp": "xAI_(company)", "db_slug": "xai"},
        "Meta AI": {"slug": "meta", "wp": "Meta_AI", "db_slug": "meta_ai"},
        "Microsoft": {"slug": "microsoft", "wp": "Microsoft", "db_slug": "microsoft_corporation"},
        "Amazon": {"slug": "amazon_aws", "wp": "Amazon_(company)", "db_slug": "amazon_aws"},
        "NVIDIA": {"slug": "nvidia", "wp": "Nvidia", "db_slug": "nvidia"},
        "AMD": {"slug": "amd", "wp": "Advanced_Micro_Devices", "db_slug": "amd"},
        "Intel": {"slug": "intel", "wp": "Intel", "db_slug": "intel"},
        "TSMC": {"slug": "tsmc", "wp": "TSMC", "db_slug": "tsmc"},
        "ASML": {"slug": "asml", "wp": "ASML_Holding", "db_slug": "asml"},
        "Broadcom": {"slug": "broadcom", "wp": "Broadcom_Inc.", "db_slug": "broadcom"},
        "Apple": {"slug": "apple", "wp": "Apple_Inc.", "db_slug": "apple"},
        "DeepSeek": {"slug": "deepseek", "wp": "DeepSeek", "db_slug": "deepseek"},
        "Alibaba": {"slug": "alibaba", "wp": "Alibaba_Group", "db_slug": "alibaba_cloud_alibaba_group"},
        "Baidu": {"slug": "baidu", "wp": "Baidu", "db_slug": "baidu-ai"},
        "IBM": {"slug": "ibm", "wp": "IBM", "db_slug": "ibm"},
        "Oracle": {"slug": "oracle", "wp": "Oracle_Corporation", "db_slug": "oracle"},
        "Hugging Face": {"slug": "hugging-face", "wp": "Hugging_Face", "db_slug": "hugging_face"},
        "Palantir": {"slug": "palantir", "wp": "Palantir_Technologies", "db_slug": "palantir"},
        "Salesforce": {"slug": "salesforce", "wp": "Salesforce", "db_slug": "salesforce"},
    }
    
    # Get DB stats
    cur.execute("SELECT COUNT(*) FROM entities")
    total_entities = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM models")
    total_models = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM events")
    total_events = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM relationships")
    total_relationships = cur.fetchone()[0]
    
    # Get entity details from DB
    entities = []
    for name, info in entity_map.items():
        cur.execute("SELECT id, name, description, wikilink FROM entities WHERE slug = ?", (info["db_slug"],))
        r = cur.fetchone()
        if r:
            entities.append({
                "name": name,
                "slug": info["slug"],
                "wp": info["wp"],
                "description": (r[3] or "") if r[3] else (r[2] or "")[:80] if r[2] else "",
            })
        else:
            entities.append({
                "name": name,
                "slug": info["slug"],
                "wp": info["wp"],
                "description": "",
            })
    
    # Get recent events (last 14 days)
    cur.execute("""
        SELECT title, date, category, description FROM events 
        WHERE date >= date('now', '-14 days')
        ORDER BY date DESC LIMIT 15
    """)
    events_raw = cur.fetchall()
    
    # Get trending tags
    cur.execute("""
        SELECT tag, category, mention_count FROM trending_tags 
        ORDER BY mention_count DESC LIMIT 10
    """)
    trending = [{"tag": r[0], "category": r[1], "mentions": r[2]} for r in cur.fetchall()]
    
    conn.close()
    
    data = {
        "date": DATE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "db_stats": {
            "entities": total_entities,
            "models": total_models,
            "events": total_events,
            "relationships": total_relationships,
        },
        "entities": entities,
        "events": [{"title": r[0], "date": r[1], "category": r[2], "description": r[3]} for r in events_raw],
        "trending_tags": trending,
    }
    
    print(f"AI World Daily — {DATE}")
    print(f"  Entities: {total_entities}")
    print(f"  Models: {total_models}")
    print(f"  Events (last 14d): {len(events_raw)}")
    print(f"  Trends: {len(trending)}")
    
    if total_entities == 0:
        print("ERROR: No entities found!")
        sys.exit(1)
    
    # Write output
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    out_path = os.path.join(OUTPUT_DIR, f"ai-world-daily-{timestamp}.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"  Output: {out_path}")
    print(out_path)
    return out_path

if __name__ == "__main__":
    collect()
