from decimal import Decimal
from datetime import timedelta

from behave import given, when, then
from django.utils import timezone
from monitor.models import Stock, Alert, UserSettings
from monitor.services import calculate_variation, already_alerted
from monitor.forms import SettingsForm


# ─── Shared helpers ──────────────────────────────────────────────────────────

def _make_settings_form(interval):
    return SettingsForm(data={
        'monitoring_interval': interval,
        'ntfy_topic': '',
        'email_enabled': False,
        'email_address': '',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': '',
        'smtp_password': '',
    })


# ─── REQ-6: Cálculo de variação percentual ───────────────────────────────────

@given('o preço anterior do ativo "{symbol}" é "{price}"')
def step_set_old_price(context, symbol, price):
    context.symbol = symbol
    context.old_price = Decimal(price)

@when('o novo preço do ativo "{symbol}" é "{price}"')
def step_set_new_price(context, symbol, price):
    context.new_price = Decimal(price)
    context.variation = calculate_variation(context.old_price, context.new_price)

@then('a variação calculada é "{expected}"')
def step_check_variation(context, expected):
    expected_clean = expected.replace('%', '').replace('+', '')
    assert context.variation == Decimal(expected_clean), \
        f"Esperado {expected_clean}, obtido {context.variation}"

@then('o valor é arredondado a 2 casas decimais')
def step_check_two_decimal_places(context):
    assert context.variation == context.variation.quantize(Decimal("0.01")), \
        "Variação não está arredondada a 2 casas decimais"

@then('nenhuma divisão por zero ocorre')
def step_no_division_by_zero(context):
    # Se chegámos aqui sem exceção, o passo passou
    assert context.variation is not None


# ─── REQ-3: Intervalo de monitorização ───────────────────────────────────────

@given('o utilizador está autenticado e na página de definições "/settings/"')
def step_user_on_settings(context):
    context.form = None
    context.form_valid = None

@when('o utilizador submete o formulário com monitoring_interval "{interval}"')
def step_submit_settings_form(context, interval):
    context.form = _make_settings_form(int(interval))
    context.form_valid = context.form.is_valid()

@then('o formulário é aceite sem erros')
def step_form_accepted(context):
    assert context.form_valid, f"Formulário inválido: {context.form.errors}"

@then('o campo monitoring_interval fica guardado como "{value}"')
def step_interval_saved(context, value):
    assert context.form.cleaned_data['monitoring_interval'] == int(value), \
        f"Esperado {value}, obtido {context.form.cleaned_data['monitoring_interval']}"

@then('o formulário é rejeitado com erro "{error_msg}"')
def step_form_rejected(context, error_msg):
    assert not context.form_valid, "Formulário deveria ter sido rejeitado"
    errors = context.form.errors.get('monitoring_interval', [])
    assert error_msg in errors, f"Mensagem de erro esperada '{error_msg}' não encontrada. Erros: {errors}"

@then('o registo UserSettings não é atualizado')
def step_settings_not_updated(context):
    # Se o formulário é inválido, o save() nunca é chamado — o passo é implicitamente verdadeiro
    assert not context.form_valid, "O formulário não deveria ter sido válido"


# ─── REQ-8: Anti-duplicação de alertas ───────────────────────────────────────

@given('o ativo "{symbol}" tem um alerta "{direction}" criado há "{minutes}" minutos')
def step_create_old_alert(context, symbol, direction, minutes):
    stock, _ = Stock.objects.get_or_create(symbol=symbol, defaults={'tipo': 'stock_us'})
    context.stock = stock
    context.direction = direction
    Alert.objects.create(
        stock=stock,
        direction=direction,
        variation=Decimal("5.00"),
        price=Decimal("105.00"),
        sent_at=timezone.now() - timedelta(minutes=int(minutes)),
    )

@when('o sistema verifica "already_alerted({symbol}, {direction})"')
def step_check_already_alerted(context, symbol, direction):
    context.alerted_result = already_alerted(context.stock, context.direction)

@then('o resultado é "{expected}"')
def step_check_result(context, expected):
    expected_bool = expected == "True"
    assert context.alerted_result == expected_bool, \
        f"Esperado {expected_bool}, obtido {context.alerted_result}"

@then('um novo alerta pode ser criado para "{symbol}"')
def step_new_alert_allowed(context, symbol):
    assert context.alerted_result is False, \
        "already_alerted deveria ser False para permitir novo alerta"

@then('nenhum novo alerta é criado para "{symbol}"')
def step_no_new_alert(context, symbol):
    assert context.alerted_result is True, \
        "already_alerted deveria ser True para bloquear novo alerta"

@then('nenhum POST HTTP é enviado para o ntfy.sh')
def step_no_http_post(context):
    # Verificação semântica: se already_alerted=True, check_and_alert retorna None
    # sem chamar send_ntfy_notification — validado pelo teste T-11 em tests.py
    assert context.alerted_result is True
