# Gap Analysis — Lab 14

**Versão:** 1.0  
**Data:** 2026-06-08  
**Projeto:** TRT Invest

---

## REQs sem cobertura de testes

| REQ | Descrição | Gap identificado | Ação tomada |
|-----|-----------|-----------------|-------------|
| REQ-4 | Limiar de alta | Sem TC formal e sem UT em `tests/unit/`; apenas AC definidos | Criados cenários BDD em `thresholds_and_search.feature` |
| REQ-5 | Limiar de baixa | Sem TC, sem UT, sem BDD | Criados cenários BDD em `thresholds_and_search.feature` |
| REQ-6 | Cálculo de variação | Sem TC formal, sem BDD scenario | Marcado como fora de âmbito de aceitação — lógica pura coberta por 7 UT; BDD seria redundante |
| REQ-16 | Pesquisa de ativos | Sem TC, sem BDD | Criados 3 cenários BDD em `thresholds_and_search.feature` |
| REQ-17 | Visão geral do mercado | Sem TC, sem BDD | Marcado fora de âmbito — dados de APIs externas (yfinance, BCB) dificultam automação sem mock complexo; coberto por teste manual |

**Justificação para fora de âmbito:**
- REQ-6: A lógica é uma fórmula matemática pura já coberta por UT-09/UT-10/UT-11 e T-01 a T-04. Um cenário BDD não acrescenta valor adicional.
- REQ-17: Depende de 4 APIs externas (yfinance screener, BCB, cache Django). Teste automatizado exigiria mocking extenso de todas as dependências sem proporcional ganho de confiança.

---

## Testes/cenários sem link a REQ

| Test/Cenário | Problema | Ação tomada |
|-------------|----------|-------------|
| `T-01` a `T-04` em `monitor/tests.py` | IDs duplicam UT-09 a UT-11 em `tests/unit/test_services.py`; dois conjuntos de testes cobrem o mesmo comportamento (REQ-6) com IDs diferentes | Documentado; sugerida remoção de duplicação (ver grooming) |
| `T-05` a `T-08` em `monitor/tests.py` | Duplicam UT-05 a UT-08 em `tests/unit/test_validations.py` (REQ-3) | Documentado; sugerida remoção de duplicação |
| `T-09` a `T-12` em `monitor/tests.py` | REQ-8 coberto em `monitor/tests.py` mas não em `tests/unit/` (inconsistência de organização) | Adicionados UT-12, UT-13, UT-14 em `tests/unit/test_services.py` |

---

## Itens de AC não cobertos por testes

| AC | REQ | Ação tomada |
|----|-----|-------------|
| AC-1 (registo com username/email/password) | REQ-15 | Sem TC dedicado; coberto implicitamente por TC-011 (login pressupõe registo). Marcado como gap menor. |
| AC-4 (views protegidas redirecionam para /login/) | REQ-15 | Sem TC explícito para redirecionamento; comportamento Django padrão verificado manualmente |
| AC-4 (link direto para detalhe do ativo nos resultados de pesquisa) | REQ-16 | Coberto indiretamente pelo cenário BDD de pesquisa; sem TC isolado |
| AC-5 (dados cacheados 5 minutos) | REQ-17 | Fora de âmbito — verificação de cache requer timing preciso; documentado como gap aceite |

---

## Ações realizadas neste lab

1. Criação de `bdd/features/thresholds_and_search.feature` com 7 cenários para REQ-4, REQ-5 e REQ-16 (não existia cobertura BDD).
2. Adição de UT-12, UT-13, UT-14 em `tests/unit/test_services.py` cobrindo `already_alerted()` (REQ-8) na pasta de testes unitários organizados.
3. Atualização de `behave.ini` com instruções de execução corretas (referência a `lab11` estava obsoleta).
4. Criação de `docs/traceability_master.md` com todos os 13 REQs mapeados.
5. Identificação e documentação de 8 testes duplicados entre `monitor/tests.py` e `tests/unit/` com IDs inconsistentes.
6. Identificação dos 5 REQs sem cobertura completa e decisão sobre ação para cada um.
