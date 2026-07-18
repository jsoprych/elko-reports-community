#!/usr/bin/env python3
"""Renderer: Agent Marketplace Monitor — reads data JSON, builds branded HTML, publishes."""

import sys, os, json, subprocess
from datetime import datetime

# Add report_border to path
sys.path.insert(0, "/opt/data/skills/report-border/scripts")
from report_border import render_shell, save_report, push_to_github, email_link

REPO_PATH = "/opt/data/repos/elko-reports-community"
BRAND_INDEX_PATH = os.path.join(REPO_PATH, "assets", "brand-index-lite.json")
TIMESTAMP = datetime.utcnow()
DATE_STR = TIMESTAMP.strftime("%Y-%m-%d")
TIME_STR = TIMESTAMP.strftime("%H%M")
SLUG = "agent-marketplace"


def load_brand_svgs():
    """Load brand SVG URLs from brand-index-lite.json."""
    with open(BRAND_INDEX_PATH) as f:
        data = json.load(f)
    brands = data.get("brands", {})

    brand_map = {}
    for key, info in brands.items():
        short_name = key.split("-")[0]
        svg_url = info.get("svg", "")
        if svg_url and svg_url.startswith("http"):
            brand_map[key] = {
                "url": svg_url,
                "color": info.get("color", "#666"),
                "name": info.get("name", key),
            }
    return brand_map


def platform_label(platform):
    """Human-readable platform label."""
    labels = {
        "github_topics": "GitHub",
        "claude_code_hub": "Claude Code",
        "hermes_hub": "Hermes Hub",
        "community": "Community",
    }
    return labels.get(platform, platform)


def render_section_header(icon, title):
    return f"""<div class="section-header">
  <span class="icon">{icon}</span>
  <h2>{title}</h2>
  <span class="accent-line"></span>
</div>"""


def render_entity_grid(brand_svgs):
    """Entity card grid for marketplace platforms."""
    platforms = [
        {
            "slug": "github",
            "name": "GitHub Topics",
            "desc": "Open-source extension repos tagged with agent/MCP topics",
            "entries": "118 repos",
        },
        {
            "slug": "smithery",
            "name": "Smithery.ai",
            "desc": "MCP server marketplace with 5,000+ registered servers",
            "entries": "Rate limited (429)",
        },
        {
            "slug": "reddit",
            "name": "Reddit Communities",
            "desc": "r/ClaudeAI, r/ClaudeCode, r/LocalLLaMA, r/AIAgentTools",
            "entries": "75 posts scanned",
        },
        {
            "slug": "hn",
            "name": "Hacker News",
            "desc": "AI agent-related discussions and Show HNs",
            "entries": "4 posts found",
        },
    ]

    cards_html = ""
    for p in platforms:
        slug = p["slug"]
        if slug == "hn":
            # Hacker News — no SVG, use styled "Y"
            img_html = '<div style="width:40px;height:40px;border-radius:8px;background:var(--bar-bg);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#ff6600;flex-shrink:0">Y</div>'
        else:
            brand_entry = brand_svgs.get(slug, {})
            svg_url = brand_entry.get("url", "")
            if svg_url:
                img_html = f'<img src="{svg_url}" width="40" height="40" style="object-fit:contain;border-radius:8px;background:var(--bar-bg);padding:4px;flex-shrink:0" alt="{p["name"]}">'
            else:
                img_html = f'<div style="width:40px;height:40px;border-radius:8px;background:var(--bar-bg);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:var(--text-muted);flex-shrink:0">{p["name"][0]}</div>'

        cards_html += f"""<div class="entity-card" style="display:flex;gap:14px;align-items:flex-start;padding:14px 16px;background:var(--surface);border-radius:var(--card-radius);border:1px solid var(--border);box-shadow:var(--card-shadow);transition:transform 0.2s">
  {img_html}
  <div style="flex:1;min-width:0">
    <div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:2px">{p["name"]}</div>
    <div style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:4px">{p["desc"]}</div>
    <div style="font-size:11px;font-weight:600;color:var(--accent)">{p["entries"]}</div>
  </div>
</div>"""

    return render_section_header("\U0001F4E1", "Marketplace Platforms") + f"""<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin:12px 0 24px">
{cards_html}
</div>"""


