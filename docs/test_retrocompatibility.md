# Test Retrocompatibility — Lab 14

**Versão:** 1.0  
**Data:** 2026-06-08  
**Projeto:** TRT Invest

---

## Que mudanças podem quebrar os nossos testes?

### Mudanças de requisitos
- Alterar o intervalo válido de monitorização (1–3600) quebraria UT-05 a UT-08 e os cenários BDD correspondentes.
- Mudar a janela de anti-duplicação de 60 minutos para outro valor quebraria UT-13, UT-14, T-10, T-11 e os cenários BDD de REQ-8.
- Mudar a fórmula de variação (atualmente `((novo-antigo)/antigo)*100`) quebraria UT-09 a UT-11 e T-01 a T-04.
- Alterar a mensagem de erro de validação (`"Entre 1 e 3600 segundos."`) quebraria UT-07, UT-08 e o cenário BDD "outside valid range".

### Mudanças de UI/URLs
- Renomear `/portfolio/` quebraria os cenários BDD que navegam diretamente para esse URL.
- Renomear `/alerts/` quebraria TC-008 e o cenário "Alert history is accessible".
- Renomear `/search/` ou `/search/suggest/` quebraria os novos cenários BDD de REQ-16.
- Mudar o formulário de login (campo `identifier` para outro nome) quebraria TC-011/TC-012 e os BDD steps correspondentes.

### Refactoring interno
- Renomear `calculate_variation()` quebraria todos os testes que importam diretamente esta função.
- Renomear `already_alerted()` quebraria UT-12 a UT-14 e T-09 a T-12.
- Mover `services.py` para outro módulo quebraria todos os imports nos testes.
- Alterar a estrutura do modelo `Alert` (campos `direction`, `sent_at`, `variation`, `price`) quebraria múltiplos testes de integração.

### Mudanças de ambiente/dependências
- Upgrade de `yfinance` com mudança de interface quebraria os cenários BDD que mocam `yfinance.Ticker`.
- Mudança do backend de cache Django quebraria testes que assumem `cache.get()`/`cache.set()`.
- Mudança da versão de `Django` com alterações no sistema de autenticação quebraria tests de login.
- A remoção do `DJANGO_SETTINGS_MODULE` do `pytest.ini` quebraria todos os testes pytest.

### Instabilidade de dados de teste
- Cenários BDD com dados hard-coded (`"levi@mail.com"`, `"AAPL"`, `"trt-test-topic"`) falham se o `before_scenario` não criar o estado correto.
- Testes de `already_alerted()` que usam `timezone.now() - timedelta(minutes=61)` são frágeis se o servidor de BD tiver fuso horário diferente do Django.

---

## Pontos frágeis identificados (mínimo 3)

### 1. Mensagens de erro hard-coded nos testes
**Ponto frágil:** UT-07, UT-08, o cenário BDD "outside valid range" e T-07, T-08 verificam a string exacta `"Entre 1 e 3600 segundos."`. Se o texto da mensagem de erro mudar (ex: tradução, typo fix), todos estes testes falham.  
**Porquê frágil:** A mensagem está definida em `forms.py` e copiada como literal nos testes; qualquer pequena alteração de texto sem actualizar os testes causa falha.  
**Ação de melhoria:** Extrair a mensagem para uma constante partilhada (ex: `monitor/constants.py`) e importá-la nos testes. Assim uma mudança de texto propaga-se automaticamente.

### 2. Duplicação de testes entre `tests/unit/` e `monitor/tests.py`
**Ponto frágil:** Os mesmos comportamentos (REQ-3, REQ-6, REQ-8) estão cobertos em dois ficheiros com IDs diferentes (UT-xx vs T-xx). Se um teste falha num ficheiro mas não no outro, é difícil perceber qual é a fonte da verdade.  
**Porquê frágil:** Um developer pode corrigir um bug, fazer passar os testes em `monitor/tests.py`, e não perceber que `tests/unit/` tem os mesmos testes ainda a falhar (ou vice-versa).  
**Ação de melhoria:** Consolidar todos os testes unitários em `tests/unit/` com IDs únicos (UT-xx). Remover as classes `TestCalculateVariation` e `TestMonitoringIntervalValidation` de `monitor/tests.py`, mantendo apenas `TestAlreadyAlerted` (que usa modelos Django e precisa da BD).

### 3. Dependência de `timezone.now()` nos testes de anti-duplicação
**Ponto frágil:** UT-13, UT-14, T-10, T-11 criam alertas com `sent_at = timezone.now() - timedelta(minutes=N)`. Se o relógio do servidor de BD diferir do Django, ou se o teste for muito lento (edge case perto dos 60 minutos), os resultados podem ser incorretos.  
**Porquê frágil:** Testes dependentes do tempo real (wall clock) são não-determinísticos em ambientes de CI com carga variável.  
**Ação de melhoria:** Usar `unittest.mock.patch('django.utils.timezone.now', return_value=...)` para congelar o relógio durante o teste. Assim `already_alerted()` é testado com tempo previsível.

### 4. Cenários BDD com dados hard-coded de utilizador
**Ponto frágil:** Os steps BDD criam utilizadores com credenciais fixas (`username="levi"`, `password="pass1234"`). Se outro teste criar o mesmo utilizador antes, o `before_scenario` pode falhar silenciosamente.  
**Porquê frágil:** O `environment.py` faz setup/teardown por cenário, mas se houver estado partilhado entre cenários (ex: cache Django que não é limpa), pode haver interferência.  
**Ação de melhoria:** Usar prefixos únicos por cenário (ex: `uuid4()`) para criar utilizadores de teste. Garantir que o `after_scenario` também limpa a cache Django (`cache.clear()`).

### 5. Steps BDD que verificam conteúdo HTML com strings exactas
**Ponto frágil:** O cenário "Alert history is accessible" verifica `direction "Alta"` (string traduzida em PT). Se a tradução mudar ou se o template for reestruturado, o step falha.  
**Porquê frágil:** Tests de UI em BDD são frágeis a mudanças de template — testam apresentação, não comportamento.  
**Ação de melhoria:** Verificar dados via resposta JSON ou via ORM em vez de conteúdo HTML. Para o histórico, verificar `Alert.objects.filter(...)` em vez de fazer parse do HTML.
