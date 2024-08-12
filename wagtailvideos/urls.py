from django.urls import path, re_path

from wagtailvideos.views import multiple, videos

app_name = 'wagtailvideos'

urlpatterns = [
    path('add/', videos.add, name='add'),
    re_path(r'^usage/(\d+)/$', videos.usage, name='video_usage'),

    path("multiple/add/", multiple.AddView.as_view(), name="add_multiple"),
    path("multiple/<int:video_id>/", multiple.EditView.as_view(), name="edit_multiple"),
    path(
        "multiple/create_from_uploaded_image/<int:uploaded_file_id>/",
        multiple.CreateFromUploadedVideoView.as_view(),
        name="create_multiple_from_uploaded_image",
    ),
    path(
        "multiple/<int:video_id>/delete/",
        multiple.DeleteView.as_view(),
        name="delete_multiple",
    ),
    path(
        "multiple/delete_upload/<int:uploaded_file_id>/",
        multiple.DeleteUploadView.as_view(),
        name="delete_upload_multiple",
    ),

    re_path(r'^(\d+)/delete/$', videos.delete, name='delete'),
    re_path(r'^(\d+)/create_transcode/$', videos.create_transcode, name='create_transcode'),
    re_path(r'^(\d+)/$', videos.edit, name='edit'),
    path('', videos.IndexView.as_view(), name='index'),
    path("results/", videos.IndexView.as_view(results_only=True), name="index_results"),
]