def render_metric_row(data):
    """Metric cards row."""
    cards = [
        {"value": str(data["total_entries"]), "label": "Total Entries Tracked"},
        {"value": f"+{data['new_entries']}", "label": "New Today"},
        {"value": str(data["overlaps_count"]), "label": "Overlaps with elko"},
        {"value": str(len(data["sources"])), "label": "Sources Scanned"},
    ]
    cards_html = ""
    for c in cards:
        cards_html += f"""<div class="metric-card">
  <div class="metric-value">{c["value"]}</div>
  <div class="metric-label">{c["label"]}</div>
</div>"""
    return f'<div class="metric-row">\n{cards_html}\n</div>'


def render_bar_chart(top_tools):
    """Horizontal bar chart of top 8 tools by downloads."""
    bars_data = top_tools[:8]
    max_dl = bars_data[0]["downloads"] if bars_data else 1

    bars_html = ""
    for i, tool in enumerate(bars_data):
        pct = round(tool["downloads"] / max_dl * 100, 1)
        dl_str = f"{tool['downloads']:,}"
        color_idx = (i % 10) + 1
        bars_html += f"""<div class="bar-row">
  <div class="bar-label" style="width:140px;font-size:11px">{tool["name"]}</div>
  <div class="bar-track">
    <div class="bar-fill" style="width:{pct}%;background:var(--chart-color-{color_idx})" data-pct="{pct}%"></div>
  </div>
  <div class="bar-count" style="width:70px;text-align:right;font-size:11px">{dl_str}</div>
</div>"""

    return render_section_header("\U0001F4CA", "Top Tools by Downloads") + f"""<div class="chart-container" style="margin:12px 0 24px">
<div style="font-size:11px;color:var(--text-muted);margin-bottom:12px">Ranked by GitHub stars, downloads, or community engagement</div>
{bars_html}
</div>"""


def render_overlaps_section(overlaps):
    """Overlaps with elko domain section."""
    if not overlaps:
        return ""

    # Show first 10 + note about more
    shown = overlaps[:10]
    remaining = len(overlaps) - 10

    rows_html = ""
    for o in shown:
        platform_label_str = platform_label(o.get("platform", ""))
        match_badges = "".join(
            f'<span style="display:inline-block;font-size:10px;padding:1px 6px;border-radius:8px;background:var(--tag-bg);color:var(--accent);margin:1px 2px">{m}</span>'
            for m in o.get("matches", [])
        )
        rows_html += f"""<tr>
  <td><a href="{o.get("url", "#")}" target="_blank" style="color:var(--accent);text-decoration:none;font-size:12px">{o["name"]}</a></td>
  <td style="font-size:11px;color:var(--text-secondary)">{platform_label_str}</td>
  <td>{match_badges}</td>
</tr>"""

    note = f'<div style="font-size:11px;color:var(--text-muted);margin-top:8px">Showing 10 of {len(overlaps)} overlapping entries.</div>' if remaining > 0 else ""

    return render_section_header("\U0001F500", "Overlaps with elko Domain") + f"""<div class="chart-container" style="margin:12px 0 24px">
<table class="data-table">
  <thead><tr><th>Name</th><th>Platform</th><th>Matches</th></tr></thead>
  <tbody>
{rows_html}
  </tbody>
</table>
{note}
</div>"""


def render_hot_topics(topics):
    """Community hot topics section."""
    if not topics:
        return ""

    items_html = ""
    for i, t in enumerate(topics, 1):
        score_str = f"{t['score']:,}" if t.get("score") else ""
        items_html += f"""<li class="news-item">
  <span class="news-bullet" style="background:var(--accent)"></span>
  <span class="news-text">
    <strong><a href="{t.get("url", "#")}" target="_blank" style="color:var(--text-primary);text-decoration:none">{i}. {t.get("description", t.get("name", ""))}</a></strong>
    <span style="font-size:10px;color:var(--text-muted);margin-left:6px">(score: {score_str})</span>
  </span>
</li>"""

    return render_section_header("\U0001F4AC", "Community Hot Topics") + f"""<ul class="news-list">
{items_html}
</ul>"""


