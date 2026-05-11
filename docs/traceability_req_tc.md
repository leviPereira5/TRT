# Traceability — Requirements ↔ Test Cases (Lab 9)

## Selected requirements (8)

| # | REQ | Type | Description |
|---|-----|------|-------------|
| 1 | REQ-1 | FR | Cadastro de ações (adicionar, rejeitar duplicado, persistir) |
| 2 | REQ-7 | FR | Envio de notificações push via ntfy.sh |
| 3 | REQ-9 | FR | Histórico de alertas acessível |
| 4 | REQ-15 | FR | Autenticação de utilizadores |
| 5 | REQ-8 | NFR | Evitar notificações duplicadas (janela 60 min) |
| 6 | REQ-13 | NFR | Tempo de resposta: timeout 5s, retry 3x, fallback |
| 7 | REQ-2 | Other | Obter cotações via yfinance com retry e fallback |
| 8 | REQ-3 | Other | Configurar intervalo de monitorização (1–3600 s) |

---

## Mapping (REQ → TC)

| Requirement | Test Cases | Coverage type |
|---|---|---|
| REQ-1 | TC-001, TC-002 | Happy path, Negative |
| REQ-2 | TC-009, TC-010 | NFR — retry, fallback |
| REQ-3 | TC-003 | Boundary (0, 1, 3600, 3601) |
| REQ-7 | TC-004, TC-005 | Happy path, Negative |
| REQ-8 | TC-006, TC-007 | Negative, Alternative flow |
| REQ-9 | TC-008 | Happy path |
| REQ-13 | TC-009, TC-010 | NFR — retry, fallback |
| REQ-15 | TC-011, TC-012 | Alternative flow, Negative |

---

## Mapping (TC → REQ)

| Test Case | REQs | Type | Path |
|---|---|---|---|
| TC-001 | REQ-1 | Acceptance | Happy path |
| TC-002 | REQ-1 | Acceptance | Negative |
| TC-003 | REQ-3 | System | Boundary |
| TC-004 | REQ-7, REQ-4 | Integration | Happy path |
| TC-005 | REQ-7 | Integration | Negative |
| TC-006 | REQ-8 | Integration | Negative |
| TC-007 | REQ-8 | Integration | Alternative flow |
| TC-008 | REQ-9 | Acceptance | Happy path |
| TC-009 | REQ-2, REQ-13 | Integration | NFR |
| TC-010 | REQ-2, REQ-13 | Integration | NFR / Alternative flow |
| TC-011 | REQ-15 | Acceptance | Alternative flow |
| TC-012 | REQ-15 | Acceptance | Negative |

---

## Mapping (Gherkin Scenarios → REQ → TC)

| Gherkin Scenario | REQ | TC |
|---|---|---|
| Happy path — Add valid US stock | REQ-1 | TC-001 |
| Happy path — Push notification on threshold breach | REQ-7, REQ-4 | TC-004 |
| Happy path — Alert history accessible | REQ-9 | TC-008 |
| Happy path — Login with email | REQ-15 | TC-011 |
| Alternative flow — Duplicate alert after 60 min window | REQ-8 | TC-007 |
| Alternative flow — Fallback to last price | REQ-2, REQ-13 | TC-010 |
| Alternative flow — Guest login | REQ-15 | TC-011 |
| Negative — Reject duplicate stock symbol | REQ-1 | TC-002 |
| Negative — No notification when ntfy_topic empty | REQ-7 | TC-005 |
| Negative — Duplicate notification blocked within 60 min | REQ-8 | TC-006 |
| Negative — Login with wrong password | REQ-15 | TC-012 |
| Negative — Interval out of range rejected | REQ-3 | TC-003 |
| Boundary — Interval min/max values | REQ-3 | TC-003 |
| NFR — API retries 3 times before returning None | REQ-2, REQ-13 | TC-009 |

---

## Coverage analysis

| Coverage type | Required | Delivered |
|---|---|---|
| Happy path | ≥ 1 | 4 (TC-001, TC-004, TC-008, TC-011) |
| Alternative flow | ≥ 1 | 3 (TC-007, TC-010, TC-011) |
| Negative / error | ≥ 2 | 4 (TC-002, TC-005, TC-006, TC-012) |
| Boundary | ≥ 1 | 1 (TC-003) |
| Total test cases | ≥ 8 | 12 |
| Gherkin scenarios | ≥ 3 | 14 |

---

## Gaps / observations

- TC-009 e TC-010 cobrem REQ-13 de forma integrada via REQ-2 (retry e fallback são inseparáveis)
- REQ-4 (limiar de alta) é coberto indiretamente em TC-004 e no cenário Gherkin de notificação — não selecionado como requisito primário para não exceder o limite de 8, mas está referenciado
- REQ-8 necessitou de 2 TCs para cobrir tanto o bloqueio (TC-006) como a expiração da janela (TC-007) — variantes importantes do mesmo requisito
