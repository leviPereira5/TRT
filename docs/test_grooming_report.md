# Test Grooming Report — Lab 14

**Versão:** 1.0  
**Data:** 2026-06-08  
**Projeto:** TRT Invest  
**Branch:** main

---

## Ações de grooming realizadas (mínimo 5)

### 1. Adição de UT-12, UT-13, UT-14 — cobertura de REQ-8 em `tests/unit/`
- **Ficheiro(s):** `tests/unit/test_services.py`
- **Porquê:** A função `already_alerted()` (REQ-8) estava coberta apenas em `monitor/tests.py` (T-09 a T-12) mas ausente da pasta organizada `tests/unit/`. Esta inconsistência significava que a cobertura da pasta canónica de testes unitários estava incompleta para REQ-8.

### 2. Criação de `bdd/features/thresholds_and_search.feature`
- **Ficheiro(s):** `bdd/features/thresholds_and_search.feature` (novo ficheiro)
- **Porquê:** REQ-4 (limiar de alta), REQ-5 (limiar de baixa) e REQ-16 (pesquisa) não tinham nenhum cenário BDD. Este feature cobre 7 novos cenários (happy, alternative e negative) para os 3 requisitos em falta. A falta de cobertura foi identificada durante a análise de gaps no `traceability_master.md`.

### 3. Correcção do `behave.ini` — instrução de execução obsoleta
- **Ficheiro(s):** `behave.ini`
- **Porquê:** O ficheiro continha o comentário `"Run from trt_project/: cd trt_project && python -m behave ../bdd/features/lab11.feature"` que era obsoleto (referência a `lab11`) e as instruções eram incorrectas (o Behave deve correr da raiz do repositório, não de dentro de `trt_project/`). Substituído por instruções correctas e actuais.

### 4. Padronização e documentação da duplicação de IDs (UT-xx vs T-xx)
- **Ficheiro(s):** `docs/gap_analysis_lab14.md`, `docs/traceability_master.md`
- **Porquê:** Existem dois conjuntos de testes que cobrem os mesmos comportamentos (REQ-3 e REQ-6) com IDs incompatíveis — UT-05..08 em `tests/unit/test_validations.py` e T-05..08 em `monitor/tests.py`; UT-09..11 em `tests/unit/test_services.py` e T-01..04 em `monitor/tests.py`. Esta duplicação cria ambiguidade sobre qual é o "conjunto canónico" de testes. A situação foi documentada e a acção de remoção dos duplicados em `monitor/tests.py` foi identificada como melhoria futura.

### 5. Criação da matriz de rastreabilidade completa (`traceability_master.md`)
- **Ficheiro(s):** `docs/traceability_master.md` (novo ficheiro)
- **Porquê:** O ficheiro existente `docs/traceability_req_ac_tc.md` (Lab 10) cobria apenas 8 dos 13 REQs. REQ-4, REQ-5, REQ-6, REQ-16 e REQ-17 não tinham rastreabilidade consolidada. O novo ficheiro mapeia todos os 13 REQs com TC, UT, BDD e evidências, e inclui a cobertura de testes adicionados no Lab 14.

### 6. Identificação e documentação de 5 pontos de fragilidade com acções de melhoria
- **Ficheiro(s):** `docs/test_retrocompatibility.md` (novo ficheiro)
- **Porquê:** Não existia qualquer análise de retrocompatibilidade no projecto. Os 5 pontos identificados (mensagens hard-coded, duplicação de testes, dependência de `timezone.now()`, dados BDD hard-coded, verificação de HTML frágil) representam os principais riscos de regressão quando o código ou os requisitos evoluírem.

### 7. Actualização do cabeçalho de `test_services.py` com referência a REQ-8
- **Ficheiro(s):** `tests/unit/test_services.py`
- **Porquê:** O cabeçalho do ficheiro indicava apenas `REQ-6` e `UT-09 … UT-11`. Após adicionar os novos testes UT-12 a UT-14, o cabeçalho foi actualizado para incluir `REQ-8` e o intervalo correcto `UT-09 … UT-14`, mantendo a rastreabilidade interna do ficheiro consistente.

---

## Actualizações de rastreabilidade
- **O que mudou em `traceability_master.md`:** Criado de raiz com todos os 13 REQs (vs 8 no ficheiro de Lab 10). REQ-4, REQ-5, REQ-16 adicionados com cobertura BDD criada neste lab. REQ-17 marcado como gap aceite.
- **Gaps resolvidos:**
  - REQ-4: 2 cenários BDD criados
  - REQ-5: 2 cenários BDD criados
  - REQ-16: 3 cenários BDD criados
  - REQ-8 em `tests/unit/`: 3 novos UTs adicionados (UT-12, UT-13, UT-14)

---

## Evidência de execução de testes

- **Data:** 2026-06-08
- **Comando:** `python -m pytest tests/ trt_project/monitor/tests.py -v`
- **Testes unitários executados:** 26
- **Passou:** 26
- **Falhou:** 0

**Distribuição:**

| Ficheiro | Testes | Passaram | Falharam |
|----------|--------|----------|---------|
| `tests/unit/test_services.py` | 6 (UT-09..14) | 6 | 0 |
| `tests/unit/test_validations.py` | 8 (UT-01..08) | 8 | 0 |
| `trt_project/monitor/tests.py` | 12 (T-01..12) | 12 | 0 |
| **Total** | **26** | **26** | **0** |

**Cenários BDD:** `bdd/features/lab9.feature` — 12 cenários documentados (Lab 13). `bdd/features/thresholds_and_search.feature` — 7 cenários novos adicionados no Lab 14. Steps para os novos cenários ainda não automatizados (fora de âmbito deste sprint de grooming).

---

## Lições aprendidas

- **Principal fonte de fragilidade:** A duplicação silenciosa entre `tests/unit/` e `monitor/tests.py`. O projecto acumulou dois conjuntos de testes com IDs diferentes para os mesmos comportamentos — qualquer manutenção tem de ser feita em dois sítios, criando risco de divergência.
- **Melhoria com maior valor:** A criação do `traceability_master.md` completo revelou 5 REQs sem cobertura automatizada que não eram evidentes ao olhar apenas para os ficheiros de testes. A rastreabilidade explícita é a ferramenta mais eficaz para identificar gaps.
