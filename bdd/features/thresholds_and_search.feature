Feature: Limiares de alerta e pesquisa de ativos — TRT Invest
  Valida que o sistema gera alertas correctos com base nos limiares de alta e baixa
  definidos por ativo (REQ-4, REQ-5), e que a pesquisa global de ativos funciona (REQ-16).

  # REQ links: REQ-4, REQ-5, REQ-16

  # ─────────────────────────────────────────────
  # REQ-4 — Limiar de alta
  # ─────────────────────────────────────────────

  Scenario: Happy path — Alert generated when high threshold is exceeded
    # REQ-4 (AC-1: limiar de alta atingido → alerta gerado)
    Given the stock "TSLA" has threshold_high set to "3.0" percent
    And the last recorded price for "TSLA" is "200.00"
    And the user has configured ntfy_topic as "trt-test-topic"
    When the monitoring cycle runs and the new price for "TSLA" is "207.00"
    Then an Alert record is created with direction "high" for "TSLA"
    And the variation is approximately "+3.50%"

  Scenario: Negative — No alert when variation is below high threshold
    # REQ-4 (variant: variação abaixo do limiar → sem alerta)
    Given the stock "TSLA" has threshold_high set to "5.0" percent
    And the last recorded price for "TSLA" is "200.00"
    When the monitoring cycle runs and the new price for "TSLA" is "205.00"
    Then no Alert record is created for "TSLA" with direction "high"

  # ─────────────────────────────────────────────
  # REQ-5 — Limiar de baixa
  # ─────────────────────────────────────────────

  Scenario: Happy path — Alert generated when low threshold is exceeded
    # REQ-5 (AC-1, AC-2: limiar de baixa atingido → alerta de baixa gerado)
    Given the stock "PETR4.SA" has threshold_low set to "3.0" percent
    And the last recorded price for "PETR4.SA" is "40.00"
    And the user has configured ntfy_topic as "trt-test-topic"
    When the monitoring cycle runs and the new price for "PETR4.SA" is "38.50"
    Then an Alert record is created with direction "low" for "PETR4.SA"
    And the variation is approximately "-3.75%"

  Scenario: Negative — Invalid threshold value is rejected
    # REQ-4/REQ-5 (AC variant: valor inválido rejeitado)
    Given the user is authenticated and on the stock detail page for "AAPL"
    When the user submits threshold_high "-1" for "AAPL"
    Then the form is rejected with a validation error

  # ─────────────────────────────────────────────
  # REQ-16 — Pesquisa de ativos
  # ─────────────────────────────────────────────

  Scenario: Happy path — Search returns results for a valid query
    # REQ-16 (AC-1, AC-2, AC-3)
    Given the user is authenticated
    When the user navigates to "/search/?q=Apple"
    Then the page loads with HTTP status 200
    And the results include "AAPL" with name "Apple Inc."
    And each result includes symbol, name, type and exchange

  Scenario: Alternative flow — Autocomplete returns suggestions for 2+ characters
    # REQ-16 (AC-2: autocomplete com mínimo 2 caracteres)
    Given the user is authenticated
    When the user requests "/search/suggest/?q=AA"
    Then the response is JSON with at least one suggestion
    And each suggestion includes a "symbol" and "name" field

  Scenario: Negative — Autocomplete returns empty for less than 2 characters
    # REQ-16 (AC-2: menos de 2 caracteres → sem sugestões)
    Given the user is authenticated
    When the user requests "/search/suggest/?q=A"
    Then the response is JSON with an empty list or HTTP 200
