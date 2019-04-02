from __future__ import unicode_literals

from django.test import TestCase, override_settings
from wagtail.tests.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video


class TestVideoModel(WagtailTestUtils, TestCase):

    @override_settings(WAGTAILVIDEOS_CREATE_FILE_HASH=True)
    def test_create_file_hash(self):
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert video.file_hash
        assert video.file_size

    def test_create_file_hash_disabled(self):
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert not video.file_hash
        assert video.file_size
