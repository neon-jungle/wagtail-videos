from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

default_app_config = 'wagtailvideos.apps.WagtailVideosApp'


default_transcoder_settings = {
    "BACKEND": "wagtailvideos.transcoders.ffmpeg.FFmpegBackend",
    "OPTIONS": {},
}


def is_modeladmin_installed():
    from django.apps import apps
    return apps.is_installed('wagtail_modeladmin')


def get_video_model_string():
    return getattr(settings, 'WAGTAILVIDEOS_VIDEO_MODEL', 'wagtailvideos.Video')


def get_video_model():
    from django.apps import apps
    model_string = get_video_model_string()
    try:
        return apps.get_model(model_string)
    except ValueError:
        raise ImproperlyConfigured("WAGTAILVIDEOS_VIDEO_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILVIDEOS_VIDEO_MODEL refers to model '%s' that has not been installed" % model_string
        )


def get_transcoder_settings():
    val = getattr(settings, "WAGTAILVIDEOS_TRANSCODER", default_transcoder_settings)
    return {**default_transcoder_settings, **val}


def get_transcoder_backend():
    tsettings = get_transcoder_settings()
    try:
        BackendKlass = import_string(tsettings["BACKEND"])
    except ImportError:
        raise ImproperlyConfigured(
            "WAGTAILVIDEOS_TRANSCODER refers to class '%s' that does not exist"
            % tsettings["BACKEND"]
        )
    return BackendKlass(**tsettings["OPTIONS"])
