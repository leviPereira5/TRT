# Traceability — REQ → AC → Test Cases / BDD (Lab 10)

## Selected requirements (8)

| # | REQ | Type | Variant-driven |
|---|-----|------|---------------|
| 1 | REQ-1 | FR | No |
| 2 | REQ-2 | FR | Yes (retry/fallback) |
| 3 | REQ-3 | FR | No |
| 4 | REQ-7 | FR | No |
| 5 | REQ-8 | NFR | Yes (60-min window) |
| 6 | REQ-13 | NFR | Yes (timeout/retry) |
| 7 | REQ-9 | FR | No |
| 8 | REQ-15 | FR | No |

---

## Traceability matrix

| Requirement | Acceptance Criteria | Test Cases (TC-###) | BDD Scenario |
|---|---|---|---|
| **REQ-1** — Cadastro de ações | AC-1: Utilizador adiciona ação pelo símbolo e tipo | TC-001 | "Add a valid US stock to the portfolio" |
| | AC-2: Símbolo normalizado automaticamente (.SA, -USD) | TC-001 | — |
| | AC-3: Símbolo duplicado rejeitado | TC-002 | "Reject adding a duplicate stock symbol" |
| | AC-5: Persistido na BD após reinício | TC-001 | "Add a valid US stock to the portfolio" |
| **REQ-2** *(variant)* — Obter cotações | AC: Cotação válida obtida quando API disponível | TC-009 | "API retries exactly 3 times before returning None" |
| | AC: Retry automático até 3 tentativas em falha | TC-009 | "API retries exactly 3 times before returning None" |
| | AC: Fallback para último StockPrice em falha total | TC-010 | "No price stored when API returns fallback value" |
| | AC: Fallback retorna erro se nenhum StockPrice existir | TC-010 | "No price stored when API returns fallback value" |
| **REQ-3** — Configurar intervalo | AC-1: Intervalo entre 1 e 3600 segundos aceite | TC-003 | "Monitoring interval accepts minimum and maximum valid values" |
| | AC-3: Valores fora do intervalo rejeitados com erro | TC-003 | "Monitoring interval outside valid range is rejected" |
| | AC-4: Configuração persistida na BD | TC-003 | — |
| **REQ-7** — Notificações push (ntfy.sh) | AC-1: Notificação enviada quando limiar atingido | TC-004 | "Push notification sent when price threshold is exceeded" |
| | AC-2: Notificação inclui símbolo, direção, variação, preço | TC-004 | "Push notification sent when price threshold is exceeded" |
| | AC-3: Header Title ASCII; corpo UTF-8; prioridade "high"; tag emoji | TC-004 | "Push notification sent when price threshold is exceeded" |
| | AC-4: `email_sent = True` registado no alerta | TC-004 | "Push notification sent when price threshold is exceeded" |
| | AC-5: ntfy_topic vazio → silencioso, sem erro | TC-005 | "No notification sent when ntfy_topic is empty" |
| **REQ-8** *(NFR, variant)* — Anti-duplicação | AC-1: Nenhum alerta (stock, direction) repetido < 60 min | TC-006 | "Duplicate push notification blocked within 60 minutes" |
| | AC-2: Verificação via `already_alerted()` antes de criar alerta | TC-006 | "Duplicate push notification blocked within 60 minutes" |
| | AC-3: Após 60 min, novo alerta pode ser gerado | TC-007 | "Duplicate alert allowed after 60-minute window expires" |
| **REQ-9** — Histórico de alertas | AC-1: Todos os alertas guardados na tabela `Alert` | TC-008 | "Alert history is accessible and complete" |
| | AC-2: Histórico acessível em `/alerts/` (últimos 100) | TC-008 | "Alert history is accessible and complete" |
| | AC-3: Registo inclui ativo, direção, variação, preço, timestamp | TC-008 | "Alert history is accessible and complete" |
| **REQ-13** *(NFR, variant)* — Robustez e tempo de resposta | AC-1: Timeout máximo 5s por requisição | TC-009 | "API retries exactly 3 times before returning None" |
| | AC-2: Até 3 tentativas antes de usar fallback | TC-009 | "API retries exactly 3 times before returning None" |
| | AC-3: Último preço válido usado como fallback | TC-010 | "No price stored when API returns fallback value" |
| | AC-4: Erros registados via `logger` | TC-009, TC-010 | — |
| **REQ-15** — Autenticação | AC-1: Registo com username, email, password (≥8 chars) | — | — |
| | AC-2: Login com username ou email | TC-011 | "Login using email address instead of username" |
| | AC-3: Acesso visitante via `/guest/` sem registo | — | "Guest user can access portfolio without registration" |
| | AC-4: Views protegidas redirecionam para `/login/` | TC-012 | "Login rejected with incorrect password" |

---

## Resumo de cobertura por REQ

| REQ | Nº ACs mapeadas | Nº TCs | Nº Cenários Gherkin | Variant |
|---|---|---|---|---|
| REQ-1 | 4 | 2 (TC-001, TC-002) | 2 | No |
| REQ-2 | 4 | 2 (TC-009, TC-010) | 2 | Yes |
| REQ-3 | 3 | 1 (TC-003) | 2 | No |
| REQ-7 | 5 | 2 (TC-004, TC-005) | 2 | No |
| REQ-8 | 3 | 2 (TC-006, TC-007) | 2 | Yes |
| REQ-9 | 3 | 1 (TC-008) | 1 | No |
| REQ-13 | 4 | 2 (TC-009, TC-010) | 2 | Yes |
| REQ-15 | 4 | 2 (TC-011, TC-012) | 2 | No |

---

## Notas

- REQ-2 e REQ-13 partilham TC-009 e TC-010 — os comportamentos de retry e fallback são inseparáveis na implementação (`fetch_price()` → `monitor_stock()`)
- REQ-8 é variant-driven: a janela de 60 minutos é um requisito de negócio não-óbvio que necessitou de 2 TCs para cobrir bloqueio (TC-006) e expiração (TC-007)
- REQ-13 é NFR variant-driven: timeout de 5s e máximo de 3 retries são restrições de performance que devem ser verificadas por medição e por mock de falhas
- Todos os 8 REQs têm ≥ 1 TC e ≥ 1 cenário Gherkin associado
