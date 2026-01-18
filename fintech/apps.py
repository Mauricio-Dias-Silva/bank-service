from django.apps import AppConfig

class FintechConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard.apps.fintech'
    verbose_name = "The Bank of PythonJet"

    def ready(self):
        import dashboard.apps.fintech.signals
