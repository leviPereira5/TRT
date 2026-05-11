# Requirements Validation

## REQ-1 — Cadastro de ações

- AC-1: O sistema permite adicionar uma ação por símbolo e tipo (EUA, Brasil, FII, Crypto)
- AC-2: Símbolo normalizado automaticamente (PETR4 → PETR4.SA, BTC → BTC-USD)
- AC-3: O sistema rejeita símbolo já existente na lista
- AC-4: O utilizador pode remover ações existentes
- AC-5: A lista de ações é persistida na base de dados após reinício

---

## REQ-2 — Obter cotações (Given/When/Then)

- Given que a API yfinance está disponível
- When o sistema consulta uma ação
- Then deve receber uma cotação válida em menos de 5 segundos

- Given que a API não responde
- When ocorre timeout ou erro
- Then o sistema executa até 3 tentativas (retry automático)

- Given falha persistente após 3 tentativas
- When todas as tentativas falham
- Then o sistema usa o último `StockPrice` registado (fallback)

---

## REQ-3 — Configurar intervalo de monitorização

- AC-1: Utilizador pode definir intervalo entre 1 e 3600 segundos via `/settings/`
- AC-2: O daemon `run_monitor` respeita o intervalo configurado em `UserSettings`
- AC-3: Valores fora do intervalo (< 1 ou > 3600) são rejeitados com mensagem de erro
- AC-4: Configuração é persistida na base de dados

---

## REQ-4 — Limiar de alta por ativo (Given/When/Then)

- Given um limiar de alta definido de 5% para o ativo AAPL
- When a variação de AAPL atinge ou ultrapassa 5%
- Then o sistema gera um alerta e envia notificação push via ntfy.sh

- Given valor inválido (negativo, > 100 ou não numérico)
- When o utilizador tenta guardar
- Then o sistema rejeita e apresenta mensagem de erro

---

## REQ-5 — Limiar de baixa por ativo

- AC-1: Utilizador pode definir limiar de baixa independente por ativo (default 5%)
- AC-2: Alerta de baixa é gerado quando variação negativa atinge ou supera o limiar
- AC-3: Valores inválidos são rejeitados (mesmas regras de REQ-4)

---

## REQ-7 — Envio de notificações push (ntfy.sh)

- AC-1: Sistema envia notificação push via HTTP POST para `https://ntfy.sh/{topic}` quando limiar é atingido
- AC-2: Notificação inclui: símbolo, direção (Alta/Baixa), variação (%), preço atual e timestamp
- AC-3: Notificação inclui título ASCII, prioridade "high" e tag emoji (📈/📉)
- AC-4: Sistema regista a notificação no histórico (`email_sent = True` no modelo Alert)
- AC-5: Se `ntfy_topic` não estiver configurado, notificação é silenciosamente ignorada (sem erro crítico)
- AC-6: Utilizador pode testar a notificação em `/settings/test-ntfy/`

---

## REQ-8 — Evitar notificações duplicadas

- AC-1: Sistema não envia mais do que uma notificação por ativo e direção dentro de 60 minutos
- AC-2: Verificação feita via `already_alerted()` antes de criar o alerta
- AC-3: Após 60 minutos, novo alerta pode ser gerado para o mesmo ativo e direção

---

## REQ-9 — Histórico de alertas

- AC-1: Todos os alertas gerados são guardados na tabela `Alert`
- AC-2: Histórico acessível em `/alerts/` com os últimos 100 alertas
- AC-3: Cada registo inclui: ativo, direção, variação (%), preço, data/hora

---

## REQ-13 — Tempo de resposta (Variant-driven)

- AC-1: Cada requisição à API tem timeout máximo de 5 segundos
- AC-2: Sistema executa até 3 tentativas antes de usar fallback
- AC-3: Sistema usa o último preço válido registado como fallback
- AC-4: Erros e timeouts são registados via `logger` Python

---

## REQ-15 — Autenticação de utilizadores

- AC-1: Utilizador pode registar conta com username, email e password (mín. 8 caracteres)
- AC-2: Utilizador pode fazer login com username ou email
- AC-3: Acesso de visitante disponível sem registo via `/guest/`
- AC-4: Todas as views protegidas redirecionam para `/login/` se não autenticado

---

## REQ-16 — Pesquisa de ativos

- AC-1: Utilizador pode pesquisar qualquer ativo mundial em `/search/`
- AC-2: Autocomplete disponível a partir de 2 caracteres via `/search/suggest/` (JSON)
- AC-3: Resultados incluem símbolo, nome, tipo e exchange
- AC-4: Cada resultado tem link direto para `/ativo/{symbol}/`

---

## REQ-17 — Visão geral do mercado

- AC-1: Página inicial (`/`) apresenta ativos em destaque: EUA, Brasil, FIIs, Crypto
- AC-2: Secção "Top Movers" mostra os maiores ganhos do dia por categoria
- AC-3: Taxas BCB (SELIC, IPCA, CDI) apresentadas com fonte e data
- AC-4: Simulação de Tesouro Direto via ETFs B3 (IMAB11, B5P211, TESD11, XFIX11)
- AC-5: Dados cacheados 5 minutos (BCB: 30 minutos) para performance
