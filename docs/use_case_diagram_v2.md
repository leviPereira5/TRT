# Use Case Diagram v2 — Lab 6

## System boundary
- System name: Financial Market Monitoring System
- Slice covered: Monitorização automática de ações e geração de alertas com base em variações percentuais

## System Boundary Definition
O sistema inclui:
- Gestão de ações monitorizadas
- Configuração de limites e intervalos
- Integração com API de mercado financeiro
- Cálculo automático de variações percentuais
- Geração e envio de notificações
- Persistência de histórico e configurações

O sistema NÃO inclui:
- Implementação da API externa
- Infraestrutura do serviço de notificações (email/Telegram)

## Actors (2–4)
- A1: Utilizador (Investidor Individual)
- A2: API de Mercado Financeiro
- A3: Serviço de Notificação

## Use cases (min. 6)
- UC-01: Gerir ações monitorizadas
- UC-02: Configurar limites de alerta
- UC-03: Configurar intervalo de monitorização
- UC-04: Consultar cotação de ações
- UC-05: Calcular variação percentual
- UC-06: Enviar notificação de alerta
- UC-07: Registar histórico de alertas
- UC-08: Evitar notificações duplicadas
- UC-09: Monitorizar ações

## Modeling notes (refinement)
- UC-04 inclui UC-05 pois o cálculo depende dos dados obtidos
- UC-06 inclui UC-07 e UC-08 (comportamentos obrigatórios)
- Relações <<include>> usadas apenas para comportamento obrigatório e reutilizado

## Diagram file
- Path: `docs/diagrams/use_case_diagram_v2.puml`