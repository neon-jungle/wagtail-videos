import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import filesizeformat
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Collection, GroupCollectionPermission
from wagtail.test.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video


class TestVideoIndexView(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:index"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/index.html")
        self.assertContains(response, "Add a video")

    def test_search(self):
        response = self.get({"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    def test_pagination(self):
        pages = ["0", "1", "-1", "9999", "Not a page"]
        for page in pages:
            response = self.get({"p": page})
            self.assertEqual(response.status_code, 200)

    def test_ordering(self):
        orderings = ["title", "-created_at"]
        for ordering in orderings:
            response = self.get({"ordering": ordering})
            self.assertEqual(response.status_code, 200)


class TestVideoAddView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos:add"), params)

    def post(self, post_data={}):
        return self.client.post(reverse("wagtailvideos:add"), post_data)

    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(
            response,
            '<label class="w-field__label" for="id_collection" id="id_collection-label">',
        )

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_get_with_collections(self):
        root_collection = Collection.get_first_root_node()
        collection_name = "Takeflight manifesto"
        root_collection.add_child(name=collection_name)

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        self.assertContains(
            response,
            '<label class="w-field__label" for="id_collection" id="id_collection-label">',
        )
        self.assertContains(response, collection_name)

    def test_add(self):
        video_file = create_test_video_file()
        title = "Test Video"
        response = self.post(
            {
                "title": title,
                "file": SimpleUploadedFile("small.mp4", video_file.read(), "video/mp4"),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        videos = Video.objects.filter(title=title)
        self.assertEqual(videos.count(), 1)

        # Test that extra fields were populated from post_save signal
        video = videos.first()
        self.assertTrue(video.thumbnail)
        self.assertTrue(video.duration)
        self.assertTrue(video.file_size)
        self.assertTrue(video.width)
        self.assertTrue(video.height)

        # Test that it was placed in the root collection
        root_collection = Collection.get_first_root_node()
        self.assertEqual(video.collection, root_collection)

    @patch("wagtailvideos.transcoders.ffmpeg.ffmpeg.installed")
    def test_add_no_ffmpeg(self, ffmpeg_installed):
        ffmpeg_installed.return_value = False

        video_file = create_test_video_file()
        title = "no_ffmpeg"

        response = self.post(
            {
                "title": title,
                "file": SimpleUploadedFile("small.mp4", video_file.read(), "video/mp4"),
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check video exists but has no thumb or duration
        videos = Video.objects.filter(title=title)
        self.assertEqual(videos.count(), 1)
        video = videos.first()

        self.assertFalse(video.thumbnail)
        self.assertFalse(video.duration)
        self.assertFalse(video.width)
        self.assertFalse(video.height)

    def test_add_no_file_selected(self):
        response = self.post(
            {
                "title": "nothing here",
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # The form should have an error
        self.assertFormError(
            response.context["form"], "file", "This field is required."
        )

    @override_settings(WAGTAILVIDEOS_MAX_UPLOAD_SIZE=1)
    def test_add_too_large_file(self):
        video_file = create_test_video_file()

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile("small.mp4", video_file.read(), "video/mp4"),
            }
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/add.html")

        # The form should have an error
        self.assertFormError(
            response.context["form"],
            "file",
            "This file is too big ({file_size}). Maximum filesize {max_file_size}.".format(
                file_size=filesizeformat(video_file.size),
                max_file_size=filesizeformat(1),
            ),
        )

    def test_add_too_long_filename(self):
        video_file = create_test_video_file()

        name = "a_very_long_filename_" + ("x" * 100) + ".mp4"
        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(name, video_file.read(), "video/mp4"),
            }
        )

        # Should be valid
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get()

        self.assertEqual(len(video.file.name), Video._meta.get_field("file").max_length)

    def test_add_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        response = self.post(
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "small.mp4", create_test_video_file().read(), "video/mp4"
                ),
                "collection": evil_plans_collection.id,
            }
        )

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

        # Test that it was placed in the Evil Plans collection
        video = videos.first()
        self.assertEqual(video.collection, evil_plans_collection)


class TestVideoEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        self.video = Video.objects.create(
            title="Test video",
            file=create_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:edit", args=(self.video.id,)), params
        )

    def post(self, post_data={}):
        return self.client.post(
            reverse("wagtailvideos:edit", args=(self.video.id,)), post_data
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_usage_count(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")
        self.assertContains(response, "Used 0 times")
        expected_url = "/admin/videos/usage/%d/" % self.video.id
        self.assertContains(response, expected_url)

    def test_edit(self):
        self.post(
            {
                "title": "Edited",
            }
        )

        # Check that the video was edited
        video = Video.objects.get(id=self.video.id)
        self.assertEqual(video.title, "Edited")
        self.assertEqual(self.video.file, video.file)

    def test_edit_with_new_video_file(self):
        # Change the file size of the video
        self.video.file_size = 100000
        self.video.save()

        new_file = create_test_video_file()
        self.post(
            {
                "title": "Edited",
                "file": SimpleUploadedFile("new.mp4", new_file.read(), "video/mp4"),
            }
        )

        # Check that the video file size changed (assume it changed to the correct value)
        video = Video.objects.get(id=self.video.id)
        self.assertNotEqual(video.file_size, 100000)

    def test_with_missing_video_file(self):
        self.video.file.delete(False)

        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/edit.html")
        self.assertContains(response, "The source video file could not be found")


class TestVideoDeleteView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=create_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos:delete", args=(self.video.id,)), params
        )

    def post(self, post_data={}):
        return self.client.post(
            reverse("wagtailvideos:delete", args=(self.video.id,)), post_data
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/videos/confirm_delete.html")

    def test_delete(self):
        # FIXME HACK Not sure why the test fails when no data is posted
        response = self.post({"data": "data"})

        # Should redirect back to index
        self.assertRedirects(response, reverse("wagtailvideos:index"))

        # Check that the video was deleted
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 0)


class TestVideoChooserView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos_chooser:choose"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "choose")

    def test_search(self):
        response = self.get({"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_query"], "Hello")

    def test_pagination(self):
        # page numbers in range should be accepted
        response = self.get({"p": 1})
        self.assertEqual(response.status_code, 200)
        # page numbers out of range should return 404
        response = self.get({"p": 9999})
        self.assertEqual(response.status_code, 404)

    def test_filter_by_tag(self):
        for i in range(0, 10):
            video = Video.objects.create(
                title="Test video %d is even better than the last one" % i,
                file=create_test_video_file(),
            )
            if i % 2 == 0:
                video.tags.add("even")

        response = self.get({"tag": "even"})
        self.assertEqual(response.status_code, 200)

        # Results should include videos tagged 'even'
        self.assertContains(response, "Test video 2 is even better")

        # Results should not include videos that just have 'even' in the title
        self.assertNotContains(response, "Test video 3 is even better")


class TestVideoChooserChosenView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create an video to edit
        self.video = Video.objects.create(
            title="Test video",
            file=create_test_video_file(),
        )

    def get(self, params={}):
        return self.client.get(
            reverse("wagtailvideos_chooser:chosen", args=(self.video.id,)), params
        )

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "chosen")


class TestVideoChooserUploadView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailvideos_chooser:create"), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/chooser/creation_form.html"
        )
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "reshow_creation_form")

    def test_upload(self):
        response = self.client.post(
            reverse("wagtailvideos_chooser:create"),
            {
                "title": "Test video",
                "file": SimpleUploadedFile(
                    "small.mp4", create_test_video_file().read(), "video/mp4"
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        videos = Video.objects.filter(title="Test video")
        self.assertEqual(videos.count(), 1)

    def test_upload_no_file_selected(self):
        response = self.client.post(
            reverse("wagtailvideos_chooser:create"),
            {
                "title": "Test video",
            },
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/chooser/creation_form.html"
        )

        # The form should have an error
        self.assertFormError(
            response.context["form"], "file", "This field is required."
        )


class TestVideoChooserUploadViewWithLimitedPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        add_video_permission = Permission.objects.get(
            content_type__app_label="wagtailvideos", codename="add_video"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=self.evil_plans_collection,
            permission=add_video_permission,
        )

        user = get_user_model().objects.create_user(
            username="moriarty", email="moriarty@example.com", password="password"
        )
        user.groups.add(conspirators_group)

        self.client.login(username="moriarty", password="password")

    def test_get(self):
        response = self.client.get(reverse("wagtailvideos_chooser:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailadmin/generic/chooser/creation_form.html"
        )

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(
            response,
            '<label class="w-field__label" for="id_collection" id="id_collection-label">',
        )

    def test_get_chooser(self):
        response = self.client.get(reverse("wagtailvideos_chooser:choose"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/chooser/chooser.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(
            response,
            '<label class="w-field__label" for="id_collection" id="id_collection-label">',
        )


class TestMultipleVideoUploader(TestCase, WagtailTestUtils):
    """
    This tests the multiple video upload views located in wagtailvideos/views/multiple.py
    """

    def setUp(self):
        self.login()

        # Create an video for running tests on
        self.video = Video.objects.create(
            title="Test video",
            file=create_test_video_file(),
        )

    def test_add(self):
        """
        This tests that the add view responds correctly on a GET request
        """
        # Send request
        response = self.client.get(reverse("wagtailvideos:add_multiple"))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailvideos/multiple/add.html")

    def test_add_post(self):
        """
        This tests that a POST request to the add view saves the video and returns an edit form
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile(
                    "small.mp4", create_test_video_file().read(), "video/mp4"
                ),
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(response, "wagtailvideos/multiple/edit_form.html")

        # Check video
        self.assertIn("video", response.context)
        self.assertEqual(response.context["video"].title, "small.mp4")
        self.assertTrue(response.context["video"].file_size)

        # Check form
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["title"], "small.mp4")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], response.context["video"].id)
        self.assertTrue(response_json["success"])

    def test_add_post_noajax(self):
        """
        This tests that only AJAX requests are allowed to POST to the add view
        """
        response = self.client.post(reverse("wagtailvideos:add_multiple"), {})

        # Check response
        self.assertEqual(response.status_code, 400)

    def test_add_post_nofile(self):
        """
        This tests that the add view checks for a file when a user POSTs to it
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 400)

    def test_add_post_badfile(self):
        """
        This tests that the add view checks for a file when a user POSTs to it
        """
        response = self.client.post(
            reverse("wagtailvideos:add_multiple"),
            {
                "files[]": SimpleUploadedFile("small.mp4", b"This is not an video!"),
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertNotIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertIn("error_message", response_json)
        self.assertFalse(response_json["success"])
        self.assertIn("Not a valid video.", response_json["error_message"])

    def test_edit_get(self):
        """
        This tests that a GET request to the edit view returns a 405 "METHOD NOT ALLOWED" response
        """
        # Send request
        response = self.client.get(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 405)

    def test_edit_post(self):
        """
        This tests that a POST request to the edit view edits the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "New title!",
                ("video-%d-tags" % self.video.id): "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertNotIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])

    def test_edit_post_noajax(self):
        """
        This tests that a POST request to the edit view without AJAX returns a 400 response
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "New title!",
                ("video-%d-tags" % self.video.id): "",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 400)

    def test_edit_post_validation_error(self):
        """
        This tests that a POST request to the edit page returns a json document with "success=False"
        and a form with the validation error indicated
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:edit_multiple", args=(self.video.id,)),
            {
                ("video-%d-title" % self.video.id): "",  # Required
                ("video-%d-tags" % self.video.id): "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTemplateUsed(response, "wagtailvideos/multiple/edit_form.html")

        # Check that a form error was raised
        self.assertFormError(
            response.context["form"], "title", "This field is required."
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("form", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertFalse(response_json["success"])

    def test_delete_get(self):
        """
        This tests that a GET request to the delete view returns a 405 "METHOD NOT ALLOWED" response
        """
        # Send request
        response = self.client.get(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 405)

    def test_delete_post(self):
        """
        This tests that a POST request to the delete view deletes the video
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,)),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Make sure the video is deleted
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("video_id", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["video_id"], self.video.id)
        self.assertTrue(response_json["success"])

    def test_delete_post_noajax(self):
        """
        This tests that a POST request to the delete view without AJAX returns a 400 response
        """
        # Send request
        response = self.client.post(
            reverse("wagtailvideos:delete_multiple", args=(self.video.id,))
        )

        # Check response
        self.assertEqual(response.status_code, 400)
