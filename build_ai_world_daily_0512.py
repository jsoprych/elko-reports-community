#!/usr/bin/env python3
"""
Build AI World Daily report for 2026-05-12.
Uses report-border template and report-panels patterns.
"""
import sys
sys.path.insert(0, "/opt/data/skills/report-border/scripts")
from report_border import render_shell, save_report, push_to_github

DATE = "2026-05-12"
TIMESTAMP = "0400"
SLUG = "ai-world-daily"
PAGES_URL = f"https://jsoprych.github.io/elko-reports-community/daily/{DATE}-{TIMESTAMP}-{SLUG}.html"
REPO_PATH = "/opt/data/repos/elko-reports-community"

# ──────────────────────────────────────────
# Stock Data (from Yahoo Finance, May 11 close)
# ──────────────────────────────────────────
stocks = {
    "NVDA": {"name": "NVIDIA", "price": 219.44, "prev": 196.50, "range52w": "124.47–222.30", "slug": "nvidia"},
    "MSFT": {"name": "Microsoft", "price": 412.66, "prev": 0, "range52w": "356.28–555.45", "slug": "microsoft"},
    "GOOGL": {"name": "Alphabet", "price": 388.64, "prev": 0, "range52w": "156.16–402.00", "slug": "google"},
    "AMZN": {"name": "Amazon", "price": 268.99, "prev": 0, "range52w": "196.00–278.56", "slug": "amazon"},
    "META": {"name": "Meta", "price": 598.86, "prev": 0, "range52w": "520.26–796.25", "slug": "meta"},
    "AVGO": {"name": "Broadcom", "price": 428.43, "prev": 0, "range52w": "221.60–437.68", "slug": "broadcom"},
    "TSM": {"name": "TSMC", "price": 404.54, "prev": 0, "range52w": "187.72–420.00", "slug": "tsmc"},
    "AMD": {"name": "AMD", "price": 458.79, "prev": 0, "range52w": "107.67–469.22", "slug": "amd"},
    "INTC": {"name": "Intel", "price": 129.44, "prev": 0, "range52w": "18.97–132.75", "slug": "intel"},
    "AAPL": {"name": "Apple", "price": 292.68, "prev": 0, "range52w": "193.46–294.76", "slug": "apple"},
    "BABA": {"name": "Alibaba", "price": 137.30, "prev": 0, "range52w": "103.71–192.67", "slug": "alibaba"},
    "BIDU": {"name": "Baidu", "price": 145.78, "prev": 0, "range52w": "81.17–165.30", "slug": "baidu"},
    "ASML": {"name": "ASML", "price": 1565.81, "prev": 0, "range52w": "683.48–1595.31", "slug": "asml"},
    "ARM": {"name": "Arm", "price": 212.65, "prev": 0, "range52w": "100.02–239.50", "slug": "arm"},
    "ORCL": {"name": "Oracle", "price": 193.84, "prev": 0, "range52w": "134.57–345.72", "slug": "oracle"},
    "IBM": {"name": "IBM", "price": 223.55, "prev": 0, "range52w": "220.72–324.90", "slug": "ibm"},
    "PLTR": {"name": "Palantir", "price": 136.89, "prev": 0, "range52w": "118.93–207.52", "slug": "palantir"},
    "CRM": {"name": "Salesforce", "price": 177.49, "prev": 0, "range52w": "163.52–296.05", "slug": "salesforce"},
    "NOW": {"name": "ServiceNow", "price": 91.49, "prev": 0, "range52w": "81.24–211.48", "slug": "servicenow"},
    "SNOW": {"name": "Snowflake", "price": 151.50, "prev": 0, "range52w": "118.30–280.67", "slug": "snowflake"},
    "CRWD": {"name": "CrowdStrike", "price": 542.26, "prev": 0, "range52w": "342.72–566.90", "slug": "crowdstrike"},
    "PANW": {"name": "Palo Alto", "price": 213.66, "prev": 0, "range52w": "139.57–223.61", "slug": "paltoalto"},
    "DDOG": {"name": "Datadog", "price": 202.32, "prev": 0, "range52w": "98.01–203.58", "slug": "datadog"},
    "QCOM": {"name": "Qualcomm", "price": 237.53, "prev": 0, "range52w": "121.99–247.90", "slug": "qualcomm"},
    "MU": {"name": "Micron", "price": 795.33, "prev": 0, "range52w": "90.93–818.67", "slug": "micron"},
    "MRVL": {"name": "Marvell", "price": 170.84, "prev": 0, "range52w": "58.61–175.80", "slug": "marvell"},
    "UBER": {"name": "Uber", "price": 76.15, "prev": 0, "range52w": "68.46–101.99", "slug": "uber"},
    "SHOP": {"name": "Shopify", "price": 102.54, "prev": 0, "range52w": "100.31–182.19", "slug": "shopify"},
    "ADBE": {"name": "Adobe", "price": 246.15, "prev": 0, "range52w": "224.13–422.95", "slug": "adobe"},
    "RDDT": {"name": "Reddit", "price": 159.51, "prev": 0, "range52w": "94.89–282.95", "slug": "reddit"},
}

