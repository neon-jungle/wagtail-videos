from __future__ import unicode_literals

from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video


class TestVideoModel(WagtailTestUtils, TestCase):

    def test_file_hash(self):
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert video.file_hash
        assert video.file_size
