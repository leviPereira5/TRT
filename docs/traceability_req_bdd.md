# Traceability — Requirements ↔ BDD Scenarios (Lab 13)

## Selected requirements (min. 2)
- REQ-1 — Cadastro de ações (stock portfolio CRUD)
- REQ-15 — Autenticação de utilizadores (access control)

## Mapping (REQ → Scenario)

| Requirement (REQ-###) | Scenario name | Feature file | Notes |
|---|---|---|---|
| REQ-1 (AC-1, AC-5) | Happy path — Adicionar ativo válido ao portfólio | bdd/features/lab13.feature | Verifica criação e persistência em BD |
| REQ-1 (AC-3) | Negative path — Ativo duplicado não é adicionado | bdd/features/lab13.feature | Simula lógica de verificação da view |
| REQ-15 (AC-4) | Alternative flow — Acesso sem autenticação redireciona | bdd/features/lab13.feature | Testa redirect HTTP 302 para /login/ |
| REQ-1 (AC-4) | Boundary — Remover único ativo resulta em portfólio vazio | bdd/features/lab13.feature | Caso limite: portfólio com 1 ativo |

## Acceptance criteria coverage

### REQ-1 — Cadastro de ações
| AC | Coberto por | Verificação |
|---|---|---|
| AC-1: Adicionar ativo por símbolo | Happy path scenario | Stock.objects.filter(symbol).exists() |
| AC-3: Rejeitar símbolo duplicado | Negative path scenario | Contagem permanece 1 |
| AC-4: Remover ativo existente | Boundary scenario | Stock.objects.count() == 0 |
| AC-5: Persistência em BD | Happy path scenario | ORM confirma após criação |

### REQ-15 — Autenticação de utilizadores
| AC | Coberto por | Verificação |
|---|---|---|
| AC-4: Views protegidas redirecionam para /login/ | Alternative flow scenario | HTTP 302 + Location header contém /login/ |
