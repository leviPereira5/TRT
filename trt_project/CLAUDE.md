# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the dev server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create a new migration after model changes
python manage.py makemigrations

# Create a superuser
python manage.py createsuperuser

# Run the continuous background monitoring loop
python manage.py run_monitor

# Run tests
python manage.py test monitor

# Clear Django cache (required after changing cached service data)
python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trt_project.settings'); django.setup(); from django.core.cache import cache; cache.clear()"
```

## Architecture

Single Django app (`monitor`) inside the `trt_project` project. SQLite database. No `.env` variables required — all configuration is done via the web UI (`/settings/`).

### Data flow
1. `services.py` — all market data and alert logic. `fetch_price()` hits yfinance; `run_monitoring_cycle()` iterates active `Stock` objects, saves a `StockPrice`, and triggers `Alert` creation + ntfy.sh push notification if thresholds are exceeded.
2. `views.py` — thin HTTP layer that calls services and renders templates.
3. `management/commands/run_monitor.py` — long-running process that calls `run_monitoring_cycle()` in a loop using `UserSettings.monitoring_interval` as the sleep period.

### Models
- `Stock` — tracked asset with fields: `symbol`, `name`, `tipo` (stock_us / stock_br / fii / crypto), `is_active`, `threshold_high`, `threshold_low` (per-stock alert thresholds, default 5%).
- `StockPrice` — time-series price snapshots, FK to Stock, ordered by `-fetched_at`.
- `Alert` — fired when variation exceeds `threshold_high`/`threshold_low`; suppressed within 60-minute windows via `already_alerted()`. Fields: `stock`, `direction` (high/low), `variation`, `price`, `sent_at`, `notified`, `email_sent` (repurposed: True when ntfy notification was sent).
- `UserSettings` — singleton row; `monitoring_interval` (seconds, 1–3600) and `ntfy_topic` (ntfy.sh topic name).

### Auth
Django's built-in `User` model. `login_view` supports both username and email login (resolves email → username before calling `authenticate()`). Guest access via the `visitante` user created on-demand via `/guest/`. Register at `/register/`.

### Push notifications (ntfy.sh)
No SMTP or credentials required. `UserSettings.ntfy_topic` holds the chosen ntfy.sh topic name. `services.send_ntfy_notification()` POSTs to `https://ntfy.sh/{topic}` with a title, priority, and emoji tag (headers must be ASCII — no em dashes). Test via `/settings/test-ntfy/`. User subscribes to the topic in the free ntfy app (Android/iOS).

### Market data (`services.py`)
All market functions use Django's cache to avoid hammering external APIs:

| Function | Source | Cache TTL |
|---|---|---|
| `fetch_market_overview()` | yfinance via `_fetch_single` for each symbol in FEATURED_* lists | 300s |
| `fetch_top_movers()` | Static lists + `_fetch_single` for all categories including BR | 300s |
| `fetch_tesouro()` | yfinance via B3 ETFs (IMAB11, B5P211, TESD11, XFIX11) | 300s |
| `fetch_taxas_bcb()` | BCB open API — SELIC (432), IPCA (433), CDI (4389) | 1800s |
| `fetch_price(symbol)` | yfinance, 3 retry attempts, no cache | — |

**`_fetch_single(symbol)`** — core function used by all overview/top-movers fetches. Returns: `symbol`, `symbol_yf`, `name`, `price`, `change_pct`, `currency`, `logo_url`, and **`spark`** (list of last 10 days close prices for sparkline charts).

**Top 10 Brasil** uses `TOP_BR_LIST` (static list of B3 symbols) + `_fetch_single`, NOT the Yahoo Finance screener POST API — that API requires a crumb token and returns 401. All other top-10 categories (FII, Crypto, EU, CN) use the same static-list pattern.

### Search
`search_suggest` (`/search/suggest/`) — autocomplete via Yahoo Finance search API, returns JSON (symbol, name, tipo, exchange, url). `search` (`/search/`) — full search page using the same API, renders `search.html`.

### Stock detail (`/ativo/<symbol>/`)
Fetches full yfinance `info` dict and exposes ~35 fundamental fields. History fetched for **1 year** (`period='1y'`) including volume — passed to the template as `chart_labels`, `chart_data`, `vol_data`. The template renders:
- Price chart (Chart.js line) with 1M/3M/6M/1A period selector (client-side slice)
- Volume chart (Chart.js bar) below price chart
- 52-week range bar (CSS + inline JS for position calculation)
- Margins horizontal bar chart (gross/EBITDA/operating/net)
- Fundamental indicator tabs (Valuation, Eficiência, Rentabilidade, Endividamento, Crescimento)
- Last 10 alerts for the stock

