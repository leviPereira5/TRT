# Acceptance Criteria

## REQ-1 — Cadastro de ações
- AC-1: Utilizador pode adicionar uma ação pelo símbolo (ex: AAPL, PETR4, BTC-USD)
- AC-2: Sistema normaliza o símbolo automaticamente (.SA para BR/FII, -USD para crypto)
- AC-3: Sistema rejeita símbolo já existente na lista
- AC-4: Utilizador pode remover uma ação existente
- AC-5: Lista de ações é persistida na base de dados após reinício

---

## REQ-2 — Obter cotações (Given/When/Then)
- Given que a API yfinance está disponível
- When o sistema consulta uma ação
- Then deve receber uma cotação válida dentro do tempo limite (3 tentativas, timeout 5s cada)

- Given que a API não responde
- When ocorre timeout ou erro
- Then o sistema executa até 3 tentativas (retry automático)

- Given falha persistente após 3 tentativas
- When todas as tentativas falham
- Then o sistema usa o último valor válido registado (fallback)

---

## REQ-3 — Configurar intervalo de monitorização
- AC-1: Utilizador pode definir intervalo entre 1 e 3600 segundos
- AC-2: Sistema aplica o intervalo corretamente no daemon `run_monitor`
- AC-3: Valores fora do intervalo (< 1 ou > 3600) são rejeitados com mensagem de erro
- AC-4: Configuração é persistida na base de dados

---

## REQ-4 — Limiar de alta por ativo (Given/When/Then)
- Given um limiar de alta definido de 5% para um ativo
- When a variação do ativo atinge ou ultrapassa 5%
- Then o sistema gera um alerta e envia notificação push via ntfy.sh

- Given valor inválido (negativo, > 100, ou não numérico)
- When o utilizador tenta guardar
- Then o sistema rejeita e apresenta mensagem de erro

---

## REQ-5 — Limiar de baixa por ativo
- AC-1: Utilizador pode definir limiar de baixa independente por ativo (default 5%)
- AC-2: Alerta de baixa é gerado quando variação negativa atinge o limiar
- AC-3: Valores inválidos são rejeitados (mesmas regras de REQ-4)

---

## REQ-6 — Cálculo de variação percentual
- AC-1: Variação é calculada automaticamente com base no preço anterior e atual
- AC-2: Fórmula: `((novo - antigo) / antigo) * 100`, arredondado a 2 casas decimais
- AC-3: Se não existir preço anterior, o preço atual é usado como base (variação 0%)

---

## REQ-7 — Envio de notificações push (ntfy.sh)
- AC-1: Sistema envia notificação push via ntfy.sh quando limiar é atingido
- AC-2: Notificação inclui: símbolo do ativo, direção (Alta/Baixa), variação (%) e preço atual
- AC-3: Notificação inclui título, prioridade "high" e emoji adequado (📈/📉)
- AC-4: Sistema regista a notificação no histórico (campo `email_sent = True`)
- AC-5: Se `ntfy_topic` não estiver configurado, a notificação é silenciosamente ignorada

---

## REQ-8 — Evitar notificações duplicadas
- AC-1: Sistema não envia mais do que uma notificação por ativo/direção dentro de 60 minutos
- AC-2: Verificação feita via `already_alerted()` antes de criar alerta

---

## REQ-9 — Histórico de alertas
- AC-1: Todos os alertas gerados são guardados na tabela `Alert`
- AC-2: Histórico acessível em `/alerts/` com os últimos 100 alertas
- AC-3: Histórico inclui: ativo, direção, variação, preço, data/hora

---

## REQ-13 — Tempo de resposta (Variant-driven)
- AC-1: Cada requisição à API tem timeout máximo de 5 segundos
- AC-2: Sistema executa até 3 tentativas antes de usar fallback
- AC-3: Sistema usa o último preço válido registado como fallback
- AC-4: Eventos de timeout e erros são registados via `logger`

---

## REQ-15 — Autenticação de utilizadores
- AC-1: Utilizador pode registar conta com username, email e password
- AC-2: Utilizador pode fazer login com username ou email
- AC-3: Acesso de visitante disponível sem registo (conta `visitante` criada automaticamente)
- AC-4: Todas as views protegidas redirecionam para `/login/` se não autenticado

---

## REQ-16 — Pesquisa de ativos
- AC-1: Utilizador pode pesquisar qualquer ativo mundial em `/search/`
- AC-2: Autocomplete em tempo real disponível via `/search/suggest/` (mínimo 2 caracteres)
- AC-3: Resultados incluem símbolo, nome, tipo e exchange
- AC-4: Cada resultado tem link direto para a página de detalhe do ativo

---

## REQ-17 — Visão geral do mercado
- AC-1: Página inicial apresenta ativos em destaque: EUA, Brasil, FIIs e Crypto
- AC-2: Secção "Top Movers" mostra os maiores ganhos do dia por categoria
- AC-3: Taxas BCB (SELIC, IPCA, CDI) são apresentadas com dados atualizados
- AC-4: Simulação de Tesouro Direto apresentada via ETFs B3 (IMAB11, B5P211, TESD11, XFIX11)
- AC-5: Dados são cacheados 5 minutos para evitar excesso de chamadas à API
