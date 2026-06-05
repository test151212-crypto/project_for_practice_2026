from django.apps import AppConfig

class ResponsesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.responses'

    def ready(self):
        import apps.responses.signals