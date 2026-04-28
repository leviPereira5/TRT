# Generated Scope — Lab 8

---

## Selected slice
- Slice: A (Core System Setup + Monitoring Foundation)
- Description: Gestão de ações, configuração de alertas e preparação da base para monitorização do sistema financeiro (UC-01 a UC-09 conceptualizados, mas apenas parte do fluxo implementado)

---

## Actors / roles
- Primary actor: Utilizador
- Secondary actor: Sistema (automático)
- External actor: API de Mercado Financeiro
- External actor: Serviço de Notificação

---

## Use Cases implemented
- UC-01: Gerir ações monitorizadas
- UC-02: Configurar limites de alerta
- UC-03: Configurar intervalo de monitorização
- UC-04: Consultar cotação de ações
- UC-05: Calcular variação percentual
- UC-06: Enviar notificação de alerta
- UC-07: Registar histórico de alertas
- UC-08: Evitar notificações duplicadas
- UC-09: Monitorizar ações

---

## Requirements implemented (max 10)
- REQ-1: O sistema deve permitir o cadastro de ações pelo utilizador
- REQ-10: O sistema deve permitir adicionar e remover ações dinamicamente
- REQ-14: O sistema deve persistir configurações em ficheiro
- REQ-2: O sistema deve obter cotações através de API de mercado financeiro
- REQ-3: O sistema deve permitir configurar intervalo de monitorização
- REQ-4: O sistema deve permitir definir limite mínimo de alta
- REQ-5: O sistema deve permitir definir limite mínimo de baixa
- REQ-6: O sistema deve calcular variação percentual automaticamente
- REQ-7: O sistema deve enviar notificação quando limite for atingido
- REQ-8: O sistema deve evitar notificações duplicadas

---

## Variant constraints implemented (min. 2)
- Persistência de dados em ficheiros JSON para garantir continuidade entre execuções
- Evitar notificações duplicadas para o mesmo evento de variação
- Tratamento de falhas de API (timeout / indisponibilidade)
- Monitorização contínua baseada em intervalo configurável
- Validação de dados recebidos da API antes de processamento

---

## Out of scope
- Implementação real de API de mercado financeiro (apenas simulação ou integração parcial)
- Sistema completo de notificações externas (email/Telegram real)
- Dashboard avançado com gráficos
- Autenticação de utilizadores (login/sessões)
- Base de dados relacional (SQL/PostgreSQL)
- Sistema completo de histórico persistente avançado
- Otimizações de performance em larga escala

---

## Notes
Este scope representa a visão completa do sistema financeiro de monitorização, mas o Lab 8 implementa apenas um subconjunto funcional simplificado (principalmente UC-01 e UC-02). Os restantes use cases representam comportamento futuro ou conceptual para garantir rastreabilidade completa do sistema.