# NVDA has prev_close data from history
stocks["NVDA"]["prev"] = 211.50  # May 8 close (last trading day before May 11)

# For other tickers without prev_close, use None
# Build the market table rows
market_rows = []
for ticker, info in sorted(stocks.items()):
    price = info["price"]
    prev = info["prev"]
    if prev and prev > 0:
        change = price - prev
        pct = (change / prev) * 100
        change_str = f"{change:+.2f} ({pct:+.1f}%)"
        chg_class = "td-green" if change >= 0 else "td-red"
    else:
        change_str = "—"
        chg_class = ""

    # Use ticker SWG icon or fallback
    slug = info["slug"]
    svg_url = f"https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/default.svg"
    
    market_rows.append(f"""
  <tr>
    <td class="td-svg"><img src="{svg_url}" class="ticker-svg" alt="{ticker}" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block'"><span class="ticker-svg-fallback" style="display:none">{ticker}</span></td>
    <td><strong>{ticker}</strong><br><span style="font-size:11px;color:var(--text-muted)">{info['name']}</span></td>
    <td class="td-price">${price:.2f}</td>
    <td class="{chg_class}">{change_str}</td>
    <td style="font-size:11px;color:var(--text-muted)">{info['range52w']}</td>
  </tr>""")

market_table_html = f"""<div class="chart-container">
  <div class="section-header">
    <span class="icon">📊</span>
    <h2>AI Market Snapshot</h2>
    <span class="accent-line"></span>
  </div>
  <p style="font-size:12px;color:var(--text-muted);margin-bottom:8px">Prices as of market close May 11, 2026. NVDA change vs May 8 close.</p>
  <div style="overflow-x:auto">
  <table class="data-table" style="width:100%;border-collapse:collapse;font-size:13px">
    <thead>
      <tr style="border-bottom:2px solid var(--border)">
        <th></th>
        <th style="text-align:left;padding:6px 8px;font-size:10px;text-transform:uppercase;color:var(--text-muted)">Ticker</th>
        <th style="text-align:right;padding:6px 8px;font-size:10px;text-transform:uppercase;color:var(--text-muted)">Price</th>
        <th style="text-align:right;padding:6px 8px;font-size:10px;text-transform:uppercase;color:var(--text-muted)">Change</th>
        <th style="text-align:right;padding:6px 8px;font-size:10px;text-transform:uppercase;color:var(--text-muted)">52W Range</th>
      </tr>
    </thead>
    <tbody>
      {''.join(market_rows)}
    </tbody>
  </table>
  </div>
</div>"""

# ──────────────────────────────────────────
# Metrics
# ──────────────────────────────────────────
metrics_html = """<div class="metric-row">
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#4a6cf7,#6c5ce7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">339</div>
    <div class="metric-label">Entities Tracked</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#00b894,#00cec9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">310</div>
    <div class="metric-label">Relationships</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#e17055,#fd79a8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">52</div>
    <div class="metric-label">Models Tracked</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#fdcb6e,#e17055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">34</div>
    <div class="metric-label">Categories</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#55efc4,#81ecec);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">123</div>
    <div class="metric-label">Timeline Events</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="background:linear-gradient(135deg,#a29bfe,#6c5ce7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">91</div>
    <div class="metric-label">Companies</div>
  </div>
</div>"""