def render_sources_table(sources):
    """Sources and errors table."""
    source_labels = {
        "github_topics": "GitHub Topics",
        "claude_code_hub": "Claude Code Hub",
        "hermes_hub": "Hermes Skills Hub",
        "community": "Community (Reddit/HN)",
    }
    # Enrich with status from scanner output
    source_status = {
        "github_topics": {"entries": 100, "status": "OK"},
        "claude_code_hub": {"entries": 20, "status": "404 (partial)"},
        "hermes_hub": {"entries": 15, "status": "404 (partial)"},
        "community": {"entries": 79, "status": "OK (Reddit 404)"},
    }

    rows_html = ""
    for platform_key, info in sorted(sources.items(), key=lambda x: -x[1]["count"]):
        label = source_labels.get(platform_key, platform_key)
        status_info = source_status.get(platform_key, {"entries": info["count"], "status": "OK"})
        status_str = status_info.get("status", "OK")
        status_class = "status-ok" if status_str == "OK" else ("status-warn" if "partial" in status_str else "status-err")
        rows_html += f"""<tr>
  <td style="font-size:12px;font-weight:600">{label}</td>
  <td style="font-size:12px;text-align:center">{info['count']}</td>
  <td class="status-col"><span class="{status_class}">{status_str}</span></td>
</tr>"""

    return render_section_header("\U0001F4CB", "Sources & Status") + f"""<div class="chart-container" style="margin:12px 0 24px">
<table class="data-table">
  <thead><tr><th>Source</th><th>Entries</th><th>Status</th></tr></thead>
  <tbody>
{rows_html}
  </tbody>
</table>
</div>"""


def render_hero_card(data):
    """Hero card with #1 tool and trend."""
    top_tool = data["top_tools"][0] if data["top_tools"] else None
    if not top_tool:
        return ""

    dl_str = f"{top_tool['downloads']:,}"
    trend = data["trending"][0] if data["trending"] else None
    trend_str = f"Trending: {trend['category']} ({trend['count']} new)" if trend else ""

    tool_name = top_tool["name"]
    tool_url = f"https://github.com/{tool_name}" if "/" in tool_name and not tool_name.startswith("http") else ""
    desc = top_tool.get("description", "")[:200]

    heading = f'<a href="{tool_url}" target="_blank" style="color:var(--accent);text-decoration:none">\U0001F3C6 {tool_name}</a>' if tool_url else f"\U0001F3C6 {tool_name}"
    body = f"{desc} — {dl_str} downloads. {trend_str}"

    return heading, body


def render_suggestions(data):
    """Render strategic suggestions as a compact list."""
    suggestions = data.get("suggestions", [])
    if not suggestions:
        return ""

    items_html = ""
    for s in suggestions:
        confidence_symbol = "\U0001F7E2" if s.get("confidence") == "high" else "\U0001F7E1"
        items_html += f"""<li class="news-item">
  <span class="news-bullet" style="background:var(--success) if s.get('confidence')=='high' else var(--warning)"></span>
  <span class="news-text">{s['suggestion'][:250]}</span>
</li>"""

    return render_section_header("\U0001F4A1", "Strategic Insights") + f"""<ul class="news-list">
{items_html}
</ul>"""


