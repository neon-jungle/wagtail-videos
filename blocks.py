from django.utils.functional import cached_property
from wagtail.core.blocks import ChooserBlock


class VideoChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtailvideos.models import Video

        return Video

    @cached_property
    def widget(self):
        from wagtailvideos.widgets import AdminVideoChooser

        return AdminVideoChooser

    def render_basic(self, value, context=None):
        if value:
            return value.video_tag(attrs={"controls": True})
        else:
            return ""

    class Meta:
        icon = "fa-play"
