# Acceptance Criteria — Lab 7

## REQ-1 — Cadastro de ações
- AC-1: O sistema permite adicionar uma ação válida (ex: AAPL, TSLA)
- AC-2: O sistema rejeita símbolos inválidos
- AC-3: O utilizador pode remover ações existentes
- AC-4: A lista de ações é persistida após reinício

---

## REQ-2 — Obter cotações (Given/When/Then)
- Given que a API está disponível
- When o sistema consulta uma ação
- Then deve receber uma cotação válida em menos de 5 segundos

- Given que a API não responde
- When ocorre timeout
- Then o sistema deve executar até 3 tentativas (retry)

- Given falha persistente
- When todas as tentativas falham
- Then o sistema deve usar o último valor válido

---

## REQ-3 — Configurar intervalo
- AC-1: Utilizador pode definir intervalo entre 1 e 3600 segundos
- AC-2: Sistema aplica o intervalo corretamente
- AC-3: Valores fora do intervalo são rejeitados
- AC-4: Alterações são persistidas

---

## REQ-4 — Percentual mínimo de alta (Given/When/Then)
- Given um limite definido de 5%
- When a variação atinge ou ultrapassa 5%
- Then o sistema deve gerar uma notificação

- Given valor inválido (>100% ou <0%)
- When o utilizador tenta guardar
- Then o sistema rejeita e mostra erro

---

## REQ-7 — Envio de notificações
- AC-1: Sistema envia notificação quando limite é atingido
- AC-2: Notificação inclui ação, variação (%) e timestamp
- AC-3: Notificação é enviada por pelo menos um canal configurado
- AC-4: Sistema regista a notificação no histórico

---

## REQ-13 — Tempo de resposta (Variant-driven)
- AC-1: Cada requisição não excede 5 segundos
- AC-2: Sistema executa até 3 retries em caso de falha
- AC-3: Sistema usa fallback após falha
- AC-4: Eventos de timeout são registados em log