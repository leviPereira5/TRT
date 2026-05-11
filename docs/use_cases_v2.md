# Use Cases v2

## UC-01 — Gerir ações monitorizadas
- Primary actor: Utilizador
- Supporting actors: API yfinance (para auto-preenchimento do nome)
- Goal: Permitir adicionar, remover, ativar/pausar e configurar limiares das ações a monitorizar
- Preconditions: Utilizador autenticado
- Trigger: Utilizador acede a `/portfolio/`
- Postconditions (success): Lista de ações atualizada e persistida
- Postconditions (failure/cancel): Nenhuma alteração feita
- Related requirements: REQ-1, REQ-4, REQ-5

### Main flow (happy path)
1. Utilizador acede ao portfolio
2. Sistema apresenta lista atual de ações com último preço e limiares
3. Utilizador adiciona ação por símbolo e tipo (EUA, Brasil, FII, Crypto)
4. Sistema normaliza símbolo (ex: PETR4 → PETR4.SA) e vai buscar o nome via yfinance
5. Sistema valida que o símbolo não está duplicado
6. Sistema guarda na base de dados e confirma operação

### Alternative flows
A1. Utilizador pausa uma ação → sistema marca `is_active=False` sem remover da lista  
A2. Utilizador reativa ação pausada → `is_active=True`  
A3. Utilizador altera limiares de alta/baixa por ativo → sistema guarda novos valores

### Exceptions / errors
E1. Símbolo já existente → sistema rejeita com mensagem de erro  
E2. Limiar inválido (negativo, >100%) → sistema rejeita e pede correção

---

## UC-02 — Configurar intervalo de monitorização e tópico ntfy.sh
- Primary actor: Utilizador
- Supporting actors: —
- Goal: Definir intervalo de verificação de preços e canal de notificação push
- Preconditions: Utilizador autenticado
- Trigger: Utilizador acede a `/settings/`
- Postconditions (success): Configurações guardadas no singleton `UserSettings`
- Postconditions (failure/cancel): Configuração anterior mantida
- Related requirements: REQ-3, REQ-7

### Main flow (happy path)
1. Utilizador acede às configurações
2. Sistema apresenta valores atuais (intervalo e tópico ntfy.sh)
3. Utilizador define intervalo (1–3600 segundos) e/ou tópico ntfy.sh
4. Sistema valida os valores introduzidos
5. Sistema guarda configurações persistentes
6. Sistema confirma operação ao utilizador

### Alternative flows
A1. Utilizador altera apenas o intervalo → sistema aceita alteração parcial  
A2. Utilizador altera apenas o tópico ntfy.sh → sistema aceita  
A3. Utilizador clica "Enviar notificação de teste" → sistema faz POST a ntfy.sh e confirma

### Exceptions / errors
E1. Intervalo inválido (< 1 ou > 3600) → sistema rejeita e apresenta erro  
E2. Falha ao contactar ntfy.sh no teste → sistema apresenta erro detalhado

---

## UC-04 — Consultar cotação de ações
- Primary actor: Sistema
- Supporting actors: API yfinance
- Goal: Obter preço atualizado de cada ativo monitorizado
- Related requirements: REQ-2, REQ-13

### Main flow (happy path)
1. Sistema chama `fetch_price(symbol)` via yfinance
2. Tenta `regularMarketPrice`, `currentPrice`, `previousClose` por ordem
3. Retorna `Decimal` com o preço válido
4. Guarda `StockPrice` na base de dados

### Alternative flows
A1. Primeira tentativa falha → sistema executa retry (até 3 tentativas)  
A2. Todas as tentativas falham → `fetch_price` retorna `None`, sistema usa último preço registado

### Exceptions / errors
E1. Ativo sem histórico e sem preço → sistema regista erro e salta ativo

---

## UC-06 — Enviar notificação de alerta push
- Primary actor: Sistema (evento interno com impacto no utilizador)
- Supporting actors: ntfy.sh (serviço de push notifications)
- Goal: Notificar o utilizador no telemóvel quando uma variação relevante é detetada
- Preconditions:
    - `UserSettings.ntfy_topic` configurado
    - Limiar de alerta atingido
    - Não existe alerta do mesmo tipo nos últimos 60 minutos
- Trigger: `check_and_alert()` deteta variação acima do limiar
- Postconditions (success):
    - Alerta criado na tabela `Alert`
    - POST enviado para `https://ntfy.sh/{topic}`
    - `email_sent = True` registado no alerta
- Postconditions (failure/cancel):
    - Alerta criado mas notificação não enviada
    - Erro registado no log
- Related requirements: REQ-7, REQ-8, REQ-9

### Main flow (happy path)
1. Sistema deteta nova cotação e calcula variação percentual
2. Sistema compara variação com `threshold_high` / `threshold_low` do ativo
3. Sistema verifica `already_alerted()` — janela de 60 minutos
4. Sistema cria registo em `Alert`
5. `send_ntfy_notification()` faz HTTP POST para `https://ntfy.sh/{topic}`
6. POST inclui: título, corpo com variação/preço/hora, prioridade "high", tag emoji
7. Sistema regista `email_sent = True` no alerta

### Alternative flows
A1. Variação não atinge nenhum limiar → nenhum alerta gerado  
A2. Alerta já enviado nos últimos 60 minutos → sistema ignora (evita duplicação)  
A3. `ntfy_topic` vazio → sistema cria alerta mas não envia notificação

### Exceptions / errors
E1. Falha no POST a ntfy.sh → erro registado em log, `email_sent` permanece False  
E2. Timeout da API yfinance → sistema usa último preço registado (fallback)