---

## CSS / Dark Mode — Critical Invariants

### Dark mode class location
The `dark` class lives **only on `<html>` (documentElement)**, never on `<body>`. This is set by an inline `<head>` script before any CSS renders (prevents flash).

**Always use:**
```javascript
document.documentElement.classList.contains('dark')  // ✓
document.documentElement.classList.toggle('dark', bool)  // ✓
```

**Never use:**
```javascript
document.body.classList.contains('dark')  // ✗ — body has no dark class
```

All CSS dark mode selectors use `html.dark`, never `body.dark`.

### Dark mode CSS rules must use explicit hex colors
Dark mode overrides use **explicit hex values**, not CSS variables. CSS variables (`var(--surface)`, `var(--white)`) can fail to resolve correctly when used in `html.dark` overrides, causing white cards.

```css
/* ✓ Correct */
html.dark .market-card { background: #1c1f28; border-color: rgba(255,255,255,.09); }

/* ✗ Avoid in dark mode overrides */
html.dark .market-card { background: var(--surface); }
```

### Dark mode color palette
| Element | Color |
|---|---|
| Page background | `#0d0f14` |
| Cards / surfaces | `#1c1f28` |
| Sidebar | `#06080c` |
| Filter bar | `#0a0a0a` |
| Text | `#e4e4e8` |
| Muted text | `#8a8a95` |
| Accent (yellow) | `#FFD600` |

### CSS cache busting
The main stylesheet is linked as `{% static 'monitor/css/main.css' %}?v=4`. **Bump the version** whenever making CSS changes that need to bust the browser cache, otherwise users see old styles.

### Category color palette
Used consistently across donut chart, mkt-stat cards, bar chart, and legend:

| Category | Color |
|---|---|
| EUA | `#FFD600` |
| Brasil | `#34d399` |
| FIIs | `#fb923c` |
| Cripto | `#a78bfa` |
| Europa | `#60a5fa` |
| China/HK | `#f87171` |
| ETFs | `#94a3b8` |

### Icons
All icons throughout the UI are **monochromatic SVGs** with `stroke="currentColor"` — no emojis, no colored icons. This applies to the filter bar, Top 10 tabs, section titles, and bar chart labels.

---

## URLs

| URL | View | Name |
|---|---|---|
| `/` | `home` | `home` |
| `/login/` | `login_view` | `login` |
| `/logout/` | `logout_view` | `logout` |
| `/register/` | `register_view` | `register` |
| `/guest/` | `guest_login` | `guest_login` |
| `/portfolio/` | `stock_list` | `stock_list` |
| `/portfolio/add/` | `stock_add` | `stock_add` |
| `/portfolio/<pk>/remove/` | `stock_remove` | `stock_remove` |
| `/portfolio/<pk>/toggle/` | `stock_toggle` | `stock_toggle` |
| `/portfolio/<pk>/thresholds/` | `stock_set_thresholds` | `stock_set_thresholds` |
| `/ativo/<symbol_yf>/` | `stock_detail` | `stock_detail` |
| `/settings/` | `settings_view` | `settings` |
| `/settings/test-ntfy/` | `test_ntfy` | `test_ntfy` |
| `/monitor/run/` | `run_monitor` | `run_monitor` |
| `/alerts/` | `alert_history` | `alert_history` |
| `/search/` | `search` | `search` |
| `/search/suggest/` | `search_suggest` | `search_suggest` |

## Templates
All under `monitor/templates/monitor/`. `login.html` and `register.html` are standalone (no base template). All authenticated views extend `base.html`.

| Template | View |
|---|---|
| `base.html` | base layout; contains dark mode JS, sidebar, filter bar block |
| `home.html` | market overview, sparkline cards, donut chart, bar chart, Top 10, Tesouro, BCB rates |
| `stock_list.html` | portfolio with per-stock thresholds and toggle |
| `stock_detail.html` | full fundamentals + 1y price/volume chart + margins chart + 52w range + alerts |
| `settings.html` | monitoring interval + ntfy.sh config |
| `alert_history.html` | last 100 alerts |
| `search.html` | search results |
| `login.html` | login form |
| `register.html` | registration form |

## Data freshness
- yfinance market data has **~15 min delay** on most exchanges (US, Nasdaq). B3 (Brazil) may have more.
- Home page data is cached for **5 minutes**; reloading within that window returns cached prices.
- `run_monitor` alert checks run on a configurable interval but are still subject to yfinance delay.
- True real-time data would require a paid API (Alpaca, Polygon.io, etc.).
