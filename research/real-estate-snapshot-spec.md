# Real Estate Investor-Grade ZIP Intelligence — Implementation Spec

## 1. Overview

A standardized Elko Reports skill (`real-estate-snapshot`) that produces a comprehensive, ZIP-code-indexed real estate intelligence panel. Designed for investors, contractors, developers, and news-junkies. All fields optional — renders whatever data is available.

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│              real-estate-snapshot skill                   │
│                                                          │
│  DATA PIPELINE (cron refreshable)                       │
│  ┌────────────┐ ┌──────────────┐ ┌──────────┐           │
│  │ Redfin S3  │ │ Zillow CSV   │ │ FHFA HPI │           │
│  │ (resid)    │ │ (rents)      │ │ (index)  │           │
│  └─────┬──────┘ └──────┬───────┘ └────┬─────┘           │
│        │               │              │                  │
│        ▼               ▼              ▼                  │
│  ┌────────────────────────────────────────┐             │
│  │   SQLite: real_estate_snapshot.db       │             │
│  │   zip_snapshots (zip → JSON blob)      │             │
│  └──────────────────┬─────────────────────┘             │
│                     │                                    │
│                     ▼                                    │
│  ┌────────────────────────────────────────┐             │
│  │   HTML Renderer                         │             │
│  │   1 Snapshot Row + 10 Section Panels    │             │
│  └────────────────────────────────────────┘             │
│                                                          │
│  OUTPUT: Standard Elko Report Panel                      │
│          with data-panel nav sections                    │
└─────────────────────────────────────────────────────────┘
```

## 3. Core Files to Build

| File | Purpose |
|------|---------|
| `SKILL.md` | The spec doc (this) |
| `scripts/redfin_pipeline.py` | Download + cache Redfin S3 data |
| `scripts/zillow_pipeline.py` | Download + cache Zillow rent/zhvi data |
| `scripts/render_panel.py` | Takes snapshot JSON → HTML panel output |
| `scripts/init_db.py` | Create SQLite schema |

## 4. SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS zip_snapshots (
    zip TEXT PRIMARY KEY,
    city TEXT,
    state TEXT,
    snapshot_json TEXT,       -- full JSON blob (the investor-grade schema)
    redfin_period TEXT,       -- most recent data date from Redfin
    zillow_period TEXT,       -- most recent data date from Zillow
    data_sources TEXT,        -- JSON: which sources contributed
    last_updated INTEGER,     -- unix timestamp
    expires_at INTEGER        -- unix timestamp when data is stale
);
```

## 5. Investor-Grade JSON Schema

Every field is optional. The renderer shows only what's populated. Sections marked `[L1]` = achievable from free Redfin S3 data. Sections marked `[L2]` = achievable from free Zillow CSV. Sections marked `[L3]` = requires scraping or local knowledge (GSDC, City permits, LoopNet).

### 5.1 Snapshot Row (drives the top metric cards)

```json
{
  "type": "real-estate-investor",
  "data": {
    "zips": [{
      "zip": "60632",
      "city": "Chicago",
      "state": "IL",
```

```json
      "snapshot": {
        "median_home_value": 360000,           // [L1] Redfin
        "median_home_value_yoy_pct": 20.0,    // [L1]
        "median_rent": 1450,                   // [L2] Zillow
        "cap_rate_pct": 5.8,                   // [L2] rent/price calc
        "price_per_sqft": 295,                 // [L1]
        "days_on_market": 42,                  // [L1]
        "months_of_supply": 2.1,               // [L1]
        "sale_to_list_ratio": 0.987,           // [L1]
        "market_temp": "Seller's Market",      // [L1] inferred
        "data_quality": "redfin_live"          // auto-set
      },
```

### 5.2 Residential Deep [L1 — Redfin S3]

