# Test Plan — Lab 10

## 1) Scope

### Slice covered
TRT Invest — sistema completo de monitorização de ativos financeiros, incluindo:
- Gestão de portfolio de ações (REQ-1)
- Obtenção de cotações via yfinance com retry/fallback (REQ-2)
- Configuração de intervalo de monitorização (REQ-3)
- Notificações push automáticas via ntfy.sh (REQ-7)
- Anti-duplicação de alertas com janela de 60 minutos (REQ-8)
- Histórico persistente de alertas (REQ-9)
- Robustez e tempo de resposta da API (REQ-13 — NFR, variant-driven)
- Autenticação de utilizadores (REQ-15)

### Out of scope
- Deploy em produção / cloud (Railway, Render, etc.)
- PostgreSQL — apenas SQLite é testado
- Portfolios isolados por utilizador (feature não implementada)
- Notificações por email ou Telegram
- Automação completa dos testes de aceitação (execução manual ou semântica Gherkin)
- Testes de carga / stress em larga escala

---

## 2) Test strategy (static + dynamic)

### Static testing (reviews)
**O que rever:**
- Requisitos (REQ-###): clareza, ausência de ambiguidade, testabilidade
- Acceptance Criteria: observabilidade do resultado, critérios mensuráveis
- Test cases: cobertura de caminhos (happy/alt/negative/boundary)
- Gherkin scenarios: alinhamento com ACs, Given/When/Then bem formados

**Review checklist:**
- [ ] Cada AC descreve um resultado observável e verificável (não "funciona corretamente")
- [ ] Cada TC tem precondições, dados de teste, passos e resultado esperado explícito
- [ ] Cada cenário Gherkin referencia pelo menos um REQ
- [ ] Nenhum TC duplica exatamente outro TC
- [ ] ACs de NFR têm método de medição definido (timeout em ms, nº de retries, etc.)
- [ ] Casos de fronteira (min, max, vazio, inválido) estão cobertos
- [ ] Headers de HTTP para ntfy.sh usam apenas ASCII (sem caracteres Unicode como `—`)

**Issues encontrados durante revisão estática (ver `docs/ac_dod_updates.md`):**
1. REQ-7 AC-3: encoding dos headers HTTP não estava especificado → corrigido
2. REQ-8 AC-1: não especificava que a janela é por par (stock, direction) → corrigido
3. REQ-2 AC-3 (fallback): não cobria o caso em que não existe nenhum StockPrice → corrigido

---

### Dynamic testing (planned execution)

| Level | O que testamos | Exemplos | Evidência |
|---|---|---|---|
| **Unit** | Lógica isolada: validação, cálculo | `calculate_variation()`, `clean_monitoring_interval()`, `already_alerted()` | Resultados em `monitor/tests.py` |
| **Integration** | Interação entre componentes | `monitor_stock()` → `fetch_price()` → `StockPrice` → `check_and_alert()` → ntfy.sh | TC-004 a TC-010; logs do servidor |
| **System** | Ciclo completo end-to-end | `run_monitoring_cycle()` com ativos reais; `/portfolio/` add → monitor → `/alerts/` | Execução manual; registo em `docs/test_cases.md` |
| **Acceptance (BDD)** | Comportamento vs AC | Cenários em `bdd/features/lab9.feature` | Feature file + evidência manual |

---

## 3) TDD plan (candidatos)

### Candidato 1 — `calculate_variation()` (REQ-6)
- **Regra:** `((novo - antigo) / antigo) * 100`, arredondado a 2 casas decimais; resultado 0.00 quando antigo = 0
- **Por que TDD é adequado:** Função pura sem dependências externas — fácil de escrever o teste antes da implementação; resultado determinístico dado o input
- **Casos a escrever primeiro:**
  - `calculate_variation(100, 105)` → `Decimal("5.00")`
  - `calculate_variation(100, 95)` → `Decimal("-5.00")`
  - `calculate_variation(0, 105)` → `Decimal("0.00")` (edge case: divisão por zero)
  - `calculate_variation(100, 100)` → `Decimal("0.00")`

### Candidato 2 — `already_alerted()` (REQ-8, variant-driven)
- **Regra:** Retorna `True` se existir `Alert` com o mesmo `(stock, direction)` nos últimos 60 minutos
- **Por que TDD é adequado:** Regra de negócio crítica, variant-driven — a janela de 60 minutos é um requisito de negócio que deve ser codificado como teste antes da implementação; isola lógica de tempo que pode regredir
- **Casos a escrever primeiro:**
  - Alerta criado há 30 min → `True`
  - Alerta criado há 61 min → `False`
  - Alerta de `direction='high'` não bloqueia `direction='low'` → `False`
  - Sem alertas na BD → `False`

### Candidato 3 — `clean_monitoring_interval()` (REQ-3)
- **Regra:** Valor entre 1 e 3600 aceite; fora rejeita com `ValidationError`
- **Por que TDD é adequado:** Validação de formulário com fronteiras claras e bem definidas — perfeito para escrever testes de boundary antes do código
- **Casos:**
  - `0` → `ValidationError`
  - `1` → aceite
  - `3600` → aceite
  - `3601` → `ValidationError`

---

## 4) BDD plan

### Feature(s)
- `bdd/features/lab9.feature` — "Stock Monitoring, Alerts and Authentication — TRT Invest"

### Comportamentos representados como cenários

| Comportamento | Tipo | REQ | Cenário Gherkin |
|---|---|---|---|
| Adicionar ação válida | Happy path | REQ-1 | "Add a valid US stock to the portfolio" |
| Rejeitar símbolo duplicado | Negative | REQ-1 | "Reject adding a duplicate stock symbol" |
| Notificação enviada quando limiar atingido | Happy path | REQ-7 | "Push notification sent when price threshold is exceeded" |
| Sem notificação com ntfy_topic vazio | Negative | REQ-7 | "No notification sent when ntfy_topic is empty" |
| Duplicado bloqueado < 60 min | Negative | REQ-8 | "Duplicate push notification blocked within 60 minutes" |
| Duplicado permitido após 60 min | Alternative | REQ-8 | "Duplicate alert allowed after 60-minute window expires" |
| Histórico acessível | Happy path | REQ-9 | "Alert history is accessible and complete" |
| Fallback ao último preço | Alternative/NFR | REQ-2, REQ-13 | "No price stored when API returns fallback value" |
| Login com email | Alternative | REQ-15 | "Login using email address instead of username" |
| Login com password errada | Negative | REQ-15 | "Login rejected with incorrect password" |
| Intervalo de fronteira | Boundary | REQ-3 | "Monitoring interval accepts minimum and maximum valid values" |
| Retry 3x da API | NFR | REQ-2, REQ-13 | "API retries exactly 3 times before returning None" |

### Links diretos a REQs
Cada cenário inclui comentário `# REQ links:` com os requisitos cobertos.

---

## 5) Coverage goals

| Tipo | Meta | Entregue |
|---|---|---|
| Happy path | ≥ 1 por REQ selecionado | TC-001, TC-004, TC-008, TC-011 + 4 cenários Gherkin |
| Alternative flows | ≥ 1 total | TC-007, TC-010, TC-011 + 3 cenários Gherkin |
| Negative / error | ≥ 2 total | TC-002, TC-005, TC-006, TC-012 + 5 cenários Gherkin |
| Boundary | ≥ 1 total | TC-003 + cenário "interval min/max" |
| NFR | ≥ 1 por NFR | TC-009 (retry), TC-010 (fallback) + 2 cenários Gherkin |

---

## 6) NFR validation approach

### NFR-1 — REQ-13: Tempo de resposta e robustez (variant-driven)
- **O que verificar:** Timeout ≤ 5s por chamada; máximo 3 tentativas; fallback ativo após falha total
- **Como verificar:**
  - *Review estático:* inspecionar `fetch_price()` — confirmar loop `for attempt in range(3)` e `timeout=5` implícito no yfinance
  - *Teste de integração:* TC-009 — mock de API com 2 falhas + 1 sucesso → validar exatamente 3 chamadas
  - *Teste de integração:* TC-010 — mock de API com 3 falhas → validar fallback via `get_last_price()`
  - *Medição:* log de tempo por ciclo via `logger.info`

### NFR-2 — REQ-8: Anti-duplicação de alertas (variant-driven)
- **O que verificar:** Nenhum alerta (stock, direction) repetido dentro de 60 minutos
- **Como verificar:**
  - *Review estático:* inspecionar `already_alerted()` — confirmar query com `sent_at__gte=cutoff` onde `cutoff = now - timedelta(minutes=60)`
  - *Teste de integração:* TC-006 — alerta criado há 30 min → `check_and_alert()` retorna `None`
  - *Teste de integração:* TC-007 — alerta criado há 61 min → novo alerta criado corretamente
  - *TDD:* escrever testes unitários para `already_alerted()` antes de qualquer alteração futura

---

## 7) Evidence recording and responsibilities

### Onde os resultados são guardados
| Artefacto | Path no repositório |
|---|---|
| Test cases documentados | `docs/test_cases.md` |
| BDD / Gherkin scenarios | `bdd/features/lab9.feature` |
| Traceability REQ → AC → TC | `docs/traceability_req_ac_tc.md` |
| AC e DoD atualizados | `docs/ac_dod_updates.md` |
| Testes unitários (futuros) | `trt_project/monitor/tests.py` |
| Evidência de execução manual | `docs/test_evidence/` (a criar por execução) |

### Responsabilidades
- Manutenção da traceabilidade: equipa de desenvolvimento — atualizar `traceability_req_ac_tc.md` a cada novo TC ou REQ
- Revisão de ACs: validar com stakeholders antes de fechar sprint
- Execução de testes manuais: registo em `docs/test_evidence/` com data e resultado (Pass/Fail)

### Como as atualizações são rastreadas
- Cada commit que adiciona TC ou modifica REQ deve referenciar o ID relevante na mensagem de commit
- `traceability_req_ac_tc.md` atualizado na mesma PR que introduz a alteração de requisito ou teste
- Cenários Gherkin novos adicionados ao `lab9.feature` ou a um novo `.feature` por funcionalidade
