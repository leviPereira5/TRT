# Use Cases — Lab 5

## UC-01 — Gerir ações monitorizadas
- Primary actor: Utilizador
- Supporting actors: —
- Goal: Permitir adicionar ou remover ações a monitorizar
- Preconditions: Sistema em execução
- Trigger: Utilizador decide gerir lista de ações
- Postconditions (success): Lista de ações atualizada
- Postconditions (failure/cancel): Nenhuma alteração feita
- Related requirements: REQ-1, REQ-10, REQ-14

### Main flow (happy path)
1. Utilizador acede à funcionalidade de gestão
2. Sistema apresenta lista atual de ações
3. Utilizador adiciona ou remove ações
4. Sistema valida dados
5. Sistema guarda configurações

### Alternative flows
A1. Utilizador adiciona ação inválida → sistema rejeita e pede correção

### Exceptions / errors
E1. Erro ao guardar ficheiro → sistema notifica falha


## UC-02 — Configurar limites de alerta
- Primary actor: Utilizador
- Supporting actors: —
- Goal: Definir percentuais de alta e baixa
- Preconditions: Ações já configuradas
- Trigger: Utilizador define novos limites
- Postconditions (success): Limites atualizados
- Postconditions (failure/cancel): Configuração anterior mantida
- Related requirements: REQ-4, REQ-5, REQ-8, REQ-14

### Main flow (happy path)
1. Utilizador acede às configurações
2. Define percentual de alta
3. Define percentual de baixa
4. Sistema valida valores
5. Sistema guarda configurações

### Alternative flows
A1. Utilizador altera apenas um dos limites → sistema aceita

### Exceptions / errors
E1. Valor inválido → sistema apresenta erro


## UC-03 — Consultar cotação de ações
- Primary actor: Sistema
- Supporting actors: API de Mercado Financeiro
- Goal: Obter dados atualizados
- Related requirements: REQ-2, REQ-13, REQ-12


## UC-04 — Calcular variação percentual
- Primary actor: Sistema
- Goal: Calcular variação automaticamente
- Related requirements: REQ-6


## UC-05 — Enviar notificação de alerta
- Primary actor: Sistema
- Supporting actors: Serviço de Notificação
- Goal: Alertar utilizador
- Related requirements: REQ-7


## UC-06 — Evitar notificações duplicadas
- Primary actor: Sistema
- Goal: Garantir unicidade de alertas
- Related requirements: REQ-8, REQ-9