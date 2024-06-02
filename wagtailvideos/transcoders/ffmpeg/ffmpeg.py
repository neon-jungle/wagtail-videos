import datetime
import json
import logging
import os
import os.path
import shutil
import subprocess
import tempfile
from typing import List, Optional, TypedDict

from django.conf import settings
from django.core.files.base import ContentFile

from wagtailvideos.enums import MediaFormats, VideoQuality

logger = logging.getLogger(__name__)


class VideoStats(TypedDict):
    width: int
    height: int
    duration: datetime.timedelta


def installed(path: Optional[str] = None) -> bool:
    return shutil.which("ffmpeg", path=path) is not None


def get_stats(file_path: str) -> Optional[VideoStats]:
    if not installed():
        raise RuntimeError("ffmpeg is not installed")
    cmd = [
        "ffprobe",
        file_path,
        # Return output in JSON
        "-of",
        "json",
        # Quiet mode
        "-v",
        "quiet",
        # Ignore audio tracks
        "-select_streams",
        "v",
        # Return video format info
        "-show_format",
        # Return video dimensions
        "-show_entries",
        "stream=width,height",
    ]
    try:
        with open(os.devnull, "r+b") as fnull:
            resp = json.loads(
                subprocess.check_output(
                    cmd,
                    stdin=fnull,
                    stderr=fnull,
                )
            )
    except subprocess.CalledProcessError:
        logger.exception("Getting video duration failed")
        return None
    stream = resp["streams"][0]
    return VideoStats(
        width=int(stream["width"]),
        height=int(stream["height"]),
        duration=datetime.timedelta(seconds=float(resp["format"]["duration"])),
    )


def get_thumbnail(file_path: str) -> Optional[ContentFile]:
    if not installed():
        raise RuntimeError("ffmpeg is not installed")

    file_name = os.path.basename(file_path)
    thumb_extension = getattr(
        settings, "WAGTAIL_VIDEOS_THUMBNAIL_EXTENSION", "jpg"
    ).lower()
    thumb_name = "{}_thumb.{}".format(os.path.splitext(file_name)[0], thumb_extension)

    try:
        output_dir = tempfile.mkdtemp()
        output_file = os.path.join(output_dir, thumb_name)
        cmd = [
            "ffmpeg",
            "-v",
            "quiet",
            "-itsoffset",
            "-4",
            "-i",
            file_path,
            "-update",
            "true",
            "-vframes",
            "1",
            "-an",
            "-vf",
            "scale=iw:-1",  # Make thumbnail the size & aspect ratio of the input video
            output_file,
        ]
        try:
            with open(os.devnull, "r+b") as fnull:
                subprocess.check_call(
                    cmd,
                    stdin=fnull,
                    stdout=fnull,
                )
        except subprocess.CalledProcessError:
            return None
        return ContentFile(open(output_file, "rb").read(), thumb_name)
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


class FFmpegTranscoder:
    def __init__(self, transcode):
        self.transcode = transcode

    def run(self):
        video = self.transcode.video
        media_format = self.transcode.media_format
        input_file = self._get_file_url(video.file)
        if not input_file:
            raise ValueError(
                "Invalid input_file value {0} for file {1}".format(
                    input_file, video.file
                )
            )

        output_dir = tempfile.mkdtemp()
        transcode_name = "{0}.{1}".format(
            video.filename(include_ext=False), media_format
        )

        output_file = os.path.join(output_dir, transcode_name)
        ffmpeg_cmd = self._get_ffmpeg_command(
            input_file, output_file, media_format, self.transcode.quality
        )
        try:
            with open(os.devnull, "r") as fnull:
                subprocess.check_output(
                    ffmpeg_cmd,
                    stdin=fnull,
                    stderr=subprocess.STDOUT,
                )
            self.transcode.file = ContentFile(
                open(output_file, "rb").read(), transcode_name
            )
            self.transcode.error_message = ""
        except subprocess.CalledProcessError as error:
            self.transcode.error_message = error.output
        finally:
            self.transcode.processing = False
            self.transcode.save()
            shutil.rmtree(output_dir, ignore_errors=True)

    def _get_file_url(self, file):
        input_file = None
        # Check if it is a local file
        try:
            input_file = file.path
        except NotImplementedError:
            input_file = None
        if input_file:
            return input_file
        # Check if it is a file stored with django-storages
        try:
            input_file = file.url
        except NotImplementedError:
            input_file = None
        return input_file

    def _get_ffmpeg_command(
        self,
        input_file: str,
        output_file: str,
        media_format: MediaFormats,
        quality: VideoQuality,
    ) -> List[str]:
        quality_param = self._get_quality_param(media_format, quality)
        args = ["ffmpeg", "-hide_banner", "-i", input_file]
        if media_format == MediaFormats.OGG:
            return args + [
                "-codec:v",
                "libtheora",
                "-qscale:v",
                quality_param,
                "-codec:a",
                "libvorbis",
                "-qscale:a",
                "5",
                output_file,
            ]

        if media_format == MediaFormats.MP4:
            return args + [
                "-codec:v",
                "libx264",
                "-preset",
                "slow",  # TODO Checkout other presets
                "-crf",
                quality_param,
                "-codec:a",
                "aac",
                output_file,
            ]

        if media_format == MediaFormats.WEBM:
            return args + [
                "-codec:v",
                "libvpx",
                "-crf",
                quality_param,
                "-codec:a",
                "libvorbis",
                output_file,
            ]

    def _get_quality_param(
        self, media_format: MediaFormats, quality: VideoQuality
    ) -> str:
        if media_format is MediaFormats.WEBM:
            return {
                VideoQuality.LOWEST: "50",
                VideoQuality.DEFAULT: "22",
                VideoQuality.HIGHEST: "4",
            }[quality]
        elif media_format is MediaFormats.MP4:
            return {
                VideoQuality.LOWEST: "28",
                VideoQuality.DEFAULT: "24",
                VideoQuality.HIGHEST: "18",
            }[quality]
        elif media_format is MediaFormats.OGG:
            return {
                VideoQuality.LOWEST: "5",
                VideoQuality.DEFAULT: "7",
                VideoQuality.HIGHEST: "9",
            }[quality]
