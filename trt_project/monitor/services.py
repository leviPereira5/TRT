import yfinance as yf
import math
import logging
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from django.conf import settings as django_settings
from django.core.cache import cache
from .models import Stock, StockPrice, Alert, UserSettings

logger = logging.getLogger(__name__)

FEATURED_US = ['AAPL','MSFT','GOOGL','AMZN','TSLA','NVDA','META','BRK-B']

_YF_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

TOP_BR_LIST = [
    'PETR4.SA','VALE3.SA','ITUB4.SA','BBDC4.SA','ABEV3.SA','WEGE3.SA',
    'RENT3.SA','RAIL3.SA','SUZB3.SA','RADL3.SA','PRIO3.SA','BBAS3.SA',
    'B3SA3.SA','LREN3.SA','MGLU3.SA','VIVT3.SA','HAPV3.SA','RDOR3.SA',
    'EQTL3.SA','CSAN3.SA',
]

TOP_FIIS_LIST = [
    'HGLG11.SA','XPML11.SA','KNRI11.SA','MXRF11.SA','VISC11.SA',
    'BRCO11.SA','GGRC11.SA','HSML11.SA','MALL11.SA','RBRR11.SA',
    'TGAR11.SA','XPLG11.SA','BTLG11.SA','KNCR11.SA','PVBI11.SA',
    'VGHF11.SA','IRDM11.SA','RBVA11.SA','CSHG11.SA','HFOF11.SA',
]

TOP_CRYPTO_LIST = [
    'BTC-USD','ETH-USD','BNB-USD','XRP-USD','SOL-USD','ADA-USD',
    'DOGE-USD','AVAX-USD','DOT-USD','MATIC-USD','LINK-USD','LTC-USD',
    'UNI-USD','ATOM-USD','XLM-USD','NEAR-USD','ALGO-USD','ICP-USD',
    'SHIB-USD','TRX-USD',
]

TOP_EU_LIST = [
    'ASML.AS','MC.PA','SAP.DE','NESN.SW','NOVN.SW','TTE.PA','SIE.DE','BMW.DE',
    'ADS.DE','AIR.PA','BNP.PA','OR.PA','RMS.PA','ITX.MC','IBE.MC',
    'ENEL.MI','ENI.MI','IFX.DE','DTE.DE','PHIA.AS',
]

TOP_CN_LIST = [
    '0700.HK','9988.HK','3690.HK','9618.HK','1211.HK',
    '0005.HK','2318.HK','0941.HK','2382.HK','1299.HK',
    '0388.HK','9999.HK','2269.HK','3988.HK','0762.HK',
]

# ETFs B3 que aproximam os índices do Tesouro Direto
TESOURO_ETFS = [
    {'nome': 'Tesouro IPCA+',      'etf': 'IMAB11.SA', 'tipo': 'IPCA+',      'desc': 'Protegido contra inflação'},
    {'nome': 'Tesouro Prefixado',   'etf': 'B5P211.SA', 'tipo': 'Prefixado',  'desc': 'Taxa fixa pré-definida'},
    {'nome': 'Tesouro SELIC',       'etf': 'TESD11.SA', 'tipo': 'SELIC',      'desc': 'Acompanha a taxa SELIC'},
    {'nome': 'Tesouro IGPM+',       'etf': 'XFIX11.SA', 'tipo': 'IGP-M+',     'desc': 'Indexado ao IGP-M'},
]
FEATURED_BR     = ['PETR4.SA','VALE3.SA','ITUB4.SA','BBDC4.SA','ABEV3.SA','WEGE3.SA']
FEATURED_FII    = ['HGLG11.SA','XPML11.SA','KNRI11.SA','MXRF11.SA','VISC11.SA']
FEATURED_CRYPTO = ['BTC-USD','ETH-USD','SOL-USD','BNB-USD','XRP-USD','ADA-USD','AVAX-USD','DOGE-USD']
FEATURED_EU     = ['ASML.AS','MC.PA','SAP.DE','NESN.SW','TTE.PA','SIE.DE','BMW.DE','AIR.PA']
FEATURED_CN     = ['0700.HK','9988.HK','3690.HK','9618.HK','1211.HK','0005.HK','2318.HK','0941.HK']
FEATURED_ETF    = ['SPY','QQQ','VTI','EFA','GLD','TLT','VWO','ARKK']

