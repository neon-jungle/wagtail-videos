from django.conf import settings
from django.core.checks import Warning

from . import ffmpeg


def ffmpeg_check(app_configs, **kwargs):
    messages = []
    if not ffmpeg.installed() and not getattr(
        settings, "WAGTAIL_VIDEOS_DISABLE_TRANSCODE", False
    ):
        messages.append(
            Warning(
                "ffmpeg could not be found on your system. Transcoding will be disabled",
                hint=None,
                id="wagtailvideos.W001",
            )
        )
    return messages
