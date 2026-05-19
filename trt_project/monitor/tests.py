from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from .models import Stock, Alert, UserSettings
from .services import calculate_variation, already_alerted
from .forms import SettingsForm


# ─── REQ-6: Cálculo de variação percentual ───────────────────────────────────

class TestCalculateVariation(TestCase):

    def test_T01_happy_positive_variation(self):
        """T-01: Variação positiva — 100→105 deve retornar 5.00% (REQ-6 AC-1, AC-2)"""
        result = calculate_variation(Decimal("100"), Decimal("105"))
        self.assertEqual(result, Decimal("5.00"))

    def test_T02_happy_negative_variation(self):
        """T-02: Variação negativa — 100→90 deve retornar -10.00% (REQ-6 AC-1, AC-2)"""
        result = calculate_variation(Decimal("100"), Decimal("90"))
        self.assertEqual(result, Decimal("-10.00"))

    def test_T03_boundary_old_price_zero(self):
        """T-03: Boundary — old_price=0 deve retornar 0.00 sem divisão por zero (REQ-6 AC-3)"""
        result = calculate_variation(Decimal("0"), Decimal("105"))
        self.assertEqual(result, Decimal("0.00"))

    def test_T04_happy_no_variation(self):
        """T-04: Happy — preço igual deve retornar 0.00% (REQ-6 AC-2)"""
        result = calculate_variation(Decimal("100"), Decimal("100"))
        self.assertEqual(result, Decimal("0.00"))


# ─── REQ-3: Configurar intervalo de monitorização ────────────────────────────

class TestMonitoringIntervalValidation(TestCase):

    def _make_form(self, interval):
        return SettingsForm(data={
            'monitoring_interval': interval,
            'ntfy_topic': '',
            'email_enabled': False,
            'email_address': '',
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': '',
            'smtp_password': '',
        })

    def test_T05_boundary_min_value_accepted(self):
        """T-05: Boundary — intervalo=1 deve ser aceite (REQ-3 AC-1, AC-3)"""
        form = self._make_form(1)
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data['monitoring_interval'], 1)

    def test_T06_boundary_max_value_accepted(self):
        """T-06: Boundary — intervalo=3600 deve ser aceite (REQ-3 AC-1, AC-3)"""
        form = self._make_form(3600)
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data['monitoring_interval'], 3600)

    def test_T07_negative_below_min_rejected(self):
        """T-07: Negative — intervalo=0 deve ser rejeitado com erro (REQ-3 AC-3)"""
        form = self._make_form(0)
        self.assertFalse(form.is_valid())
        self.assertIn('monitoring_interval', form.errors)
        self.assertIn("Entre 1 e 3600 segundos.", form.errors['monitoring_interval'])

    def test_T08_negative_above_max_rejected(self):
        """T-08: Negative — intervalo=3601 deve ser rejeitado com erro (REQ-3 AC-3)"""
        form = self._make_form(3601)
        self.assertFalse(form.is_valid())
        self.assertIn('monitoring_interval', form.errors)
        self.assertIn("Entre 1 e 3600 segundos.", form.errors['monitoring_interval'])


# ─── REQ-8: Evitar notificações duplicadas ───────────────────────────────────

class TestAlreadyAlerted(TestCase):

    def setUp(self):
        self.stock = Stock.objects.create(symbol="AAPL", tipo="stock_us")

    def test_T09_happy_no_alerts_in_db(self):
        """T-09: Happy — sem alertas na BD deve retornar False (REQ-8 AC-1, AC-2)"""
        result = already_alerted(self.stock, 'high')
        self.assertFalse(result)

    def test_T10_happy_alert_older_than_60_min(self):
        """T-10: Happy — alerta há 61 minutos deve retornar False (REQ-8 AC-1)"""
        Alert.objects.create(
            stock=self.stock,
            direction='high',
            variation=Decimal("5.00"),
            price=Decimal("105.00"),
            sent_at=timezone.now() - timedelta(minutes=61),
        )
        result = already_alerted(self.stock, 'high')
        self.assertFalse(result)

    def test_T11_negative_alert_within_60_min(self):
        """T-11: Negative — alerta há 30 minutos deve retornar True e bloquear duplicado (REQ-8 AC-1, AC-2)"""
        Alert.objects.create(
            stock=self.stock,
            direction='high',
            variation=Decimal("5.00"),
            price=Decimal("105.00"),
            sent_at=timezone.now() - timedelta(minutes=30),
        )
        result = already_alerted(self.stock, 'high')
        self.assertTrue(result)

    def test_T12_happy_different_direction_not_blocked(self):
        """T-12: Happy — alerta 'high' não deve bloquear alerta 'low' do mesmo ativo (REQ-8 AC-1)"""
        Alert.objects.create(
            stock=self.stock,
            direction='high',
            variation=Decimal("5.00"),
            price=Decimal("105.00"),
            sent_at=timezone.now() - timedelta(minutes=10),
        )
        result = already_alerted(self.stock, 'low')
        self.assertFalse(result)
