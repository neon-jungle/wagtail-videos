wagtailvideos
=============

Based on wagtailimages. The aim was to have feature parity with images
but for html5 videos. Includes the ability to transcode videos to a
html5 compliant codec using ffmpeg.

Requirements
------------

-  Wagtail >= 2.0
-  `ffmpeg <https://ffmpeg.org/>`__

Installing
----------

Install using pypi

.. code:: bash

    pip install wagtailvideos


Using
-----

On a page model:
~~~~~~~~~~~~~~~~

Implement as a ``ForeignKey`` relation, same as wagtailimages.

.. code:: python


    from django.db import models

    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailcore.fields import RichTextField
    from wagtail.wagtailcore.models import Page

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

In template:
~~~~~~~~~~~~

The video template tag takes one required postitional argument, a video
field. All extra attributes are added to the surrounding ``<video>``
tag. The original video and all extra transcodes are added as
``<source>`` tags.

.. code:: django

    {% load wagtailvideos_tags %}
    {% video self.header_video autoplay controls width=256 %}

How to transcode using ffmpeg:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the video collection manager from the left hand menu. In the video
editing section you can see the available transcodes and a form that can
be used to create new transcodes. It is assumed that your compiled
version of ffmpeg has the matching codec libraries required for the
transcode.

Settings:
~~~~~~~~~

The following settings are available to control the behavior of the module.

* `WAGTAILVIDEOS_MAX_UPLOAD_SIZE` - Maximum upload size of video files in bytes. Defaults to 1GB
* `WAGTAILVIDEOS_CREATE_FILE_HASH` - If True, a file hash will be calculated and added to the model. Defaults to False.

Future features
---------------

-  Richtext embed
-  Streamfield block
-  Transcoding via amazon service rather than ffmpeg
-  Wagtail homescreen video count
