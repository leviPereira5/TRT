# Vibe Coding Log — Lab 8

## Tool used

* Codex / ChatGPT / AI Assistant
* Environment/stack:

    * Python 3.10+
    * FastAPI
    * Uvicorn
    * yfinance
    * pandas

---

## Iteration 1

**Prompt (summary or paste):**

* "Em Python crie uma API que seja capaz de enviar dados do mercado financeiro, ações e coisas desse tipo."

**Generated output (what appeared):**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime
import math

app = FastAPI(
    title="Financial Market API",
    description="API para dados do mercado financeiro",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean(val):
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

@app.get("/")
def root():
    return {
        "message": "Financial Market API online",
        "docs": "/docs"
    }

@app.get("/quote/{symbol}")
def get_quote(symbol: str):
    t = yf.Ticker(symbol.upper())
    info = t.info

    if not info:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    price = (
        info.get("regularMarketPrice")
        or info.get("currentPrice")
        or info.get("previousClose")
    )

    prev = info.get("previousClose")

    change = None
    change_pct = None

    if price and prev:
        change = round(price - prev, 4)
        change_pct = round((change / prev) * 100, 2)

    return {
        "symbol": symbol.upper(),
        "name": info.get("longName"),
        "price": clean(price),
        "currency": info.get("currency"),
        "change": change,
        "change_pct": change_pct,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/history/{symbol}")
def history(symbol: str, period: str = "1mo"):
    t = yf.Ticker(symbol.upper())
    df = t.history(period=period)

    if df.empty:
        raise HTTPException(status_code=404, detail="Sem histórico")

    data = []

    for idx, row in df.iterrows():
        data.append({
            "date": str(idx),
            "open": clean(row["Open"]),
            "high": clean(row["High"]),
            "low": clean(row["Low"]),
            "close": clean(row["Close"]),
            "volume": clean(row["Volume"])
        })

    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Kept (accepted):**

* FastAPI como framework principal
* yfinance como fonte de dados
* JSON responses
* Estrutura REST simples
* Endpoints úteis para mercado financeiro

**Rejected (feature drift / out of scope):**

* Nenhum nesta fase

**Manual verification:**

* Happy path:

    * GET /quote/AAPL devolveu preço atual

* Alternative flow:

    * GET /history/MSFT devolveu histórico de preços

* Exception/error path:

    * GET /quote/XXXX retornou erro 404

**Changes made after generation (manual edits):**

* Organização do código
* Melhorias na descrição dos endpoints
* Ajustes de nomes em respostas JSON
* Preparação para futura integração com frontend

---

## Notes (lessons learned)

* Requisitos vagos geram features extra.
* É importante limitar o scope logo no prompt.
* Especificar endpoints desejados melhora muito o resultado.
* O uso de requisitos REQ-### no prompt ajuda a manter rastreabilidade.
* APIs externas exigem tratamento robusto de erros.


## Iteration 2

**Prompt (summary or paste):**

* "https://github.com/leviPereira5/TRT , esse é o meu repositório, gostaria que me ajudasses a implementar o use case 1."

**Generated output (what appeared):**

```python
# monitor/models.py
from django.db import models
from django.utils import timezone

class Stock(models.Model):
    symbol    = models.CharField(max_length=10, unique=True)
    name      = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    added_at  = models.DateTimeField(default=timezone.now)

class UserSettings(models.Model):
    monitoring_interval  = models.PositiveIntegerField(default=60)
    alert_threshold_high = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    alert_threshold_low  = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

# monitor/forms.py
class StockForm(forms.ModelForm):
    def clean_symbol(self):
        # valida regex ^[A-Z]{1,10}$, normaliza maiúsculas, verifica duplicados
        ...

# monitor/views.py
def stock_list(request):       ...
def stock_add(request):        ...
def stock_remove(request, pk): ...
def stock_toggle(request, pk): ...

# monitor/urls.py
path('', views.stock_list, name='stock_list')
path('stocks/add/', views.stock_add, name='stock_add')
path('stocks/<int:pk>/remove/', views.stock_remove, name='stock_remove')
path('stocks/<int:pk>/toggle/', views.stock_toggle, name='stock_toggle')

# monitor/tests.py        — 16 testes unitários
# monitor/templates/monitor/stock_list.html
# monitor/migrations/0001_initial.py
# trt_project/settings.py + urls.py + manage.py
```

**Kept (accepted):**

* Django como framework principal
* Model Stock com is_active para pausar sem apagar (REQ-10)
* Validação de símbolo via regex `^[A-Z]{1,10}$` com normalização para maiúsculas (AC-2, REQ-1)
* Verificação de duplicados em `clean_symbol()`
* `stock_toggle` para ativar/pausar sem remover — Alternative Flow A1 do UC-01
* Persistência via Django ORM / SQLite (REQ-14)
* 16 testes unitários cobrindo todos os Acceptance Criteria (AC-1 a AC-4)

**Rejected (feature drift / out of scope):**

* Dashboard com gráficos de cotações (pertence a UC-04/UC-05)
* Integração com API financeira real via yfinance (fora do UC-01)
* Sistema de autenticação de utilizadores (out of scope Lab 8)
* Export da lista de ações para CSV (não contemplado nos requisitos)

**Manual verification:**

* Happy path:
    * GET / → formulário visível; submeter símbolo "AAPL" + nome "Apple Inc." → ação aparece na tabela como Ativa com data de adição e mensagem de sucesso
* Alternative flow:
    * Submeter símbolo em minúsculas "tsla" → sistema normaliza para "TSLA" e aceita
    * Clicar "Pausar" numa ação → estado muda para Pausada sem remover da lista
* Exception/error path:
    * Submeter "AAP1" (com número) → formulário rejeita com "Símbolo inválido"
    * Tentar adicionar "AAPL" já existente → rejeita com "A ação AAPL já está na lista de monitorização"

**Changes made after generation (manual edits):**

* Adicionado `onsubmit="return confirm(...)"` no botão Remover para evitar remoção acidental
* Template ajustado com filtro `|safe` nas mensagens de feedback para renderizar HTML
* Comentários de rastreabilidade adicionados no código (ex: `# AC-1 REQ-1`, `# REQ-10`)
* Stack alterada de FastAPI (Iteração 1) para Django, justificada pela necessidade de ORM, admin e templates integrados
