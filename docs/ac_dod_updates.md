# AC & DoD Updates — Lab 10

## Contexto

Durante a revisão estática (Lab 10) e a elaboração dos test cases (Lab 9), foram identificados problemas concretos nos Acceptance Criteria e na Definition of Done:
- ACs vagas que não especificavam o resultado exato verificável
- Um bug real causado por AC incompleto (encoding de headers HTTP)
- ACs que não cobriam edge cases identificados nos TCs
- DoD sem critérios de verificação para comportamentos NFR e variant-driven

---

## Acceptance Criteria improvements (5 itens)

---

### Item 1 — REQ-7 AC-3 (variant-driven: encoding HTTP)

- **Requirement:** REQ-7 — Envio de notificações push (ntfy.sh)
- **Before:**
  - AC-3: Notificação inclui título, prioridade "high" e emoji adequado (📈/📉)
- **After:**
  - AC-3: O header HTTP `Title` contém apenas caracteres ASCII (sem `—`, `–` ou outros Unicode); o corpo da mensagem é codificado em UTF-8 (emojis 📈/📉 permitidos no corpo, não nos headers); a prioridade é o string literal `"high"`; a tag é `"chart_with_upwards_trend"` para Alta e `"chart_with_downwards_trend"` para Baixa
- **Why changed:**
  - Durante a implementação, o header `Title` continha `"TRT Alerta — AAPL Alta"` com travessão Unicode (`—`, U+2014). Isso causou o erro real: `'latin-1' codec can't encode character '—'`. O AC original não especificava a restrição de encoding dos headers HTTP. Sem esta distinção (headers ASCII vs corpo UTF-8), qualquer desenvolvedor poderia reproduzir o bug. É um critério variant-driven porque o comportamento correto é não-óbvio e diverge das expectativas habituais de strings em Python.

---

### Item 2 — REQ-8 AC-1 (variant-driven: precisão da janela)

- **Requirement:** REQ-8 — Evitar notificações duplicadas
- **Before:**
  - AC-1: Sistema não envia mais do que uma notificação por ativo/direção dentro de 60 minutos
- **After:**
  - AC-1: O sistema não cria um novo `Alert` se já existir um registo na tabela `Alert` com o mesmo `stock` e o mesmo `direction` com `sent_at >= now() - 60 minutos`; a janela é avaliada por par `(stock, direction)` — um alerta de `direction='high'` para AAPL não bloqueia um alerta de `direction='low'` para AAPL; um alerta de AAPL não bloqueia um alerta de TSLA
- **Why changed:**
  - O AC original usava "por ativo/direção" sem definir o que constitui um par único. TC-006 e TC-007 revelaram que era necessário especificar explicitamente: (a) que a janela é por `(stock_id, direction)` em conjunto, e (b) que Alta e Baixa são independentes. Sem esta precisão, um implementador poderia bloquear todos os alertas de um ativo durante 60 minutos, o que seria incorreto. É variant-driven porque a granularidade da janela é uma decisão de negócio não-trivial.

---

### Item 3 — REQ-2 AC-3 (fallback sem StockPrice)

- **Requirement:** REQ-2 — Obter cotações via API
- **Before:**
  - AC-3: o sistema usa o último valor válido registado (fallback)
- **After:**
  - AC-3a: Se a API falhar em todas as 3 tentativas e existir um `StockPrice` anterior para o ativo, `monitor_stock()` usa esse preço via `get_last_price()` e inclui `'fallback': True` no resultado; nenhum novo `StockPrice` é criado
  - AC-3b: Se a API falhar em todas as 3 tentativas e **não existir nenhum** `StockPrice` para o ativo, `monitor_stock()` retorna `{'symbol': ..., 'error': 'Sem dados'}` e o ativo é ignorado nesse ciclo
- **Why changed:**
  - O AC original dizia "último valor válido" sem especificar o que acontece quando não existe valor prévio. TC-010 testou o caso com StockPrice existente, mas o edge case "sem histórico" não estava coberto por nenhum TC nem pelo AC. A separação em AC-3a e AC-3b torna ambos os caminhos verificáveis independentemente.

---

### Item 4 — REQ-13 AC-1 (medição concreta do timeout)

- **Requirement:** REQ-13 — Tempo de resposta (NFR, variant-driven)
- **Before:**
  - AC-1: Cada requisição à API tem timeout máximo de 5 segundos
- **After:**
  - AC-1: Cada chamada a `fetch_price()` tem um timeout implícito de 5 segundos herdado do comportamento por defeito do yfinance; em caso de implementação explícita de timeout (ex: `requests.get(..., timeout=5)`), o valor deve ser ≤ 5 segundos; verificável por inspeção estática do código e por mock de latência em teste de integração
