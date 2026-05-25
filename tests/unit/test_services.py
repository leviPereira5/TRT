"""
Unit tests — REQ-6 (Percentage variation calculation)

Maps to docs/unit_test_report.md UT-09 … UT-11
"""

from decimal import Decimal
from django.test import TestCase
from monitor.services import calculate_variation


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