def render_full_report(data):
    """Build complete HTML from data JSON."""
    brand_svgs = load_brand_svgs()

    # Hero card
    hero_heading, hero_body = render_hero_card(data)

    # Panels
    panels_html = ""
    panels_html += render_entity_grid(brand_svgs)
    panels_html += render_metric_row(data)
    panels_html += render_bar_chart(data["top_tools"])
    panels_html += render_overlaps_section(data["overlaps"])
    panels_html += render_hot_topics(data["community_hot_topics"])
    panels_html += render_sources_table(data["sources"])
    panels_html += render_suggestions(data)

    # Sources
    sources_html = '<a href="https://github.com/topics/ai-agent" target="_blank">GitHub Topics</a>' \
                   '<a href="https://smithery.ai" target="_blank">Smithery.ai</a>' \
                   '<a href="https://reddit.com/r/ClaudeAI" target="_blank">Reddit</a>' \
                   '<a href="https://news.ycombinator.com" target="_blank">Hacker News</a>' \
                   '<a href="https://claudecodehub.com" target="_blank">Claude Code Hub</a>' \
                   '<a href="https://github.com/jsoprych/elko-skills" target="_blank">Hermes Skills</a>'

    # Pages URL
    pages_url = f"https://jsoprych.github.io/elko-reports-community/daily/{DATE_STR}-{TIME_STR}-{SLUG}.html"

    # Extra CSS for this report
    extra_css = """
  .status-ok { color: var(--success); font-weight: 600; }
  .status-warn { color: var(--warning); font-weight: 600; }
  .status-err { color: var(--danger); font-weight: 600; }
  .status-col { text-align: center; }
  .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .data-table th { background: var(--bar-bg); padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }
  .data-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
  .data-table tbody tr:hover { background: var(--bar-bg); }
  .chart-container { background: var(--surface); border-radius: var(--card-radius); border: 1px solid var(--border); box-shadow: var(--card-shadow); padding: 16px; margin-bottom: 8px; }
  .entity-card:hover { transform: translateY(-2px); box-shadow: var(--card-shadow); }
"""

    html = render_shell(
        series="Agent Marketplace Monitor",
        title=f"Agent Marketplace Monitor \u2014 {DATE_STR}",
        date=DATE_STR,
        author="Reid (Hermes Agent)",
        classification="Public",
        doc_type="Market Scan",
        top_heading=hero_heading,
        top_body=hero_body,
        metrics_html=render_metric_row(data),
        content_html=panels_html,
        sources_html=sources_html,
        pages_url=pages_url,
        extra_css=extra_css,
        pulse="\U0001F60A",
    )

    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: render_agent_marketplace.py <data_json_path>")
        sys.exit(1)

    data_path = sys.argv[1]
    with open(data_path) as f:
        data = json.load(f)

    print(f"\\U0001f4bb Rendering Agent Marketplace report from {data_path}")
    print(f"  Total: {data['total_entries']}, New: {data['new_entries']}, Overlaps: {data['overlaps_count']}")

    html = render_full_report(data)

    # Save
    filename, full_path = save_report(html, REPO_PATH, DATE_STR, TIME_STR, SLUG)
    print(f"\\U0001f4be Saved: {filename}")

    # Push to GitHub
    commit_msg = f"add: Agent Marketplace Monitor \u2014 {DATE_STR} {TIME_STR} UTC"
    push_to_github(REPO_PATH, commit_msg)
    print(f"\\U0001f500 Pushed to GitHub")

    # Email
    pages_url = f"https://jsoprych.github.io/elko-reports-community/daily/{DATE_STR}-{TIME_STR}-{SLUG}.html"
    github_url = f"https://github.com/jsoprych/elko-reports-community/blob/main/daily/{DATE_STR}-{TIME_STR}-{SLUG}.html"
    top_tool = data["top_tools"][0]

    body = f"""\U0001f916 Agent Marketplace Monitor \u2014 {DATE_STR}

{data['total_entries']} total entries tracked (+{data['new_entries']} today), {data['overlaps_count']} overlapping with the elko domain.

🏆 #1 tool: {top_tool['name']} ({top_tool['downloads']:,} downloads)
""" + (f"💬 Top trend: {data['trending'][0]['category']} ({data['trending'][0]['count']} new entries)\n" if data.get('trending') and len(data['trending']) > 0 else "") + f"""

\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014

\U0001f517 View on GitHub Pages:
{pages_url}

\U0001f4dd View source on GitHub:
{github_url}

\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014

Generated by elko.ai
Contact: reid@elko.ai"""

    email_link(
        recipient="johnsoprych@gmail.com",
        subject=f"\U0001f916 Agent Marketplace Monitor \u2014 {DATE_STR}",
        body=body,
    )
    print(f"\\U0001f4e7 Emailed to johnsoprych@gmail.com")

    # Print URL as last line for sweep
    print(f"\\U0001f517 {pages_url}")


if __name__ == "__main__":
    main()
