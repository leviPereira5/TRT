import os
import django
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trt_project.settings")
django.setup()
setup_test_environment()


def before_scenario(context, scenario):
    from django.test.runner import DiscoverRunner
    context.test_runner = DiscoverRunner(verbosity=0)
    context.old_config = context.test_runner.setup_databases()


def after_scenario(context, scenario):
    context.test_runner.teardown_databases(context.old_config)
