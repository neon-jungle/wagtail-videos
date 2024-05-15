from django.db import models
from django.utils.translation import gettext_lazy as _


class VideoQuality(models.TextChoices):
    DEFAULT = "default", _("Default")
    LOWEST = "lowest", _("Low")
    HIGHEST = "highest", _("High")


class MediaFormats(models.TextChoices):
    WEBM = "webm", _("VP8 and Vorbis in WebM")
    MP4 = "mp4", _("H.264 and AAC in Mp4")
    OGG = "ogg", _("Theora and Vorbis in Ogg")

    def get_quality_param(self, quality):
        if self is MediaFormats.WEBM:
            return {
                VideoQuality.LOWEST: '50',
                VideoQuality.DEFAULT: '22',
                VideoQuality.HIGHEST: '4'
            }[quality]
        elif self is MediaFormats.MP4:
            return {
                VideoQuality.LOWEST: '28',
                VideoQuality.DEFAULT: '24',
                VideoQuality.HIGHEST: '18'
            }[quality]
        elif self is MediaFormats.OGG:
            return {
                VideoQuality.LOWEST: '5',
                VideoQuality.DEFAULT: '7',
                VideoQuality.HIGHEST: '9'
            }[quality]


class VideoTrackKind(models.TextChoices):
    SUBTITLES = 'subtitles', _('Subtitles')
    CAPTIONS = 'captions', _('Captions')
    DESCRIPTIONS = 'descriptions', _('Descriptions')
    CHAPTERS = 'chapters', _('Chapters')
    METADATA = 'metadata', _('Metadata')
