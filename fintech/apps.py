from django.apps import AppConfig

class FintechConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fintech'
    verbose_name = "The Bank of PythonJet"

    def ready(self):
        import fintech.signals
