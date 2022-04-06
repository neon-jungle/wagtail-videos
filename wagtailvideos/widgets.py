import json

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from wagtail.admin.widgets import AdminChooser

from wagtailvideos import get_video_model


class AdminVideoChooser(AdminChooser):
    choose_one_text = _('Choose a video')
    choose_another_text = _('Choose another video')
    link_to_chosen_text = _('Edit this video')

    def __init__(self, **kwargs):
        super(AdminVideoChooser, self).__init__(**kwargs)
        self.video_model = get_video_model()

    def render_html(self, name, value, attrs):
        instance, value_data = self.get_instance_and_id(self.video_model, value)

        print('value: ', value)
        print('instance: ', instance)
        print('value_data: ', value_data)

        original_field_html = super(AdminVideoChooser, self).render_html(name, value, attrs)

        return render_to_string("wagtailvideos/widgets/video_chooser.html", {
            'widget': self,
            'original_field_html': original_field_html,
            'attrs': attrs,
            'value': value_data,
            'video': instance,
        })

    def render_js_init(self, id_, name, value):
        return "createVideoChooser({0});".format(json.dumps(id_))

    class Media:
        js = [
            'wagtailvideos/js/video-chooser-modal.js',
            'wagtailvideos/js/video-chooser.js',
        ]
