# BDD Automation Report — Lab 13

## Tool used
- **Tool:** Behave 1.2.6
- **Language/stack:** Python 3.13 + Django 6.0.4
- **BDD format:** Gherkin (`.feature` files)

## How to run

```bash
# From the repo root:
cd trt_project && python -m behave ../bdd/features/lab13.feature
```

## Execution results

- **Date:** 2026-06-01
- **Scenarios executed:** 4
- **Passed:** 4
- **Failed:** 0

```
1 feature passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
14 steps passed, 0 failed, 0 skipped
Took 0min 0.073s
```

## Scenarios summary

| # | Scenario | REQ | Result |
|---|---|---|---|
| 1 | Happy path — Adicionar ativo válido ao portfólio | REQ-1 (AC-1, AC-5) | PASS |
| 2 | Negative path — Ativo duplicado não é adicionado | REQ-1 (AC-3) | PASS |
| 3 | Alternative flow — Acesso sem autenticação redireciona para login | REQ-15 (AC-4) | PASS |
| 4 | Boundary — Remover único ativo resulta em portfólio vazio | REQ-1 (AC-4) | PASS |

## Notes

**What worked well:**
- Step definitions reutilizam o Django ORM diretamente (sem HTTP para os cenários REQ-1), tornando os testes rápidos (0.073s total) e estáveis
- O `environment.py` existente (setup/teardown de BD por cenário) funciona corretamente para Lab 13 sem alterações
- O Django test `Client` para o cenário REQ-15 confirma o comportamento real do `@login_required` sem precisar de UI automation

**What could be improved:**
- REQ-1 AC-2 (normalização automática de símbolo .SA / -USD) não foi coberto neste lab — poderia ser adicionado como cenário extra
- REQ-15 AC-2 (login com email em vez de username) é um bom candidato para cenário futuro usando o Django test client com POST
- Integração com CI/CD (GitHub Actions) permitiria correr os cenários automaticamente a cada push
