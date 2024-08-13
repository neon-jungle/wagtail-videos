import os

from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.views.generic.multiple_upload import AddView as BaseAddView
from wagtail.admin.views.generic.multiple_upload import \
    CreateFromUploadView as BaseCreateFromUploadView
from wagtail.admin.views.generic.multiple_upload import \
    DeleteUploadView as BaseDeleteUploadView
from wagtail.admin.views.generic.multiple_upload import \
    DeleteView as BaseDeleteView
from wagtail.admin.views.generic.multiple_upload import \
    EditView as BaseEditView

from wagtailvideos import get_video_model
from wagtailvideos.forms import get_video_form
from wagtailvideos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)


def get_video_edit_form(video_model):
    VideoForm = get_video_form(video_model)

    class VideoEditForm(VideoForm):
        class Meta(VideoForm.Meta):
            model = video_model
            exclude = (
                'file',
            )

    return VideoEditForm


class AddView(BaseAddView):
    permission_policy = permission_policy
    template_name = 'wagtailvideos/multiple/add.html'
    edit_form_template_name = 'wagtailvideos/multiple/edit_form.html'

    edit_object_url_name = "wagtailvideos:edit_multiple"
    delete_object_url_name = "wagtailvideos:delete_multiple"
    edit_object_form_prefix = "video"
    context_object_name = "video"
    context_object_id_name = "video_id"

    edit_upload_url_name = "wagtailvideos:create_multiple_from_uploaded_image"
    delete_upload_url_name = "wagtailvideos:delete_upload_multiple"
    edit_upload_form_prefix = "uploaded-video"
    context_upload_name = "uploaded_video"
    context_upload_id_name = "uploaded_file_id"

    def get_model(self):
        return get_video_model()

    def get_upload_form_class(self):
        return get_video_form(self.model)

    def get_edit_form_class(self):
        return get_video_edit_form(self.model)

    def save_object(self, form):
        video = form.save(commit=False)
        video.uploaded_by_user = self.request.user
        video.save()
        return video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "max_filesize": self.form.fields["file"].max_upload_size,
                "max_title_length": self.form.fields["title"].max_length,
                "error_max_file_size": self.form.fields["file"].error_messages[
                    "file_too_large_unknown_size"
                ],
                "error_accepted_file_types": self.form.fields["file"].error_messages[
                    "invalid_video_format"
                ],
            }
        )

        return context


class EditView(BaseEditView):
    permission_policy = permission_policy
    pk_url_kwarg = "video_id"
    edit_object_form_prefix = "video"
    context_object_name = "video"
    context_object_id_name = "video_id"
    edit_object_url_name = "wagtailvideos:edit_multiple"
    delete_object_url_name = "wagtailvideos:delete_multiple"

    def get_model(self):
        return get_video_model()

    def get_edit_form_class(self):
        return get_video_edit_form(self.model)


class DeleteView(BaseDeleteView):
    permission_policy = permission_policy
    pk_url_kwarg = "video_id"
    context_object_id_name = "video_id"

    def get_model(self):
        return get_video_model()


class CreateFromUploadedVideoView(BaseCreateFromUploadView):
    edit_upload_url_name = "wagtailvideos:create_multiple_from_uploaded_image"
    delete_upload_url_name = "wagtailvideos:delete_upload_multiple"
    upload_pk_url_kwarg = "uploaded_file_id"
    edit_upload_form_prefix = "uploaded-video"
    context_object_id_name = "video_id"
    context_upload_name = "uploaded_video"

    def get_model(self):
        return get_video_model()

    def get_edit_form_class(self):
        return get_video_edit_form(self.model)

    def save_object(self, form):
        #  See wagtailimages.views.multiple.CreateFromUploadedImageView.save_object
        self.object.file.save(
            os.path.basename(self.upload.file.name), self.upload.file.file, save=False
        )
        self.object.uploaded_by_user = self.request.user

        self.object._set_image_file_metadata()

        form.save()


class DeleteUploadView(BaseDeleteUploadView):
    upload_pk_url_kwarg = "uploaded_file_id"

    def get_model(self):
        return get_video_model()