def _screener_to_item(q):
    price      = q.get('regularMarketPrice', 0)
    change_pct = q.get('regularMarketChangePercent', 0)
    symbol     = q.get('symbol', '')
    return {
        'symbol':     symbol.replace('.SA', '').replace('-USD', ''),
        'symbol_yf':  symbol,
        'name':       q.get('shortName') or q.get('longName', symbol),
        'price':      round(float(price), 2) if price else '—',
        'change_pct': round(float(change_pct), 2),
        'currency':   q.get('currency', 'USD'),
    }


def fetch_top_movers():
    import requests
    cached = cache.get('top_movers')
    if cached:
        return cached

    def _us_top():
        try:
            url  = ('https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved'
                    '?scrIds=day_gainers&count=10&formatted=false&lang=en-US&region=US')
            data = requests.get(url, headers=_YF_HEADERS, timeout=6).json()
            quotes = data['finance']['result'][0]['quotes']
            return [_screener_to_item(q) for q in quotes if q.get('symbol')]
        except Exception as e:
            logger.warning(f"US top movers: {e}")
            return []

    def _br_top():
        indexed = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(TOP_BR_LIST)}
            for future in as_completed(futures):
                r = future.result()
                if r:
                    indexed[futures[future]] = r
        return sorted(indexed.values(), key=lambda x: x.get('change_pct', 0), reverse=True)[:10]

    def _fii_top():
        indexed = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(TOP_FIIS_LIST)}
            for future in as_completed(futures):
                r = future.result()
                if r:
                    indexed[futures[future]] = r
        items = sorted(indexed.values(), key=lambda x: x.get('change_pct', 0), reverse=True)
        return items[:10]

    def _crypto_top():
        indexed = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(TOP_CRYPTO_LIST)}
            for future in as_completed(futures):
                r = future.result()
                if r:
                    indexed[futures[future]] = r
        items = sorted(indexed.values(), key=lambda x: x.get('change_pct', 0), reverse=True)
        return items[:10]

    def _eu_top():
        indexed = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(TOP_EU_LIST)}
            for future in as_completed(futures):
                r = future.result()
                if r:
                    indexed[futures[future]] = r
        return sorted(indexed.values(), key=lambda x: x.get('change_pct', 0), reverse=True)[:10]

    def _cn_top():
        indexed = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(TOP_CN_LIST)}
            for future in as_completed(futures):
                r = future.result()
                if r:
                    indexed[futures[future]] = r
        return sorted(indexed.values(), key=lambda x: x.get('change_pct', 0), reverse=True)[:10]

    with ThreadPoolExecutor(max_workers=6) as ex:
        fu = ex.submit(_us_top)
        fb = ex.submit(_br_top)
        ff = ex.submit(_fii_top)
        fc = ex.submit(_crypto_top)
        fe = ex.submit(_eu_top)
        fn = ex.submit(_cn_top)
        result = {
            'us': fu.result(), 'br': fb.result(),
            'fii': ff.result(), 'crypto': fc.result(),
            'eu': fe.result(), 'cn': fn.result(),
        }

    cache.set('top_movers', result, 300)
    return result


def fetch_price(symbol):
    for attempt in range(3):
        try:
            ticker = yf.Ticker(symbol)
            info   = ticker.info
            price  = (
                info.get("regularMarketPrice") or
                info.get("currentPrice") or
                info.get("previousClose")
            )
            if price and not (isinstance(price, float) and (math.isnan(price) or math.isinf(price))):
                return Decimal(str(price))
        except Exception as e:
            logger.warning(f"Tentativa {attempt+1} falhou para {symbol}: {e}")
    return None

