# Acceptance Criteria — Lab 7

## REQ-1 — Cadastro de ações
- AC-1: Utilizador pode adicionar uma ação válida
- AC-2: Utilizador pode remover uma ação existente
- AC-3: Lista é persistida após reinício

---

## REQ-2 — Obter cotações (Given/When/Then)
- Given que a API está disponível
- When o sistema consulta uma ação
- Then deve receber uma cotação válida dentro do tempo limite

- Given que a API falha
- When a requisição expira
- Then o sistema deve usar último valor válido

---

## REQ-3 — Configurar intervalo
- AC-1: Utilizador define intervalo de verificação
- AC-2: Sistema respeita intervalo configurado
- AC-3: Intervalos inválidos são rejeitados

---

## REQ-4 — Percentual de alta (Given/When/Then)
- Given um limite definido de 5%
- When a variação atinge 5%
- Then o sistema deve gerar notificação

- Given valor inválido
- When utilizador tenta guardar
- Then sistema rejeita configuração

---

## REQ-7 — Envio de notificações
- AC-1: Sistema envia notificação quando limite é atingido
- AC-2: Notificação contém ação e variação
- AC-3: Notificação é enviada por canal configurado

---

## REQ-13 — Tempo de resposta (Variant)
- AC-1: Requisições não excedem 5 segundos
- AC-2: Sistema executa retry em caso de falha
- AC-3: Sistema usa fallback se API indisponível