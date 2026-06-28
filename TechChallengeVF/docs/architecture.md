# Architecture

The full architecture, setup, and run instructions live in the root
[`README.md`](../../README.md). This file is the detailed component view.

## Data flow

```
┌──────────────────────┐        ┌──────────────────────┐
│  Real public site    │        │  Static HTML site     │
│  tiendamonge.com     │        │  web_sample/ served   │
│  (JS, scroll, paging) │        │  via http.server      │
└──────────┬───────────┘        └──────────┬───────────┘
           │ Selenium                       │ requests + BeautifulSoup
           ▼                                ▼
┌──────────────────────┐        ┌──────────────────────┐
│ scraper_dynamic.py   │        │ scraper_static.py     │
│ extract_products()   │        │ download + SHA-256    │
└──────────┬───────────┘        └──────────┬───────────┘
           │ reconcile_products             │ file detection
           │ E1 new / E2 mod / E3 del       │ E4 replace / E5 delete
           ▼                                ▼
        ┌───────────────────────────────────────────┐
        │            PostgreSQL (tienda)             │
        │  products · downloaded_files               │
        │  product_versions · file_versions          │
        └───────────────────┬───────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
   generate_results_json.py        generate_files_json.py
            │                               │
            ▼                               ▼
        data/results.json            data/files.json   ──▶  dashboard (web_sample/index.html)
                                                              or Flask API (json_api_server.py)

Cross-cutting:
  • main.py        — orchestrates every stage, each guarded (resilient)
  • scheduler.py   — APScheduler, runs the pipeline hourly
  • Connections/logger.py     — structured JSON logs -> stdout + scraper.log
  • Connections/config.py     — central, cwd-independent paths + env config
  • Connections/llm_selector.py — bonus: Azure OpenAI selector generation/repair
```

## Database schema

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `products` | scraped structured records | `product_key` (UNIQUE), `title`, `price`, `image_url`, `url`, `content_hash`, `first_seen`, `last_seen`, `updated_at` |
| `downloaded_files` | tracked downloaded files | `filename` (UNIQUE), `url`, `sha256`, `version`, `download_date`, `last_seen` |
| `product_versions` | record change history | `product_key`, `title`, `price`, `changed_at` |
| `file_versions` | file change history (req D) | `filename`, `sha256`, `version`, `changed_at` |

## Change-detection rules

| Rule | Trigger | Action | Alert |
|------|---------|--------|-------|
| E1 | record/file not in DB | INSERT + download | `[NEW]` |
| E2 | record `content_hash` differs | UPDATE + history row | `[CHANGED][RECORD]` |
| E3 | record no longer scraped | DELETE row | `[DELETED][RECORD]` |
| E4 | file `sha256` differs | replace file + bump version | `[CHANGED][FILE]` |
| E5 | file gone from catalogue | delete local file + DB row | `[DELETED][FILE]` |

Safety guards: the record delete sweep is skipped when 0 records are scraped;
the file delete sweep runs only when the file catalogue was fetched successfully.

## Tech stack
Python 3.9+ · Selenium + webdriver-manager · requests + BeautifulSoup ·
PostgreSQL + psycopg2 · APScheduler · python-dotenv · Azure OpenAI (gpt-4o-mini) ·
Flask + Flask-CORS · structured JSON logging.
