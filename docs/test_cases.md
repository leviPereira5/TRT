# Test Cases — Lab 9

## Selected requirements

| Category | REQ | Description |
|---|---|---|
| FR | REQ-1 | Cadastro de ações |
| FR | REQ-7 | Envio de notificações push (ntfy.sh) |
| FR | REQ-9 | Histórico de alertas |
| FR | REQ-15 | Autenticação de utilizadores |
| NFR | REQ-8 | Evitar notificações duplicadas |
| NFR | REQ-13 | Tempo de resposta / robustez |
| Other | REQ-2 | Obter cotações via API |
| Other | REQ-3 | Configurar intervalo de monitorização |

---

## TC-001 — Adicionar ação válida ao portfolio (happy path)

- **Type:** Acceptance
- **Priority:** H
- **Related requirements:** REQ-1
- **Preconditions:** Utilizador autenticado; símbolo AAPL não existe na base de dados
- **Test data:** symbol=AAPL, tipo=stock_us
- **Steps:**
  1. Navegar para `/portfolio/`
  2. Preencher o campo "Símbolo" com `AAPL` e selecionar tipo "Ação EUA"
  3. Deixar o campo "Nome" vazio
  4. Submeter o formulário
- **Expected results:**
  - AAPL aparece na tabela do portfolio com estado "Ativa"
  - Nome preenchido automaticamente via yfinance (ex: "Apple Inc.")
  - Mensagem de sucesso: "Adicionado: AAPL — Apple Inc."
  - Registo persistido — visível após reinício do servidor
- **Notes:** Testa AC-1 e AC-5 de REQ-1

---

## TC-002 — Rejeitar símbolo duplicado (negative)

- **Type:** Acceptance
- **Priority:** H
- **Related requirements:** REQ-1
- **Preconditions:** Símbolo AAPL já existe na base de dados
- **Test data:** symbol=AAPL, tipo=stock_us
- **Steps:**
  1. Navegar para `/portfolio/`
  2. Preencher o campo "Símbolo" com `AAPL`
  3. Submeter o formulário
- **Expected results:**
  - Formulário não é submetido com sucesso
  - Mensagem de erro: "AAPL já está na lista."
  - Nenhum registo duplicado criado na base de dados
- **Notes:** Testa AC-3 de REQ-1

---

## TC-003 — Intervalo de monitorização: valores de fronteira (boundary)

- **Type:** System
- **Priority:** M
- **Related requirements:** REQ-3
- **Preconditions:** Utilizador autenticado e em `/settings/`
- **Test data:**

  | Valor | Resultado esperado |
  |---|---|
  | 0 | Rejeitado |
  | 1 | Aceite (mínimo válido) |
  | 60 | Aceite |
  | 3600 | Aceite (máximo válido) |
  | 3601 | Rejeitado |

- **Steps:**
  1. Navegar para `/settings/`
  2. Inserir cada valor da tabela no campo "Intervalo (segundos)"
  3. Submeter o formulário
- **Expected results:**
  - Valores 1 e 3600 são aceites e guardados; mensagem "Configurações guardadas!"
  - Valores 0 e 3601 são rejeitados com mensagem "Entre 1 e 3600 segundos."
- **Notes:** Testa AC-1 e AC-3 de REQ-3; cobre limites mínimo e máximo

---

## TC-004 — Notificação push enviada quando limiar é atingido (happy path)

- **Type:** Integration
- **Priority:** H
- **Related requirements:** REQ-7, REQ-4
- **Preconditions:**
  - `UserSettings.ntfy_topic = "trt-test-topic"`
  - Stock AAPL com `threshold_high = 1.0` e `is_active = True`
  - Último `StockPrice` de AAPL = 100.00
- **Test data:** Novo preço simulado = 102.00 (variação = +2.0%, acima de 1.0%)
- **Steps:**
  1. Invocar `monitor_stock(stock, settings)` com novo preço = 102.00
  2. Verificar tabela `Alert` na base de dados
  3. Verificar logs do servidor
- **Expected results:**
  - Registo criado em `Alert` com `direction='high'`, `variation=2.00`, `price=102.00`
  - `alert.email_sent = True`
  - HTTP POST enviado para `https://ntfy.sh/trt-test-topic`
  - Log: "Notificação ntfy enviada: AAPL Alta"
- **Notes:** Testa AC-1 a AC-4 de REQ-7

---

## TC-005 — Sem notificação quando tópico ntfy.sh está vazio (negative)

- **Type:** Integration
- **Priority:** M
- **Related requirements:** REQ-7
- **Preconditions:**
  - `UserSettings.ntfy_topic = ""` (campo vazio)
  - Stock AAPL com `threshold_high = 1.0`, variação > 1.0%
- **Test data:** Novo preço que gera variação de +3.0%
- **Steps:**
  1. Invocar `send_ntfy_notification(alert, settings)` com `settings.ntfy_topic = ""`
  2. Verificar que nenhum HTTP POST é feito
- **Expected results:**
  - Função retorna imediatamente sem fazer qualquer pedido HTTP
  - `alert.email_sent` permanece `False`
  - Nenhuma exceção lançada
- **Notes:** Testa AC-5 de REQ-7; comportamento silencioso esperado

---

## TC-006 — Notificação duplicada bloqueada dentro de 60 minutos (negative)

- **Type:** Integration
- **Priority:** H
- **Related requirements:** REQ-8
- **Preconditions:**
  - Alerta `direction='high'` para AAPL já criado há 30 minutos
  - Stock AAPL com `threshold_high = 1.0`
