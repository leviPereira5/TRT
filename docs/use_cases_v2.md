# Use Cases v2 — Lab 6

## UC-02 — Configurar limites de alerta
- Primary actor: Utilizador
- Supporting actors: —
- Goal: Permitir ao utilizador definir percentuais de alta e baixa para disparo de notificações
- Preconditions:
    - Pelo menos uma ação monitorizada
    - Sistema em execução
- Trigger:
    - Utilizador acede à área de configuração
- Postconditions (success):
    - Limites guardados com sucesso
- Postconditions (failure/cancel):
    - Configuração anterior mantida
- Related requirements: REQ-4, REQ-5, REQ-8, REQ-14

### Main flow (happy path)
1. Utilizador acede ao menu de configuração
2. Sistema apresenta valores atuais
3. Utilizador introduz percentuais de alta e baixa
4. Sistema valida os valores introduzidos
5. Sistema guarda configurações persistentes
6. Sistema confirma operação ao utilizador

### Alternative flows (min. 2)
A1. Utilizador altera apenas um limite  
→ Sistema aceita alteração parcial e mantém outro valor

A2. Utilizador redefine limites  
→ Sistema substitui valores anteriores por novos

A3. Utilizador cancela operação  
→ Sistema não altera configurações

### Exceptions / errors (min. 2)
E1. Valor inválido (ex: negativo ou não numérico)  
→ Sistema rejeita input e solicita correção

E2. Falha ao persistir dados  
→ Sistema mantém configuração anterior e regista erro

E3. Falha de acesso ao ficheiro  
→ Sistema notifica erro e impede alteração

---

## UC-06 — Enviar notificação de alerta
- Primary actor: Sistema (evento interno com impacto no utilizador)
- Supporting actors: Serviço de Notificação
- Goal: Notificar o utilizador quando uma variação relevante é detetada
- Preconditions:
    - Limites definidos
    - Dados de cotação disponíveis
- Trigger:
    - Variação percentual atinge limite configurado
- Postconditions (success):
    - Notificação enviada com sucesso
    - Evento registado no histórico
- Postconditions (failure/cancel):
    - Notificação não enviada
    - Erro registado
- Related requirements: REQ-7, REQ-8, REQ-9

### Main flow (happy path)
1. Sistema deteta nova cotação
2. Sistema calcula variação percentual
3. Sistema compara com limites definidos
4. Sistema verifica histórico para evitar duplicação
5. Sistema envia notificação via serviço externo
6. Sistema regista evento no histórico

### Alternative flows (min. 2)
A1. Variação não atinge limite  
→ Sistema não envia notificação

A2. Evento já notificado anteriormente  
→ Sistema bloqueia envio duplicado

A3. Canal de notificação alternativo disponível  
→ Sistema utiliza canal secundário

### Exceptions / errors (min. 2)
E1. Falha no serviço de notificação  
→ Sistema regista erro e executa retry automático

E2. Timeout da API de mercado  
→ Sistema usa último valor válido (fallback)

E3. Dados inconsistentes da API  
→ Sistema descarta dados e regista erro

---

## Variant-driven notes (required)
- Performance: Timeout de 5 segundos na API (REQ-13)
- Robustez: Retry automático e fallback de dados (REQ-12)
- Qualidade de dados: Validação de dados antes do cálculo