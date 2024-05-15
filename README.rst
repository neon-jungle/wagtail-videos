wagtailvideos
=============

.. image:: https://gitlab.com/neonjungle/wagtailvideos/badges/master/pipeline.svg
    :target: https://gitlab.com/neonjungle/wagtailvideos/pipelines?ref=master


Based on wagtailimages. The aim was to have feature parity with images
but for html5 videos. Includes the ability to transcode videos to a
html5 compliant codec using ffmpeg.

Requirements
------------

-  Wagtail >= 5.2 (for older wagtail version see the tags)
-  `ffmpeg <https://ffmpeg.org/>`__ (optional, for transcoding)

Installing
----------

Install using pypi

.. code:: bash

    pip install wagtailvideos

Add `wagtailvideos` to your installed apps.

.. code:: python

    INSTALLED_APPS = [
        'wagtailvideos',
    ]

Using
-----

On a page model:
~~~~~~~~~~~~~~~~

Implement as a ``ForeignKey`` relation, same as wagtailimages.

.. code:: python

    from django.db import models

    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.core.fields import RichTextField
    from wagtail.core.models import Page

    from wagtailvideos.edit_handlers import VideoChooserPanel


    class HomePage(Page):
        body = RichtextField()
        header_video = models.ForeignKey('wagtailvideos.Video',
                                         related_name='+',
                                         null=True,
                                         on_delete=models.SET_NULL)

        content_panels = Page.content_panels + [
            FieldPanel('body'),
            VideoChooserPanel('header_video'),
        ]

In a Streamfield:
~~~~~~~~~~~~~~~~~

A VideoChooserBlock is included

.. code:: python

  from wagtail.admin.edit_handlers import StreamFieldPanel
  from wagtail.core.fields import StreamField
  from wagtail.core.models import Page

  from wagtailvideos.blocks import VideoChooserBlock


  class ContentPage(Page):
    body = StreamField([
        ('video', VideoChooserBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

In template:
~~~~~~~~~~~~

The video template tag takes one required postitional argument, a video
field. All extra attributes are added to the surrounding ``<video>``
tag. The original video and all extra transcodes are added as
``<source>`` tags.

.. code:: django

    {% load wagtailvideos_tags %}
    {% video self.header_video autoplay controls width=256 %}

Jinja2 extensions are also included.

How to transcode using ffmpeg:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the video collection manager from the left hand menu. In the video
editing section you can see the available transcodes and a form that can
be used to create new transcodes. It is assumed that your compiled
version of ffmpeg has the matching codec libraries required for the
transcode.


Disable transcode:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transcode can be disabled using the ``WAGTAIL_VIDEOS_DISABLE_TRANSCODE`` setting.

.. code:: django

    # settings.py
    WAGTAIL_VIDEOS_DISABLE_TRANSCODE = True

Modify Thumbnail extension:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The automatically generated Thumbnail extension can be modified  using the ``WAGTAIL_VIDEOS_THUMBNAIL_EXTENSION`` setting. Default value is jpg

.. code:: django

    # settings.py
    WAGTAIL_VIDEOS_THUMBNAIL_EXTENSION = 'webp'

Custom Video models:
~~~~~~~~~~~~~~~~~~~~

Same as Wagtail Images, a custom model can be used to replace the built in Video model using the
``WAGTAILVIDEOS_VIDEO_MODEL`` setting.

.. code:: django

    # settings.py
    WAGTAILVIDEOS_VIDEO_MODEL = 'videos.AttributedVideo'

    # app.videos.models
    from django.db import models
    from modelcluster.fields import ParentalKey
    from wagtailvideos.models import AbstractVideo, AbstractVideoTranscode

    class AttributedVideo(AbstractVideo):
        attribution = models.TextField()

        admin_form_fields = (
            'title',
            'attribution',
            'file',
            'collection',
            'thumbnail',
            'tags',
        )

    class CustomTranscode(AbstractVideoTranscode):
        video = models.ForeignKey(AttributedVideo, related_name='transcodes', on_delete=models.CASCADE)

        class Meta:
            unique_together = (
                ('video', 'media_format')
            )

    # Only needed if you are using the text tracks feature
    class CustomTrackListing(AbstractTrackListing):
        video = models.OneToOneField(AttributedVideo, related_name='track_listing', on_delete=models.CASCADE)

    class CustomVideoTrack(AbstractVideoTrack):
        listing = ParentalKey(CustomTrackListing, related_name='tracks', on_delete=models.CASCADE)


Video text tracks:
~~~~~~~~~~~~~~~~~~

To enable the uploading and displaying of VTT tracks (e.g. subtitles, captions) you'll need to add ``wagtail_modeladmin`` to your installed apps.
Once added, there will be an new area in the admin for attaching VTT files to videos with associaled metadata.

Future features
---------------

-  Some docs
-  Richtext embed
-  Transcoding via external service rather than ffmpeg
