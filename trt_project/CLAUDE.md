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
| `fetch_market_overview()` | yfinance (featured US, BR, FII, crypto lists) | 300s |
| `fetch_top_movers()` | Yahoo Finance screener API + yfinance for FII/crypto | 300s |
| `fetch_tesouro()` | yfinance via B3 ETFs (IMAB11, B5P211, TESD11, XFIX11) | 300s |
| `fetch_taxas_bcb()` | BCB open API — SELIC (432), IPCA (433), CDI (4389) | 1800s |
| `fetch_price(symbol)` | yfinance, 3 retry attempts, no cache | — |

All grouped fetches (`_fetch_group`, `_fii_top`, `_crypto_top`) use `ThreadPoolExecutor` for parallel requests.

### Search
`search_suggest` (`/search/suggest/`) — autocomplete via Yahoo Finance search API, returns JSON (symbol, name, tipo, exchange, url). `search` (`/search/`) — full search page using the same API, renders `search.html`.

### Stock detail (`/ativo/<symbol>/`)
Fetches full yfinance `info` dict and exposes ~35 fundamental fields (price, P/E, P/B, margins, ROE, ROA, debt/equity, market cap, revenue, EBITDA, free cash flow, etc.). Also renders a 1-month price chart (Chart.js) and the last 10 alerts for the stock. Supports add/remove/toggle actions via POST.

### URLs

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

### Templates
All under `monitor/templates/monitor/`. `login.html` and `register.html` are standalone (no base template). All authenticated views extend `base.html`.

| Template | View |
|---|---|
| `base.html` | base layout for authenticated views |
| `home.html` | market overview, top movers, Tesouro, BCB rates |
| `stock_list.html` | portfolio with per-stock thresholds and toggle |
| `stock_detail.html` | full fundamentals + chart + alerts |
| `settings.html` | monitoring interval + ntfy.sh config |
| `alert_history.html` | last 100 alerts |
| `search.html` | search results |
| `login.html` | login form |
| `register.html` | registration form |
