"""
Unit tests — REQ-6 (Percentage variation calculation)
              REQ-8 (Evitar notificações duplicadas — already_alerted)

Maps to docs/unit_test_report.md UT-09 … UT-14
"""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from monitor.services import calculate_variation, already_alerted
from monitor.models import Stock, Alert


class TestCalculateVariation(TestCase):
    """REQ-6 AC-2, AC-3 — Variation is calculated correctly and handles edge cases."""

    def test_UT09_happy_positive_variation(self):
        """UT-09 Happy — 100→110 should return +10.00% rounded to 2 d.p. (REQ-6 AC-2)"""
        result = calculate_variation(Decimal("100"), Decimal("110"))
        self.assertEqual(result, Decimal("10.00"))

    def test_UT10_happy_negative_variation(self):
        """UT-10 Happy — 200→150 should return -25.00% rounded to 2 d.p. (REQ-6 AC-2)"""
        result = calculate_variation(Decimal("200"), Decimal("150"))
        self.assertEqual(result, Decimal("-25.00"))

    def test_UT11_boundary_old_price_zero_returns_zero(self):
        """UT-11 Boundary — old_price=0 must return 0.00 without ZeroDivisionError (REQ-6 AC-3)"""
        result = calculate_variation(Decimal("0"), Decimal("100"))
        self.assertEqual(result, Decimal("0.00"))


# ── REQ-8: Evitar notificações duplicadas ────────────────────────────────────

class TestAlreadyAlerted(TestCase):
    """REQ-8 AC-1, AC-2 — already_alerted() blocks duplicates within 60-min window."""

    def setUp(self):
        self.stock = Stock.objects.create(symbol="AAPL", tipo="stock_us")

    def test_UT12_happy_no_alerts_returns_false(self):
        """UT-12 Happy — no alerts in DB → already_alerted() returns False (REQ-8 AC-1)"""
        result = already_alerted(self.stock, "high")
        self.assertFalse(result)

    def test_UT13_negative_alert_within_30min_returns_true(self):
        """UT-13 Negative — alert sent 30 min ago → already_alerted() returns True (REQ-8 AC-1, AC-2)"""
        Alert.objects.create(
            stock=self.stock,
            direction="high",
            variation=Decimal("5.00"),
            price=Decimal("105.00"),
            sent_at=timezone.now() - timedelta(minutes=30),
        )
        result = already_alerted(self.stock, "high")
        self.assertTrue(result)

    def test_UT14_happy_alert_older_than_60min_returns_false(self):
        """UT-14 Alternative — alert sent 61 min ago → window expired, returns False (REQ-8 AC-3)"""
        Alert.objects.create(
            stock=self.stock,
            direction="high",
            variation=Decimal("5.00"),
            price=Decimal("105.00"),
            sent_at=timezone.now() - timedelta(minutes=61),
        )
        result = already_alerted(self.stock, "high")
        self.assertFalse(result)
