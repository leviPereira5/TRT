# Generated Scope

---

## Selected slice
- Slice: Full System (implementação completa do sistema de monitorização financeira)
- Description: Gestão de ações, configuração de alertas por ativo, monitorização contínua, notificações push, autenticação, pesquisa global e dashboard de mercado

---

## Actors / roles
- Primary actor: Utilizador (Investidor Individual)
- Secondary actor: Sistema (daemon automático `run_monitor`)
- External actor: API yfinance (cotações em tempo real)
- External actor: Yahoo Finance Screener API (top movers, pesquisa)
- External actor: ntfy.sh (serviço de push notifications)
- External actor: API BCB (taxas SELIC, IPCA, CDI)

---

## Use Cases implemented

| UC | Título | Estado |
|----|--------|--------|
| UC-01 | Gerir ações monitorizadas | ✅ Done |
| UC-02 | Configurar intervalo e tópico ntfy.sh | ✅ Done |
| UC-04 | Consultar cotação de ações | ✅ Done |
| UC-06 | Enviar notificação de alerta push (ntfy.sh) | ✅ Done |
| UC-07 | Registar histórico de alertas | ✅ Done |
| UC-08 | Evitar notificações duplicadas | ✅ Done |
| UC-09 | Monitorizar ações (ciclo automático) | ✅ Done |
| UC-10 | Autenticar utilizador | ✅ Done |
| UC-11 | Pesquisar ativos mundiais | ✅ Done |
| UC-12 | Consultar detalhe de ativo | ✅ Done |
| UC-13 | Visualizar visão geral do mercado | ✅ Done |

---

## Requirements implemented

| REQ | Descrição | Estado |
|-----|-----------|--------|
| REQ-1 | Cadastro de ações (adicionar, remover, tipo, símbolo normalizado) | ✅ Done |
| REQ-2 | Obter cotações via yfinance com retry (3x) e fallback | ✅ Done |
| REQ-3 | Configurar intervalo de monitorização (1–3600 s) | ✅ Done |
| REQ-4 | Limiar de alta por ativo (threshold_high, default 5%) | ✅ Done |
| REQ-5 | Limiar de baixa por ativo (threshold_low, default 5%) | ✅ Done |
| REQ-6 | Cálculo automático de variação percentual | ✅ Done |
| REQ-7 | Envio de notificação push via ntfy.sh | ✅ Done |
| REQ-8 | Evitar notificações duplicadas (janela 60 min) | ✅ Done |
| REQ-9 | Histórico de alertas persistido na BD | ✅ Done |
| REQ-13 | Tempo de resposta: timeout 5s, retry 3x, fallback | ✅ Done |
| REQ-15 | Autenticação (login, registo, visitante, email+username) | ✅ Done |
| REQ-16 | Pesquisa global de ativos + autocomplete | ✅ Done |
| REQ-17 | Visão geral do mercado com cache e dados BCB | ✅ Done |

---

## Variant constraints implemented

- Timeout máximo de 5 segundos por requisição à API (REQ-13)
- Retry automático até 3 tentativas em caso de falha (REQ-2)
- Fallback para último valor válido se API indisponível (REQ-2)
- Anti-duplicação: janela de 60 minutos por ativo e direção (REQ-8)
- Cache de 5 minutos para dados de mercado (home + tesouro + top movers)
- Cache de 30 minutos para taxas BCB
- Paralelismo via `ThreadPoolExecutor` para fetch de múltiplos ativos
- Limiares de alerta independentes por ativo (não globais)
- Notificações via HTTP POST (ntfy.sh) — sem SMTP, sem credenciais, grátis

---

## Anteriormente "Out of scope" — agora implementado

| Item | Estado anterior | Estado atual |
|------|----------------|--------------|
| Notificações externas reais | Out of scope | ✅ ntfy.sh implementado |
| Dashboard com gráficos | Out of scope | ✅ Chart.js na página de detalhe |
| Autenticação de utilizadores | Out of scope | ✅ Login, registo, visitante |
| Histórico persistente avançado | Out of scope | ✅ Tabela Alert, /alerts/ |
| Visão geral do mercado | Out of scope | ✅ Home com top movers, BCB, Tesouro |
| Pesquisa de ativos | Out of scope | ✅ Search + autocomplete |
| Detalhe fundamentalista de ativos | Out of scope | ✅ ~35 métricas por ativo |

---

## Ainda fora de scope

- PostgreSQL em produção (apenas SQLite em uso)
- Deploy em ambiente cloud
- Múltiplos utilizadores com portfolios separados
- Interface SPA / React
- Notificações por email ou Telegram (substituídas por ntfy.sh)
