# Traceability — Use Cases ↔ Requirements (Lab 6)

## Mapping (UC → REQ)

| Use Case | Linked Requirements (REQ-###) | Notes |
|----------|-----------------------------|------|
| UC-01 | REQ-1, REQ-10, REQ-14 | Gestão e persistência |
| UC-02 | REQ-4, REQ-5, REQ-14 | Configuração |
| UC-03 | REQ-3 | Intervalo |
| UC-04 | REQ-2, REQ-12, REQ-13 | API e robustez |
| UC-05 | REQ-6 | Cálculo |
| UC-06 | REQ-7, REQ-8, REQ-9 | Notificações |
| UC-07 | REQ-9, REQ-14 | Histórico |
| UC-08 | REQ-8 | Anti-duplicação |

## Coverage analysis

- Todos os Use Cases possuem ligação a requisitos ✔
- Requisitos críticos (REQ-2, REQ-7, REQ-8) estão bem cobertos ✔
- UC-06 cobre múltiplos requisitos → boa coesão ✔

## Gaps / Observations

- REQ-11 (Python) não mapeado → requisito técnico, não funcional

- Possíveis melhorias:
    - Sistema deve permitir reenvio manual de notificações falhadas
    - Sistema deve permitir visualização do histórico pelo utilizador

## Missing requirement candidates

- REQ-15 (candidato): O sistema deve permitir consulta do histórico de alertas pelo utilizador
- REQ-16 (candidato): O sistema deve permitir reenvio de notificações falhadas