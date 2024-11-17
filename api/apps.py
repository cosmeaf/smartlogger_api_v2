from django.apps import AppConfig
from .tasks import run_converter_script

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):

        import api.signals  # noqa: F401
        run_converter_script.delay()