# ──────────────────────────────────────────
# Entity Grid
# ──────────────────────────────────────────
WIKIPEDIA_MAP = {
    "OpenAI": "OpenAI", "Anthropic": "Anthropic", "Google DeepMind": "Google_DeepMind",
    "xAI": "xAI_(company)", "Meta AI": "Meta_AI", "Microsoft": "Microsoft",
    "Amazon": "Amazon_(company)", "NVIDIA": "Nvidia", "AMD": "Advanced_Micro_Devices",
    "Intel": "Intel", "TSMC": "TSMC", "ASML": "ASML_Holding",
    "Broadcom": "Broadcom_Inc.", "Apple": "Apple_Inc.", "DeepSeek": "DeepSeek",
    "Alibaba": "Alibaba_Group", "Baidu": "Baidu", "IBM": "IBM",
    "Oracle": "Oracle_Corporation", "Hugging Face": "Hugging_Face",
    "Palantir": "Palantir_Technologies", "Salesforce": "Salesforce"
}

SVG_SLUGS = {
    "OpenAI": "openai", "Anthropic": "anthropic", "Google DeepMind": "google",
    "xAI": "xai", "Meta AI": "meta", "Microsoft": "microsoft",
    "Amazon": "amazon", "NVIDIA": "nvidia", "AMD": "amd",
    "Intel": "intel", "TSMC": "tsmc", "ASML": "asml",
    "Broadcom": "broadcom", "Apple": "apple", "DeepSeek": "deepseek",
    "Alibaba": "alibaba", "Baidu": "baidu", "IBM": "ibm",
    "Oracle": "oracle", "Hugging Face": "hugging-face",
    "Palantir": "palantir", "Salesforce": "salesforce"
}

entity_cards = []
for name, wp in WIKIPEDIA_MAP.items():
    slug = SVG_SLUGS.get(name, name.lower().replace(" ", "-"))
    svg = f"https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/default.svg"
    entity_cards.append(f"""    <a href="https://en.wikipedia.org/wiki/{wp}" target="_blank" rel="noopener" style="text-decoration:none">
    <div class="entity-card" data-wp="{wp}">
      <img src="{svg}" width="28" height="28" alt="{name}" style="object-fit:contain;background:var(--bar-bg);border-radius:4px;padding:2px;" onerror="this.src=''">
      <span style="font-size:11px;font-weight:600;color:var(--text-primary)">{name}</span>
    </div>
  </a>""")

entity_grid_html = f"""<div class="section-header">
  <span class="icon">🏢</span>
  <h2>AI Ecosystem Map</h2>
  <span class="accent-line"></span>
</div>
<div class="entity-row" style="grid-template-columns:repeat(auto-fill,minmax(100px,1fr))">
  {'  '.join(entity_cards)}
</div>"""

# ──────────────────────────────────────────
# Trending Themes
# ──────────────────────────────────────────
trending_html = """<div class="section-header">
  <span class="icon">📌</span>
  <h2>Trending Themes This Week</h2>
  <span class="accent-line"></span>
</div>
<div style="display:flex;flex-wrap:wrap;gap:8px;margin:12px 0">
  <span class="trend-pill" style="background:#4a6cf7;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f3af AI-Powered Cyber Attacks</span>
  <span class="trend-pill" style="background:#e17055;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f6e1\ufe0f US-China AI Diplomacy</span>
  <span class="trend-pill" style="background:#00b894;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f3ed CAISI AI Model Vetting</span>
  <span class="trend-pill" style="background:#6c5ce7;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f4ba Chief AI Officer Wave</span>
  <span class="trend-pill" style="background:#fdcb6e;color:#2d3436;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f3ed IPO Boom (Cerebras, etc.)</span>
  <span class="trend-pill" style="background:#fd79a8;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f9e0 Inference Infrastructure</span>
  <span class="trend-pill" style="background:#00cec9;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f916 Frontier Model Race</span>
  <span class="trend-pill" style="background:#636e72;color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">\U0001f30d Chip Export Controls</span>
</div>"""

# ──────────────────────────────────────────
# News Stories
# ──────────────────────────────────────────
def entity_badge(slug):
    return f'''<span class="entity-badge"><img src="https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/default.svg" alt="{slug}" style="width:18px;height:18px;object-fit:contain;background:var(--bar-bg);border-radius:3px;padding:1px;vertical-align:middle"></span>'''

