# Objectives

## OBJ-1 — Monitorização Automática de Cotações em Tempo Real

- **Description (why/outcome):** Permitir que o sistema obtenha e monitorize cotações de ações continuamente, garantindo que o investidor seja notificado rapidamente sobre variações relevantes no mercado.
- **Stakeholders impacted:** Investidor Individual, Sistema de API de Mercado Financeiro
- **Success signal (how we know):** O sistema consulta cotações com sucesso via API e deteta variações dentro do intervalo de verificação configurado.
- **Variant-driven:** Yes

---

## OBJ-2 — Configuração Personalizada de Alertas por Perfil de Investidor

- **Description:** Permitir que o investidor defina os seus próprios limites percentuais de alta e baixa para disparo de notificações, adaptando o sistema ao seu perfil de risco.
- **Stakeholders impacted:** Investidor Individual
- **Success signal:** O investidor consegue configurar percentuais mínimos de alta e baixa, e o sistema respeita esses limites ao gerar alertas.
- **Variant-driven:** Yes

---

## OBJ-3 — Registo e Persistência do Histórico de Alertas e Variações

- **Description:** Garantir que todas as variações detetadas e notificações enviadas sejam armazenadas de forma persistente, permitindo ao investidor consultar o histórico de eventos.
- **Stakeholders impacted:** Investidor Individual, Sistema de Persistência
- **Success signal:** O histórico de alertas e variações está disponível para consulta após reinício do sistema, sem perda de dados.
- **Variant-driven:** No

---

# Critical Success Factors

## CSF-1 — Integração Fiável com API de Mercado Financeiro

- **Linked objective:** OBJ-1
- **Definition (what must go right):** O sistema deve integrar-se com uma API de mercado financeiro que forneça cotações em tempo real ou com atraso aceitável, com tratamento de falhas e tolerância a erros.
- **Evidence (how we check):** Cotações são obtidas com sucesso dentro do tempo máximo de resposta definido; falhas de API são tratadas sem interrupção do serviço.
- **Variant-driven:** Yes

### Linked requirements

- REQUISITO 2 – O sistema deve obter cotações em tempo real ou com atraso aceitável por meio de uma API de mercado financeiro
- REQUISITO 1 – O sistema deve permitir o cadastro de uma ou mais ações pelo utilizador
- REQUISITO 3 – O sistema deve permitir configurar o intervalo de verificação
- FEATURE 2 – Consulta de Cotação com Tempo Máximo de Resposta
- EPIC 9 – Tolerância a Falhas e Robustez

---

## CSF-2 — Configuração Precisa e Funcional dos Limites de Alerta

- **Linked objective:** OBJ-2
- **Definition:** O sistema deve permitir ao utilizador definir percentuais mínimos de alta e baixa de forma independente, e o motor de cálculo deve aplicar esses limites corretamente no disparo de notificações.
- **Evidence:** Notificações são disparadas apenas quando os limiares configurados são atingidos; testes com variações acima e abaixo dos limites confirmam o comportamento esperado.
- **Variant-driven:** Yes

### Linked requirements

- REQUISITO 4 – O sistema deve permitir definir um percentual mínimo de alta para disparo de notificação
- REQUISITO 5 – O sistema deve permitir definir um percentual mínimo de baixa para disparo de notificação
- FEATURE 3 – Configuração Personalizada de Limites de Alerta
- FEATURE 4 – Cálculo Automático da Variação Percentual
- EPIC 6 – Prevenção de Notificações Duplicadas

---

## CSF-3 — Persistência e Rastreabilidade do Histórico de Eventos

- **Linked objective:** OBJ-3
- **Definition:** O sistema deve armazenar de forma durável todas as notificações enviadas e variações registadas, garantindo que os dados não sejam perdidos entre sessões.
- **Evidence:** Após reinício do sistema, o histórico de alertas permanece acessível e íntegro; registos incluem data, hora, ação e variação percentual.
- **Variant-driven:** No

### Linked requirements

- EPIC 7 – Histórico de Alertas e Variações
- EPIC 8 – Persistência de Configurações
- FEATURE 6 – Registo e Controlo de Notificações
- FEATURE 5 – Envio de Notificações com Integração Externa
- EPIC 10 – Configuração de Intervalo de Monitorização  