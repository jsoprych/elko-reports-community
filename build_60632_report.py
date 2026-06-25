#!/usr/bin/env python3
"""60632 Archer Heights Daily Sweep — build branded Elko HTML report."""
import sys, os, json, sqlite3, datetime
sys.path.insert(0, "/opt/data/skills/report-border/scripts")
from report_border import render_shell, save_report, push_to_github, email_link

REPO_PATH = "/opt/data/repos/elko-reports-community"
DB_PATH = "/opt/data/60632_business_inventory.db"
NOW = datetime.datetime.utcnow()
DATE_STR = NOW.strftime("%Y-%m-%d")
TIME_STR = NOW.strftime("%H%M")
SLUG = "60632-daily-sweep"

# Emoji constants
EMOJI = {
    "ecosystem": "\U0001F3E2",
    "news": "\U0001F4F0",
    "chart": "\U0001F4CA",
    "search": "\U0001F50D",
    "construction": "\U0001F3D7\uFE0F",
    "factory": "\U0001F3ED",
}

# Query DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM businesses")
total_biz = c.fetchone()[0]

c.execute("""SELECT
  SUM(CASE WHEN biz_type IN ('industrial','manufacturing','warehouse','logistics','distribution','industrial_supply','industrial_property','industrial_developer','import_warehouse','cold_storage_warehouse','cold_storage_logistics','packaging_manufacturing','food_manufacturing') THEN 1 ELSE 0 END),
  SUM(CASE WHEN biz_type IN ('commercial','office','professional','service','employment_agency','estate_agent','insurance','bank','tax_advisor','accountant','lawyer') THEN 1 ELSE 0 END),
  SUM(CASE WHEN biz_type IN ('retail','food','restaurant','bar','cafe','fast_food','convenience','grocery','supermarket','bakery','ice_cream','coffee','confectionery','chocolate','alcohol','tobacco','cannabis','pharmacy','books','clothes','shoes','jewelry','electronics','furniture','department_store','variety_store','gift','cosmetics','perfumery','hardware','doityourself','paint','toys','bag','newsagent') THEN 1 ELSE 0 END),
  SUM(CASE WHEN biz_type NOT IN ('industrial','manufacturing','warehouse','logistics','distribution','industrial_supply','industrial_property','industrial_developer','import_warehouse','cold_storage_warehouse','cold_storage_logistics','packaging_manufacturing','food_manufacturing','commercial','office','professional','service','employment_agency','estate_agent','insurance','bank','tax_advisor','accountant','lawyer','retail','food','restaurant','bar','cafe','fast_food','convenience','grocery','supermarket','bakery','ice_cream','coffee','confectionery','chocolate','alcohol','tobacco','cannabis','pharmacy','books','clothes','shoes','jewelry','electronics','furniture','department_store','variety_store','gift','cosmetics','perfumery','hardware','doityourself','paint','toys','bag','newsagent') THEN 1 ELSE 0 END)
FROM businesses""")
r = c.fetchone()
industrial = r[0] or 0
commercial = r[1] or 0
retail_food = r[2] or 0
other = r[3] or 0

c.execute("""SELECT biz_type, COUNT(*) as cnt FROM businesses
  WHERE biz_type IS NOT NULL AND biz_type != '' AND biz_type != 'other' AND biz_type != 'yes'
  GROUP BY biz_type ORDER BY cnt DESC LIMIT 10""")
top_types = [(row[0], row[1]) for row in c.fetchall()]
max_cnt = top_types[0][1] if top_types else 1

c.execute("SELECT topic, note, source_url, created_at FROM research_notes ORDER BY created_at DESC LIMIT 12")
recent_notes = [(row[0], row[1], row[2], row[3]) for row in c.fetchall()]
conn.close()

# Metric row
METRICS_HTML = (
    '<div class="metric-row">'
    '<div class="metric-card"><div class="metric-value">' + str(total_biz) + '</div><div class="metric-label">Total Businesses</div></div>'
    '<div class="metric-card"><div class="metric-value">' + str(industrial) + '</div><div class="metric-label">Industrial / Logistics</div></div>'
    '<div class="metric-card"><div class="metric-value">' + str(commercial) + '</div><div class="metric-label">Commercial / Office</div></div>'
    '<div class="metric-card"><div class="metric-value">' + str(retail_food) + '</div><div class="metric-label">Retail / Food</div></div>'
    '<div class="metric-card"><div class="metric-value">' + str(other) + '</div><div class="metric-label">Other / Services</div></div>'
    '</div>'
)