def news_item(idx, headline, url, body, badges, sources):
    badges_html = ''.join(entity_badge(s) for s in badges)
    sources_html = ' \u2022 '.join(f'<a href="{s[1]}" target="_blank">{s[0]}</a>' for s in sources)
    return f'''    <li class="news-item">
      <span class="news-bullet" style="background:var(--accent)"></span>
      <span class="news-text">
        <strong><a href="{url}" target="_blank" style="color:var(--text-primary);text-decoration:none">{idx}. {headline}</a></strong>
        {badges_html}<br>
        {body}<br>
        <span class="news-sublinks">
          <span class="links-label">LINKS:</span>
          {sources_html}
        </span>
      </span>
    </li>'''

stories = [
    news_item(1,
        "Google Says Criminal Hackers Used AI to Find Major Software Flaw for the First Time",
        "https://www.nytimes.com/2026/05/11/us/politics/google-hackers-attack-ai.html",
        "Google Threat Intelligence Group identified hackers using AI to discover and weaponize a zero-day exploit for the first time. The report details how cybercriminals leveraged commercial AI models to autonomously hunt for vulnerabilities, build malware, and scale operations. John Hultquist called it \"a taste of what\u2019s to come.\" Russia-linked groups targeted Ukrainian networks, while North Korea's APT45 used AI to refine cyber methods.",
        ["google", "microsoft"],
        [("NYT","https://www.nytimes.com/2026/05/11/us/politics/google-hackers-attack-ai.html"), ("Reuters","https://www.reuters.com/legal/litigation/hackers-pushing-innovation-ai-enabled-hacking-operations-google-says-2026-05-11/"), ("The Guardian","https://www.theguardian.com/technology/2026/may/11/ai-powered-hacking-industrial-scale-threat-three-months-google"), ("Politico","https://www.politico.com/news/2026/05/11/google-hackers-ai-security-00913247")]),

    news_item(2,
        "AI-Powered Hacking Has Exploded Into Industrial-Scale Threat, Google Says",
        "https://www.theguardian.com/technology/2026/may/11/ai-powered-hacking-industrial-scale-threat-three-months-google",
        "Google's threat intelligence report reveals that AI-enabled hacking has reached industrial scale in just three months. Criminal groups and state-linked actors are using commercial models to refine attacks. The findings add to an intensifying global discussion about how the newest AI models are extremely adept at coding and becoming powerful tools for exploiting vulnerabilities.",
        ["google"],
        [("The Guardian","https://www.theguardian.com/technology/2026/may/11/ai-powered-hacking-industrial-scale-threat-three-months-google")]),

    news_item(3,
        "In Trump Administration Battle Over AI, U.S. Spy Agencies Seek More Power",
        "https://www.washingtonpost.com/politics/2026/05/11/trump-ai-regulation-commerce-intelligence/",
        "As the White House grapples with cybersecurity threats from advanced AI models, national security officials want more sway in AI regulation. The battle pits the Commerce Department's CAISI framework against intelligence community demands for greater oversight. The WaPo report details how the administration is divided over how to balance AI innovation with national security.",
        ["google", "microsoft", "xai", "openai", "anthropic"],
        [("WaPo","https://www.washingtonpost.com/politics/2026/05/11/trump-ai-regulation-commerce-intelligence/")]),

    news_item(4,
        "Fears of an AI Breakthrough Force the U.S. and China to Talk",
        "https://www.latimes.com/politics/story/2026-05-11/fears-of-ai-breakthrough-force-u-s-china-to-talk",
        "A Trump administration once eager to gun for technological supremacy is now, for the first time, reckoning with the power AI could unleash if left unchecked. The LA Times reports that concerns over an uncontrolled AI breakthrough are driving unprecedented US-China diplomatic talks ahead of Trump's Beijing visit.",
        ["deepseek", "alibaba", "baidu"],
        [("LA Times","https://www.latimes.com/politics/story/2026-05-11/fears-of-ai-breakthrough-force-u-s-china-to-talk")]),

    news_item(5,
        "China's AI Ascent Leaves Trump a Stark Choice: Escalate or Relax Chip Controls",
        "https://www.scmp.com/economy/global-economy/article/3353180/chinas-ai-ascent-leaves-trump-stark-choice-escalate-or-relax-chip-controls",
        "Beijing and Washington are locked in an era-defining contest \u2014 and China's rapid technological progress raises questions about the limits of containment. With DeepSeek V4 Pro closing the gap to ~8 months behind US frontier models, the SCMP analyzes whether further chip export controls can slow China's AI ascent or if de-escalation is the smarter path.",
        ["nvidia", "amd", "tsmc", "asml", "deepseek"],
        [("SCMP","https://www.scmp.com/economy/global-economy/article/3353180/chinas-ai-ascent-leaves-trump-stark-choice-escalate-or-relax-chip-controls")]),

    news_item(6,
        "Here's How Artificial Intelligence Is Changing Boardrooms",
        "https://www.cnbc.com/2026/05/11/heres-how-artificial-intelligence-is-changing-boardrooms.html",
        "IBM reports that 76% of companies are now staffing Chief AI Officer roles. McKinsey sees centralized AI coordination as increasingly important, while 93.2% cite cultural challenges as the principal hurdle to AI adoption. The AI C-suite wave is reshaping corporate governance structures across industries.",
        ["ibm", "microsoft"],
        [("CNBC","https://www.cnbc.com/2026/05/11/heres-how-artificial-intelligence-is-changing-boardrooms.html")]),

    news_item(7,
        "Nvidia CEO Tells Graduates to 'Run, Don't Walk' Into AI Buildout As Demand Surges",
        "https://www.ibtimes.com/nvidia-ceo-tells-graduates-run-dont-walk-ai-buildout-demand-surges-3802638",
        "Jensen Huang told graduates that the AI sector's expansion will require large-scale labor across multiple industries, including construction and utilities. Nvidia shares surged to new highs above $219, with the 52-week range extending to $222.30 intraday. The AI infrastructure buildout continues to accelerate.",
        ["nvidia"],
        [("IBT","https://www.ibtimes.com/nvidia-ceo-tells-graduates-run-dont-walk-ai-buildout-demand-surges-3802638")]),

    news_item(8,
        "IMF Warns of AI Attacks on Global Financial Systems",
        "https://www.computerworld.com/article/4169682/imf-warns-of-ai-attacks-on-the-global-financial-system.html",
        "The International Monetary Fund warns that AI-powered cyber attacks could destabilize global financial systems. The IMF points to Anthropic's Claude Mythos Preview as an example of how quickly technology is advancing, and calls for coordinated international regulation of AI capabilities in the financial sector.",
        ["anthropic"],
        [("Computerworld","https://www.computerworld.com/article/4169682/imf-warns-of-ai-attacks-on-the-global-financial-system.html")]),

    news_item(9,
        "Kneron Warns AI Industry Is Approaching a Massive Inference Infrastructure Bottleneck",
        "https://www.manilatimes.net/2026/05/12/tmt-newswire/globenewswire/kneron-warns-the-ai-industry-is-approaching-a-massive-inference-infrastructure-bottleneck/2341273",
        "San Diego-based edge AI company Kneron warns the industry may be vastly underestimating the next major bottleneck \u2014 inference infrastructure. The bottleneck has nothing to do with training larger models, but rather the compute required for inference at scale. Edge AI and specialized inference chips are positioned as the solution.",
        ["nvidia", "amd", "intel"],
        [("Manila Times","https://www.manilatimes.net/2026/05/12/tmt-newswire/globenewswire/kneron-warns-the-ai-industry-is-approaching-a-massive-inference-infrastructure-bottleneck/2341273")]),

    news_item(10,
        "Stock Market Concentration Hits Historic Proportions as AI Boom Accelerates",
        "https://www.reuters.com/commentary/reuters-open-interest/stock-market-concentration-feature-not-bug-2026-05-11/",
        "Reuters reports that stock market concentration is reaching historic proportions driven by the AI boom. Tech megacaps like Nvidia, Alphabet, and Microsoft dominate US indices, while top-heavy indices are now a feature of global equity markets. NVDA closed at $219.44, up from $196.50 a week ago \u2014 an 11.7% weekly gain.",
        ["nvidia", "google", "microsoft", "meta"],
        [("Reuters","https://www.reuters.com/commentary/reuters-open-interest/stock-market-concentration-feature-not-bug-2026-05-11/")]),
]

