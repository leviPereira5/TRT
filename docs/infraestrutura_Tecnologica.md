# Infraestrutura Tecnológica

## 1. Visão Geral

O sistema é uma aplicação web baseada em arquitetura cliente-servidor, que permite monitorização de ativos financeiros em tempo quase real, configuração de alertas personalizados por ativo, notificações push automáticas e visualização de mercado.

A solução segue o padrão **MVT (Model-View-Template)** do Django com separação clara entre lógica de negócio (`services.py`) e camada HTTP (`views.py`).

---

## 2. Stack Tecnológica

### Linguagem
- Python 3.12

### Backend
- **Framework:** Django 6.x
- **Responsabilidades:**
    - Lógica de negócio (monitorização, cálculo de variações, alertas)
    - Integração com APIs externas (yfinance, Yahoo Finance, BCB, ntfy.sh)
    - ORM e gestão de base de dados
    - Autenticação de utilizadores
    - Renderização de templates

### Frontend
- HTML5 + CSS3 (inline, sem framework externo)
- Django Templates (renderização server-side)
- JavaScript (autocomplete de pesquisa, interações dinâmicas)
- **Chart.js** (gráfico de preços históricos na página de detalhe)

### Base de Dados
- **SGBD:** SQLite (ambiente de desenvolvimento e produção atual)
- **ORM:** Django ORM
- PostgreSQL suportado como evolução futura

### Cache
- Django cache framework (cache em memória, por defeito)
- TTL de 300s (5 min) para dados de mercado
- TTL de 1800s (30 min) para taxas BCB

---

## 3. Modelos de Dados

| Modelo | Campos principais |
|--------|-------------------|
| `Stock` | symbol, name, tipo, is_active, threshold_high, threshold_low |
| `UserSettings` | monitoring_interval, ntfy_topic (singleton) |
| `StockPrice` | stock (FK), price, fetched_at |
| `Alert` | stock (FK), direction, variation, price, sent_at, notified, email_sent |

---

## 4. Integrações Externas

### API de Mercado Financeiro — yfinance
- Cotações individuais: `fetch_price(symbol)` com 3 retries e timeout 5s
- Dados fundamentais completos: P/E, P/B, margens, ROE, market cap, etc.
- Histórico de preços (1 mês) para gráfico Chart.js
- Grupos de ativos em paralelo via `ThreadPoolExecutor`

### Yahoo Finance Screener API
- Top movers do dia: EUA (gainers), Brasil, FIIs, Crypto
- Pesquisa global de ativos: `/search/` e `/search/suggest/` (autocomplete)

### API BCB (Banco Central do Brasil)
- Série 432: Meta SELIC (% a.a.)
- Série 433: IPCA (% mês)
- Série 4389: CDI (% a.a.)
- Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/1`

### ntfy.sh (Notificações Push)
- **Tipo:** HTTP REST (POST)
- **Autenticação:** Nenhuma — tópico secreto escolhido pelo utilizador
- **Custo:** Gratuito
- **Funcionalidade:** Push notifications para telemóvel (Android/iOS via app ntfy)
- **Payload:** corpo UTF-8 com variação/preço/hora; headers: Title, Priority, Tags
- **Requisitos associados:** REQ-7, REQ-8

---

## 5. Arquitetura de Serviços (`services.py`)

```
fetch_price()           → yfinance, 3 retries, Decimal
fetch_market_overview() → 4 grupos em paralelo, cache 300s
fetch_top_movers()      → screener API + yfinance, cache 300s
fetch_tesouro()         → 4 ETFs B3 via yfinance, cache 300s
fetch_taxas_bcb()       → API BCB série temporal, cache 1800s
run_monitoring_cycle()  → itera Stocks ativos, guarda StockPrice, dispara alertas
send_ntfy_notification()→ HTTP POST para ntfy.sh
```

---

## 6. Autenticação

- Django built-in `User` model
- Login por username **ou** email (resolução automática email → username)
- Registo com validação de unicidade de username e email
- Acesso de visitante: conta `visitante` criada on-demand, sem password
- Proteção de todas as views com `@login_required`

---

## 7. Robustez e Qualidade (Variant-driven)

- Timeout máximo de 5 segundos por requisição à API (REQ-13)
- Retry automático até 3 tentativas em falha de API (REQ-2)
- Fallback para último `StockPrice` registado se API indisponível (REQ-12)
- Janela anti-duplicação de 60 minutos por ativo e direção (REQ-8)
- Cache de dados de mercado para evitar sobrecarga das APIs externas
- `ThreadPoolExecutor` para fetch paralelo de múltiplos ativos
- Logging de erros e eventos via `logging` Python

---

## 8. Segurança

- Comunicação HTTPS com todas as APIs externas
- Sem credenciais sensíveis no código (ntfy.sh não requer API key)
- Validação de inputs do utilizador (formulários Django)
- CSRF protection em todos os formulários POST
- Sem SQL raw — acesso exclusivo via Django ORM

---

## 9. Escalabilidade e Evolução

A arquitetura atual permite evolução para:

- Múltiplos utilizadores com portfolios separados
- PostgreSQL em produção
- Celery para monitorização assíncrona (substituindo o daemon `run_monitor`)
- Deploy em ambiente cloud (Railway, Render, etc.)

---

## 10. Suporte aos Requisitos

| Componente | Requisitos suportados |
|---|---|
| Django + ORM | REQ-1, REQ-3, REQ-4, REQ-5, REQ-9, REQ-15 |
| yfinance + retry | REQ-2, REQ-6, REQ-13 |
| run_monitor daemon | REQ-3, REQ-6, REQ-7 |
| ntfy.sh HTTP POST | REQ-7, REQ-8 |
| Yahoo Finance Screener | REQ-16, REQ-17 |
| BCB API | REQ-17 |
| Django Auth | REQ-15 |
| SQLite (Django ORM) | REQ-9, REQ-14 |
