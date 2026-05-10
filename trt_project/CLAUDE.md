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

Single Django app (`monitor`) inside the `trt_project` project. SQLite database.

### Data flow
1. `services.py` — all market data logic. `fetch_price()` hits yfinance; `run_monitoring_cycle()` iterates active `Stock` objects, saves a `StockPrice`, and triggers `Alert` creation + email if thresholds are exceeded.
2. `views.py` — thin HTTP layer that calls services and renders templates.
3. `management/commands/run_monitor.py` — long-running process that calls `run_monitoring_cycle()` in a loop using `UserSettings.monitoring_interval` as the sleep period.

### Models
- `Stock` — tracked asset (symbol, tipo, thresholds per stock).
- `StockPrice` — time-series price snapshots, FK to Stock, ordered by `-fetched_at`.
- `Alert` — fired when variation exceeds `threshold_high`/`threshold_low`; suppressed within 60-minute windows via `already_alerted()`.
- `UserSettings` — singleton row; `monitoring_interval` (seconds) and `alert_email`.

### Auth
Django's built-in `User` model. `login_view` supports both username and email login (resolves email → username before calling `authenticate()`). Guest access via the `visitante` user created on-demand.

### Email alerts
Configured via `.env` (Gmail SMTP). `UserSettings.alert_email` is the recipient. `services.send_alert_email()` sends formatted plain-text alerts. Test via `/settings/test-email/`.

### Market data
`services.fetch_market_overview()` fetches curated lists of US stocks, BR stocks (`.SA` suffix), FIIs, and crypto on every home page load — no caching. `fetch_tesouro()` approximates Tesouro Direto with B3 ETFs (IMAB11, B5P211, TESD11, XFIX11).

### Templates
All under `monitor/templates/monitor/`. Standalone HTML files with inline CSS (no base template inheritance for login/register). `base.html` is used by authenticated views.