def _fetch_single(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info
        price  = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
        prev   = info.get("previousClose")
        change_pct = round(((price - prev) / prev) * 100, 2) if price and prev else 0
        try:
            hist  = ticker.history(period='10d', interval='1d')['Close'].dropna().tolist()
            spark = [round(p, 4) for p in hist] if len(hist) >= 2 else []
        except Exception:
            spark = []
        return {
            'symbol':     symbol.replace('.SA', '').replace('-USD', ''),
            'symbol_yf':  symbol,
            'name':       info.get('shortName', symbol),
            'price':      round(price, 2) if price else '—',
            'change_pct': change_pct,
            'currency':   info.get('currency', ''),
            'logo_url':   info.get('logo_url', ''),
            'spark':      spark,
        }
    except Exception as e:
        logger.warning(f"Erro ao obter {symbol}: {e}")
        return None


def _fetch_group(symbols, _categoria=None):
    indexed = {}
    with ThreadPoolExecutor(max_workers=min(len(symbols), 8)) as ex:
        futures = {ex.submit(_fetch_single, s): i for i, s in enumerate(symbols)}
        for future in as_completed(futures):
            r = future.result()
            if r:
                indexed[futures[future]] = r
    return [indexed[i] for i in sorted(indexed)]

def fetch_taxas_bcb():
    import requests
    cached = cache.get('taxas_bcb')
    if cached:
        return cached

    series = {
        'selic': (432,  'Meta SELIC',  '% a.a.'),
        'ipca':  (433,  'IPCA',        '% mês'),
        'cdi':   (4389, 'CDI',         '% a.a.'),
    }

    def _fetch_serie(chave, codigo, nome, unidade):
        try:
            url  = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/1?formato=json"
            data = requests.get(url, timeout=5).json()
            if data:
                return chave, {'nome': nome, 'valor': data[0]['valor'], 'data': data[0]['data'], 'unidade': unidade}
        except Exception:
            pass
        return chave, None

    taxas = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(_fetch_serie, k, c, n, u) for k, (c, n, u) in series.items()]
        for f in as_completed(futures):
            chave, valor = f.result()
            taxas[chave] = valor

    cache.set('taxas_bcb', taxas, 1800)
    return taxas


def _fetch_tesouro_single(item):
    entry = dict(item)
    try:
        info  = yf.Ticker(item['etf']).info
        price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
        prev  = info.get('previousClose')
        entry['price']      = round(price, 2) if price else None
        entry['change_pct'] = round(((price - prev) / prev) * 100, 2) if price and prev else 0
        entry['disponivel'] = True
    except Exception:
        entry['price']      = None
        entry['change_pct'] = 0
        entry['disponivel'] = False
    return entry


def fetch_tesouro():
    cached = cache.get('tesouro')
    if cached:
        return cached
    with ThreadPoolExecutor(max_workers=len(TESOURO_ETFS)) as ex:
        result = list(ex.map(_fetch_tesouro_single, TESOURO_ETFS))
    cache.set('tesouro', result, 300)
    return result


def fetch_market_overview():
    cached = cache.get('market_overview')
    if cached:
        return cached
    with ThreadPoolExecutor(max_workers=7) as ex:
        f_us     = ex.submit(_fetch_group, FEATURED_US)
        f_br     = ex.submit(_fetch_group, FEATURED_BR)
        f_fii    = ex.submit(_fetch_group, FEATURED_FII)
        f_crypto = ex.submit(_fetch_group, FEATURED_CRYPTO)
        f_eu     = ex.submit(_fetch_group, FEATURED_EU)
        f_cn     = ex.submit(_fetch_group, FEATURED_CN)
        f_etf    = ex.submit(_fetch_group, FEATURED_ETF)
        result = {
            'us':     f_us.result(),
            'br':     f_br.result(),
            'fii':    f_fii.result(),
            'crypto': f_crypto.result(),
            'eu':     f_eu.result(),
            'cn':     f_cn.result(),
            'etf':    f_etf.result(),
        }
    cache.set('market_overview', result, 300)
    return result

def get_last_price(stock):
    last = stock.prices.first()
    return last.price if last else None

