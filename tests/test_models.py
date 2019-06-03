from __future__ import unicode_literals

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video


class TestVideoModel(WagtailTestUtils, TestCase):

    def test_thumbnail(self):
        # Creating a video with no provided thumbnail should auto-create one
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert video.thumbnail
        # Change the thumbnail to a manually provided one
        video.thumbnail = SimpleUploadedFile('test.jpg', b'')
        video.save()
        # Change the video file, and ensure that our manually provided
        # thumbnail is still there
        video_file = create_test_video_file()
        video.file = video_file
        video.save()
        assert video.thumbnail.name == 'original_videos/test.jpg'
