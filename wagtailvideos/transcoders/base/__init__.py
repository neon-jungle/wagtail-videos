import abc
import os
from contextlib import contextmanager

from django.core.files.temp import NamedTemporaryFile


class BaseBackend(abc.ABC):
    """
    Abstract base class for a transcoding backend
    """

    @abc.abstractmethod
    def installed(self) -> bool:
        ...

    @abc.abstractmethod
    def update_video_metadata(self, video) -> None:
        ...

    @abc.abstractmethod
    def do_transcode(self, transcode):
        ...

    def get_system_checks(self):
        return []

    @contextmanager
    def _get_local_file(self, file):
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
