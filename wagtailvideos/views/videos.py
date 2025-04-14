from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from wagtail.admin import messages
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.filters import BaseMediaFilterSet
from wagtail.admin.views import generic
from wagtail.search.backends import get_search_backends

from wagtailvideos import (get_transcoder_backend, get_video_model)
from wagtailvideos.forms import VideoTranscodeAdminForm, get_video_form
from wagtailvideos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)


Video = get_video_model()


class VideoFilterSet(BaseMediaFilterSet):
    permission_policy = permission_policy

    class Meta:
        model = Video
        fields = []


class IndexView(generic.IndexView):
    context_object_name = "videos"
    model = Video
    filterset_class = VideoFilterSet
    permission_policy = permission_policy
    any_permission_required = ['add', 'change', 'delete']
    header_icon = 'media'
    template_name = 'wagtailvideos/videos/index.html'
    results_template_name = 'wagtailvideos/videos/results.html'
    _show_breadcrumbs = True
    add_url_name = "wagtailvideos:add_multiple"
    edit_url_name = "wagtailvideos:edit"
    index_results_url_name = 'wagtailvideos:index_results'
    add_item_label = "Add a video"

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [
            {"url": "", "label": "Videos"},
        ]

    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs["is_searching"] = self.is_searching
        return kwargs

    def get_paginate_by(self, queryset):
        return 32  # 4 x 8


@permission_checker.require('change')
def edit(request, video_id):
    Video = get_video_model()
    VideoForm = get_video_form(Video)
    video = get_object_or_404(Video, id=video_id)

    if request.POST:
        original_file = video.file
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            if 'file' in form.changed_data:
                # if providing a new video file, delete the old one and all renditions.
                # NB Doing this via original_file.delete() clears the file field,
                # which definitely isn't what we want...
                original_file.storage.delete(original_file.name)

                # Set new video file size
                video.file_size = video.file.size

            video = form.save()
            video.save()

            # Reindex the video to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(video)

            messages.success(request, _("Video '{0}' updated.").format(video.title))
        else:
            messages.error(request, _("The video could not be saved due to errors."))
    else:
        form = VideoForm(instance=video)

    if not video._meta.get_field('file').storage.exists(video.file.name):
        # Give error if video file doesn't exist
        messages.error(request, _(
            "The source video file could not be found. Please change the source or delete the video."
        ).format(video.title), buttons=[
            messages.button(reverse('wagtailvideos:delete', args=(video.id,)), _('Delete'))
        ])
    if hasattr(video, 'track_listing'):
        action_url = reverse('wagtailvideos_tracks:edit', args=(video.track_listing.pk,))
    else:
        action_url = reverse('wagtailvideos_tracks:create', args=(video.pk,))

    return render(request, "wagtailvideos/videos/edit.html", {
        'video': video,
        'form': form,
        'filesize': video.get_file_size(),
        'transcoder_installed': get_transcoder_backend().installed(),
        'transcoder_enabled': not getattr(settings, 'WAGTAIL_VIDEOS_DISABLE_TRANSCODE', False),
        'transcodes': video.transcodes.all(),
        'transcode_form': VideoTranscodeAdminForm(video=video),
        'tracks_action_url': action_url,
        'user_can_delete': permission_policy.user_has_permission_for_instance(request.user, 'delete', video)
    })


@require_POST
def create_transcode(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)
    transcode_form = VideoTranscodeAdminForm(data=request.POST, video=video)

    if transcode_form.is_valid():
        transcode_form.save()
    return redirect('wagtailvideos:edit', video_id)


@permission_checker.require('delete')
def delete(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    if request.POST:
        video.delete()
        messages.success(request, _("Video '{0}' deleted.").format(video.title))
        return redirect('wagtailvideos:index')

    return render(request, "wagtailvideos/videos/confirm_delete.html", {
        'video': video,
    })


@permission_checker.require('add')
def add(request):
    Video = get_video_model()
    VideoForm = get_video_form(Video)

    if request.POST:
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(request.POST, request.FILES, instance=video, user=request.user)
        if form.is_valid():
            # Save
            video = form.save(commit=False)
            video.file_size = video.file.size
            video.save()

            # Success! Send back an edit form
            for backend in get_search_backends():
                backend.add(video)

            messages.success(request, _("Video '{0}' added.").format(video.title), buttons=[
                messages.button(reverse('wagtailvideos:edit', args=(video.id,)), _('Edit'))
            ])
            return redirect('wagtailvideos:index')
        else:
            messages.error(request, _("The video could not be created due to errors."))
    else:
        form = VideoForm(user=request.user)

    return render(request, "wagtailvideos/videos/add.html", {
        'form': form,
    })


def usage(request, video_id):
    video = get_object_or_404(get_video_model(), id=video_id)

    paginator = Paginator(video.get_usage(), per_page=12)
    page = paginator.get_page(request.GET.get('p'))

    return render(request, "wagtailvideos/videos/usage.html", {
        'video': video,
        'used_by': page
    })
