$(function () {
    // Add General Tags
    var static_url = "https://192.168.1.12:8080/";
    var event_styles = $('#editor_event_stylesheet').val();
    var min_height = parseInt($('#editor_min_height').val());
    var max_height = parseInt($('#editor_max_height').val());
    var editor_editor_iframe_style = $('#editor_editor_iframe_style').val();
    var editor_toolbar_inline_data = $('#editor_toolbar_inline').val();
    var editor_toolbar_inline = false;
    if (editor_toolbar_inline_data == '1') {
        editor_toolbar_inline = true;
    }
    if (min_height == NaN) {
        min_height = 200;
    }
    if (max_height == NaN) {
        max_height = 200;
    }
    if (event_styles == undefined) {
        event_styles = '';
    }
    var editor_fullpage = $('#editor_fullpage').val();
    var is_fullpage = false;
    if (editor_fullpage == 'true') {
        is_fullpage = true;
    }
    var editor_link_styles = JSON.parse($('#editor_link_styles').val().replace(/'/g, '"'));
    var editor_font_familys = JSON.parse($('#editor_font_familys').val().replace(/'/g, '"'));
    $.FroalaEditor.DefineIcon('general_tags', {NAME: 'tags'});
    $.FroalaEditor.RegisterCommand('general_tags', {
        title: 'General Tags',
        type: 'dropdown',
        focus: false,
        undo: false,
        refreshAfterCallback: true,
        options: {
            'uid_link': 'UID Link',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email_address': 'Email Address',
            'registration_date': 'Registration Date',
            'uid': 'UID',
            'bid': 'BID',
            'bidqr': 'BIDQR',
            'updated_date': 'Last Updated Date',
            'attendee_groups': 'Attendee Groups',
            'tags': 'Tags',
            'calendar': 'Calendar',
            'reset_password_hash_link': 'Reset Password Hash Link',
            'messages_link': 'Messgae Link',
            'base_url': 'Base Url'
        },
        callback: function (cmd, val) {
            if (val == 'reset_password_hash_link') {
                var text = "[start_hash:]" +
                    "Do you want to reset your password for {event_name}?" +
                    "<p>To change the password, please click the button below:</p>" +
                    "<p><a href=\"{" + val + "}\" class=\"button\">Reset your password</a></p>" +
                    "[:end_hash]";
                this.html.insert(text);
            } else {
                this.html.insert('{' + val + '}');
            }
            $('textarea#froala_content_editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            clog('do refresh tag');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            clog('do refresh when show tag');
        }
    });
    // Add Economy Tags
    $.FroalaEditor.DefineIcon('economy_tags', {NAME: 'money'});
    $.FroalaEditor.RegisterCommand('economy_tags', {
        title: 'Economy Tags',
        type: 'dropdown',
        focus: false,
        undo: false,
        refreshAfterCallback: true,
        options: {
            'order_owner': 'Order Owner',
            'order_table': 'Order Table',
            'multiple_order_table': 'Multiple Order Table',
            'balance_table': 'Balance Table',
            'order_value_paid_order': 'Order value paid order',
            'multiple_order_value_paid_order': 'Multiple Order value paid order',
            'order_value_pending_order': 'Order value pending order',
            'multiple_order_value_pending_order': 'Multiple Order value pending order',
            'order_value_open_order': 'Order value open order',
            'multiple_order_value_open_order': 'Multiple Order value open order',
            'order_value_all_order': 'Order value all order',
            'multiple_order_value_all_order': 'Multiple Order value all order',
            'order_value_credit_order': 'Order value credit order',
            'multiple_order_value_credit_order': 'Multiple Order value credit order',
            'receipt': 'Receipt'
        },
        callback: function (cmd, val) {
            this.html.insert('{' + val + '}');
            $('textarea#froala_content_editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            clog('do refresh economy');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            clog('do refresh when show economy');
        }
    });
    // Add Group Tags
    $.FroalaEditor.DefineIcon('group_tags', {NAME: 'object-group'});
    $.FroalaEditor.RegisterCommand('group_tags', {
        title: 'Group Tags',
        type: 'dropdown',
        focus: false,
        undo: false,
        refreshAfterCallback: true,
        options: {
            'questions': 'Questions',
            'sessions': 'Sessions',
            'travels': 'Travels',
            'hotels': 'Hotels',
            'photos': 'Photos'
        },
        callback: function (cmd, val) {
            var date_format = 'm-d-Y';
            var time_format = 'H:i';
            var date_time_format = date_format + ' ' + time_format;
            var default_date_format = $('#editor_default_date_format').val();
            var default_time_format = $('#editor_default_time_format').val();
            var default_date_time_format = $('#editor_default_date_time_format').val();
            if ((default_date_format != '' || default_date_format != undefined) && (default_time_format != '' || default_time_format != undefined) && (default_date_time_format != '' || default_date_time_format != undefined)) {
                date_format = default_date_format
                time_format = default_time_format
                date_time_format = default_date_time_format
            }
            if (val == 'questions') {
                this.html.insert('{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"' + date_time_format + '"}]}');
            } else if (val == 'sessions') {
                this.html.insert('{"sessions":[{"id":"","group-id":"","columns":"name,start,end", "sort-column":"start",  "status":"attending","time-date":"' + date_time_format + '"}]}');
            } else if (val == 'travels') {
                this.html.insert('{"travels":[{"id":"","group-id":"","columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"' + date_time_format + '"}]}');
            } else if (val == 'hotels') {
                this.html.insert('{"hotels":[{"id":"","group-id":"","columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"' + date_format + '"}]}');
            } else if (val == 'photos') {
                this.html.insert('{"photo":[{ "group":""}]}');
            }
            $('textarea#froala_content_editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            clog('do refresh group');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            clog('do refresh when show group');
        }
    });
    // Add General Questions
    var general_questions = $('#editor_question_group_list').val().replace(/'/g, '"');
    var general_questions = JSON.parse(general_questions);
    var general_question_buttons = [];
    for (var i = 0; i < general_questions.length; i++) {
        $.map(general_questions[i], function (elementOfArray, indexInArray) {
            var group_name = indexInArray;
            var general_question_tag = group_name.toLowerCase();
            general_question_buttons.push(general_question_tag);
            $.FroalaEditor.DefineIcon(general_question_tag, {NAME: 'question-circle'});
            $.FroalaEditor.RegisterCommand(general_question_tag, {
                title: group_name,
                type: 'dropdown',
                focus: false,
                undo: false,
                refreshAfterCallback: true,
                options: elementOfArray,
                callback: function (cmd, val) {
                    this.html.insert('{qid:' + val + '}');
                    $('textarea#froala_content_editor').froalaEditor('events.trigger', 'contentChanged', [], true);
                },
                // Callback on refresh.
                refresh: function ($btn) {
                    clog('do refresh question');
                },
                // Callback on dropdown show.
                refreshOnShow: function ($btn, $dropdown) {
                    clog('do refresh when show question');
                }
            });
        });
    }
    var toolbarButtons = ['bold', 'italic', 'underline', 'strikeThrough', 'subscript', 'superscript', 'fontFamily', 'fontSize', '|', 'specialCharacters', 'color', 'emoticons', 'paragraphStyle', '|', 'paragraphFormat', 'align', 'formatOL', 'formatUL', 'outdent', 'indent', '-', 'quote', 'insertHR', 'insertLink', 'insertImage', 'insertVideo', 'insertFile', 'insertTable', '|', 'undo', 'redo', 'clearFormatting', 'selectAll', 'html', 'applyFormat', 'removeFormat', 'fullscreen', 'print', 'help', '-', 'general_tags', 'economy_tags', 'group_tags'];
    toolbarButtons = $.merge(toolbarButtons, general_question_buttons);

    $('textarea#froala_content_editor').on('froalaEditor.initialized', function (e, editor) {
        editor.events.bindClick($('body'), 'button#btn-reset-editor-content', function () {
            editor.html.set('');
            editor.events.focus();
        }), editor.events.bindClick($('body'), 'button#btn-save-email-content', function (e) {
            addOrUpdateEmailContent(editor);
        }), editor.events.bindClick($('body'), 'button#btn-save-email-template', function (e) {
            addOrUpdateTemplateContent(editor);
        });
    }).froalaEditor({
        toolbarInline: editor_toolbar_inline,
        charCounterCount: false,
        toolbarButtons: toolbarButtons,
        toolbarButtons: toolbarButtons,
        toolbarButtonsMD: toolbarButtons,
        toolbarButtonsSM: toolbarButtons,
        toolbarButtonsXS: toolbarButtons,
        pluginsEnabled: null,
        entities: '',
        // Set a preloader.
        imageManagerPreloader: static_url + "assets/images/712.GIF",

        // Set page size.
        imageManagerPageSize: 20,

        // Set a scroll offset (value in pixels).
        imageManagerScrollOffset: 10,

        // Set the load images request URL.
        imageManagerLoadURL: base_url + '/admin/get-editor-all-images/',

        // Set the load images request type.
        imageManagerLoadMethod: "POST",

        // Additional load params.
        imageManagerLoadParams: {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},

        // Set the delete image request URL.
        imageManagerDeleteURL: base_url + '/admin/delete-image-from-editor/',

        // Set the delete image request type.
        imageManagerDeleteMethod: "POST",

        // Additional delete params.
        imageManagerDeleteParams: {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},
        // Set the image upload parameter.
        imageUploadParam: 'image_param',

        // Set the image upload URL.
        imageUploadURL: base_url + '/admin/upload-image-from-editor/',

        // Additional upload params.
        imageUploadParams: {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},

        // Set request type.
        imageUploadMethod: 'POST',

        // Set max image size to 5MB.
        imageMaxSize: 5 * 1024 * 1024,

        // Allow to upload PNG and JPG.
        imageAllowedTypes: ['jpeg', 'jpg', 'png', 'svg'],
        codeMirrorOptions: {
            tabSize: 4,
            lineNumbers: true,
            matchBrackets: true,
            mode: "text/html",
            styleActiveLine: true,
            indentWithTabs: true
        },
        iframe: true,
        fullPage: is_fullpage,
        iframeStyleFiles: [event_styles],
        htmlRemoveTags: [],
        heightMin: min_height,
        heightMax: max_height,
        // iframeStyle: editor_editor_iframe_style,
        zIndex: 8000,
        toolbarSticky: false,
        linkStyles: editor_link_styles,
        fontFamily: editor_font_familys,
        htmlExecuteScripts: false
        // enter: $.FroalaEditor.ENTER_P
    })
        .on('froalaEditor.imageManager.error', function (e, editor, error, response) {
            // Bad link. One of the returned image links cannot be loaded.
            if (error.code == 10) {
            }
            // Error during request.
            else if (error.code == 11) {
            }
            // Missing imagesLoadURL option.
            else if (error.code == 12) {
            }
            // Parsing response failed.
            else if (error.code == 13) {
            }
        })
        .on('froalaEditor.imageManager.imagesLoaded', function (e, editor, data) {
            // clog(data);
            // Do something when the request finishes with success.
            // alert('Images have been loaded.');
        }).on('froalaEditor.imageManager.imageLoaded', function (e, editor, $img) {
        // Do something when an image is loaded in the image manager
        //     alert('Image has been loaded.');
    }).on('froalaEditor.imageManager.beforeDeleteImage', function (e, editor, $img) {
        // Do something before deleting an image from the image manager.
        // alert('Image will be deleted.');
    }).on('froalaEditor.imageManager.imageDeleted', function (e, editor, data) {
        // Do something after the image was deleted from the image manager.
        // alert('Image has been deleted.');
    }).on('froalaEditor.image.beforeUpload', function (e, editor, images) {
        // Return false if you want to stop the image upload.
    })
        .on('froalaEditor.image.uploaded', function (e, editor, response) {
            // Image was uploaded to the server.
        })
        .on('froalaEditor.image.inserted', function (e, editor, $img, response) {
            // Image was inserted in the editor.
        })
        .on('froalaEditor.image.replaced', function (e, editor, $img, response) {
            // Image was replaced in the editor.
        })
        .on('froalaEditor.image.error', function (e, editor, error, response) {
            // Bad link.
            if (error.code == 1) {
            }

            // No link in upload response.
            else if (error.code == 2) {
            }

            // Error during image upload.
            else if (error.code == 3) {
            }

            // Parsing response failed.
            else if (error.code == 4) {
            }

            // Image too text-large.
            else if (error.code == 5) {
            }

            // Invalid image type.
            else if (error.code == 6) {
            }

            // Image can be uploaded only to same domain in IE 8 and IE 9.
            else if (error.code == 7) {
            }

            // Response contains the original server response to the request if available.
        }).on('froalaEditor.html.get', function (e, editor) {
        if (editor.codeView.isActive()) {
            return editor.codeView.get();
        }
    });
    $('body').on('click', '#btn-email-preview', function () {
        var input = $("<textarea>")
            .css('display', 'none')
            .attr("name", "content").val($('textarea#froala_content_editor').froalaEditor('html.get'));
        $('#editor-preview-form').append($(input));
        $('#editor-preview-form').submit();
    });
    $('body').on('click', '#btn-description-preview', function () {
        var form = document.createElement("form");
        form.action = base_url + '/admin/description-preview/';
        form.target = '_blank';
        form.method = 'POST';
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var node1 = document.createElement("input");
        node1.name = 'csrfmiddlewaretoken';
        node1.value = csrfToken;
        form.appendChild(node1.cloneNode());
        var node2 = document.createElement("textarea");
        node2.name = 'content';
        node2.value = $('textarea#froala_content_editor').froalaEditor('html.get');
        form.appendChild(node2.cloneNode());
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    });
    $('#email-preset').select2({
        placeholder: "Please select a preset"
    })
        .on("change", function (e) {
            clog(e);
            var content_id = $('#btn-save-email-content').attr('data-id');
            var language_id = e.val;
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var data = {
                content_id: content_id,
                language_id: language_id,
                csrfmiddlewaretoken: csrfToken
            };
            $.ajax({
                url: base_url + '/admin/emails-content/get-with-lang/',
                type: 'POST',
                data: data,
                cache: false
            })
                .done(function (response) {
                    if (response.success) {
                        $('#editor_default_date_format').val(response.language_data.date_format);
                        $('#editor_default_time_format').val(response.language_data.time_format);
                        $('#editor_default_date_time_format').val(response.language_data.datetime_format);
                        $('textarea#froala_content_editor').froalaEditor('html.set', response.email_content);
                    }
                });
            clog("change val=" + e.val);

        });
});

function addOrUpdateEmailContent(editor) {

    var content = editor.html.get();
    // content = content.replace(/(\r\n|\n|\r)/gm, "");
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    var email_id = $.trim($('#btn-save-email-content').attr('data-id'));
    var language_id = $('#email-preset').val();
    var data = {
        content: content,
        language_id: language_id,
        csrfmiddlewaretoken: csrfToken
    };
    $.ajax({
        url: base_url + '/admin/emails-content/' + email_id + '/',
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

function addOrUpdateTemplateContent(editor) {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var content = editor.html.get();
    // content = content.replace(/(\r\n|\n|\r)/gm, "");
    content = content.replace('<div id="content-body-data">{content}</div>', '{content}');
    content = content.replace('<p>{content}</p>', '{content}');
    var template_id = window.location.pathname.split('/')[3];
    $.ajax({
        url: base_url + '/admin/templates/',
        type: "POST",
        data: {
            content: JSON.stringify(content),
            csrfmiddlewaretoken: csrf_token,
            id: template_id
        },
        success: function (response) {
            if (response.success) {
                $.growl.notice({message: response.message});
                // setTimeout(function () {
                //     window.location = ''
                // }, 500);
            }
            else {
                $.growl.error({message: response.message});
            }
        }
    });
}