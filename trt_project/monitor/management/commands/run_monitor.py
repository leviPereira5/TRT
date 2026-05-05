import time
import logging
from django.core.management.base import BaseCommand
from monitor.models import UserSettings
from monitor.services import run_monitoring_cycle

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corre o motor de monitorização automática contínua (UC-09)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Motor de monitorização iniciado...'))
        self.stdout.write('Prima Ctrl+C para parar.\n')

        while True:
            settings = UserSettings.objects.first()
            if not settings:
                settings = UserSettings.objects.create()

            intervalo = settings.monitoring_interval
            self.stdout.write(f'\n[Ciclo] A monitorizar... (intervalo: {intervalo}s)')

            try:
                results = run_monitoring_cycle()

                for r in results:
                    if 'error' in r:
                        self.stdout.write(self.style.ERROR(
                            f"  ✗ {r['symbol']}: {r['error']}"
                        ))
                    elif r.get('fallback'):
                        self.stdout.write(self.style.WARNING(
                            f"  ⚠ {r['symbol']}: fallback — último preço: {r['price']}"
                        ))
                    else:
                        variacao = r.get('variation', 0)
                        sinal    = '+' if variacao >= 0 else ''
                        linha    = f"  ✓ {r['symbol']}: {r['price']} ({sinal}{variacao}%)"
                        if r.get('alert'):
                            linha += '  ⚠️  ALERTA!'
                            self.stdout.write(self.style.WARNING(linha))
                        else:
                            self.stdout.write(self.style.SUCCESS(linha))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro no ciclo: {e}'))
                logger.exception('Erro no ciclo de monitorização')

            self.stdout.write(f'A aguardar {intervalo}s...')
            time.sleep(intervalo)