# Bar chart
CHART_COLORS = ["#4a6cf7", "#6c63ff", "#818cf8", "#a78bfa", "#c4b5fd", "#f472b6", "#fb7185", "#f87171", "#fbbf24", "#34d399"]
bars_html = ""
for i, (btype, cnt) in enumerate(top_types):
    pct = round(cnt / max_cnt * 100)
    color = CHART_COLORS[i % len(CHART_COLORS)]
    label = btype.replace("_", " ").title()
    bars_html += (
        '<div class="bar-row">\n'
        '  <div class="bar-label">' + label + '</div>\n'
        '  <div class="bar-track">\n'
        '    <div class="bar-fill" style="width:' + str(pct) + '%;background:' + color + '" data-pct="' + str(pct) + '%"></div>\n'
        '  </div>\n'
        '  <div class="bar-count">' + str(cnt) + '</div>\n'
        '</div>\n'
    )

BAR_CHART_HTML = (
    '<div class="chart-container">\n'
    '<div class="section-header"><span class="icon">' + EMOJI["chart"] + '</span><h2>Top Business Types</h2><span class="accent-line"></span></div>\n'
    + bars_html +
    '</div>'
)

# News items
news_items = [
    {
        "headline": "Brookfield Breaks Ground on $100M Western Works Industrial Campus in Back of the Yards",
        "link": "https://chicago.suntimes.com/real-estate/2026/04/17/brookfield-breaks-ground-4-building-industrial-campus-back-of-the-yards",
        "body": "Brookfield Properties broke ground on Western Works \u2014 a 4-building, 560,000+ SF industrial campus at 47th & Western in Back of the Yards. Major industrial investment on Chicago's Southwest Side, directly adjacent to the 60632 industrial corridor.",
        "sources": [("Chicago Sun-Times", "https://chicago.suntimes.com/real-estate/2026/04/17/brookfield-breaks-ground-4-building-industrial-campus-back-of-the-yards")]
    },
    {
        "headline": "Archer Avenue Complete Streets: City Re-Adding 17 Parking Spots After Community Protests",
        "link": "https://blockclubchicago.org/2026/04/30/city-removes-brand-new-concrete-bike-lanes-pedestrian-islands-in-brighton-park-amid-protests/",
        "body": "CDOT reversed course on some Archer Ave (Brighton Park) bike lane configurations, restoring 17 parking spots across three sections. Ald. Ramirez signed off on reasonable edits after months of dueling rallies. Tribune editorial board weighed in, sparking rebuttals from safe streets advocates.",
        "sources": [
            ("Block Club Chicago", "https://blockclubchicago.org/2026/04/30/city-removes-brand-new-concrete-bike-lanes-pedestrian-islands-in-brighton-park-amid-protests/"),
            ("Streetsblog Chicago", "https://chi.streetsblog.org/2026/04/24/archer-edits-ald-julia-ramirez-signs-off-on-reasonable-edits-to-traffic-safety-plan-says-theyre-not-a-win-for-archer-guardians-nimbys-like-claudia-zuno")
        ]
    },
    {
        "headline": "Chicago Industrial Market: Vacancy at 5.3%, Rents Climbing to $6.80/SF",
        "link": "https://www.nmrk.com/insights/market-report/chicago-market-reports",
        "body": "Newmark Q1 2026 report shows Chicago industrial vacancy flat at 5.3% \u2014 250 bps below 20-year average. Class A product accounts for 59.4% of leasing. Rents rose to $6.80/SF. Nearly 15M SF under construction across metro Chicago.",
        "sources": [
            ("Newmark", "https://www.nmrk.com/insights/market-report/chicago-market-reports"),
            ("Crain's Chicago Business", "https://www.chicagobusiness.com/real-estate/commercial/ccb-chicago-first-quarter-industrial-vacancy-20260427/")
        ]
    },
    {
        "headline": "Mixed-Use Development Approved at 3198 S. Archer Ave (24 Units + Retail)",
        "link": "https://chicago.urbanize.city/post/zba-approves-variation-development-3198-s-archer",
        "body": "ZBA approved a variation for SkyRiver Archer Development's mixed-use project at 3198 S. Archer Ave. The building will have 24 residential units with ground-floor retail \u2014 joining a nearly identical neighboring project approved in March.",
        "sources": [("Urbanize Chicago", "https://chicago.urbanize.city/post/zba-approves-variation-development-3198-s-archer")]
    },
    {
        "headline": "Galvanize Real Estate Acquires 462,300 SF Industrial Portfolio Near Chicago",
        "link": "https://www.connectcre.com/stories/galvanize-real-estate-acquires-chicagoland-industrial-portfolio/",
        "body": "Galvanize Real Estate (GRE) acquired a three-property, 462,300 SF industrial portfolio in Green Oaks, IL. Portfolio now spans 2.8M+ SF. CEO: We view Chicago as one of the most important industrial markets in the country.",
        "sources": [("Connect CRE", "https://www.connectcre.com/stories/galvanize-real-estate-acquires-chicagoland-industrial-portfolio/")]
    },
    {
        "headline": "Chicago Restaurant Industry Lost 2,100 Jobs Amid Wage Hike Pressure",
        "link": "https://www.thecentersquare.com/illinois/article_f81e1a86-3db7-4a0c-a7e7-0eb590705085.html",
        "body": "Chicago lost 2,100 restaurant jobs as the industry fights mandated wage hikes. Sub-minimum wage phase-out creating headwinds for food businesses \u2014 potentially affecting restaurants and fast-food establishments in 60632.",
        "sources": [("The Center Square", "https://www.thecentersquare.com/illinois/article_f81e1a86-3db7-4a0c-a7e7-0eb590705085.html")]
    },
    {
        "headline": "Illinois House Approves 'Megaprojects' Bill \u2014 Could Unlock SW Side Development",
        "link": "https://news.wttw.com/2026/04/23/illinois-house-approves-megaprojects-bill-bears-want-changes",
        "body": "Illinois House approved legislation allowing projects over $500M to negotiate property tax freezes. Could enable Bears' Arlington Heights stadium and potentially unlock other large-scale developments across Cook County, including Southwest Side.",
        "sources": [
            ("WTTW", "https://news.wttw.com/2026/04/23/illinois-house-approves-megaprojects-bill-bears-want-changes"),
            ("FOX 32", "https://www.fox32chicago.com/news/illinois-mega-projects-bears-bill")
        ]
    },
    {
        "headline": "Angelica Garcilazo Agency Inc. \u2014 New Business License at 5030 S Archer Ave",
        "link": "https://data.cityofchicago.org/Business-Transactions/Business-Licenses/uc4x-hmav",
        "body": "Insurance agency issued new business license at 5030 S Archer Ave, Floor 1, Chicago 60632 \u2014 a new small business entering the Archer Heights commercial corridor.",
        "sources": [("City of Chicago Data", "https://data.cityofchicago.org/Business-Transactions/Business-Licenses/uc4x-hmav")]
    },
]

