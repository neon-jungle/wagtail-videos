import threading

from ..base import BaseBackend
from . import checks, ffmpeg


class FFmpegBackend(BaseBackend):
    """
    FFmpeg-based transcoder backend. By default these transcodes run in the
    background by starting a new thread in the current process. Can optionally
    run in the foreground thread by passing blocking=True. This is mostly useful
    if you want to generate transcodes via a management command, celery task, etc.
    """

    def __init__(self, blocking: bool = False):
        self.blocking = blocking

    def installed(self):
        return ffmpeg.installed()

    def get_system_checks(self):
        return [checks.ffmpeg_check]

    def update_video_metadata(self, video) -> None:
        has_changed = video._initial_file is not video.file
        filled_out = video.thumbnail is not None and video.duration is not None
        if not has_changed and filled_out:
            return
        with self._get_local_file(video.file) as file_path:
            if has_changed or not video.thumbnail:
                video.thumbnail = ffmpeg.get_thumbnail(file_path)
            if has_changed or video.duration is None:
                video.duration = ffmpeg.get_duration(file_path)

    def do_transcode(self, transcode):
        if self.blocking:
            ffmpeg.FFmpegTranscoder(transcode).run()
        else:
            TranscodingThread(transcode).start()


class TranscodingThread(threading.Thread):
    def __init__(self, transcode, **kwargs):
        super().__init__(**kwargs)
        self.transcode = transcode

    def run(self):
        ffmpeg.FFmpegTranscoder(self.transcode).run()
