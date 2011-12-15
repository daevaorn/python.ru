function onReady(preview_url) {
    $(document).ready(function() {
        var preview = $('#preview');
        var usertext = preview.find('.usertext');
        var textarea = $('#id_text');
        var scroller = document.body.parentNode;
        var delay = 200;

        function updatePreview(next) {
            $.post(preview_url, textarea.closest("form").serialize(),
                function(value, status) {
                    if (status == 'success' && value) {
                        preview.toggle(!!textarea.val());

                        var offset = scroller.scrollHeight - scroller.scrollTop;

                        usertext.html(value.html);

                        scroller.scrollTop = scroller.scrollHeight - offset;

                        usertext.find('pre code').each(function() {
                            hljs.highlightBlock(this);
                        });

                        next();
                    }
                },
                'json'
            );
        }

        var scheduled = false;

        preview.bind('do_update', function(e) {
            console.log('foobar!!!');
            if (!scheduled && textarea.val()) {
                preview.addClass('updating');

                setTimeout(function() {
                    updatePreview(function () {

                        scheduled = false;

                        preview.show();
                        preview.removeClass('updating');
                    });
                }, delay);

                scheduled = true;
            }
        });

        $('#id_text').keyup(function(e) {
            preview.trigger('do_update');
        });

        $('#id_filter').change(function(e) {
            preview.trigger('do_update');
        });

        preview.trigger('do_update');
    });
}
