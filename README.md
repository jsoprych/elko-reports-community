# Elko Reports — Community Edition

![Elko Reports](assets/elko-reports-logo.svg)

**Public research reports, newsletters, and business intelligence from [elko.ai](https://elko.ai).**

---

## 📂 Structure

```
elko-reports-community/
├── daily/          # Daily reports (YYYY-MM-DD-slug.pdf + .json)
├── weekly/         # Weekly roundups (YYYY-Www-slug.pdf + .json)
├── monthly/        # Monthly summaries
├── archive/        # Historical / superseded reports
├── assets/         # Branding assets (SVG logos, icons)
├── schemas/        # JSON schema for report format
└── templates/      # Report templates and examples
```

Each report is published as **PDF + JSON**:
- **PDF** — Human-readable, formatted, ready to share
- **JSON** — Machine-readable, structured data, maps to markdown

## 📋 Current Report Types

| Type | Frequency | Description |
|------|-----------|-------------|
| 🌐 AI World Briefing | Daily | AI industry news, funding, model releases |
| 🏭 Business Inventory | On-demand | OSM-based business catalogs by geography |
| 📊 AI Benchmark Report | Weekly | Model performance, pricing, competitive landscape |
| 📈 Market Intelligence | Weekly | Financial data, economic indicators |

## 🔍 How to Use

Browse the `daily/` or `weekly/` directories by date. Each entry has:

```
daily/2026-05-01-slug.pdf    — Full formatted report
daily/2026-05-01-slug.json   — Structured data
```

The JSON files follow the schema at `schemas/elko-report-schema-v1.json` and can be consumed programmatically by any MCP client, AI agent, or data pipeline.

## ✉️ Contact

Questions or feedback? Reach us at **reid@elko.ai**

---

*Built by [elko.ai](https://elko.ai) — AI Infrastructure. Local-First. AI Agnostic.*
