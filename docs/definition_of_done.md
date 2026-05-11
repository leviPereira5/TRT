# Definition of Done (DoD)

## DoD — Requirement (REQ-###)

Um requisito é considerado "Done" quando:

1. Possui ID único (REQ-###) e título claro
2. Está classificado (Funcional / Não Funcional / Restrição)
3. Tem descrição clara e sem ambiguidade
4. Não contém detalhes de implementação (sem "como")
5. Inclui 2–5 critérios de aceitação testáveis
6. Está ligado a Use Cases relevantes
7. Impacto de variante identificado (Yes/No)
8. Foi validado com stakeholders
9. Não entra em conflito com outros requisitos
10. Possui método de verificação definido (teste, demo ou medição)

---

## DoD — User Story (US-###)

Uma user story é considerada "Done" quando:

1. Está escrita no formato: "Como [ator], quero [ação], para [valor]"
2. É pequena, clara e testável
3. Possui critérios de aceitação definidos e validados
4. Implementação cumpre todos os critérios de aceitação
5. Testes (unitários e/ou integração) foram executados com sucesso
6. Não existem defeitos críticos ou bloqueadores
7. Código foi revisto (code review)
8. Documentação foi atualizada (quando aplicável)
9. Funcionalidade foi demonstrada ao stakeholder
10. Stakeholder validou e aceitou a funcionalidade

---

## DoD — Feature (funcionalidade implementada)

Uma funcionalidade é considerada "Done" quando:

1. Todos os critérios de aceitação dos requisitos associados são cumpridos
2. Fluxo principal (happy path) funciona corretamente no browser
3. Fluxos alternativos e de exceção tratados (mensagens de erro claras)
4. Base de dados migrada (`makemigrations` + `migrate` executados)
5. Sem erros no servidor Django (`runserver`) nem no log
6. Funciona após reinício do servidor (persistência confirmada)

---

## Estado atual dos requisitos

| REQ | Título | Estado |
|-----|--------|--------|
| REQ-1 | Cadastro de ações | ✅ Done |
| REQ-2 | Obter cotações via API | ✅ Done |
| REQ-3 | Configurar intervalo de monitorização | ✅ Done |
| REQ-4 | Limiar de alta por ativo | ✅ Done |
| REQ-5 | Limiar de baixa por ativo | ✅ Done |
| REQ-6 | Cálculo de variação percentual | ✅ Done |
| REQ-7 | Envio de notificações push (ntfy.sh) | ✅ Done |
| REQ-8 | Evitar notificações duplicadas | ✅ Done |
| REQ-9 | Histórico de alertas | ✅ Done |
| REQ-13 | Tempo de resposta / robustez | ✅ Done |
| REQ-15 | Autenticação de utilizadores | ✅ Done |
| REQ-16 | Pesquisa de ativos | ✅ Done |
| REQ-17 | Visão geral do mercado | ✅ Done |

---

## Notes

- Evitar critérios vagos como "funciona corretamente"
- Preferir critérios mensuráveis e verificáveis
- DoD deve ser aplicado consistentemente pela equipa
- Notificações são via ntfy.sh (HTTP POST) — sem SMTP, sem credenciais
