from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Stock, UserSettings, Alert
from .forms import StockForm, SettingsForm
from .services import run_monitoring_cycle, fetch_market_overview, fetch_price, fetch_tesouro, fetch_taxas_bcb, fetch_top_movers


def register_view(request):
    from django.contrib.auth.models import User
    if request.user.is_authenticated:
        return redirect('home')
    form_data = {}
    errors = {}
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password  = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        form_data = {'username': username, 'email': email}

        if not username:
            errors['username'] = 'O nome de utilizador é obrigatório.'
        elif len(username) < 3:
            errors['username'] = 'O nome de utilizador deve ter pelo menos 3 caracteres.'
        elif User.objects.filter(username__iexact=username).exists():
            errors['username'] = 'Este nome de utilizador já está em uso.'

        if not email:
            errors['email'] = 'O email é obrigatório.'
        elif User.objects.filter(email__iexact=email).exists():
            errors['email'] = 'Este email já está registado.'

        if not password:
            errors['password'] = 'A password é obrigatória.'
        elif len(password) < 8:
            errors['password'] = 'A password deve ter pelo menos 8 caracteres.'
        elif password != password2:
            errors['password2'] = 'As passwords não coincidem.'

        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}.')
            return redirect('home')

    return render(request, 'monitor/register.html', {'form': form_data, 'errors': errors})


