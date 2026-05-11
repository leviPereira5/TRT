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
    smtp_password = forms.CharField(
        label='Password de aplicação',
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={'autocomplete': 'current-password'}),
    )

    class Meta:
        model  = UserSettings
        fields = [
            'monitoring_interval', 'ntfy_topic',
            'email_enabled', 'email_address',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
        ]
        labels = {
            'monitoring_interval': 'Intervalo (segundos)',
            'ntfy_topic':          'Tópico ntfy.sh',
            'email_enabled':       'Ativar alertas por email',
            'email_address':       'Email de destino',
            'smtp_host':           'Servidor SMTP',
            'smtp_port':           'Porta SMTP',
            'smtp_user':           'Email de envio',
        }

    def clean_monitoring_interval(self):
        val = self.cleaned_data['monitoring_interval']
        if not (1 <= val <= 3600):
            raise forms.ValidationError("Entre 1 e 3600 segundos.")
        return val