news_html = f"""<div class="section-header">
  <span class="icon">📰</span>
  <h2>Top AI Stories</h2>
  <span class="accent-line"></span>
</div>
<ul class="news-list">
{''.join(stories)}
</ul>"""

# ──────────────────────────────────────────
# Sources
# ──────────────────────────────────────────
sources_html = """<a href="https://nytimes.com" target="_blank">NYT</a>
<a href="https://reuters.com" target="_blank">Reuters</a>
<a href="https://theguardian.com" target="_blank">The Guardian</a>
<a href="https://politico.com" target="_blank">Politico</a>
<a href="https://washingtonpost.com" target="_blank">WaPo</a>
<a href="https://latimes.com" target="_blank">LA Times</a>
<a href="https://scmp.com" target="_blank">SCMP</a>
<a href="https://cnbc.com" target="_blank">CNBC</a>
<a href="https://ibtimes.com" target="_blank">IBT</a>
<a href="https://computerworld.com" target="_blank">Computerworld</a>
<a href="https://bloomberg.com" target="_blank">Bloomberg</a>
<a href="https://newsweek.com" target="_blank">Newsweek</a>
<a href="https://github.com/jsoprych/elko-reports-community" target="_blank">GitHub</a>"""

# ──────────────────────────────────────────
# Hero Story
# ──────────────────────────────────────────
top_heading = '<a href="https://www.nytimes.com/2026/05/11/us/politics/google-hackers-attack-ai.html" target="_blank" style="color:var(--accent);text-decoration:none">\U0001f3af AI-Powered Zero-Day: Google Confirms Hackers Used AI to Find Software Flaw for the First Time</a>'