def login_view(request):
    from django.contrib.auth.models import User
    if request.user.is_authenticated:
        return redirect('home')
    form_data = {}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        form_data['username'] = username
        # Support login by email address as well as username
        login_username = username
        if '@' in username:
            try:
                login_username = User.objects.get(email__iexact=username).username
            except User.DoesNotExist:
                pass
        user = authenticate(request, username=login_username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        messages.error(request, 'Utilizador ou password incorretos.')
    return render(request, 'monitor/login.html', {
        'form': form_data,
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def guest_login(request):
    from django.contrib.auth.models import User
    guest, _ = User.objects.get_or_create(
        username='visitante',
        defaults={'first_name': 'Visitante', 'is_active': True},
    )
    login(request, guest, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('home')


@login_required
def home(request):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        f_overview   = ex.submit(fetch_market_overview)
        f_tesouro    = ex.submit(fetch_tesouro)
        f_taxas      = ex.submit(fetch_taxas_bcb)
        f_top_movers = ex.submit(fetch_top_movers)
        overview   = f_overview.result()
        tesouro    = f_tesouro.result()
        taxas      = f_taxas.result()
        top_movers = f_top_movers.result()
    top10_sections = [
        ('us',     top_movers.get('us', []),     'USD'),
        ('br',     top_movers.get('br', []),     'R$'),
        ('fii',    top_movers.get('fii', []),    'R$'),
        ('crypto', top_movers.get('crypto', []), 'auto'),
        ('eu',     top_movers.get('eu', []),     'auto'),
        ('cn',     top_movers.get('cn', []),     'HKD'),
    ]
    return render(request, 'monitor/home.html', {
        'overview':       overview,
        'tesouro':        tesouro,
        'taxas':          taxas,
        'top10_sections': top10_sections,
    })


@login_required
def stock_detail(request, symbol_yf):
    import yfinance as yf
    stock    = Stock.objects.filter(symbol=symbol_yf).first()
    settings = UserSettings.objects.first() or UserSettings.objects.create()
    ticker   = yf.Ticker(symbol_yf)
    info     = ticker.info
    price      = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
    prev_close = info.get("previousClose")
    change_pct = round(((price - prev_close) / prev_close) * 100, 2) if price and prev_close else 0
    def _pct(v):
        return f"{round(v * 100, 2)}%" if v else '—'
    def _r2(v):
        # yfinance devolve 0.0 para BR stocks quando mercado fechado — tratar como indisponível
        if not v or v == 0.0: return '—'
        return round(v, 2)
    def _fmt(v):
        if not v or v == 0: return '—'
        if v >= 1_000_000_000: return f"{round(v/1_000_000_000, 2)} B"
        if v >= 1_000_000:     return f"{round(v/1_000_000, 2)} M"
        if v >= 1_000:         return f"{round(v/1_000, 1)} K"
        return str(round(v, 2))
    def _get(*keys):
        """Tenta vários campos até encontrar um valor válido (não None, não 0)."""
        for k in keys:
            v = info.get(k)
            if v and v != 0 and v != 0.0:
                return v
        return None

    net_debt = None
    total_debt = info.get('totalDebt')
    total_cash = info.get('totalCash')
    if total_debt and total_cash:
        net_debt = total_debt - total_cash

    stats = {
        # Preço
        'price':        round(price, 2) if price else '—',
        'change_pct':   change_pct,
        'currency':     info.get('currency', ''),
        'name':         info.get('shortName', symbol_yf),
        'long_name':    info.get('longName', ''),
        'sector':       info.get('sector', '—'),
        'industry':     info.get('industry', '—'),
        # Preço / dia / 52w — múltiplos fallbacks para ações BR
        'week52_low':    _r2(_get('fiftyTwoWeekLow', 'regularMarketDayLow')),
        'week52_high':   _r2(_get('fiftyTwoWeekHigh', 'regularMarketDayHigh')),
        'day_low':       _r2(_get('dayLow', 'regularMarketDayLow')),
        'day_high':      _r2(_get('dayHigh', 'regularMarketDayHigh')),
        'volume':        _fmt(_get('regularMarketVolume', 'volume')),
        'avg_volume':    _fmt(_get('averageVolume', 'averageDailyVolume3Month')),
        # Campos extra sempre disponíveis
        'ask':           _r2(_get('ask')),
        'bid':           _r2(_get('bid')),
        'ma50':          _r2(_get('fiftyDayAverage')),
        'ma200':         _r2(_get('twoHundredDayAverage')),
        'prev_close':    _r2(_get('previousClose')),
        'open_price':    _r2(_get('open', 'regularMarketOpen')),
        # Valuation
        'div_yield':    _pct(info.get('dividendYield')),
        'pe_ratio':     _r2(info.get('trailingPE')),
        'forward_pe':   _r2(info.get('forwardPE')),
        'pb_ratio':     _r2(info.get('priceToBook')),
        'ps_ratio':     _r2(info.get('priceToSalesTrailing12Months')),
        'ev_ebitda':    _r2(info.get('enterpriseToEbitda')),
        'ev_revenue':   _r2(info.get('enterpriseToRevenue')),
        'eps':          _r2(info.get('trailingEps')),
        'book_value':   _r2(info.get('bookValue')),
        'peg_ratio':    _r2(info.get('pegRatio')),
        # Eficiência (margens)
        'gross_margin':  _pct(info.get('grossMargins')),
        'ebitda_margin': _pct(info.get('ebitdaMargins')),
        'op_margin':     _pct(info.get('operatingMargins')),
        'net_margin':    _pct(info.get('profitMargins')),
        # Rentabilidade
        'roe':   _pct(info.get('returnOnEquity')),
        'roa':   _pct(info.get('returnOnAssets')),
        # Endividamento
        'current_ratio': _r2(info.get('currentRatio')),
        'debt_equity':   _r2(info.get('debtToEquity')),
        # Balanço
        'market_cap':        _fmt(info.get('marketCap')),
        'enterprise_value':  _fmt(info.get('enterpriseValue')),
        'total_debt':        _fmt(total_debt),
        'total_cash':        _fmt(total_cash),
        'net_debt':          _fmt(net_debt),
        'shares':            _fmt(info.get('sharesOutstanding')),
        # Crescimento
        'rev_growth':  _pct(info.get('revenueGrowth')),
        'earn_growth': _pct(info.get('earningsGrowth')),
        'revenue':     _fmt(info.get('totalRevenue')),
        'ebitda':      _fmt(info.get('ebitda')),
        'free_cash':   _fmt(info.get('freeCashflow')),
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


@login_required
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

@login_required
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


@login_required
def stock_set_thresholds(request, pk):
    from decimal import Decimal, InvalidOperation
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        try:
            high = Decimal(request.POST.get('threshold_high', '').replace(',', '.'))
            low  = Decimal(request.POST.get('threshold_low',  '').replace(',', '.'))
            if high <= 0 or low <= 0:
                messages.error(request, 'Os limiares devem ser maiores que 0%.')
            elif high > 100 or low > 100:
                messages.error(request, 'Os limiares não podem ultrapassar 100%.')
            else:
                stock.threshold_high = high
                stock.threshold_low  = low
                stock.save()
                messages.success(request, f'Alertas de {stock.display_symbol()} atualizados: ▲{high}% / ▼{low}%.')
        except (InvalidOperation, ValueError):
            messages.error(request, 'Valores inválidos.')
    return redirect('stock_list')


@login_required
def stock_remove(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    messages.success(request, f"{stock.symbol} removido.")
    return redirect('stock_list')


@login_required
def stock_toggle(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.is_active = not stock.is_active
    stock.save()
    estado = 'ativado' if stock.is_active else 'pausado'
    messages.success(request, f"{stock.symbol} {estado}.")
    return redirect('stock_list')


@login_required
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


@login_required
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


@login_required
def test_ntfy(request):
    import requests as _requests
    s = UserSettings.objects.first() or UserSettings.objects.create()
    if not s.ntfy_topic:
        messages.error(request, 'Configura primeiro um tópico ntfy.sh nas Configurações.')
        return redirect('settings')
    try:
        resp = _requests.post(
            f"https://ntfy.sh/{s.ntfy_topic}",
            data='✅ Teste TRT Invest — sistema de alertas a funcionar!'.encode('utf-8'),
            headers={"Title": "TRT - Teste", "Priority": "default", "Tags": "white_check_mark"},
            timeout=5,
        )
        resp.raise_for_status()
        messages.success(request, f'Notificação enviada para ntfy.sh/{s.ntfy_topic}.')
    except Exception as e:
        messages.error(request, f'Erro ao enviar notificação: {e}')
    return redirect('settings')


@login_required
def test_email(request):
    s = UserSettings.objects.first() or UserSettings.objects.create()
    if not s.email_enabled or not s.email_address:
        messages.error(request, 'Ativa e configura o email nas Configurações antes de testar.')
        return redirect('settings')
    try:
        from django.core.mail import EmailMessage, get_connection
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password,
            use_tls=True,
            fail_silently=False,
        )
        msg = EmailMessage(
            'TRT — Teste de alertas por email',
            '✅ Sistema de alertas por email a funcionar!\n\n—\nTRT Monitor',
            s.smtp_user,
            [s.email_address],
            connection=connection,
        )
        msg.send()
        messages.success(request, f'Email de teste enviado para {s.email_address}.')
    except Exception as e:
        messages.error(request, f'Erro ao enviar email: {e}')
    return redirect('settings')


@login_required
def alert_history(request):
    alerts = Alert.objects.select_related('stock').all()[:100]
    return render(request, 'monitor/alert_history.html', {'alerts': alerts})


@login_required
@login_required
def search_suggest(request):
    import requests as req
    from django.http import JsonResponse
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    try:
        url  = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=pt&region=BR&quotesCount=8&newsCount=0"
        resp = req.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=4)
        data = resp.json()
        results = []
        for item in data.get('quotes', [])[:8]:
            symbol = item.get('symbol', '')
            if not symbol:
                continue
            results.append({
                'symbol':   symbol,
                'name':     item.get('shortname') or item.get('longname', symbol),
                'tipo':     item.get('quoteType', ''),
                'exchange': item.get('exchange', ''),
                'url':      f"/ativo/{symbol}/",
            })
        return JsonResponse({'results': results})
    except Exception:
        return JsonResponse({'results': []})


@login_required
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