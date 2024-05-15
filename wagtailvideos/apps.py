from django.apps import AppConfig
from django.core.checks import register

from . import get_transcoder_backend


class WagtailVideosApp(AppConfig):
    name = "wagtailvideos"
    label = "wagtailvideos"
    verbose_name = "Wagtail Videos"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from wagtailvideos.signals import register_signal_handlers

        register_signal_handlers()

        backend = get_transcoder_backend()
        for check in backend.get_system_checks():
            register(check)
