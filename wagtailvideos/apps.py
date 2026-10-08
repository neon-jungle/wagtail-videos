from django.apps import AppConfig
from django.core.checks import register

from . import get_transcoder_backend, get_video_model


class WagtailVideosApp(AppConfig):
    name = "wagtailvideos"
    label = "wagtailvideos"
    verbose_name = "Wagtail Videos"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from wagtailvideos.signals import register_signal_handlers

        register_signal_handlers()

        # Wagtail 8 looks a model's permission policy up in a registry and
        # deprecates setting it on the chooser viewset; older versions have
        # no registry and take it from the viewset (see views/chooser.py).
        try:
            from wagtail.permissions import register_permission_policy
        except ImportError:
            pass
        else:
            from wagtailvideos.permissions import permission_policy

            register_permission_policy(get_video_model(), permission_policy)

        backend = get_transcoder_backend()
        for check in backend.get_system_checks():
            register(check)
