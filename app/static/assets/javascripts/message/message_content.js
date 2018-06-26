/**
 * Created by mahedi on 7/6/17.
 */
 $(function () {

            $('#filter').select2().on('select2-selecting', function (e) {
                if (e.object.css == 'quick-filter') {
                    $.ajax({
                        url: base_url + '/admin/filters/quick_filter_exists/',
                        success: function (response) {
                            if (response.status) {
                                var modal_class = 'filters-add-filter';
                                $('#quick-save-div').show();
                                $('#filter-grp-div').hide();
                                $('#preset-name-div').hide();
                                showQuickFilterData(response.filter.id, modal_class);
                            } else {
                                $('#quick-save-div').show();
                                $('#filter-grp-div').hide();
                                $('#preset-name-div').hide();

                                $('#btn-update-quick-filter').show();
                                $('#btn-update-filter').hide();
                                $('.any-or-all').val(1);
                                $('#filters-add-filter').find('.modal-title').html('Quick Filter');
                                $('#preset_filter_group').select2('val', '');

                                $('.filter-panel-title').html("New Filter");
                                $('#filters-add-filter').modal('show');
                                $('#preset_name').attr('data-id', '');
                                var rowCount = 0;
                                $('.filter-list').html($('#filter-li-html').html());
                                activeDatePicker();


                            }
                        }
                    });
                }

            });


            $(".ui-accordion").accordion({
                animate: 100,
                collapsible: true,
                heightStyle: "content",
                header: "> div > h3",
                active: false
            });
            $(".panel-collapse").collapse("hide");
            $(".accordion-toggle").addClass("collapsed");

            var $textBox = $('#message_content');

            function saveSelection() {
                $textBox.data("lastSelection", $textBox.getSelection());
            }

            $textBox.focusout(saveSelection);

            $textBox.bind("beforedeactivate", function () {
                saveSelection();
            });

            $(".question-markdown").click(function () {
                var selection = $textBox.data("lastSelection");
                $textBox.focus();
                if (selection != undefined) {
                    $textBox.setSelection(selection.start, selection.end);
                }
                $textBox.replaceSelectedText("{qid:" + $(this).attr('data-id') + "}", "end");
            });
            $(".general-markdown").click(function () {
                $textBox.replaceSelectedText("{" + $(this).attr('data-id') + "}", "end");
            });
            //            $(".calendar-markdown").click(function () {
            //                $textBox.replaceSelectedText("{calendar}", "end");
            //            });
            //            $(".uid-link-markdown").click(function () {
            //                var url = base_url + "/" + $('.current-event').attr('data-url') + "/";
            //                $textBox.replaceSelectedText(url + "?uid={secret_key}", "end");
            //            });

            $('body').on('click', '#btn-message-preview', function () {
                var input = $("<textarea>")
                        .css('display', 'none')
                        .attr("name", "content").val($('#message_content').val());
                $('#message-preview-form').append($(input));
                $('#message-preview-form').submit();
            });
            $('body').on('click', '#bt-reset-message-content', function () {
                bootbox.confirm("Are you sure you want to reset all content?", function (result) {
                    if (result) {
                        $('#message_content').val("");
                    }
                });

            });

            // Message Content view
            $('body').on('click', '#btn-save-message-content', function () {
                addOrUpdateMessageContent($(this));
            });

            function addOrUpdateMessageContent(button) {
                var content = $('#message_content').val(),
                        csrfToken = $('input[name=csrfmiddlewaretoken]').val(),
                        message_id = $.trim(button.attr('data-id'));
                var language_id = $('#message-preset').val();
                var data = {
                    content: content,
                    language_id: language_id,
                    csrfmiddlewaretoken: csrfToken
                };
                $.ajax({
                    url: base_url + '/admin/messages-content/' + message_id + '/',
                    type: 'POST',
                    data: data,
                    success: function (response) {

                        if (response.success) {
                            $.growl.notice({message: response.message});
                        }
                        else {
                            var errors = response.message;
                            $.growl.warning({message: errors});
                        }
                    },
                    error: function (e) {
                        clog(e);
                    }
                })
                ;
            }
        });

$(document).ready(function () {
    $('#message-preset').select2({
        placeholder: "Please select a preset"
    })
        .on("change", function (e) {
            clog(e);
            var content_id = $('#btn-save-message-content').attr('data-id');
            var language_id = e.val;
            clog(language_id)
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var data = {
                content_id: content_id,
                language_id: language_id,
                csrfmiddlewaretoken: csrfToken
            };
            $.ajax({
                url: base_url + '/admin/messages-content/get-with-lang/',
                type: 'POST',
                data: data,
                cache: false
            })
                .done(function (response) {
                   $("#message_content").val(response.message_content)
                });
            clog("change val=" + e.val);
        });
});