```json
      "residential": {
        "inventory": {
          "active_listings": 120,
          "new_listings_30d": 85,
          "pending_sales": 40,
          "homes_sold_30d": 55,
          "months_of_supply": 2.1,
          "price_drops_30d": 18,
          "sold_above_list_pct": 0.32
        },
        "pricing": {
          "median_list_price": 375000,
          "median_sale_price": 355000,
          "sale_to_list_ratio": 0.987,
          "avg_price_per_sqft": 295,
          "median_price_per_sqft_yoy_pct": 8.5,
          "avg_discount_from_list": -1.3
        },
        "historical": {
          "1yr_appreciation": 20.0,
          "3yr_appreciation": 42.0,
          "5yr_appreciation": 68.0,
          "foreclosure_rate_pct": 0.8
        }
      },
```

### 5.3 Commercial / Industrial [L3 — GSDC, LoopNet, scraping]

```json
      "commercial": {
        "industrial": {
          "total_sf": 45000000,
          "vacancy_pct": 5.9,
          "avg_rent_psf": 5.75,
          "under_construction_sf": 14900000,
          "absorption_sf_12mo": 850000,
          "major_tenants": ["GEODIS", "Bagcraft", "Vitner's"]
        },
        "office": {
          "total_sf": 1200000,
          "vacancy_pct": 12.4,
          "avg_rent_psf": 18.50,
          "class_a_rent_psf": 24.00,
          "class_b_rent_psf": 16.00
        },
        "retail": {
          "total_sf": 800000,
          "vacancy_pct": 8.2,
          "avg_rent_psf": 14.00,
          "major_corridors": ["Archer Ave", "Pulaski Rd", "Cicero Ave"]
        },
        "logistics": {
          "proximity_to_hubs": ["Midway Airport (2mi)", "I-55 (1mi)", "BNSF Rail"],
          "last_mile_delivery_suitability": "high"
        }
      },
```

### 5.4 New Construction [L3 — City permits, developer PR]

```json
      "construction": {
        "major_projects": [
          {
            "name": "Sterling Bay — 4510 W Ann Lurie",
            "type": "industrial",
            "status": "under_construction",
            "sf": 850000,
            "developer": "Sterling Bay",
            "est_completion": "2026-Q4",
            "est_jobs": 500,
            "investor": "Sterling Bay"
          }
        ],
        "permits": {
          "new_building_permits_30d": 8,
          "total_permit_value_30d": 45000000,
          "permit_trend_yoy": "up 15%"
        },
        "subsidies_and_incentives": [
          {"name": "Class 6b Tax Incentive", "type": "tax_abatement", "years": 12, "max_savings_pct": 80},
          {"name": "Neighborhood Opportunity Fund", "type": "grant", "max_amount": 250000}
        ]
      },
```

### 5.5 Zoning + Regulatory [L3 — Chicago DPD, scraping]

```json
      "zoning": {
        "current_designations": [
          {"district": "Greater Southwest PMD", "type": "Planned Manufacturing District", "allowed": "mfg, warehouse, distribution"}
        ],
        "active_changes": [
          {"name": "Chicago Zoning Ordinance Rewrite", "status": "planning", "impact": "First major overhaul in decades"}
        ],
        "overlay_districts": ["TIF District", "Enterprise Zone"],
        "density": {
          "current_far_max": 2.5,
          "height_restrictions": "none for industrial"
        }
      },
```

### 5.6 Brokers & Investors [L3 — GSDC, Crain's, LoopNet ownership]

```json
      "brokers_and_investors": {
        "active_developers": [
          {"name": "Sterling Bay", "type": "Developer", "focus": "Industrial"}
        ],
        "commercial_brokers": [
          {"name": "Colliers International", "focus": "Industrial/office", "office": "Chicago"},
          {"name": "Cushman & Wakefield", "focus": "Industrial/logistics"},
          {"name": "JLL", "focus": "Industrial/retail"},
          {"name": "CBRE", "focus": "Full service"}
        ],
        "recent_sales": [
          {"property": "4510 W Ann Lurie (site)", "buyer": "Sterling Bay", "price": 8500000, "date": "2025-06", "sf": 850000, "price_psf": 10.00}
        ],
        "institutional_owners": ["Prologis", "Duke Realty", "Blackstone"]
      },
```

