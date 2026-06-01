"""
Behave step definitions for lab13.feature
REQ-1 (stock portfolio CRUD) and REQ-15 (authentication / access control)
Run: cd trt_project && python -m behave ../bdd/features/lab13.feature
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trt_project.settings")

from behave import given, when, then
from monitor.models import Stock


# ─── REQ-1: Gestão de ativos no portfólio ────────────────────────────────────

@given('a base de dados está limpa de ativos')
def step_clean_stocks(context):
    Stock.objects.all().delete()


@when('o utilizador adiciona o ativo "{symbol}" do tipo "{tipo}"')
def step_add_stock(context, symbol, tipo):
    context.add_error = None
    try:
        Stock.objects.create(symbol=symbol, tipo=tipo)
    except Exception as e:
        context.add_error = e


@then('o ativo "{symbol}" existe no portfólio')
def step_stock_exists(context, symbol):
    assert Stock.objects.filter(symbol=symbol).exists(), \
        f"Ativo '{symbol}' não encontrado no portfólio"


@then('o total de ativos no portfólio é "{count}"')
def step_portfolio_count(context, count):
    total = Stock.objects.count()
    assert total == int(count), \
        f"Esperado {count} ativo(s), encontrado(s) {total}"


@given('o ativo "{symbol}" já existe no portfólio')
def step_stock_already_exists(context, symbol):
    Stock.objects.get_or_create(symbol=symbol, defaults={'tipo': 'stock_br'})


@when('o utilizador tenta adicionar "{symbol}" novamente')
def step_try_add_duplicate(context, symbol):
    # mirrors the view logic: only creates if symbol does not exist
    if not Stock.objects.filter(symbol=symbol).exists():
        Stock.objects.create(symbol=symbol, tipo='stock_br')


@then('o portfólio contém exatamente "{count}" ativo com símbolo "{symbol}"')
def step_exactly_n_stocks_with_symbol(context, count, symbol):
    n = Stock.objects.filter(symbol=symbol).count()
    assert n == int(count), \
        f"Esperado {count} registo(s) para '{symbol}', encontrado(s) {n}"


@given('o ativo "{symbol}" é o único ativo no portfólio')
def step_only_stock_in_portfolio(context, symbol):
    Stock.objects.all().delete()
    context.stock = Stock.objects.create(symbol=symbol, tipo='stock_br')


@when('o utilizador remove o ativo "{symbol}"')
def step_remove_stock(context, symbol):
    context.remove_error = None
    try:
        Stock.objects.filter(symbol=symbol).delete()
    except Exception as e:
        context.remove_error = e


@then('o portfólio está vazio')
def step_portfolio_empty(context):
    total = Stock.objects.count()
    assert total == 0, \
        f"Portfólio deveria estar vazio, mas tem {total} ativo(s)"


@then('não ocorre nenhum erro durante a remoção')
def step_no_removal_error(context):
    assert context.remove_error is None, \
        f"Erro inesperado durante remoção: {context.remove_error}"


# ─── REQ-15: Autenticação / controlo de acesso ───────────────────────────────

@given('o utilizador não está autenticado')
def step_not_authenticated(context):
    from django.test import Client
    context.client = Client()


@when('acede à página protegida "{url}"')
def step_access_protected_url(context, url):
    context.response = context.client.get(url)


@then('é redirecionado para "{expected_url}"')
def step_redirected_to(context, expected_url):
    status = context.response.status_code
    assert status in (301, 302), \
        f"Esperado redirect (301/302), obtido HTTP {status}"
    location = context.response.get('Location', '')
    assert expected_url in location, \
        f"Esperado redirect para '{expected_url}', obtido '{location}'"
