# TRT Invest — Monitorização de Ativos Financeiros

Aplicação web Django para monitorização automática de ações, FIIs, criptomoedas e ETFs.
Envia notificações push via ntfy.sh quando os limiares de preço são atingidos.

---

## Requisitos do Sistema

- Python 3.11+
- pip

---

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd TRT
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r trt_project/requirements.txt
```

### 4. Configurar o ambiente

Criar o ficheiro `.env` dentro da pasta `trt_project/`:

```bash
cp trt_project/.env.example trt_project/.env
```

Editar `trt_project/.env`:

```
SECRET_KEY=qualquer-chave-secreta-longa
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Executar a Aplicação

```bash
cd trt_project
python manage.py migrate
python manage.py runserver
```

Aceder em: **http://127.0.0.1:8000/**

### Criar superutilizador (opcional)

```bash
python manage.py createsuperuser
```

### Iniciar o daemon de monitorização (opcional)

```bash
python manage.py run_monitor
```

---

## Executar os Testes

> **Os testes usam SQLite — não precisam de configuração adicional além do `.env`.**

### Testes unitários puros (pyUnit — sem base de dados)

```bash
python -m pytest tests/unit/test_pure_logic.py -v
```

> 9 testes — lógica de `calculate_variation()` e janela de 60 min com mocks

### Todos os testes unitários

```bash
python -m pytest tests/ -v
```

> 35 testes (UT-01 a UT-14 + testes puros)

### Testes de integração (monitor/tests.py)

```bash
python -m pytest trt_project/monitor/tests.py -v
```

> 12 testes — REQ-6, REQ-3, REQ-8 com base de dados SQLite

### Todos os testes de uma vez

```bash
python -m pytest tests/ trt_project/monitor/tests.py -v
```

> **35 testes, 0 falhas**

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

## Estrutura do Projeto

```
TRT/
├── trt_project/                    # Aplicação Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example                # Template de configuração
│   ├── db.sqlite3                  # Base de dados SQLite
│   ├── monitor/                    # App principal
│   │   ├── models.py               # Stock, StockPrice, Alert, UserSettings
│   │   ├── views.py                # Portfolio, settings, alertas, pesquisa
│   │   ├── services.py             # fetch_price(), calculate_variation(), already_alerted()
│   │   ├── forms.py                # StockForm, SettingsForm
│   │   └── tests.py                # Testes de integração (T-01..T-12)
│   └── trt_project/
│       └── settings.py
├── tests/
│   └── unit/
│       ├── test_pure_logic.py      # Testes pyUnit puros (sem base de dados)
│       ├── test_validations.py     # UT-01..UT-08 — REQ-1, REQ-3
│       └── test_services.py        # UT-09..UT-14 — REQ-6, REQ-8
├── bdd/
│   └── features/
│       ├── lab9.feature            # 12 cenários BDD — Labs 9/13
│       ├── thresholds_and_search.feature  # 7 cenários — REQ-4, REQ-5, REQ-16 (Lab 14)
│       ├── environment.py          # Setup Django para Behave
│       └── steps/
│           └── lab13_steps.py      # Step definitions
├── docs/                           # Documentação de requisitos e testes
│   ├── requirements_validation.md
│   ├── acceptance_criteria.md      # REQ-1..REQ-17
│   ├── test_plan.md
│   ├── test_cases.md               # TC-001..TC-012
│   ├── traceability_master.md      # Lab 14 — rastreabilidade completa
│   ├── gap_analysis_lab14.md       # Lab 14
│   ├── test_retrocompatibility.md  # Lab 14
│   └── test_grooming_report.md     # Lab 14
├── pytest.ini                      # Config pytest (SQLite, sem .env especial)
└── behave.ini                      # Config Behave
```

---

## Funcionalidades

- Monitorização automática de ações EUA, Brasil, FIIs, Criptomoedas, Europa e China
- Alertas push via **ntfy.sh** quando limiares de alta/baixa são atingidos
- Prevenção de notificações duplicadas (janela de 60 minutos por ativo/direção)
- Histórico de alertas com os últimos 100 registos
- Pesquisa global de ativos com autocomplete
- Visão geral do mercado com dados em tempo real (cached 5 min)
- Taxas BCB: SELIC, IPCA, CDI
- Autenticação com login por email ou username; acesso de visitante sem registo

---

## Autor

Trabalho de Requisitos e Testes — Engenharia Informática
