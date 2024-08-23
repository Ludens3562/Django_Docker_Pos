from django.apps import AppConfig


class DbmaintConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.DBmaint"
    verbose_name = "販売管理サブシステム"

    # def ready(self):
    #     import DBmaint.signals
