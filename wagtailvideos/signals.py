import os
from contextlib import contextmanager

from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from django.db.models.signals import post_delete, post_save

from wagtailvideos import get_transcoder_backend, get_video_model


@contextmanager
def get_local_file(file):
    """
    Get a local version of the file, downloading it from the remote storage if
    required. The returned value should be used as a context manager to
    ensure any temporary files are cleaned up afterwards.
    """
    try:
        with open(file.path):
            yield file.path
    except NotImplementedError:
        _, ext = os.path.splitext(file.name)
        with NamedTemporaryFile(prefix='wagtailvideo-', suffix=ext) as tmp:
            try:
                file.open('rb')
                for chunk in file.chunks():
                    tmp.write(chunk)
            finally:
                file.close()
            tmp.flush()
            yield tmp.name


def post_delete_file_cleanup(instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    transaction.on_commit(lambda: instance.file.delete(False))
    if hasattr(instance, 'thumbnail'):
        # Delete the thumbnail for videos too
        transaction.on_commit(lambda: instance.thumbnail.delete(False))


# Fields that need the actual video file to create using the transcoding backend.
def video_post_save(instance, **kwargs):
    backend = get_transcoder_backend()
    if not backend.installed():
        return
    if hasattr(instance, '_from_signal'):
        # Sender was us, don't run post save
        return
    backend.update_video_metadata(instance)
    instance.file_size = instance.file.size
    instance._from_signal = True
    instance.save()
    del instance._from_signal


def register_signal_handlers():
    Video = get_video_model()
    VideoTranscode = Video.get_transcode_model()
    TrackListing = Video.get_track_listing_model()
    VideoTrack = TrackListing.get_track_model()

    post_save.connect(video_post_save, sender=Video)
    post_delete.connect(post_delete_file_cleanup, sender=Video)
    post_delete.connect(post_delete_file_cleanup, sender=VideoTranscode)
    post_delete.connect(post_delete_file_cleanup, sender=VideoTrack)
