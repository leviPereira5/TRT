# Objectives & Critical Success Factors

## OBJ-1 — Monitorização Automática de Cotações

- **Description:** Permitir que o sistema obtenha e monitorize cotações de ativos financeiros continuamente, garantindo que o investidor seja notificado rapidamente sobre variações relevantes no mercado.
- **Stakeholders impacted:** Utilizador (Investidor Individual), API yfinance
- **Success signal:** O daemon `run_monitor` consulta cotações com sucesso via yfinance, deteta variações dentro do intervalo configurado e envia notificação push via ntfy.sh.
- **Variant-driven:** Yes

---

## OBJ-2 — Configuração Personalizada de Alertas por Ativo

- **Description:** Permitir que o investidor defina os seus próprios limiares percentuais de alta e baixa independentemente para cada ativo, e configure o canal de notificação push (ntfy.sh) sem necessidade de credenciais.
- **Stakeholders impacted:** Utilizador (Investidor Individual)
- **Success signal:** O investidor configura limiares por ativo e tópico ntfy.sh; o sistema respeita esses limiares ao gerar alertas e as notificações chegam ao telemóvel automaticamente.
- **Variant-driven:** Yes

---

## OBJ-3 — Histórico e Rastreabilidade de Eventos

- **Description:** Garantir que todos os alertas gerados e cotações registadas sejam armazenados de forma persistente em base de dados, permitindo ao investidor consultar o histórico de eventos.
- **Stakeholders impacted:** Utilizador (Investidor Individual)
- **Success signal:** O histórico de alertas está disponível em `/alerts/` após reinício do servidor, sem perda de dados; cada registo inclui data, hora, ativo e variação percentual.
- **Variant-driven:** No

---

## OBJ-4 — Dashboard de Mercado e Pesquisa Global

- **Description:** Proporcionar ao investidor uma visão rápida e contextualizada do estado do mercado financeiro, incluindo ativos em destaque, maiores subidas do dia, taxas económicas e possibilidade de pesquisar qualquer ativo mundial.
- **Stakeholders impacted:** Utilizador (Investidor Individual)
- **Success signal:** A página inicial carrega dados atualizados de mercado (com cache de 5 min); pesquisa global funciona com autocomplete e redireciona para página de detalhe com ~35 métricas fundamentais.
- **Variant-driven:** Yes

---

# Critical Success Factors

## CSF-1 — Integração Fiável com API de Mercado Financeiro

- **Linked objective:** OBJ-1, OBJ-4
- **Definition:** O sistema deve integrar-se com yfinance e Yahoo Finance de forma robusta, com retry automático (3x), timeout de 5s e fallback para último valor válido.
- **Evidence:** Cotações obtidas com sucesso; falhas tratadas sem interrupção do serviço; logs registam tentativas e erros.
- **Variant-driven:** Yes

### Linked requirements
- REQ-2 — Obter cotações via API com retry e fallback
- REQ-13 — Timeout 5s, retry 3x, fallback
- REQ-16 — Pesquisa de ativos via Yahoo Finance Search API
- REQ-17 — Dados de mercado via screener + yfinance + BCB

---

## CSF-2 — Notificações Push Automáticas e Sem Configuração Complexa

- **Linked objective:** OBJ-2
- **Definition:** O sistema deve enviar notificações push ao telemóvel do utilizador via ntfy.sh sem necessidade de SMTP, passwords de aplicação ou qualquer credencial. O utilizador apenas configura um nome de tópico.
- **Evidence:** Utilizador recebe notificação no telemóvel após atingir limiar; botão "Enviar notificação de teste" em `/settings/test-ntfy/` confirma funcionamento.
- **Variant-driven:** Yes

### Linked requirements
- REQ-7 — Envio de notificações push via ntfy.sh
- REQ-8 — Anti-duplicação (janela 60 minutos)
- REQ-3 — Intervalo de monitorização configurável

---

## CSF-3 — Persistência e Rastreabilidade do Histórico

- **Linked objective:** OBJ-3
- **Definition:** O sistema deve armazenar de forma durável todos os alertas e cotações na base de dados SQLite via Django ORM, garantindo disponibilidade após reinício.
- **Evidence:** Após reinício do servidor, `/alerts/` apresenta histórico completo; tabelas `Alert` e `StockPrice` mantêm dados íntegros.
- **Variant-driven:** No

### Linked requirements
- REQ-9 — Histórico de alertas
- REQ-1 — Persistência de ações monitorizadas
- REQ-3 — Persistência do intervalo de monitorização

---

## CSF-4 — Experiência de Utilizador Acessível

- **Linked objective:** OBJ-4
- **Definition:** O sistema deve ser acessível a qualquer utilizador sem barreiras técnicas: autenticação simples, acesso de visitante, pesquisa intuitiva, e configuração de notificações sem conhecimentos técnicos.
- **Evidence:** Utilizador não técnico consegue: registar conta, adicionar ativo, configurar ntfy.sh e receber notificação no telemóvel em menos de 5 minutos.
- **Variant-driven:** No

### Linked requirements
- REQ-15 — Autenticação (login, registo, visitante)
- REQ-16 — Pesquisa global com autocomplete
- REQ-7 — ntfy.sh (sem SMTP, sem credenciais)
