from django.db import models
from django.utils import timezone

class Stock(models.Model):
    TIPO_CHOICES = [
        ('stock_us', 'Ação EUA'),
        ('stock_br', 'Ação Brasil'),
        ('fii',      'Fundo Imobiliário'),
        ('crypto',   'Criptomoeda'),
    ]
    symbol         = models.CharField(max_length=15, unique=True)
    name           = models.CharField(max_length=100, blank=True)
    tipo           = models.CharField(max_length=10, choices=TIPO_CHOICES, default='stock_us')
    is_active      = models.BooleanField(default=True)
    added_at       = models.DateTimeField(default=timezone.now)
    threshold_high = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    threshold_low  = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    def display_symbol(self):
        return self.symbol.replace('.SA', '').replace('-USD', '')

    def __str__(self):
        return self.symbol

class UserSettings(models.Model):
    monitoring_interval = models.PositiveIntegerField(default=60)
    ntfy_topic          = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Configurações (intervalo: {self.monitoring_interval}s)"

class StockPrice(models.Model):
    stock      = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    price      = models.DecimalField(max_digits=12, decimal_places=4)
    fetched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fetched_at']

class Alert(models.Model):
    DIRECTION_CHOICES = [('high', 'Alta'), ('low', 'Baixa')]
    stock      = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    direction  = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    variation  = models.DecimalField(max_digits=6, decimal_places=2)
    price      = models.DecimalField(max_digits=12, decimal_places=4)
    sent_at    = models.DateTimeField(default=timezone.now)
    notified   = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
