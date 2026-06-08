# Traceability Master — Lab 14 (REQ → AC → Tests → Evidence)

**Versão:** 1.0  
**Data:** 2026-06-08  
**Projeto:** TRT Invest — Monitorização de Ativos Financeiros

---

| REQ | Descrição | AC | Test Case (TC) | Unit Test (UT/T) | BDD Scenario | Evidence | Notas |
|-----|-----------|----|----|----|----|----|----|
| REQ-1 | Cadastro de ações | AC-1, AC-2, AC-3, AC-4, AC-5 | TC-001, TC-002 | UT-01, UT-02, UT-03, UT-04 | "Add a valid US stock" / "Reject duplicate" | `tests/unit/test_validations.py` | ✓ Totalmente coberto |
| REQ-2 *(variant)* | Obter cotações (retry/fallback) | AC-retry, AC-fallback | TC-009, TC-010 | — | "API retries 3 times" / "No price stored on fallback" | `bdd/features/lab9.feature` | Variante retry vs fallback |
| REQ-3 | Configurar intervalo de monitorização | AC-1, AC-3, AC-4 | TC-003 | UT-05, UT-06, UT-07, UT-08 | "Monitoring interval accepts min/max" / "outside range rejected" | `tests/unit/test_validations.py` | ✓ Totalmente coberto |
| REQ-4 *(variant)* | Limiar de alta por ativo | AC-1 (alta ≥ limiar → alerta), AC-2 (rejeita valor inválido) | — | — | "Alert generated when high threshold exceeded" / "No alert below threshold" | `bdd/features/thresholds_and_search.feature` | Gap: sem TC nem UT dedicados (Lab 14) |
| REQ-5 | Limiar de baixa por ativo | AC-1, AC-2, AC-3 | — | — | "Alert generated when low threshold exceeded" / "Invalid threshold rejected" | `bdd/features/thresholds_and_search.feature` | Gap: sem TC nem UT (Lab 14) |
| REQ-6 | Cálculo de variação percentual | AC-1, AC-2, AC-3 | — | UT-09, UT-10, UT-11 / T-01, T-02, T-03, T-04 | — | `tests/unit/test_services.py`, `monitor/tests.py` | Sem TC formal; sem BDD |
| REQ-7 | Envio de notificações push (ntfy.sh) | AC-1, AC-2, AC-3, AC-4, AC-5 | TC-004, TC-005 | — | "Push notification sent" / "No notification when ntfy_topic empty" | `bdd/features/lab9.feature` | ✓ Bem coberto |
| REQ-8 *(NFR, variant)* | Evitar notificações duplicadas (60 min) | AC-1, AC-2, AC-3 | TC-006, TC-007 | UT-12, UT-13, UT-14 / T-09, T-10, T-11, T-12 | "Duplicate blocked within 60 min" / "Allowed after 60 min" | `tests/unit/test_services.py`, `bdd/features/lab9.feature` | NFR variant-driven ✓ |
| REQ-9 | Histórico de alertas | AC-1, AC-2, AC-3 | TC-008 | — | "Alert history is accessible and complete" | `bdd/features/lab9.feature` | ✓ Coberto |
| REQ-13 *(NFR, variant)* | Tempo de resposta / robustez (timeout/retry) | AC-1, AC-2, AC-3, AC-4 | TC-009, TC-010 | — | "API retries exactly 3 times" / "Fallback" | `bdd/features/lab9.feature` | NFR variant-driven; partilha TC com REQ-2 |
| REQ-15 | Autenticação de utilizadores | AC-1, AC-2, AC-3, AC-4 | TC-011, TC-012 | — | "Login using email" / "Login rejected" / "Guest user" | `bdd/features/lab9.feature` | AC-1 (registo) sem TC dedicado |
| REQ-16 | Pesquisa de ativos | AC-1, AC-2, AC-3, AC-4 | — | — | "Search returns results" / "Autocomplete" / "Autocomplete < 2 chars" | `bdd/features/thresholds_and_search.feature` | Gap resolvido no Lab 14 |
| REQ-17 | Visão geral do mercado | AC-1, AC-2, AC-3, AC-4, AC-5 | — | — | — | Manual | Gap: sem cobertura automatizada |

---

## Resumo de Cobertura

| Categoria | Total REQs | Com TC | Com UT | Com BDD | Totalmente coberto |
|-----------|-----------|--------|--------|---------|-------------------|
| Funcionais (FR) | 11 | 7 | 4 | 10 | 6 |
| Não Funcionais (NFR) | 2 | 2 | 1 | 2 | 2 |
| **Total** | **13** | **9** | **5** | **12** | **8** |

**Cobertura com pelo menos 1 tipo de teste automatizado: 12/13 REQs (92%)**  
**REQ sem nenhuma cobertura automatizada: REQ-17** (dados de mercado externos, difíceis de mockar)