### 5.7 Rents + Yield [L2 — Zillow ZORI CSV + HUD FMR]

```json
      "rental": {
        "market": {
          "median_rent": 1450,
          "median_rent_yoy_pct": 4.2,
          "rent_per_sqft": 1.85,
          "vacancy_pct": 5.1,
          "rent_concessions_pct": 0.08
        },
        "by_unit_type": {
          "studio": {"avg_rent": 1050, "avg_dom_rental": 30},
          "1br": {"avg_rent": 1250, "avg_dom_rental": 25},
          "2br": {"avg_rent": 1550, "avg_dom_rental": 22},
          "3br": {"avg_rent": 1850, "avg_dom_rental": 28}
        },
        "short_term": {
          "airbnb_listings": 15,
          "avg_daily_rate": 85,
          "occupancy_pct": 62,
          "avg_monthly_revenue": 1580
        },
        "affordability": {
          "rent_to_income_ratio": 0.28,
          "housing_choice_vouchers": 850
        }
      },
```

### 5.8 Sales Metrics + Trends [L1 — Redfin S3]

```json
      "sales_metrics": {
        "volume": {
          "total_sales_12mo": 660,
          "total_volume_12mo": 234000000,
          "avg_sale_price_12mo": 354545
        },
        "velocity": {
          "avg_dom": 42,
          "pct_sold_in_30d": 35,
          "pct_sold_in_60d": 62,
          "pct_sold_above_list": 32,
          "avg_discount": -1.3
        },
        "seasonality": {
          "peak_month": "June",
          "low_month": "January"
        }
      },
```

### 5.9 Mortgage + Financing [L3 — Freddie Mac PMMS public + local scrape]

```json
      "mortgage_and_financing": {
        "current_rates": {
          "30yr_fixed": 6.35,
          "15yr_fixed": 5.60,
          "5_1_arm": 5.85,
          "fha_30yr": 6.10,
          "va_30yr": 5.95,
          "rate_trend": "flat_to_down"
        },
        "local_lenders": [
          {"name": "Wintrust Mortgage", "type": "Bank", "specialty": "conventional"},
          {"name": "Guaranteed Rate", "type": "Mortgage Co", "specialty": "all types"},
          {"name": "BMO Harris", "type": "Bank", "specialty": "jumbo"}
        ],
        "down_payment_assistance": [
          {"name": "IHDA 1st Home Illinois", "amount": 5000, "type": "grant"}
        ]
      },
```

### 5.10 Demographics + Economic [L2 — Census Bureau API]

```json
      "demographics": {
        "population": {
          "total": 45000,
          "density_per_sqmi": 8654,
          "growth_5yr_pct": -2.1,
          "median_age": 33.5
        },
        "income": {
          "median_hh_income": 52400,
          "poverty_rate_pct": 18.5,
          "income_growth_5yr_pct": 8.2
        },
        "households": {
          "total": 16500,
          "owner_occupied_pct": 52,
          "renter_occupied_pct": 48,
          "vacant_pct": 7.5
        },
        "employment": {
          "labor_force": 22000,
          "unemployment_rate_pct": 6.8,
          "top_employers": ["Midway Airport", "Bagcraft", "GEODIS", "CPS"],
          "commute_time_avg_min": 32
        },
        "crime": {
          "overall_rating": "below_avg",
          "violent_crime_per_1k": 4.2,
          "property_crime_per_1k": 22.5,
          "trend": "downward_3yr"
        }
      },
```

### 5.11 Market News [L3 — curated/GSDC scraped/Crain's]

```json
      "market_news": [
        {
          "date": "2026-04-28",
          "headline": "Sterling Bay breaks ground on 850K SF industrial at 4510 W Ann Lurie",
          "source": "GSDC",
          "impact": "increased_industrial_supply"
        }
      ],
```

### 5.12 Summary Metrics Row (top of panel)

