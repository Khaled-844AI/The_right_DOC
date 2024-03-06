from django.apps import AppConfig


class TheRightDocConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'The_right_DOC'

    def ready(self):
        import The_right_DOC.signals


