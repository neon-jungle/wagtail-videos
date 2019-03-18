import json

from django.utils.translation import ugettext as _

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
# from wagtail.admin.forms import SearchForm
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.utils import PermissionPolicyChecker, popular_tags_for_model
from wagtail.core.models import Collection
from wagtail.search import index as search_index
from wagtail.utils.pagination import paginate

from wagtailvideos.forms import get_video_form
from wagtailvideos.models import Video, get_video_model
from wagtailvideos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)


def get_chooser_js_data():
    """construct context variables needed by the chooser JS"""
    return {
        'step': 'chooser',
        'error_label': _("Server Error"),
        'error_message': _("Report this error to your webmaster with the following information:"),
        'tag_autocomplete_url': reverse('wagtailadmin_tag_autocomplete'),
    }

def get_video_json(video):
    """
    helper function: given an image, return the json to pass back to the
    image chooser panel
    """
    return {
        'id': video.id,
        'edit_link': reverse('wagtailvideos:edit', args=(video.id,)),
        'title': video.title,
        'preview': {
            'url': video.thumbnail.url if video.thumbnail else '',
        }
    }


def get_chooser_context(request):
    """Helper function to return common template context variables for the main chooser view"""

    collections = Collection.objects.all()
    if len(collections) < 2:
        collections = None
    else:
        collections = Collection.order_for_display(collections)

    return {
        'searchform': SearchForm(),
        'is_searching': False,
        'query_string': None,
        'will_select_format': request.GET.get('select_format'),
        'popular_tags': popular_tags_for_model(Video),
        'collections': collections,
    }



def paginate1(request, items, page_key=1, per_page=20):

    page = request.GET.get(page_key, 1)
    from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
    paginator = Paginator(items, per_page)
    try:
        page = paginator.get_page(page)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    return paginator, page


def chooser(request):

    VideoForm = get_video_form(Video)
    uploadform = VideoForm()

    videos = Video.objects.order_by('-created_at')

    q = None
    if (
        'q' in request.GET or 'p' in request.GET or 'tag' in request.GET or
        'collection_id' in request.GET
    ):

        # this request is triggered from search, pagination or 'popular tags';
        # we will just render the results.html fragment
        collection_id = request.GET.get('collection_id')
        if collection_id:
            videos = videos.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            videos = videos.search(q)
            is_searching = True
        else:
            is_searching = False

            tag_name = request.GET.get('tag')
            if tag_name:
                videos = videos.filter(tags__name=tag_name)


        # Pagination
        paginator, videos = paginate(request, videos, per_page=12)
        return render(request, "wagtailvideos/chooser/results.html", {
            'videos': videos,
            'is_searching': is_searching,
            'query_string': q,
        })
    else:

        searchform = SearchForm()
        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None

        paginator, videos = paginate1(request, videos, per_page=12)

        context = get_chooser_context(request)
        context.update({
                'videos': videos,
                'uploadform': uploadform,
                'searchform': searchform,
                'is_searching': False,
                'query_string': q,
                'popular_tags': popular_tags_for_model(Video),
                # 'collections': collections,

        })

    return render_modal_workflow(
        request, 'wagtailvideos/chooser/chooser.html', None, context,
        json_data=get_chooser_js_data()
    )


def video_chosen(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    return render_modal_workflow(
        request, None, None,
        None, json_data={'step': 'video_chosen', 'result': get_video_json(video)}
    )


@permission_checker.require('add')
def chooser_upload(request):
    VideoForm = get_video_form(Video)

    searchform = SearchForm()

    if request.POST:
        video = Video(uploaded_by_user=request.user)
        form = VideoForm(request.POST, request.FILES, instance=video)

        if form.is_valid():
            video.uploaded_by_user = request.user
            video.save()

            # Reindex the video to make sure all tags are indexed
            search_index.insert_or_update_object(video)

            return render_modal_workflow(
                request, None, None,
                None, json_data={'step': 'video_chosen', 'result': get_video_json(video)}
            )

    else:
        form = VideoForm()

    videos = Video.objects.order_by('-created_at')
    paginator, videos = paginate(request, videos, per_page=12)

    context = get_chooser_context(request)
    context.update({
            'videos': videos,
            'uploadform': form,
            'searchform': searchform,
            'is_searching': False,
            'popular_tags': popular_tags_for_model(Video),
    })

    return render_modal_workflow(
        request, 'wagtailvideos/chooser/chooser.html', None, context,
        json_data=get_chooser_js_data()
    )