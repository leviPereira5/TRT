# Traceability — Use Cases ↔ Requirements

## Mapping (UC → REQ)

| Use Case | Título | Requisitos ligados |
|----------|--------|--------------------|
| UC-01 | Gerir ações monitorizadas | REQ-1, REQ-4, REQ-5 |
| UC-02 | Configurar intervalo e ntfy.sh | REQ-3, REQ-7 |
| UC-04 | Consultar cotação de ações | REQ-2, REQ-13 |
| UC-06 | Enviar notificação push (ntfy.sh) | REQ-7, REQ-8, REQ-9 |
| UC-07 | Registar histórico de alertas | REQ-9 |
| UC-08 | Evitar notificações duplicadas | REQ-8 |
| UC-09 | Monitorizar ações (ciclo automático) | REQ-2, REQ-3, REQ-6, REQ-7, REQ-8, REQ-13 |
| UC-10 | Autenticar utilizador | REQ-15 |
| UC-11 | Pesquisar ativos mundiais | REQ-16 |
| UC-12 | Consultar detalhe de ativo | REQ-2, REQ-16 |
| UC-13 | Visualizar visão geral do mercado | REQ-17 |

---

## Mapping (REQ → UC)

| Requisito | Descrição | Use Cases que o cobrem |
|-----------|-----------|------------------------|
| REQ-1 | Cadastro de ações | UC-01 |
| REQ-2 | Obter cotações via API | UC-04, UC-09, UC-12 |
| REQ-3 | Configurar intervalo | UC-02, UC-09 |
| REQ-4 | Limiar de alta por ativo | UC-01 |
| REQ-5 | Limiar de baixa por ativo | UC-01 |
| REQ-6 | Cálculo de variação | UC-09 |
| REQ-7 | Notificação push ntfy.sh | UC-02, UC-06, UC-09 |
| REQ-8 | Anti-duplicação de alertas | UC-06, UC-08, UC-09 |
| REQ-9 | Histórico de alertas | UC-06, UC-07 |
| REQ-13 | Tempo de resposta / robustez | UC-04, UC-09 |
| REQ-15 | Autenticação | UC-10 |
| REQ-16 | Pesquisa de ativos | UC-11, UC-12 |
| REQ-17 | Visão geral do mercado | UC-13 |

---

## Coverage analysis

- Todos os Use Cases têm pelo menos um requisito associado ✔
- Todos os requisitos implementados têm pelo menos um UC que os cobre ✔
- REQ-7 (notificações) coberto por 3 UCs → boa rastreabilidade ✔
- REQ-2 (cotações) coberto por 3 UCs → central ao sistema ✔
- UC-09 (monitorização) é o UC mais transversal — cobre 6 requisitos ✔

---

## Mudanças face à versão anterior

| Mudança | Impacto |
|---------|---------|
| SMTP/Email → ntfy.sh | REQ-7 atualizado; UC-06 e UC-02 atualizados |
| Limiares globais → por ativo | REQ-4/REQ-5 movidos de UC-02 para UC-01 |
| Persistência JSON → SQLite ORM | REQ-14 absorvido pelo ORM (implícito) |
| Auth adicionada | REQ-15 e UC-10 novos |
| Pesquisa global adicionada | REQ-16, UC-11, UC-12 novos |
| Home/dashboard adicionado | REQ-17, UC-13 novos |

---

## Gaps resolvidos (face à versão anterior)

- REQ-15 (autenticação): era candidato → agora implementado ✔
- Histórico de alertas visível para o utilizador: `/alerts/` implementado ✔
- Notificações externas reais: ntfy.sh substituiu o SMTP simulado ✔