top_body = "Google Threat Intelligence Group confirmed that criminal hackers used artificial intelligence to discover and weaponize a zero-day software exploit \u2014 a world first. The finding marks a watershed moment in cybersecurity: AI-powered hacking has moved from theoretical risk to operational reality. Russia-linked and North Korean groups are already using AI to scale up attacks. Meanwhile, the IMF warns AI attacks could destabilize global financial systems, spy agencies push for more regulatory power, and US-China diplomatic talks intensify over fears of an uncontrolled AI breakthrough. Nvidia extended its rally to $219.44 (+11.7% weekly) as Jensen Huang tells graduates to 'run, don\u2019t walk' into the AI buildout."

# ──────────────────────────────────────────
# Extra CSS
# ──────────────────────────────────────────
extra_css = """
.data-table td { white-space: nowrap; }
.td-green { color: #00b894; font-weight: 600; }
.td-red { color: #e17055; font-weight: 600; }
.news-sublinks { margin-top: 4px; display: block; font-size: 11px; }
.news-sublinks .links-label { font-weight: 800; color: #1a7a3a; text-transform: uppercase; letter-spacing: 0.5px; margin-right: 2px; }
.news-sublinks a { color: var(--accent); text-decoration: none; }
.news-sublinks a:hover { text-decoration: underline; }
.entity-badge { display: inline-block; margin: 2px 3px 2px 0; }
.trend-pill { transition: transform 0.15s ease; }
.trend-pill:hover { transform: translateY(-2px); }
"""

# ──────────────────────────────────────────
# Assemble Content
# ──────────────────────────────────────────
content_html = entity_grid_html + "\n\n" + trending_html + "\n\n" + news_html + "\n\n" + market_table_html

# ──────────────────────────────────────────
# Render Shell
# ──────────────────────────────────────────
html = render_shell(
    series="AI World Daily",
    title=f"AI World Daily \u2014 {DATE}",
    date=DATE,
    author="Reid (Hermes Agent)",
    classification="Public",
    doc_type="Intelligence Brief",
    top_heading=top_heading,
    top_body=top_body,
    metrics_html=metrics_html,
    content_html=content_html,
    sources_html=sources_html,
    pages_url=PAGES_URL,
    extra_css=extra_css
)

# ──────────────────────────────────────────
# Save
# ──────────────────────────────────────────
filename, full_path = save_report(html, REPO_PATH, DATE, TIMESTAMP, SLUG)
print(f"Saved: {filename}")
print(f"Path: {full_path}")

# ──────────────────────────────────────────
# Push to GitHub
# ──────────────────────────────────────────
push_to_github(REPO_PATH, f"add: AI World Daily \u2014 {DATE}")
print(f"Pushed: {PAGES_URL}")
