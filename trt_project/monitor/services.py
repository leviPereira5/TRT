import yfinance as yf
import math
import logging
from decimal import Decimal
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import Stock, StockPrice, Alert, UserSettings

logger = logging.getLogger(__name__)

FEATURED_US = ['AAPL','MSFT','GOOGL','AMZN','TSLA','NVDA','META','BRK-B']

# ETFs B3 que aproximam os índices do Tesouro Direto
TESOURO_ETFS = [
    {'nome': 'Tesouro IPCA+',      'etf': 'IMAB11.SA', 'tipo': 'IPCA+',      'desc': 'Protegido contra inflação'},
    {'nome': 'Tesouro Prefixado',   'etf': 'B5P211.SA', 'tipo': 'Prefixado',  'desc': 'Taxa fixa pré-definida'},
    {'nome': 'Tesouro SELIC',       'etf': 'TESD11.SA', 'tipo': 'SELIC',      'desc': 'Acompanha a taxa SELIC'},
    {'nome': 'Tesouro IGPM+',       'etf': 'XFIX11.SA', 'tipo': 'IGP-M+',     'desc': 'Indexado ao IGP-M'},
]
FEATURED_BR = ['PETR4.SA','VALE3.SA','ITUB4.SA','BBDC4.SA','ABEV3.SA','WEGE3.SA']
FEATURED_FII = ['HGLG11.SA','XPML11.SA','KNRI11.SA','MXRF11.SA','VISC11.SA']
FEATURED_CRYPTO = ['BTC-USD','ETH-USD','SOL-USD','BNB-USD','XRP-USD','ADA-USD','AVAX-USD','DOGE-USD']

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

def _fetch_group(symbols, categoria):
    result = []
    for symbol in symbols:
        try:
            t     = yf.Ticker(symbol)
            info  = t.info
            price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            prev  = info.get("previousClose")
            change_pct = round(((price - prev) / prev) * 100, 2) if price and prev else 0
            clean = symbol.replace('.SA', '').replace('-USD', '')
            entry = {
                'symbol':     clean,
                'symbol_yf':  symbol,
                'name':       info.get('shortName', symbol),
                'price':      round(price, 2) if price else '—',
                'change_pct': change_pct,
                'currency':   info.get('currency', ''),
                'logo_url':   info.get('logo_url', ''),
            }
            result.append(entry)
        except Exception as e:
            logger.warning(f"Erro ao obter {symbol}: {e}")
    return result

def fetch_taxas_bcb():
    import requests
    series = {
        'selic': (432,  'Meta SELIC',  '% a.a.'),
        'ipca':  (433,  'IPCA',        '% mês'),
        'cdi':   (4389, 'CDI',         '% a.a.'),
    }
    taxas = {}
    for chave, (codigo, nome, unidade) in series.items():
        try:
            url  = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/1?formato=json"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data:
                taxas[chave] = {
                    'nome':    nome,
                    'valor':   data[0]['valor'],
                    'data':    data[0]['data'],
                    'unidade': unidade,
                }
        except Exception:
            taxas[chave] = None
    return taxas


def fetch_tesouro():
    result = []
    for item in TESOURO_ETFS:
        entry = dict(item)
        try:
            t    = yf.Ticker(item['etf'])
            info = t.info
            price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            prev  = info.get('previousClose')
            change_pct = round(((price - prev) / prev) * 100, 2) if price and prev else 0
            entry['price']      = round(price, 2) if price else None
            entry['change_pct'] = change_pct
            entry['disponivel'] = True
        except Exception:
            entry['price']      = None
            entry['change_pct'] = 0
            entry['disponivel'] = False
        result.append(entry)
    return result


def fetch_market_overview():
    return {
        'us':     _fetch_group(FEATURED_US, 'us'),
        'br':     _fetch_group(FEATURED_BR, 'br'),
        'fii':    _fetch_group(FEATURED_FII, 'fii'),
        'crypto': _fetch_group(FEATURED_CRYPTO, 'crypto'),
    }

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

def send_alert_email(alert, settings):
    if not settings.alert_email:
        return
    try:
        emoji     = '📈' if alert.direction == 'high' else '📉'
        direction = 'Alta' if alert.direction == 'high' else 'Baixa'
        send_mail(
            subject=f"{emoji} Alerta TRT — {alert.stock.symbol} {direction} {alert.variation}%",
            message=(
                f"Alerta de {direction} para {alert.stock.symbol}!\n\n"
                f"Variação: {alert.variation:+}%\n"
                f"Preço atual: {alert.price}\n"
                f"Data/Hora: {alert.sent_at.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"— TRT Monitor"
            ),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.alert_email],
            fail_silently=False,
        )
        alert.email_sent = True
        alert.save()
        logger.info(f"Email enviado: {alert.stock.symbol} {direction}")
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")

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
    send_alert_email(alert, settings)
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
