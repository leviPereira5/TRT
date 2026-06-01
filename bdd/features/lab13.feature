Feature: Gestão de ativos no portfólio e autenticação de utilizadores
  Este feature valida o comportamento de registo de ativos no portfólio
  e o controlo de acesso por autenticação, alinhado com os requisitos
  REQ-1 e REQ-15 do TRT Invest.

  # REQ links: REQ-1, REQ-15

  # ─────────────────────────────────────────────
  # HAPPY PATH
  # ─────────────────────────────────────────────

  Scenario: Happy path — Adicionar ativo válido ao portfólio
    # REQ-1 (AC-1, AC-5)
    Given a base de dados está limpa de ativos
    When o utilizador adiciona o ativo "AAPL" do tipo "stock_us"
    Then o ativo "AAPL" existe no portfólio
    And o total de ativos no portfólio é "1"

  # ─────────────────────────────────────────────
  # NEGATIVE PATH
  # ─────────────────────────────────────────────

  Scenario: Negative path — Ativo duplicado não é adicionado ao portfólio
    # REQ-1 (AC-3)
    Given o ativo "PETR4.SA" já existe no portfólio
    When o utilizador tenta adicionar "PETR4.SA" novamente
    Then o portfólio contém exatamente "1" ativo com símbolo "PETR4.SA"

  # ─────────────────────────────────────────────
  # ALTERNATIVE FLOW
  # ─────────────────────────────────────────────

  Scenario: Alternative flow — Acesso a página protegida sem autenticação redireciona para login
    # REQ-15 (AC-4)
    Given o utilizador não está autenticado
    When acede à página protegida "/portfolio/"
    Then é redirecionado para "/login/"

  # ─────────────────────────────────────────────
  # BOUNDARY
  # ─────────────────────────────────────────────

  Scenario: Boundary — Remover o único ativo resulta em portfólio vazio sem erros
    # REQ-1 (AC-4)
    Given o ativo "VALE3.SA" é o único ativo no portfólio
    When o utilizador remove o ativo "VALE3.SA"
    Then o portfólio está vazio
    And não ocorre nenhum erro durante a remoção