news_html_items = ""
for i, item in enumerate(news_items, 1):
    sources_links = " \u2022 ".join(
        ['<a href="' + s[1] + '" target="_blank">' + s[0] + '</a>' for s in item["sources"]]
    )
    news_html_items += (
        '<li class="news-item">\n'
        '  <span class="news-bullet" style="background:var(--accent)"></span>\n'
        '  <span class="news-text">\n'
        '    <strong><a href="' + item["link"] + '" target="_blank" style="color:var(--text-primary);text-decoration:none">'
        + str(i) + '. ' + item["headline"] + '</a></strong><br>\n'
        + item["body"] + '<br>\n'
        '    <span class="news-sublinks"><span class="links-label">LINKS:</span> ' + sources_links + '</span>\n'
        '  </span>\n'
        '</li>\n'
    )

NEWS_HTML = (
    '<div class="section-header"><span class="icon">' + EMOJI["news"] + '</span><h2>Key Developments \u2014 May 2026</h2><span class="accent-line"></span></div>\n'
    '<ul class="news-list">\n'
    + news_html_items +
    '</ul>'
)

# Research notes
research_rows = ""
for note in recent_notes[:6]:
    topic = note[0][:60]
    t = note[1][:150]
    src = note[2] if note[2] else ""
    link = ' \u2014 <a href="' + src + '" target="_blank" style="color:var(--accent)">Source</a>' if src else ""
    research_rows += (
        '<li class="news-item">\n'
        '  <span class="news-bullet" style="background:var(--warning)"></span>\n'
        '  <span class="news-text"><strong>' + topic + '</strong><br>' + t + link + '</span>\n'
        '</li>\n'
    )

