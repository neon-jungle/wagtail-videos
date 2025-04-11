from django.conf.urls import include
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.admin.panels import InlinePanel
from wagtail.admin.search import SearchArea
from wagtail.admin.site_summary import SummaryItem
from wagtail.admin.viewsets.model import ModelViewSet

from wagtailvideos import get_video_model, urls
from wagtailvideos.edit_handlers import VideoChooserPanel
from wagtailvideos.forms import GroupVideoPermissionFormSet
from wagtailvideos.views.chooser import viewset as chooser_viewset

from .permissions import permission_policy

Video = get_video_model()


class TracksAdminViewset(ModelViewSet):
    model = Video.get_track_listing_model()
    icon = 'openquote'
    menu_label = _('Text tracks')
    url_prefix = 'videos/tracks'

    list_display = ('__str__', 'track_count')

    panels = [
        VideoChooserPanel('video'),
        InlinePanel('tracks', heading="Tracks")
    ]

tracks_viewset = TracksAdminViewset("wagtailvideos_tracks")

@hooks.register("register_admin_viewset")
def register_tracklist_viewset():
    return tracks_viewset

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('videos/', include(urls)),
    ]


@hooks.register('register_group_permission_panel')
def register_video_permissions_panel():
    return GroupVideoPermissionFormSet


class VideoMenu(Menu):
    # Dummy class
    def __init__(self, *args, **kwargs):
        self.register_hook_name = None
        self.construct_hook_name = None
        self._registered_menu_items = None

    @property
    def registered_menu_items(self):
        return [
            MenuItem(_('Manage videos'), reverse('wagtailvideos:index'),
                     name='videos', icon_name='media', order=100),
            tracks_viewset.get_menu_item(),
        ]


@hooks.register('register_admin_menu_item')
def register_images_menu_item():
    return SubmenuMenuItem(
        _('Videos'), VideoMenu(),
        name='videos', icon_name='media', order=300
    )


class VideoSummaryItem(SummaryItem):
    order = 300
    template_name = "wagtailvideos/homepage/videos_summary.html"

    def get_context_data(self, parent_context):
        return {
            "total_videos": Video.objects.count(),
        }

    def is_shown(self):
        return permission_policy.user_has_any_permission(
            self.request.user, ["add", "change", "delete"]
        )


@hooks.register("construct_homepage_summary_items")
def add_media_summary_item(request, items):
    items.append(VideoSummaryItem(request))


class VideoSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ["add", "change", "delete"]
        )


@hooks.register("register_admin_search_area")
def register_media_search_area():
    return VideoSearchArea(
        _("Video"),
        reverse("wagtailvideos:index"),
        name="video",
        icon_name="media",
        order=400,
    )


@hooks.register('insert_global_admin_css')
def summary_css():
    return format_html('<link rel="stylesheet" href="{}">', static('wagtailvideos/css/summary-override.css'))


@hooks.register("register_admin_viewset")
def register_image_chooser_viewset():
    return chooser_viewset
