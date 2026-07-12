from django.apps import AppConfig


class InternetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internet'

    def ready(self):
        # Safely initialize required auth groups when the app registry is ready.
        from django.contrib.auth.models import Group
        from django.db import connections
        from django.db.utils import OperationalError, ProgrammingError
        from django.db.utils import DEFAULT_DB_ALIAS

        try:
            connection = connections[DEFAULT_DB_ALIAS]
            if connection.introspection.table_names():
                Group.objects.get_or_create(name='Staff')
                Group.objects.get_or_create(name='User')
        except (OperationalError, ProgrammingError):
            pass