RESEARCH_HTML = (
    '<div class="section-header"><span class="icon">' + EMOJI["search"] + '</span><h2>Recent Research Findings</h2><span class="accent-line"></span></div>\n'
    '<ul class="news-list">\n'
    + research_rows +
    '</ul>'
)

# AI Ecosystem Map
ecosystem_entities = [
    ("OpenAI", "openai", "OpenAI"),
    ("Anthropic", "anthropic", "Anthropic"),
    ("Google DeepMind", "google", "Google_DeepMind"),
    ("xAI", "xai", "xAI_(company)"),
    ("Meta AI", "meta", "Meta_AI"),
    ("Microsoft", "microsoft", "Microsoft"),
    ("Amazon", "amazon", "Amazon_(company)"),
    ("NVIDIA", "nvidia", "Nvidia"),
    ("AMD", "amd", "Advanced_Micro_Devices"),
    ("Intel", "intel", "Intel"),
    ("TSMC", "tsmc", "TSMC"),
    ("ASML", "asml", "ASML_Holding"),
    ("Broadcom", "broadcom", "Broadcom_Inc."),
    ("Apple", "apple", "Apple_Inc."),
    ("DeepSeek", "deepseek", "DeepSeek"),
    ("Alibaba", "alibaba", "Alibaba_Group"),
    ("Baidu", "baidu", "Baidu"),
    ("IBM", "ibm", "IBM"),
    ("Oracle", "oracle", "Oracle_Corporation"),
    ("Hugging Face", "hugging-face", "Hugging_Face"),
    ("Palantir", "palantir", "Palantir_Technologies"),
    ("Salesforce", "salesforce", "Salesforce"),
]

entity_cards = ""
for name, slug, wp in ecosystem_entities:
    svg_url = "https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/" + slug + "/default.svg"
    entity_cards += (
        '<div class="entity-card" data-wp="' + wp + '">\n'
        '  <img src="' + svg_url + '" width="28" height="28" alt="' + name + '" onerror="this.style.display=\'none\'"'
        ' style="object-fit:contain;background:var(--bar-bg);border-radius:4px;padding:2px;">\n'
        '  <span style="font-size:11px;font-weight:600;color:var(--text-primary)">' + name + '</span>\n'
        '</div>\n'
    )

ECOSYSTEM_HTML = (
    '<div class="section-header"><span class="icon">' + EMOJI["ecosystem"] + '</span><h2>AI Ecosystem Map \u2014 Companies & Developers</h2><span class="accent-line"></span></div>\n'
    '<div class="entity-row">\n'
    + entity_cards +
    '</div>'
)

# Assemble full content
content_html = (
    '<!-- Bar Chart -->\n' + BAR_CHART_HTML + '\n\n'
    '<!-- News -->\n' + NEWS_HTML + '\n\n'
    '<!-- Research -->\n' + RESEARCH_HTML + '\n\n'
    '<!-- Ecosystem Map -->\n' + ECOSYSTEM_HTML
)

# Sources
SOURCES_HTML = (
    '<div class="sources">\n  <h3>Sources</h3>\n'
    '  <a href="https://chicago.suntimes.com" target="_blank">Chicago Sun-Times</a>\n'
    '  <a href="https://blockclubchicago.org" target="_blank">Block Club Chicago</a>\n'
    '  <a href="https://chi.streetsblog.org" target="_blank">Streetsblog Chicago</a>\n'
    '  <a href="https://www.chicagotribune.com" target="_blank">Chicago Tribune</a>\n'
    '  <a href="https://www.nmrk.com" target="_blank">Newmark</a>\n'
    '  <a href="https://chicago.urbanize.city" target="_blank">Urbanize Chicago</a>\n'
    '  <a href="https://www.connectcre.com" target="_blank">Connect CRE</a>\n'
    '  <a href="https://www.thecentersquare.com" target="_blank">The Center Square</a>\n'
    '  <a href="https://news.wttw.com" target="_blank">WTTW</a>\n'
    '  <a href="https://www.crainschicago.com" target="_blank">Crain\u2019s Chicago Business</a>\n'
    '  <a href="https://data.cityofchicago.org" target="_blank">City of Chicago Data</a>\n'
    '  <a href="https://www.cookcountyassessoril.gov" target="_blank">Cook County Assessor</a>\n'
    '</div>'
)

