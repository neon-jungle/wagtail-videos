from __future__ import unicode_literals

import os

from django.core.files import File

import tests


def create_test_video_file(file_name='small.mp4'):
    video_file = open(os.path.join(tests.__path__[0], file_name), 'rb')
    return File(video_file, name=file_name)