- **Why changed:**
  - O AC original não distinguia se o timeout era configurado explicitamente ou herdado. Na implementação atual, o timeout é implícito via yfinance (não configurado explicitamente no código de `fetch_price()`). A revisão estática revelou que o AC precisava de especificar o método de verificação — sem isso, o AC é tecnicamente não-testável de forma automatizada.

---

### Item 5 — REQ-15 AC-1 (regras de validação da password)

- **Requirement:** REQ-15 — Autenticação de utilizadores
- **Before:**
  - AC-1: Utilizador pode registar conta com username, email e password
- **After:**
  - AC-1: Utilizador pode registar conta com username (≥ 3 caracteres, único), email (único, formato válido) e password (≥ 8 caracteres); o sistema rejeita registo com username já existente mostrando "Este nome de utilizador já está em uso."; o sistema rejeita registo com email já existente mostrando "Este email já está registado."; o sistema rejeita password com < 8 caracteres mostrando "A password deve ter pelo menos 8 caracteres."
- **Why changed:**
  - O AC original era demasiado genérico — não especificava as regras de validação nem as mensagens de erro concretas. Sem mensagens esperadas explícitas, um teste de aceitação não consegue verificar o AC. TC-012 revelou a necessidade de especificar resultados exatos para testes negativos do registo.

---

## DoD updates (4 itens)

---

### DoD Update 1 — Critério de encoding para notificações HTTP

- **Secção:** DoD — Feature (funcionalidade implementada)
- **Before:**
  - (não existia critério sobre encoding de comunicações HTTP externas)
- **After:**
  - 7. Para funcionalidades que fazem chamadas HTTP com headers: headers contêm apenas ASCII puro; corpo codificado em UTF-8 se contiver caracteres não-ASCII; verificado por inspeção estática e por envio de notificação de teste
- **Why:**
  - O bug de encoding dos headers ntfy.sh (erro `latin-1 codec can't encode '—'`) foi causado pela ausência deste critério no DoD. Uma feature que envia HTTP requests com headers Unicode nunca teria passado num DoD que incluísse este check. Critério transversal a qualquer integração HTTP.

---

### DoD Update 2 — Verificação de boundary values para inputs numéricos

- **Secção:** DoD — Feature (funcionalidade implementada)
- **Before:**
  - 3. Fluxos alternativos e de exceção tratados (mensagens de erro claras)
- **After:**
  - 3. Fluxos alternativos e de exceção tratados (mensagens de erro claras); para campos com intervalo definido (ex: intervalo 1–3600, limiares 0.01–100), os valores de fronteira (mínimo válido, máximo válido, mínimo-1, máximo+1) foram testados e produzem os resultados esperados
- **Why:**
  - TC-003 (boundary para REQ-3) revelou que os critérios `< 1` e `> 3600` são testados pela validação do formulário, mas o DoD anterior não exigia verificação de boundary. Sem este critério, um desenvolvedor poderia implementar `<= 0` em vez de `< 1` e o DoD seria satisfeito na mesma.

---

### DoD Update 3 — Critério de traceabilidade entre AC, TC e código

- **Secção:** DoD — Requirement (REQ-###)
- **Before:**
  - 6. Está ligado a Use Cases relevantes
- **After:**
  - 6. Está ligado a Use Cases relevantes; cada AC tem pelo menos um Test Case (TC-###) ou cenário Gherkin que o verifica; a ligação está registada em `docs/traceability_req_ac_tc.md`
- **Why:**
  - A revisão dos Lab 9 e 10 mostrou que ACs sem TC associado (ex: REQ-15 AC-1 no Lab 9) escapam à verificação. Tornar a traceabilidade AC→TC um critério do DoD garante que nenhum AC fica sem cobertura de teste.

---

### DoD Update 4 — Verificação de NFR variant-driven por medição ou mock

- **Secção:** DoD — Requirement (REQ-###) para NFRs
- **Before:**
  - 10. Possui método de verificação definido (teste, demo ou medição)
- **After:**
  - 10. Possui método de verificação definido (teste, demo ou medição); para NFRs variant-driven (ex: timeout, retry, anti-duplicação), o método de verificação é: (a) inspeção estática do código OU (b) teste de integração com mock que simula a condição de falha/fronteira; "demo" não é suficiente para NFRs que envolvem timing ou contagem de tentativas
- **Why:**
  - REQ-13 (timeout/retry) e REQ-8 (janela 60 min) são variant-driven NFRs que não podem ser verificados por demo simples — precisam de mocks ou inspeção. O DoD original permitia "demo" como método único, o que seria inadequado para estes requisitos.