pages_url = "https://jsoprych.github.io/elko-reports-community/research/" + DATE_STR + "-" + TIME_STR + "-" + SLUG + ".html"

top_heading = (
    '<a href="https://chicago.suntimes.com/real-estate/2026/04/17/brookfield-breaks-ground-4-building-industrial-campus-back-of-the-yards" '
    'target="_blank" style="color:var(--accent);text-decoration:none">'
    + EMOJI["construction"] + ' Brookfield Breaks Ground on Western Works \u2014 $100M Industrial Campus Near 60632</a>'
)
top_body = (
    "Brookfield Properties has broken ground on a 4-building, 560,000+ SF industrial development at 47th & Western in Back of the Yards, "
    "just minutes from the 60632 corridor. Meanwhile, Chicago's industrial market maintains 5.3% vacancy with nearly 15M SF under construction, "
    "strong demand signals for the Southwest Side industrial base."
)

# Render
html = render_shell(
    series="60632 Archer Heights",
    title="60632 Archer Heights \u2014 Daily Sweep | " + DATE_STR,
    date=DATE_STR,
    author="John Soprych (Hermes Agent)",
    classification="Public",
    doc_type="Daily Intelligence Sweep",
    top_heading=top_heading,
    top_body=top_body,
    metrics_html=METRICS_HTML,
    content_html=content_html,
    sources_html=SOURCES_HTML,
    pages_url=pages_url,
    extra_css=(
        '.entity-card { min-height: 80px; padding: 16px 10px; }\n'
        '.entity-card img[src*="svg"] { width: 32px; height: 32px; margin-bottom: 6px; }\n'
        '.entity-card span { font-size: 10px; line-height: 1.3; }\n'
        '.bar-label { width: 150px; font-size: 11px; }\n'
        '@media (max-width: 600px) {\n'
        '  .bar-label { width: 90px; font-size: 10px; }\n'
        '  .entity-row { grid-template-columns: repeat(3, 1fr); }\n'
        '}'
    )
)

# Save
filename, full_path = save_report(html, REPO_PATH, DATE_STR, TIME_STR, SLUG, subdir="research")
print("Saved: " + filename)

# Push
push_to_github(REPO_PATH, "[60632] Daily sweep \u2014 " + DATE_STR)
print("Pushed to GitHub")

# Email
email_body = (
    EMOJI["factory"] + " 60632 Archer Heights \u2014 Daily Sweep | " + DATE_STR + "\n\n"
    + "Database: " + str(total_biz) + " total businesses tracked\n"
    + "  \u2022 Industrial/Logistics: " + str(industrial) + "\n"
    + "  \u2022 Commercial/Office: " + str(commercial) + "\n"
    + "  \u2022 Retail/Food: " + str(retail_food) + "\n"
    + "  \u2022 Other: " + str(other) + "\n\n"
    + "Full Report (branded HTML):\n" + pages_url + "\n\n"
    + "\u2192 Brookfield breaks ground on $100M Western Works industrial campus\n"
    + "\u2192 Archer Ave Complete Streets compromise \u2014 17 parking spots restored\n"
    + "\u2192 Chicago industrial vacancy at 5.3% \u2014 strongest in years\n"
    + "\u2192 Mixed-use development approved at 3198 S. Archer (24 units + retail)\n"
    + "\u2192 Galvanize Real Estate acquires 462K SF industrial portfolio near Chicago\n"
    + "\u2192 Illinois Megaprojects bill advances \u2014 could unlock SW Side development\n"
    + "\u2192 New business license issued at 5030 S. Archer Ave\n"
    + "\u2192 Restaurant industry loses 2,100 jobs amid wage hike pressure\n\n"
    + "Sources include: Chicago Sun-Times, Block Club Chicago, Streetsblog Chicago,\n"
    + "Chicago Tribune, Newmark, Urbanize Chicago, Connect CRE, WTTW\n\n"
    + "\u2014\nGenerated by Hermes Agent / elko.ai"
)

email_link(
    recipient="johnsoprych@gmail.com",
    subject="60632 Archer Heights - Daily Sweep | " + DATE_STR,
    body=email_body,
    bcc="johnsoprych@gmail.com"
)
print("Email sent to johnsoprych@gmail.com")
print("\n" + pages_url)