- **Test data:** Nova variação de +2.0% para AAPL
- **Steps:**
  1. Invocar `check_and_alert(stock, variation=2.0, new_price=..., settings)` 
  2. Verificar resultado retornado
  3. Verificar tabela `Alert`
- **Expected results:**
  - `already_alerted()` retorna `True`
  - `check_and_alert()` retorna `None`
  - Nenhum novo registo criado em `Alert`
  - Nenhum POST enviado para ntfy.sh
- **Notes:** Testa AC-1 e AC-2 de REQ-8

---

## TC-007 — Alerta duplicado permitido após 60 minutos (alternative flow)

- **Type:** Integration
- **Priority:** M
- **Related requirements:** REQ-8
- **Preconditions:**
  - Último alerta `direction='high'` para AAPL criado há 61 minutos
  - `ntfy_topic` configurado
- **Test data:** Nova variação de +2.0%
- **Steps:**
  1. Invocar `check_and_alert(stock, variation=2.0, ...)`
  2. Verificar tabela `Alert`
- **Expected results:**
  - `already_alerted()` retorna `False`
  - Novo alerta criado com `direction='high'`
  - Notificação ntfy.sh enviada
- **Notes:** Testa AC-3 de REQ-8; verifica que a janela expira corretamente

---

## TC-008 — Histórico de alertas acessível (happy path)

- **Type:** Acceptance
- **Priority:** M
- **Related requirements:** REQ-9
- **Preconditions:**
  - Utilizador autenticado
  - Pelo menos 1 alerta existente na tabela `Alert`
- **Test data:** Alerta pré-existente: AAPL, direction=high, variation=2.50, price=155.00
- **Steps:**
  1. Navegar para `/alerts/`
  2. Verificar conteúdo da página
- **Expected results:**
  - Tabela apresenta o alerta com: símbolo "AAPL", direção "Alta", variação "+2.50%", preço "155.00", data/hora
  - Página carrega sem erros (HTTP 200)
- **Notes:** Testa AC-1 a AC-3 de REQ-9

---

## TC-009 — Retry automático em falha da API (NFR)

- **Type:** Integration
- **Priority:** H
- **Related requirements:** REQ-2, REQ-13
- **Preconditions:** yfinance retorna exceção nas primeiras 2 chamadas; na 3.ª retorna preço válido 150.00
- **Test data:** symbol=AAPL; mock: [Exception, Exception, 150.00]
- **Steps:**
  1. Invocar `fetch_price('AAPL')` com API simulada
  2. Contar o número de tentativas feitas
  3. Verificar valor retornado
- **Expected results:**
  - Função faz exatamente 3 tentativas
  - Retorna `Decimal('150.00')` na 3.ª tentativa
  - Log regista "Tentativa 1 falhou" e "Tentativa 2 falhou"
- **Notes:** Testa AC-2 de REQ-13 e retry de REQ-2

---

## TC-010 — Fallback para último preço válido (NFR)

- **Type:** Integration
- **Priority:** H
- **Related requirements:** REQ-2, REQ-13
- **Preconditions:**
  - yfinance retorna exceção em todas as 3 tentativas
  - `StockPrice` mais recente para AAPL = 148.00
- **Test data:** symbol=AAPL; mock: [Exception, Exception, Exception]
- **Steps:**
  1. Invocar `monitor_stock(stock, settings)` com API simulada
  2. Verificar resultado retornado
- **Expected results:**
  - `fetch_price()` retorna `None`
  - `monitor_stock()` usa `get_last_price()` → retorna `148.00`
  - Resultado contém `{'price': 148.00, 'fallback': True}`
  - Nenhum novo `StockPrice` criado
- **Notes:** Testa AC-3 de REQ-13 e fallback de REQ-2

---

## TC-011 — Login com endereço de email (alternative flow)

- **Type:** Acceptance
- **Priority:** H
- **Related requirements:** REQ-15
- **Preconditions:** Conta existente com username=`levi`, email=`levi@mail.com`, password=`pass1234`
- **Test data:** login field=`levi@mail.com`, password=`pass1234`
- **Steps:**
  1. Navegar para `/login/`
  2. Inserir `levi@mail.com` no campo "Utilizador ou Email"
  3. Inserir `pass1234` no campo "Password"
  4. Submeter o formulário
- **Expected results:**
  - Utilizador autenticado com sucesso
  - Redirecionado para `/`
  - Session cookie criado
- **Notes:** Testa AC-2 de REQ-15; verifica resolução email → username

---

## TC-012 — Login com credenciais incorretas (negative)

- **Type:** Acceptance
- **Priority:** H
- **Related requirements:** REQ-15
- **Preconditions:** Conta existente com username=`levi`
- **Test data:** username=`levi`, password=`wrongpassword`
- **Steps:**
  1. Navegar para `/login/`
  2. Inserir `levi` e `wrongpassword`
  3. Submeter o formulário
- **Expected results:**
  - Página `/login/` recarregada (sem redirecionamento)
  - Mensagem de erro: "Utilizador ou password incorretos."
  - Utilizador não autenticado
- **Notes:** Testa AC-1 de REQ-15; verifica que acesso não autorizado é bloqueado

---

## Coverage summary

| Coverage type | Test cases |
|---|---|
| Happy path | TC-001, TC-004, TC-008, TC-011 |
| Alternative flow | TC-007, TC-011 |
| Negative / error | TC-002, TC-005, TC-006, TC-012 |
| Boundary | TC-003 |
| NFR (performance/robustez) | TC-009, TC-010 |
