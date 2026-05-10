from django import forms
from .models import Stock, UserSettings


class StockForm(forms.ModelForm):
    class Meta:
        model  = Stock
        fields = ['symbol', 'name', 'tipo']
        labels = {
            'symbol': 'Símbolo',
            'name':   'Nome',
            'tipo':   'Tipo de ativo',
        }

    def clean_symbol(self):
        symbol = self.cleaned_data['symbol'].upper().strip()
        tipo   = self.cleaned_data.get('tipo', 'stock_us')
        if tipo in ('stock_br', 'fii') and not symbol.endswith('.SA'):
            symbol = symbol + '.SA'
        if Stock.objects.filter(symbol=symbol).exists():
            raise forms.ValidationError(f"{symbol} já está na lista.")
        return symbol


class SettingsForm(forms.ModelForm):
    class Meta:
        model  = UserSettings
        fields = ['monitoring_interval', 'alert_email']
        labels = {
            'monitoring_interval': 'Intervalo (segundos)',
            'alert_email':         'Email para alertas',
        }

    def clean_monitoring_interval(self):
        val = self.cleaned_data['monitoring_interval']
        if not (1 <= val <= 3600):
            raise forms.ValidationError("Entre 1 e 3600 segundos.")
        return val
