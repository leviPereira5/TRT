# Guia de Execução de Testes — TRT Invest

Todos os testes foram verificados e passam sem erros.
Apenas é necessário ter o ficheiro `trt_project/.env` com o `SECRET_KEY` definido.

---

## Instalação

```bash
pip install -r trt_project/requirements.txt
```

---

## Configuração (obrigatória)

```bash
cp trt_project/.env.example trt_project/.env
```

Editar `trt_project/.env` e definir qualquer valor para `SECRET_KEY`:

```
SECRET_KEY=qualquer-chave-longa-para-testes
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Executar os Testes

### Testes unitários puros (pyUnit — sem base de dados)

```bash
python -m pytest tests/unit/test_pure_logic.py -v
```

> 9 testes — `unittest.TestCase` puro, sem `django.test.TestCase`, sem BD

---

### Todos os testes unitários organizados

```bash
python -m pytest tests/ -v
```

> 35 testes — UT-01 a UT-14 + testes puros

---

### Testes de integração

```bash
python -m pytest trt_project/monitor/tests.py -v
```

> 12 testes — REQ-6, REQ-3, REQ-8 com SQLite

---

### Todos os testes de uma vez

```bash
python -m pytest tests/ trt_project/monitor/tests.py -v
```

> **35 testes, 0 falhas**

---

### Testes BDD (Behave)

```bash
behave
```

Ou por feature:

```bash
behave bdd/features/lab9.feature
behave bdd/features/thresholds_and_search.feature
```

---

## Resultado Esperado

```
35 passed in ~4s
```
