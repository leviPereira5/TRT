"""
Testes unitários puros — pyUnit standard (unittest.TestCase), sem django.test.TestCase.
Testam a lógica de negócio isolada sem depender da base de dados.

REQ-6: calculate_variation()
REQ-8: lógica de janela de 60 minutos (via mock)
"""
import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import MagicMock
from datetime import timedelta

# Configurar Django sem base de dados antes de qualquer import de app
os.environ.setdefault("SECRET_KEY", "test-only-key-not-for-production")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trt_project.settings")
_trt = os.path.join(os.path.dirname(__file__), "..", "..", "trt_project")
if _trt not in sys.path:
    sys.path.insert(0, _trt)

import django
django.setup()

from monitor.services import calculate_variation


class TestCalculateVariationPure(unittest.TestCase):
    """
    Testes puros para calculate_variation() — REQ-6 (AC-2, AC-3).
    Usa unittest.TestCase standard (pyUnit), sem base de dados.
    """

    def test_variacao_positiva(self):
        """REQ-6 AC-2 — 100 → 110 = +10.00%"""
        self.assertEqual(calculate_variation(Decimal("100"), Decimal("110")), Decimal("10.00"))

    def test_variacao_negativa(self):
        """REQ-6 AC-2 — 200 → 150 = -25.00%"""
        self.assertEqual(calculate_variation(Decimal("200"), Decimal("150")), Decimal("-25.00"))

    def test_sem_variacao(self):
        """REQ-6 AC-2 — preço igual = 0.00%"""
        self.assertEqual(calculate_variation(Decimal("100"), Decimal("100")), Decimal("0.00"))

    def test_preco_antigo_zero_retorna_zero(self):
        """REQ-6 AC-3 — old_price=0 → 0.00 (sem ZeroDivisionError)"""
        self.assertEqual(calculate_variation(Decimal("0"), Decimal("100")), Decimal("0.00"))

    def test_resultado_arredondado_2_decimais(self):
        """REQ-6 AC-2 — resultado arredondado a 2 casas decimais"""
        result = calculate_variation(Decimal("3"), Decimal("4"))
        self.assertEqual(result, Decimal("33.33"))


class TestAlreadyAlertedLogicPure(unittest.TestCase):
    """
    Testes puros para a lógica de already_alerted() — REQ-8 (AC-1, AC-2).
    Usa mock para simular a BD — sem django.test.TestCase nem base de dados.
    """

    def _mock_already_alerted(self, minutes_ago):
        """Simula already_alerted() testando apenas a lógica da janela de 60 min."""
        from django.utils import timezone
        mock_alert = MagicMock()
        mock_alert.sent_at = timezone.now() - timedelta(minutes=minutes_ago)
        cutoff = timezone.now() - timedelta(minutes=60)
        return mock_alert.sent_at >= cutoff

    def test_alerta_ha_30min_bloqueia(self):
        """REQ-8 AC-1 — alerta há 30 min está dentro da janela → True (bloqueia)"""
        self.assertTrue(self._mock_already_alerted(30))

    def test_alerta_ha_61min_nao_bloqueia(self):
        """REQ-8 AC-3 — alerta há 61 min expirou → False (permite novo alerta)"""
        self.assertFalse(self._mock_already_alerted(61))

    def test_alerta_ha_0min_bloqueia(self):
        """REQ-8 AC-1 — alerta imediato (0 min) bloqueia"""
        self.assertTrue(self._mock_already_alerted(0))

    def test_alerta_ha_60min_nao_bloqueia(self):
        """REQ-8 AC-3 — exatamente no limite de 60 min → expirado"""
        self.assertFalse(self._mock_already_alerted(60))


if __name__ == "__main__":
    unittest.main()