def calculate_variation(old_price, new_price):
    if old_price == 0:
        return Decimal("0.00")
    return ((new_price - old_price) / old_price * 100).quantize(Decimal("0.01"))

def already_alerted(stock, direction):
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(minutes=60)
    return Alert.objects.filter(stock=stock, direction=direction, sent_at__gte=cutoff).exists()

def send_ntfy_notification(alert, settings):
    if not settings.ntfy_topic:
        return
    try:
        import requests as _requests
        emoji     = '📈' if alert.direction == 'high' else '📉'
        direction = 'Alta' if alert.direction == 'high' else 'Baixa'
        tag       = 'chart_with_upwards_trend' if alert.direction == 'high' else 'chart_with_downwards_trend'
        _requests.post(
            f"https://ntfy.sh/{settings.ntfy_topic}",
            data=(
                f"{emoji} {alert.stock.symbol} {direction} {alert.variation:+}%\n"
                f"Preço: {alert.price}\n"
                f"{alert.sent_at.strftime('%d/%m/%Y %H:%M:%S')}"
            ).encode('utf-8'),
            headers={
                "Title":    f"TRT Alerta - {alert.stock.symbol} {direction}",
                "Priority": "high",
                "Tags":     tag,
            },
            timeout=5,
        )
        alert.email_sent = True
        alert.save()
        logger.info(f"Notificação ntfy enviada: {alert.stock.symbol} {direction}")
    except Exception as e:
        logger.error(f"Erro ao enviar notificação ntfy: {e}")

def send_email_notification(alert, settings):
    if not settings.email_enabled or not settings.email_address or not settings.smtp_user or not settings.smtp_password:
        return
    try:
        from django.core.mail import EmailMessage, get_connection
        direction = 'Alta' if alert.direction == 'high' else 'Baixa'
        emoji     = '📈' if alert.direction == 'high' else '📉'
        subject   = f"TRT Alerta — {alert.stock.symbol} {direction} {alert.variation:+.2f}%"
        body      = (
            f"{emoji} {alert.stock.name or alert.stock.symbol} — {direction}\n\n"
            f"Variação: {alert.variation:+.2f}%\n"
            f"Preço atual: {alert.price}\n"
            f"Data/Hora: {alert.sent_at.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"—\nTRT Monitor"
        )
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=True,
            fail_silently=False,
        )
        msg = EmailMessage(subject, body, settings.smtp_user, [settings.email_address], connection=connection)
        msg.send()
        logger.info(f"Email de alerta enviado: {alert.stock.symbol} {direction} → {settings.email_address}")
    except Exception as e:
        logger.error(f"Erro ao enviar email de alerta: {e}")

def check_and_alert(stock, variation, new_price, settings):
    if variation >= stock.threshold_high:
        direction = 'high'
    elif variation <= -stock.threshold_low:
        direction = 'low'
    else:
        return None
    if already_alerted(stock, direction):
        return None
    alert = Alert.objects.create(
        stock=stock, direction=direction,
        variation=variation, price=new_price, notified=True
    )
    send_ntfy_notification(alert, settings)
    send_email_notification(alert, settings)
    return alert

def monitor_stock(stock, settings):
    new_price = fetch_price(stock.symbol)
    if new_price is None:
        new_price = get_last_price(stock)
        if new_price is None:
            return {'symbol': stock.symbol, 'error': 'Sem dados'}
        return {'symbol': stock.symbol, 'price': new_price, 'fallback': True}
    old_price = stock.prices.first()
    old_price = old_price.price if old_price else new_price
    StockPrice.objects.create(stock=stock, price=new_price)
    variation = calculate_variation(old_price, new_price)
    alert     = check_and_alert(stock, variation, new_price, settings)
    return {
        'symbol':    stock.symbol,
        'price':     new_price,
        'old_price': old_price,
        'variation': variation,
        'alert':     alert,
    }

def run_monitoring_cycle():
    settings = UserSettings.objects.first() or UserSettings.objects.create()
    results  = []
    for stock in Stock.objects.filter(is_active=True):
        results.append(monitor_stock(stock, settings))
    return results
