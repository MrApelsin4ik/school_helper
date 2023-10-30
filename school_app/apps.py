from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_data(sender, **kwargs):
    # Ваш код, который будет выполнен при первом запуске сайта
    pass

class SchoolAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_app'

    def ready(self):
        post_migrate.connect(create_initial_data, sender=self)

class SchoolAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_app'
