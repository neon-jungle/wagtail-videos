VIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS = {
    'chooser': function(modal, jsonData) {
        function ajaxifyLinks (context) {
            $('a.video-choice', context).click(function() {
                modal.loadUrl(this.href);
                return false;
            });

            $('.pagination a', context).click(function() {
                var page = this.getAttribute("data-page");
                setPage(page);
                return false;
            });
        };

        var searchUrl = $('form.video-search', modal.body).attr('action');
        function search() {
            $.ajax({
                url: searchUrl,
                data: {
                    q: $('#id_q').val(),
                    collection_id: $('#collection_chooser_collection_id').val()
                },
                success: function(data, status) {
                    $('#image-results').html(data);
                    ajaxifyLinks($('#image-results'));
                }
            });
            return false;
        };
        function setPage(page) {

            if($('#id_q').val().length){
                dataObj = {q: $('#id_q').val(), p: page};
            }else{
                dataObj = {p: page};
            }

            $.ajax({
                url: searchUrl,
                data: dataObj,
                success: function(data, status) {
                    $('#image-results').html(data);
                    ajaxifyLinks($('#image-results'));
                }
            });
            return false;
        }

        ajaxifyLinks(modal.body);

        $('form.video-upload', modal.body).submit(function() {
            var formdata = new FormData(this);

            $.ajax({
                url: this.action,
                data: formdata,
                processData: false,
                contentType: false,
                type: 'POST',
                dataType: 'text',
                success: function(response){
                    modal.loadResponseText(response);
                },
                error: function(response, textStatus, errorThrown) {
                    message = jsonData['error_message'] + '<br />' + errorThrown + ' - ' + response.status;
                    $('#upload').append(
                        '<div class="help-block help-critical">' +
                        '<strong>' + jsonData['error_label'] + ': </strong>' + message + '</div>');
                }
            });

            return false;
        });

        $('form.video-search', modal.body).submit(search);

        $('#id_q').on('input', function() {
            clearTimeout($.data(this, 'timer'));
            var wait = setTimeout(search, 50);
            $(this).data('timer', wait);
        });

        $('#collection_chooser_collection_id').change(search);

        // {% url 'wagtailadmin_tag_autocomplete' as autocomplete_url %}
        $('#id_tags', modal.body).tagit({
            autocomplete: {source: jsonData['tag_autocomplete_url']}
        });
    },
    'video_chosen': function(modal, jsonData) {
        modal.respond('videoChosen', jsonData['result']);
        modal.close();
    },
};
