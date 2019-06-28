from __future__ import unicode_literals

from unittest.mock import Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from wagtail.tests.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video, video_saved

class TestVideoModel(WagtailTestUtils, TestCase):

    def test_post_save_signal_raw(self):
        '''
        When called with the 'raw' kwarg, the post_save signal handler should
        do nothing. We will test this by asserting that it never calls save
        on the instance.
        '''
        mocked_instance = Mock()
        del mocked_instance._from_signal
        video_saved(Video, mocked_instance, raw=True)
        assert not mocked_instance.save.called
