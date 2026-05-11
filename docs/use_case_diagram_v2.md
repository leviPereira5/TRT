# Use Case Diagram v2

## System boundary
- System name: TRT Invest — Financial Market Monitoring System
- Slice covered: Sistema completo de monitorização, alertas push, autenticação, pesquisa e dashboard de mercado

## System Boundary Definition

O sistema inclui:
- Autenticação de utilizadores (login, registo, acesso visitante)
- Gestão de ações monitorizadas (adicionar, remover, pausar, limiares por ativo)
- Configuração de intervalo de monitorização e tópico ntfy.sh
- Integração com API yfinance (cotações, fundamentais, histórico)
- Cálculo automático de variações percentuais
- Geração e envio de notificações push via ntfy.sh
- Anti-duplicação de alertas (janela 60 minutos)
- Persistência de histórico de alertas e cotações (SQLite)
- Pesquisa global de ativos (Yahoo Finance Search API)
- Dashboard de mercado (top movers, Tesouro, taxas BCB)

O sistema NÃO inclui:
- Implementação das APIs externas (yfinance, BCB, ntfy.sh)
- Notificações por email ou Telegram
- Múltiplos utilizadores com portfolios isolados
- Deploy em produção / cloud

---

## Actors

- **A1: Utilizador** (Investidor Individual) — interage com a interface web
- **A2: API yfinance** — fornece cotações, fundamentais e histórico
- **A3: ntfy.sh** — recebe HTTP POST e entrega push notification ao telemóvel
- **A4: API BCB / Yahoo Finance Screener** — taxas económicas e top movers

---

## Use Cases

| UC | Título | Actor principal |
|----|--------|----------------|
| UC-01 | Gerir ações monitorizadas | A1 |
| UC-02 | Configurar intervalo e tópico ntfy.sh | A1 |
| UC-04 | Consultar cotação de ações | Sistema → A2 |
| UC-06 | Enviar notificação push | Sistema → A3 |
| UC-07 | Registar histórico de alertas | Sistema |
| UC-08 | Evitar notificações duplicadas | Sistema |
| UC-09 | Monitorizar ações (ciclo automático) | Sistema → A2 |
| UC-10 | Autenticar utilizador | A1 |
| UC-11 | Pesquisar ativos mundiais | A1 → A4 |
| UC-12 | Consultar detalhe de ativo | A1 → A2 |
| UC-13 | Visualizar visão geral do mercado | A1 → A2, A4 |

---

## Relações entre Use Cases

- UC-09 `<<include>>` UC-04 (monitorização requer obtenção de cotação)
- UC-09 `<<include>>` UC-06 (monitorização dispara notificação se necessário)
- UC-06 `<<include>>` UC-07 (notificação inclui registo no histórico)
- UC-06 `<<include>>` UC-08 (notificação verifica anti-duplicação)
- UC-12 `<<extend>>` UC-01 (detalhe permite adicionar ao portfolio)

---

## Mapping Objectives → Use Cases

- OBJ-1 (Monitorização automática) → UC-04, UC-09, UC-13
- OBJ-2 (Configuração personalizada de alertas) → UC-01, UC-02, UC-06, UC-08
- OBJ-3 (Histórico e persistência) → UC-07, UC-09

---

## Mapping CSF → Use Cases

- CSF-1 (Integração fiável com API) → UC-04, UC-09, UC-12, UC-13
- CSF-2 (Configuração precisa de limiares) → UC-01, UC-02, UC-06, UC-08
- CSF-3 (Persistência e rastreabilidade) → UC-07, UC-09

---

## Diagram file
- Path: `docs/diagrams/use_case_diagram_v2.puml`
