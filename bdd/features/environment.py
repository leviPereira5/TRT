import os
import sys
import django
from django.test.utils import setup_test_environment

# Add trt_project/ to sys.path so Django can find trt_project.settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DJANGO_DIR = os.path.join(BASE_DIR, "trt_project")
if DJANGO_DIR not in sys.path:
    sys.path.insert(0, DJANGO_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trt_project.settings")
django.setup()
setup_test_environment()


def before_scenario(context, scenario):
    from django.test.runner import DiscoverRunner
    context.test_runner = DiscoverRunner(verbosity=0)
    context.old_config = context.test_runner.setup_databases()


def after_scenario(context, scenario):
    context.test_runner.teardown_databases(context.old_config)
