"""
Unit tests — REQ-1 (Symbol normalisation & duplicate rejection)
            REQ-3 (Monitoring interval validation)

Maps to docs/unit_test_report.md UT-01 … UT-08
"""

import pytest
from django.test import TestCase
from monitor.forms import StockForm, SettingsForm
from monitor.models import Stock


# ── REQ-1: Cadastro de ações ─────────────────────────────────────────────────

class TestSymbolNormalisation(TestCase):
    """REQ-1 AC-2 — Symbol is normalised automatically based on asset type."""

    def _make_form(self, symbol, tipo, name="Test"):
        return StockForm(data={"symbol": symbol, "tipo": tipo, "name": name})

    def test_UT01_happy_br_stock_appends_sa(self):
        """UT-01 Happy — PETR4 + tipo=stock_br → PETR4.SA (REQ-1 AC-2)"""
        form = self._make_form("PETR4", "stock_br")
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data["symbol"], "PETR4.SA")

    def test_UT02_happy_fii_appends_sa(self):
        """UT-02 Happy — HGLG11 + tipo=fii → HGLG11.SA (REQ-1 AC-2)"""
        form = self._make_form("HGLG11", "fii")
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data["symbol"], "HGLG11.SA")

    def test_UT03_happy_us_stock_no_suffix(self):
        """UT-03 Happy — AAPL + tipo=stock_us → AAPL (no suffix added) (REQ-1 AC-2)"""
        form = self._make_form("AAPL", "stock_us")
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data["symbol"], "AAPL")


class TestSymbolDuplicateRejection(TestCase):
    """REQ-1 AC-3 — System rejects a symbol that already exists."""

    def setUp(self):
        Stock.objects.create(symbol="MSFT", tipo="stock_us")

    def test_UT04_negative_duplicate_symbol_rejected(self):
        """UT-04 Negative — MSFT already in list → ValidationError (REQ-1 AC-3)"""
        form = StockForm(data={"symbol": "MSFT", "tipo": "stock_us", "name": "Microsoft"})
        self.assertFalse(form.is_valid())
        self.assertIn("symbol", form.errors)
        self.assertIn("MSFT", form.errors["symbol"][0])


# ── REQ-3: Configurar intervalo de monitorização ─────────────────────────────

class TestMonitoringIntervalValidation(TestCase):
    """REQ-3 AC-1, AC-3 — Interval must be between 1 and 3600 seconds."""

    def _make_form(self, interval):
        return SettingsForm(data={
            "monitoring_interval": interval,
            "ntfy_topic": "",
            "email_enabled": False,
            "email_address": "",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": "",
        })

    def test_UT05_boundary_min_accepted(self):
        """UT-05 Boundary — interval=1 (lower bound) is accepted (REQ-3 AC-1)"""
        form = self._make_form(1)
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data["monitoring_interval"], 1)

    def test_UT06_boundary_max_accepted(self):
        """UT-06 Boundary — interval=3600 (upper bound) is accepted (REQ-3 AC-1)"""
        form = self._make_form(3600)
        self.assertTrue(form.is_valid(), f"Erros: {form.errors}")
        self.assertEqual(form.cleaned_data["monitoring_interval"], 3600)

    def test_UT07_negative_zero_rejected(self):
        """UT-07 Negative — interval=0 is rejected with an error message (REQ-3 AC-3)"""
        form = self._make_form(0)
        self.assertFalse(form.is_valid())
        self.assertIn("monitoring_interval", form.errors)
        self.assertIn("Entre 1 e 3600 segundos.", form.errors["monitoring_interval"])

    def test_UT08_negative_above_max_rejected(self):
        """UT-08 Negative — interval=3601 is rejected with an error message (REQ-3 AC-3)"""
        form = self._make_form(3601)
        self.assertFalse(form.is_valid())
        self.assertIn("monitoring_interval", form.errors)
        self.assertIn("Entre 1 e 3600 segundos.", form.errors["monitoring_interval"])
