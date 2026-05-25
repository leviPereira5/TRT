# Unit Test Report — Lab 12

## Selected scope

- **REQ-1** — Cadastro de ações
  - AC automated:
    - AC-2: Sistema normaliza o símbolo automaticamente (.SA para BR/FII)
    - AC-3: Sistema rejeita símbolo já existente na lista

- **REQ-3** — Configurar intervalo de monitorização
  - AC automated:
    - AC-1: Utilizador pode definir intervalo entre 1 e 3600 segundos
    - AC-3: Valores fora do intervalo são rejeitados com mensagem de erro

- **REQ-6** — Cálculo de variação percentual
  - AC automated:
    - AC-2: Fórmula correta, arredondada a 2 casas decimais
    - AC-3: Se não existir preço anterior (old_price=0), variação retorna 0%

---

## Tests implemented

| Test ID | Test name | REQ | AC | Type | Notes |
|---|---|---|---|---|---|
| UT-01 | test_UT01_happy_br_stock_appends_sa | REQ-1 | AC-2 | Happy | PETR4 + stock_br → PETR4.SA |
| UT-02 | test_UT02_happy_fii_appends_sa | REQ-1 | AC-2 | Happy | HGLG11 + fii → HGLG11.SA |
| UT-03 | test_UT03_happy_us_stock_no_suffix | REQ-1 | AC-2 | Happy | AAPL + stock_us → AAPL (sem sufixo) |
| UT-04 | test_UT04_negative_duplicate_symbol_rejected | REQ-1 | AC-3 | Negative | Símbolo duplicado → ValidationError |
| UT-05 | test_UT05_boundary_min_accepted | REQ-3 | AC-1, AC-3 | Boundary | intervalo=1 (limite mínimo) → aceite |
| UT-06 | test_UT06_boundary_max_accepted | REQ-3 | AC-1, AC-3 | Boundary | intervalo=3600 (limite máximo) → aceite |
| UT-07 | test_UT07_negative_zero_rejected | REQ-3 | AC-3 | Negative | intervalo=0 → rejeitado |
| UT-08 | test_UT08_negative_above_max_rejected | REQ-3 | AC-3 | Negative | intervalo=3601 → rejeitado |
| UT-09 | test_UT09_happy_positive_variation | REQ-6 | AC-2 | Happy | 100→110 = +10.00% |
| UT-10 | test_UT10_happy_negative_variation | REQ-6 | AC-2 | Happy | 200→150 = -25.00% |
| UT-11 | test_UT11_boundary_old_price_zero_returns_zero | REQ-6 | AC-2, AC-3 | Boundary | old_price=0 → 0.00% (sem ZeroDivisionError) |

---

## Coverage checklist
- Happy path tests: 5 (UT-01, UT-02, UT-03, UT-09, UT-10)
- Negative/error tests: 3 (UT-04, UT-07, UT-08)
- Boundary tests: 3 (UT-05, UT-06, UT-11)

---

## Bug found and fixed during testing

During the execution of UT-01 and UT-02, the tests initially **failed** and exposed a real bug in `monitor/forms.py`:

- **Root cause:** `StockForm.clean_symbol()` read `tipo` from `self.cleaned_data`, but Django processes form fields in declaration order (`symbol` → `name` → `tipo`). When `clean_symbol()` runs, `tipo` has not yet been cleaned and is absent from `cleaned_data`, so the `.SA` suffix was never appended.
- **Fix applied:** Changed `self.cleaned_data.get('tipo', ...)` to `self.data.get('tipo', ...)` inside `clean_symbol()`, reading from the raw POST data which is always available.
- **Impact:** REQ-1 AC-2 is now correctly implemented.

---

## Execution evidence
- Date: 2026-05-25
- Command used: `python -m pytest tests/unit/ -v`
- Result summary:
  - Tests run: 11
  - Passed: 11
  - Failed: 0
- Console output:
  ```
  ============================= test session starts =============================
  platform win32 -- Python 3.13.12, pytest-9.0.3, pluggy-1.6.0
  django: version: 6.0.4, settings: trt_project.settings (from ini)
  rootdir: C:\Users\kleoc\Documents\TRT
  configfile: pytest.ini
  plugins: anyio-4.11.0, django-4.12.0
  collected 11 items

  tests/unit/test_services.py::TestCalculateVariation::test_UT09_happy_positive_variation PASSED [  9%]
  tests/unit/test_services.py::TestCalculateVariation::test_UT10_happy_negative_variation PASSED [ 18%]
  tests/unit/test_services.py::TestCalculateVariation::test_UT11_boundary_old_price_zero_returns_zero PASSED [ 27%]
  tests/unit/test_validations.py::TestSymbolNormalisation::test_UT01_happy_br_stock_appends_sa PASSED [ 36%]
  tests/unit/test_validations.py::TestSymbolNormalisation::test_UT02_happy_fii_appends_sa PASSED [ 45%]
  tests/unit/test_validations.py::TestSymbolNormalisation::test_UT03_happy_us_stock_no_suffix PASSED [ 54%]
  tests/unit/test_validations.py::TestSymbolDuplicateRejection::test_UT04_negative_duplicate_symbol_rejected PASSED [ 63%]
  tests/unit/test_validations.py::TestMonitoringIntervalValidation::test_UT05_boundary_min_accepted PASSED [ 72%]
  tests/unit/test_validations.py::TestMonitoringIntervalValidation::test_UT06_boundary_max_accepted PASSED [ 81%]
  tests/unit/test_validations.py::TestMonitoringIntervalValidation::test_UT07_negative_zero_rejected PASSED [ 90%]
  tests/unit/test_validations.py::TestMonitoringIntervalValidation::test_UT08_negative_above_max_rejected PASSED [100%]

  ============================= 11 passed in 1.10s ==============================
  ```
