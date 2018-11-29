/**
 * Created by mahedi on 7/6/17.
 */

$(function () {
    $(".ui-accordion").accordion({
        animate: 100,
        collapsible: true,
        heightStyle: "content",
        header: "> div > h3",
        active: false
    });
    $(".panel-collapse").collapse("hide");
    $(".accordion-toggle").addClass("collapsed");
});

var editor;
$(function () {

    tinymce.init({
        selector: '#code',
        plugins: "image code",
        height: "450",
        convert_urls: false

    });

    // photo upload and display start
    $("#files").kendoUpload({
        async: {
            saveUrl: base_url + '/admin/upload-page-image/',
            //                    removeUrl: "remove",
            autoUpload: true
        },
        upload: function (e) {
            e.data = {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()}
        },

        success: function (e) {
            if (e.response.success) {
                $.growl.notice({message: e.response.msg});
                $('#collapseImage').collapse('hide');
                $(".k-upload-files.k-reset").find("li").remove();
            } else {
                $.growl.error({message: e.response.msg});
            }
        }


    });
    var $imageContainer = $('#email-content-uploaded-image');

    $(document).on('click', '.template-images', function () {
        retrieveImages();
    });


    function retrieveImages() {
        $.ajax({
            url: base_url + '/admin/get-page-images/',
            type: "GET",
            success: showImages
        });
    }

    function showImages(response) {
        var images = response.data;
        var imageHtml = '';
        for (var i = 0; i < images.length; i++) {
            imageHtml += '<div class="image-item"><img src="' + images[i].url + '" class="uploaded_image"/>' +
                '<button class="btn-copy-url" data-clipboard-text="' + images[i].url + '">Copy URL</button>' +
                '</div>';
        }
        $imageContainer.html(imageHtml);
        new Clipboard('.btn-copy-url');
    }

    // photo upload and display end

    //            editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    //                mode: 'gfm',
    //                lineNumbers: true,
    //                matchBrackets: true,
    //                lineWrapping: true,
    //                theme: 'base16-light',
    //                extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"},
    //            });
    //            editor.on('change', update);
    //                        $(".accordion-toggle").accordion({
    //                            active: false
    //                        });
    //            var code_content = $.trim($('#code').val());
    //
    //            if (code_content != '') {
    //                editor.setValue(code_content);
    //            }

    $('body').on('click', '#btn-email-preview', function () {
        //                var input = $("<textarea>")
        //                        .css('display', 'none')
        //                        .attr("name", "content").val($('#out').html());
        var input = $("<textarea>")
            .css('display', 'none')
            .attr("name", "content").val(tinyMCE.activeEditor.getContent({format: 'raw'}));
        $('#preview-form').append($(input));
        $('#preview-form').submit();
    });
    $('body').on('click', '#bt-reset-email-content', function () {
        bootbox.confirm("Are you sure you want to reset all content?", function (result) {
            if (result) {
                //                        editor.setValue("");
                tinyMCE.activeEditor.setContent('');
                $('#email-filter-id').select2('val', '');
                $('#email-subject').val('');
                $('#email-name').val('');
                $('#email-template-id').select2('val', '');
            }
        });

    });

    $(".question-markdown").click(function () {
        //                editor.replaceSelection('{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"Y.M.d H:i"}]}', "end")
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"Y.M.d H:i"}]}')
    });
    $(".session-markdown").click(function () {
        //                editor.replaceSelection('{"sessions":[{"id":"","group-id":"","columns":"name,start,end", "sort-column":"start",  "status":"attending","time-date":"Y.M.d H:i"}]}', "end");
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{"sessions":[{"id":"","group-id":"","columns":"name,start,end", "sort-column":"start",  "status":"attending","time-date":"Y.M.d H:i"}]}');
    });
    $(".travel-markdown").click(function () {
        //                editor.replaceSelection('{"travels":[{"id":"","group-id":"","columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"Y.M.d H:i"}]}', "end")
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{"travels":[{"id":"","group-id":"","columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"Y.M.d H:i"}]}')
    });
    $(".hotel-markdown").click(function () {
        //                editor.replaceSelection('{"hotels":[{"id":"","group-id":"","columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"Y.M.d"}]}', "end");
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{"hotels":[{"id":"","group-id":"","columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"Y.M.d"}]}');
    });
    $(".photo-markdown").click(function () {
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{"photo":[{ "group":""}]}');
    });
    $(".base-url-markdown").click(function () {
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, '{base_url}');
    });

    $(".general-markdown").click(function () {

        //                editor.replaceSelection("{" + $(this).attr('data-id') + "}", "end");
        //                tinyMCE.activeEditor.execCommand('mceInsertContent', false,"{" + $(this).attr('data-id') + "}");

        if ($(this).attr('data-id') == 'reset_password_hash_link') {
            //                editor.replaceSelection("[start_hash:]" +
            //                        "Do you want to reset your password for {event_name}?" +
            //                        "<p>To change the password, please click the button below:</p>" +
            //                        "<p><a href=\"{" + $(this).attr('data-id') + "}\" class=\"button\">Reset your password</a></p>" +
            //                    "[:end_hash]", "end");
            text = "[start_hash:]" +
                "Do you want to reset your password for {event_name}?" +
                "<p>To change the password, please click the button below:</p>" +
                "<p><a href=\"{" + $(this).attr('data-id') + "}\" class=\"button\">Reset your password</a></p>" +
                "[:end_hash]";
            tinyMCE.activeEditor.execCommand('mceInsertContent', false, text);
        } else {
            //                editor.replaceSelection("{" + $(this).attr('data-id') + "}", "end");
            tinyMCE.activeEditor.execCommand('mceInsertContent', false, "{" + $(this).attr('data-id') + "}");
        }
    });

    $(".general-question-markdown").click(function () {
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, "{qid:" + $(this).attr('data-id') + "}");
    });

    $(".calendar-markdown").click(function () {
        //                            editor.replaceSelection("{calendar}", "end");
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, "{calendar}");
    });

    $(".uid-link-markdown").click(function () {
        var url = base_url + "/" + $('.current-event').attr('data-url') + "/";
        //                editor.replaceSelection("<a href='" + url + "?uid={secret_key}'>UID Link</a>", "end");
        tinyMCE.activeEditor.execCommand('mceInsertContent', false, "<a href='" + url + "?uid={secret_key}'>UID Link</a>");
    });

    //save

    $('body').on('click', '#btn-save-email-content', function () {
        addOrUpdateEmailContent($(this));
    });


    //endddddddddddddddddddddddddddddddddddddd

    //            $('body').on('click', '#bt-send-filter-email', function (e) {
    //                e.preventDefault();
    //                var $this = $(this);
    //                var rule_id = $('#email-filter-id option:selected').val();
    //                var subject = $('#email-subject').val();
    //                var template_id = $('#email-template-id').val();
    //                var message = editor.getValue();
    //                var message = $('#out').html();
    //                var requiredFields = [
    //                    {fieldId: 'email-subject', message: 'Email Subject'},
    //                    {fieldId: 'email-template-id', message: 'Email Template'}
    //                ];
    //
    //                if (!requiredEmailFieldValidator(requiredFields)) {
    //                    return;
    //                }
    //                var data = {
    //                    'rule_id': rule_id,
    //                    'template_id': template_id,
    //                    'message': message,
    //                    'subject': subject,
    //                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    //                }
    //                console.log(data);
    //                if (rule_id != '' && message != '' && subject != '') {
    //                $('#loader').show();
    //                $this.prop('disabled', true);
    //                $.ajax({
    //                    url: base_url + '/admin/get-message-recipients/',
    //                    type: "POST",
    //                    data: {
    //                        'rule_id': rule_id,
    //                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    //                    },
    //                    success: function (response) {
    //                        if (response.error) {
    //                            $.growl.error({message: response.error});
    //                        } else {
    //                            var total_recipients = response.total_recipients;
    //                            console.log(total_recipients);
    //                            bootbox.confirm("You’re about to send the email to " + total_recipients + " attendees. Are you sure?", function (result) {
    //                                if (result) {
    //                                    send_template_mail(data);
    //                                } else {
    //                                    $('#loader').hide();
    //                                    $this.prop("disabled", false);
    //                                }
    //                            });
    //                        }
    //                    }
    //                });
    //            });


});
function requiredEmailFieldValidator(requiredFields) {
    var message = '';
    var valid = true;
    for (var i = 0; i < requiredFields.length; i++) {
        var Id = requiredFields[i].fieldId;
        if ($('#' + Id).val() == '') {
            message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
            valid = false;
        }
    }
    //            if ($('#email-filter-id option:selected').val() == '' || $('#email-filter-id option:selected').val() == undefined) {
    //                message += "* Filter Rule can't be blank" + "<br>";
    //                valid = false;
    //            }
    if (!valid) {
        $.growl.warning({message: message});
    }
    return valid;
}

function send_template_mail(data) {
    $.ajax({
        url: base_url + '/admin/emails/send-template-mail/',
        type: "POST",
        data: data,
        success: function (result) {
            $('#loader').hide();
            $('#bt-send-filter-email').prop('disabled', false);
            if (result.error) {
                $.growl.error({message: result.error});
            } else {
                $.growl.notice({message: result.success});
                //                        setTimeout(function () {
                ////                            window.location.href = '';
                //                        }, 3000);
            }
        }
    });
}

function requiredFieldValidator(requiredFields) {
    var message = '';
    var valid = true;
    for (var i = 0; i < requiredFields.length; i++) {
        var Id = requiredFields[i].fieldId;
        if ($('#' + Id).val() == '' || $('#' + Id).val() == null) {
            message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
            valid = false;
        }
    }
    if ($('#out').html() == "") {
        message += "*content can't be blank <br>";
        valid = false;
    }

    if (!valid) {
        $.growl.warning({message: message});
    }
    return valid;
}

function addOrUpdateEmailContent(button) {
    //            console.log(editor.getValue());

    //            var content = editor.getValue(),
    var content = tinyMCE.activeEditor.getContent({format: 'raw'});
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    var email_id = $.trim(button.attr('data-id'));
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


// var URL = window.URL || window.webkitURL || window.mozURL || window.msURL;
// navigator.saveBlob = navigator.saveBlob || navigator.msSaveBlob || navigator.mozSaveBlob || navigator.webkitSaveBlob;
// window.saveAs = window.saveAs || window.webkitSaveAs || window.mozSaveAs || window.msSaveAs;
//
// // Because highlight.js is a bit awkward at times
// var languageOverrides = {
//     js: 'javascript',
//     html: 'xml'
// };
//
// emojify.setConfig({img_dir: 'emoji'});
//
// var md = markdownit({
//     html: true,
//     highlight: function (code, lang) {
//         if (languageOverrides[lang]) lang = languageOverrides[lang];
//         if (lang && hljs.getLanguage(lang)) {
//             try {
//                 return hljs.highlight(lang, code).value;
//             } catch (e) {
//             }
//         }
//         return '';
//     }
// })
//     .use(markdownitFootnote);
//
//
// var hashto;
//
// function update(e) {
//     if (e != undefined) {
//         setOutput(e.getValue());
//     }
//
//     clearTimeout(hashto);
//     hashto = setTimeout(updateHash, 1000);
// }
//
// function setOutput(val) {
//     val = val.replace(/<equation>((.*?\n)*?.*?)<\/equation>/ig, function (a, b) {
//         return '<img src="http://latex.codecogs.com/png.latex?' + encodeURIComponent(b) + '" />';
//     });
//
//     var out = document.getElementById('out');
//     var old = out.cloneNode(true);
//     out.innerHTML = md.render(val);
//     emojify.run(out);
//
//     var allold = old.getElementsByTagName("*");
//     if (allold === undefined) return;
//
//     var allnew = out.getElementsByTagName("*");
//     if (allnew === undefined) return;
//
//     for (var i = 0, max = Math.min(allold.length, allnew.length); i < max; i++) {
//         if (!allold[i].isEqualNode(allnew[i])) {
//             out.scrollTop = allnew[i].offsetTop;
//             return;
//         }
//     }
// }
//
//
// document.addEventListener('drop', function (e) {
//     e.preventDefault();
//     e.stopPropagation();
//
//     var reader = new FileReader();
//     reader.onload = function (e) {
//         editor.setValue(e.target.result);
//     };
//
//     reader.readAsText(e.dataTransfer.files[0]);
// }, false);
//
//
// function saveAsMarkdown() {
//     save(editor.getValue(), "untitled.md");
// }
//
// function saveAsHtml() {
//     save(document.getElementById('out').innerHTML, "untitled.html");
// }
//
// function save(code, name) {
//     var blob = new Blob([code], {type: 'text/plain'});
//     if (window.saveAs) {
//         window.saveAs(blob, name);
//     } else if (navigator.saveBlob) {
//         navigator.saveBlob(blob, name);
//     } else {
//         url = URL.createObjectURL(blob);
//         var link = document.createElement("a");
//         link.setAttribute("href", url);
//         link.setAttribute("download", name);
//         var event = document.createEvent('MouseEvents');
//         event.initMouseEvent('click', true, true, window, 1, 0, 0, 0, 0, false, false, false, false, 0, null);
//         link.dispatchEvent(event);
//     }
// }
//
//
// var menuVisible = false;
// var menu = document.getElementById('menu');
//
// function showMenu() {
//     menuVisible = true;
//     menu.style.display = 'block';
// }
//
// function hideMenu() {
//     menuVisible = false;
//     menu.style.display = 'none';
// }
//
// document.addEventListener('keydown', function (e) {
//     if (e.keyCode == 83 && (e.ctrlKey || e.metaKey)) {
//         e.shiftKey ? showMenu() : saveAsMarkdown();
//
//         e.preventDefault();
//         return false;
//     }
//
//     if (e.keyCode === 27 && menuVisible) {
//         hideMenu();
//
//         e.preventDefault();
//         return false;
//     }
// });
//
//
// function updateHash() {
//     //            window.location.hash = btoa( // base64 so url-safe
//     //                    RawDeflate.deflate( // gzip
//     //                            unescape(encodeURIComponent( // convert to utf8
//     //                                    editor.getValue()
//     //                            ))
//     //                    )
//     //            );
// }
//
// if (window.location.hash) {
//     var h = window.location.hash.replace(/^#/, '');
//     if (h.slice(0, 5) == 'view:') {
//         setOutput(decodeURIComponent(escape(RawDeflate.inflate(atob(h.slice(5))))));
//         document.body.className = 'view';
//     } else {
//         editor.setValue(
//             decodeURIComponent(escape(
//                 RawDeflate.inflate(
//                     atob(
//                         h
//                     )
//                 )
//             ))
//         );
//         update(editor);
//         editor.focus();
//     }
// } else if (editor != undefined) {
//     update(editor);
//     editor.focus();
// }
$(document).ready(function () {
    $('#email-preset').select2({
        placeholder: "Please select a preset"
    })
        .on("change", function (e) {
            clog(e);
            var content_id = $('#btn-save-email-content').attr('data-id');
            var language_id = e.val;
            clog(language_id)
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
                    tinyMCE.activeEditor.setContent(response.email_content);
                });
            clog("change val=" + e.val);

        });
});