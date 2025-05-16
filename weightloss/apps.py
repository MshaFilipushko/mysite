from django.apps import AppConfig


class WeightlossConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weightloss'
    
    def ready(self):
        """
        Импортирует обработчики сигналов при запуске приложения
        """
        import weightloss.signals