---

## UC-09 — Monitorizar ações (ciclo automático)
- Primary actor: Sistema
- Supporting actors: API yfinance
- Goal: Monitorizar automaticamente os ativos ativos e detetar variações relevantes
- Preconditions:
    - Pelo menos uma ação com `is_active=True`
    - `run_monitor` management command em execução
- Trigger: Ciclo periódico baseado em `UserSettings.monitoring_interval`
- Postconditions (success):
    - Preços atualizados em `StockPrice`
    - Alertas gerados e notificações enviadas quando necessário
- Related requirements: REQ-2, REQ-3, REQ-6, REQ-7, REQ-8, REQ-13

### Main flow (happy path)
1. `run_monitoring_cycle()` obtém `UserSettings` singleton
2. Itera todos os `Stock` com `is_active=True`
3. Para cada ativo: chama `monitor_stock()` → `fetch_price()` → guarda `StockPrice`
4. Calcula variação vs preço anterior
5. Chama `check_and_alert()` → cria alerta e envia ntfy.sh se necessário
6. Daemon aguarda `monitoring_interval` segundos e repete

### Alternative flows
A1. Nenhuma variação relevante → ciclo continua sem gerar alertas  
A2. API falha para um ativo → usa fallback, continua para os restantes

### Exceptions / errors
E1. API indisponível → sistema usa último valor válido para esse ativo  
E2. Sem preço anterior nem atual → ativo ignorado nesse ciclo com registo de erro

---

## UC-10 — Autenticar utilizador
- Primary actor: Utilizador
- Goal: Aceder ao sistema de forma autenticada ou como visitante
- Preconditions: Sistema em execução
- Trigger: Utilizador acede a qualquer URL protegida
- Related requirements: REQ-15

### Main flow (happy path)
1. Utilizador é redirecionado para `/login/`
2. Introduz username (ou email) e password
3. Sistema autentica e redireciona para destino original

### Alternative flows
A1. Login com email em vez de username → sistema resolve email → username automaticamente  
A2. Utilizador regista nova conta em `/register/` com username, email e password  
A3. Utilizador acede como visitante via `/guest/` → conta `visitante` criada on-demand

### Exceptions / errors
E1. Credenciais incorretas → mensagem de erro, formulário mantido  
E2. Email já registado → registo rejeitado com mensagem

---

## UC-11 — Pesquisar ativos mundiais
- Primary actor: Utilizador
- Supporting actors: Yahoo Finance Search API
- Goal: Encontrar qualquer ativo financeiro mundial para visualizar ou adicionar ao portfolio
- Preconditions: Utilizador autenticado
- Trigger: Utilizador usa a barra de pesquisa
- Related requirements: REQ-16

### Main flow (happy path)
1. Utilizador escreve termo na barra de pesquisa
2. Autocomplete (`/search/suggest/`) sugere resultados a partir de 2 caracteres
3. Utilizador clica num resultado → redireciona para `/ativo/{symbol}/`
4. Ou utilizador submete pesquisa completa → `/search/?q=...` lista todos os resultados

### Exceptions / errors
E1. API de pesquisa indisponível → lista vazia, sem erro crítico

---

## UC-12 — Consultar detalhe de ativo
- Primary actor: Utilizador
- Supporting actors: API yfinance
- Goal: Ver informação fundamental completa e gráfico de preço de um ativo
- Preconditions: Utilizador autenticado
- Trigger: Utilizador acede a `/ativo/{symbol}/`
- Related requirements: REQ-2, REQ-16

### Main flow (happy path)
1. Sistema obtém `info` completo do ativo via yfinance
2. Apresenta preço atual, variação diária, setor, indústria
3. Apresenta ~35 métricas fundamentais (P/E, P/B, margens, ROE, ROA, dívida, etc.)
4. Apresenta gráfico de preços do último mês (Chart.js)
5. Apresenta últimos 10 alertas do ativo (se monitorizado)
6. Permite adicionar/remover/ativar-pausar ativo diretamente na página

---

## UC-13 — Visualizar visão geral do mercado
- Primary actor: Utilizador
- Supporting actors: API yfinance, Yahoo Finance Screener, API BCB
- Goal: Ter uma visão rápida do estado do mercado ao abrir o sistema
- Preconditions: Utilizador autenticado
- Trigger: Utilizador acede a `/` (home)
- Related requirements: REQ-17

### Main flow (happy path)
1. Sistema carrega em paralelo (ThreadPoolExecutor): market overview, top movers, Tesouro, taxas BCB
2. Apresenta ativos em destaque: EUA, Brasil, FIIs, Crypto
3. Apresenta Top 10 maiores subidas do dia por categoria
4. Apresenta simulação de Tesouro Direto via ETFs B3
5. Apresenta taxas BCB: SELIC, IPCA, CDI
6. Todos os dados são cacheados 5 minutos (300s) para performance

### Exceptions / errors
E1. API BCB indisponível → secção de taxas não apresentada  
E2. yfinance indisponível → secção afetada fica vazia, restantes continuam

---

## Variant-driven notes
- Performance: Timeout 5s por requisição à API; cache de 5 min na home; ThreadPoolExecutor para paralelismo (REQ-13)
- Robustez: Retry automático (3x) e fallback para último preço válido (REQ-2)
- Anti-duplicação: Janela de 60 minutos por ativo/direção (REQ-8)
- Notificações: ntfy.sh via HTTP POST — sem SMTP, sem credenciais (REQ-7)
- Persistência: Django ORM / SQLite — sem ficheiros JSON (REQ-3, REQ-9)
