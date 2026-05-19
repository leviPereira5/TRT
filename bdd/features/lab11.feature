Feature: Variação de preço, intervalo de monitorização e anti-duplicação de alertas
  Este feature valida o comportamento central do TRT Invest para os requisitos
  selecionados no Lab 11: cálculo de variação percentual, validação do intervalo
  de monitorização e prevenção de alertas duplicados.

  # REQ links: REQ-6, REQ-3, REQ-8

  # ─────────────────────────────────────────────
  # HAPPY PATH scenarios
  # ─────────────────────────────────────────────

  Scenario: Happy path — Cálculo de variação positiva
    # REQ-6 (AC-1, AC-2)
    Given o preço anterior do ativo "AAPL" é "100.00"
    When o novo preço do ativo "AAPL" é "105.00"
    Then a variação calculada é "+5.00%"
    And o valor é arredondado a 2 casas decimais

  Scenario: Happy path — Intervalo de monitorização mínimo aceite
    # REQ-3 (AC-1, AC-3)
    Given o utilizador está autenticado e na página de definições "/settings/"
    When o utilizador submete o formulário com monitoring_interval "1"
    Then o formulário é aceite sem erros
    And o campo monitoring_interval fica guardado como "1"

  Scenario: Happy path — Intervalo de monitorização máximo aceite
    # REQ-3 (AC-1, AC-3)
    Given o utilizador está autenticado e na página de definições "/settings/"
    When o utilizador submete o formulário com monitoring_interval "3600"
    Then o formulário é aceite sem erros
    And o campo monitoring_interval fica guardado como "3600"

  Scenario: Happy path — Alerta após janela de 60 minutos é permitido
    # REQ-8 (AC-1)
    Given o ativo "AAPL" tem um alerta "high" criado há "61" minutos
    When o sistema verifica "already_alerted(AAPL, high)"
    Then o resultado é "False"
    And um novo alerta pode ser criado para "AAPL"

  # ─────────────────────────────────────────────
  # NEGATIVE PATH scenarios
  # ─────────────────────────────────────────────

  Scenario: Negative path — Intervalo de monitorização abaixo do mínimo rejeitado
    # REQ-3 (AC-3)
    Given o utilizador está autenticado e na página de definições "/settings/"
    When o utilizador submete o formulário com monitoring_interval "0"
    Then o formulário é rejeitado com erro "Entre 1 e 3600 segundos."
    And o registo UserSettings não é atualizado

  Scenario: Negative path — Intervalo de monitorização acima do máximo rejeitado
    # REQ-3 (AC-3)
    Given o utilizador está autenticado e na página de definições "/settings/"
    When o utilizador submete o formulário com monitoring_interval "3601"
    Then o formulário é rejeitado com erro "Entre 1 e 3600 segundos."
    And o registo UserSettings não é atualizado

  Scenario: Negative path — Alerta duplicado bloqueado dentro de 60 minutos
    # REQ-8 (AC-1, AC-2)
    Given o ativo "AAPL" tem um alerta "high" criado há "30" minutos
    When o sistema verifica "already_alerted(AAPL, high)"
    Then o resultado é "True"
    And nenhum novo alerta é criado para "AAPL"
    And nenhum POST HTTP é enviado para o ntfy.sh

  Scenario: Negative path — Variação com preço anterior zero retorna 0%
    # REQ-6 (AC-3)
    Given o preço anterior do ativo "NOVO" é "0.00"
    When o novo preço do ativo "NOVO" é "150.00"
    Then a variação calculada é "0.00%"
    And nenhuma divisão por zero ocorre
