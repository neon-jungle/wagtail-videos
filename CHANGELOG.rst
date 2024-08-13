CHANGELOG
=========

7.0.1
-----

- Fixed transcodes not working
- Converted add mutliple views to use generic classes
- Fixed up JS errors on add multiple page


7.0.0
-----

- Upped minimum wagtail version to 6.1
- Converted index view to generic wagtail index view
- Removed hook that added window.chooserURL


6.1.2
-----

- Temporary fix for wt 6+


6.1.1
-----

- Fixed attribute error in admin

6.1.0
-----

- Groundwork for pluggable backends added
- Video width/height now stored against the video model
- Removed enumchoicefield as a requirement (rip)

6.0.0
-----

- Changed wagtail.contrib.modeladmin to wagtail_modeladmin
- Removed references to wagtailadmin/shared/field_as_li.html
- Removed "created in" from wagtail admin

5.2
---

- Upped minimum wagtail version to latest LTS (5.2)


4.0.1
-----

- Fixed bad migration


4.0.0
-----

- Upped min Wagtail version to 4.x
- Added support for limiting video choices based on collection permission

2.11.1
------

- Added collection dropdown to chooser

2.11.0
------

- Preliminary django 4 Support


2.10.6
------

- Default audio codec for mp4 changed to AAC


2.10.5
------

- Changed default thumbnail generation to match video size

2.10.0
------

- Added ability to use custom models for Videos + Transcodes
- Added a way to add VTT files to videos and render them

2.9.0
-----

- Added VideoChooserBlock
- Added video summary on admin homepage


2.4.0
-----

- Upped minimum wagtail to 2.4


2.0.0
-----

- Dropped python2
- Updated wagtail dependency to 2.0

0.4.0
-----

- Support remote storage engines, like AWS S3.

0.3.2
-----

- Add support for Django 1.11

0.3.1
-----

- Do not require a new video file when editing existing videos

0.3.0
-----

- Prefer transcodes over the source video
- Support Django 1.9+, Wagtail 1.7+