```json
      "summary_metrics_row": [
        {"value": "$360K", "label": "Median Home", "color": "#22c55e"},
        {"value": "+20%", "label": "YoY Price", "color": "#3b82f6"},
        {"value": "5.9%", "label": "Ind. Vacancy", "color": "#f97316"},
        {"value": "$1,450", "label": "Median Rent", "color": "#a855f7"},
        {"value": "42d", "label": "DOM", "color": "#f59e0b"},
        {"value": "2.1mo", "label": "Supply", "color": "#ec4899"},
        {"value": "6.35%", "label": "30yr Fixed", "color": "#6366f1"},
        {"value": "6.8%", "label": "Unemployment", "color": "#14b8a6"}
      ]
    }]
  }
}
```

## 6. Data Sources

| Section | Tier | Source URL | Refresh |
|---------|------|-----------|---------|
| Snapshot, Residential, Sales | L1 | `https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz` | Monthly (3rd Fri) |
| Rent, Yield | L2 | `https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_sm_month.csv` | Monthly |
| Home Values | L2 | `https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv` | Monthly |
| Demographics | L2 | `https://api.census.gov/data/2023/acs/acs5` (free API) | Annual |
| Mortgage Rates | L3 | `http://www.freddiemac.com/pmms/export-pmmbs` | Weekly |
| Commercial | L3 | LoopNet/Crexi scraping or GSDC/local EDC | Manual/Quarterly |
| Zoning | L3 | `https://data.cityofchicago.org` | Manual |
| Crime | L3 | `https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/` | Monthly |
| Construction | L3 | City permit portal + PR scraping | Manual |

## 7. HTML Renderer

Each section becomes a `data-panel`-wrapped div for the standard panel-nav widget:

```html
<div class="hero-card" style="border-left-color:#3b82f6">
  <!-- Snapshot metrics row -->
</div>

<div data-panel="residential" data-panel-title="🏡 Residential" data-panel-color="#22c55e" data-panel-default="1">
  <div class="section-header"><span class="icon">🏡</span><h2>Residential Deep</h2><span class="accent-line"></span></div>
  ...
</div>

<div data-panel="commercial" data-panel-title="🏢 Commercial" data-panel-color="#f97316" data-panel-default="1">
  ...
</div>
... (10 sections total)
```

Each missing section is simply not emitted. The panel-nav JS auto-discovers only the sections that exist.

## 8. Implementation Priority

**Phase 1 (this week):**
1. SQLite schema + Redfin S3 pipeline (download → cache → query by ZIP)
2. HTML renderer — snapshot row + residential deep + sales metrics (the 3 L1 sections)
3. Inject into existing 60632 report as proof

**Phase 2 (next week):**
4. Zillow ZORI pipeline → rental + yield section
5. Zillow ZHVI pipeline → home value supplement
6. Census API → demographics section

**Phase 3 (ongoing):**
7. Mortgage rates via Freddie Mac PMMS
8. Commercial/zoning scraping for each target ZIP
9. Chromein/EDC outreach for curated data
10. Cron job: `0 0 15 * *` → refresh Redfin cache monthly

## 9. Existing Code to Extend

The `real-estate-snapshot` skill at `/opt/data/skills/productivity/real-estate-snapshot/` already has:
- `SKILL.md` (v2.0.0 schema — this doc)
- `scripts/redfin_pipeline.py` (base pipeline stub)

Extend `redfin_pipeline.py` with:
- `fetch_zip(zip_code)` → returns cached snapshot or None
- `refresh_zip(zip_code)` → downloads Redfin, filters, caches
- `render_html(snapshots)` → outputs standard panel HTML
- `get_summary_metrics(snapshot)` → returns the 8-card row

## 10. Quality Standards

- Every field must be nullable/optional. The renderer handles partial data.
- The `data_quality` field in snapshot tells the reader: `"redfin_live"`, `"redfin_cached"`, `"partial"`, or `"estimated"`
- Redfin data is considered "live" if downloaded within the last 7 days, "cached" if 7-30 days, "stale" if >30 days
- Commercial/zoning data is manually curated and should be date-stamped
- When merging multiple ZIPs into one report, each ZIP gets its own `data-panel` section
