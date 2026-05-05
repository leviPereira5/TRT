from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Stock, UserSettings, Alert
from .forms import StockForm, SettingsForm
from .services import run_monitoring_cycle, fetch_market_overview, fetch_price


def home(request):
    overview = fetch_market_overview()
    return render(request, 'monitor/home.html', {'overview': overview})


def stock_detail(request, symbol_yf):
    import yfinance as yf
    stock    = Stock.objects.filter(symbol=symbol_yf).first()
    settings = UserSettings.objects.first() or UserSettings.objects.create()
    ticker   = yf.Ticker(symbol_yf)
    info     = ticker.info
    price      = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
    prev_close = info.get("previousClose")
    change_pct = round(((price - prev_close) / prev_close) * 100, 2) if price and prev_close else 0
    stats = {
        'price':       round(price, 2) if price else '—',
        'change_pct':  change_pct,
        'currency':    info.get('currency', ''),
        'name':        info.get('shortName', symbol_yf),
        'week52_low':  info.get('fiftyTwoWeekLow', '—'),
        'week52_high': info.get('fiftyTwoWeekHigh', '—'),
        'day_low':     info.get('dayLow', '—'),
        'day_high':    info.get('dayHigh', '—'),
        'div_yield':   round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else '—',
        'volume':      info.get('regularMarketVolume', '—'),
        'pe_ratio':    info.get('trailingPE', '—'),
    }
    hist = ticker.history(period='1mo')
    chart_labels = []
    chart_data   = []
    if not hist.empty:
        for idx, row in hist.iterrows():
            chart_labels.append(str(idx)[:10])
            chart_data.append(round(float(row['Close']), 2))
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add' and not Stock.objects.filter(symbol=symbol_yf).exists():
            if '11' in symbol_yf and '.SA' in symbol_yf:
                tipo = 'fii'
            elif '.SA' in symbol_yf:
                tipo = 'stock_br'
            else:
                tipo = 'stock_us'
            Stock.objects.create(
                symbol=symbol_yf,
                name=stats['name'],
                tipo=tipo,
            )
            messages.success(request, f"{symbol_yf} adicionado!")
            return redirect('stock_detail', symbol_yf=symbol_yf)
        elif action == 'remove' and stock:
            stock.delete()
            messages.success(request, f"{symbol_yf} removido.")
            return redirect('home')
        elif action == 'toggle' and stock:
            stock.is_active = not stock.is_active
            stock.save()
            return redirect('stock_detail', symbol_yf=symbol_yf)
    alerts = Alert.objects.filter(stock=stock).order_by('-sent_at')[:10] if stock else []
    prices = stock.prices.all()[:30] if stock else []
    return render(request, 'monitor/stock_detail.html', {
        'symbol':       symbol_yf,
        'stock':        stock,
        'stats':        stats,
        'settings':     settings,
        'alerts':       alerts,
        'prices':       prices,
        'chart_labels': chart_labels,
        'chart_data':   chart_data,
    })


def stock_list(request):
    stocks   = Stock.objects.all().order_by('-added_at')
    settings = UserSettings.objects.first()
    stocks_data = []
    for stock in stocks:
        last = stock.prices.first()
        stocks_data.append({
            'stock':        stock,
            'last_price':   last.price if last else None,
            'last_fetched': last.fetched_at if last else None,
        })
    return render(request, 'monitor/stock_list.html', {
        'stocks_data': stocks_data,
        'settings':    settings,
    })

def stock_add(request):
    import yfinance as yf
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            # Se o nome não foi preenchido, vai buscar automaticamente
            if not stock.name:
                try:
                    info = yf.Ticker(stock.symbol).info
                    stock.name = info.get('shortName', '') or info.get('longName', '')
                except Exception:
                    pass
            stock.save()
            messages.success(request, f"Adicionado: {stock.symbol} — {stock.name}")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('stock_list')


def stock_remove(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    messages.success(request, f"{stock.symbol} removido.")
    return redirect('stock_list')


def stock_toggle(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.is_active = not stock.is_active
    stock.save()
    estado = 'ativado' if stock.is_active else 'pausado'
    messages.success(request, f"{stock.symbol} {estado}.")
    return redirect('stock_list')


def settings_view(request):
    s = UserSettings.objects.first() or UserSettings.objects.create()
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações guardadas!")
            return redirect('settings')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        form = SettingsForm(instance=s)
    return render(request, 'monitor/settings.html', {'form': form, 'settings': s})


def run_monitor(request):
    results = run_monitoring_cycle()
    for r in results:
        if 'error' in r:
            messages.error(request, f"{r['symbol']}: {r['error']}")
        elif r.get('fallback'):
            messages.warning(request, f"{r['symbol']}: fallback ({r['price']})")
        else:
            msg = f"{r['symbol']}: {r['price']} ({r['variation']:+}%)"
            if r.get('alert'):
                msg += " ALERTA!"
            messages.success(request, msg)
    return redirect('stock_list')


def alert_history(request):
    alerts = Alert.objects.select_related('stock').all()[:100]
    return render(request, 'monitor/alert_history.html', {'alerts': alerts})


def search(request):
    import requests
    query   = request.GET.get('q', '').strip()
    results = []
    if query:
        try:
            # Yahoo Finance search API — devolve qualquer ativo mundial
            url     = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=pt&region=BR&quotesCount=20&newsCount=0"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp    = requests.get(url, headers=headers, timeout=5)
            data    = resp.json()

            for item in data.get('quotes', []):
                symbol = item.get('symbol', '')
                if not symbol:
                    continue
                results.append({
                    'symbol':   symbol,
                    'name':     item.get('shortname') or item.get('longname', symbol),
                    'tipo':     item.get('quoteType', ''),
                    'exchange': item.get('exchange', ''),
                    'price':    '—',
                    'currency': item.get('currency', ''),
                })
        except Exception as e:
            pass
    return render(request, 'monitor/search.html', {'results': results, 'query': query})