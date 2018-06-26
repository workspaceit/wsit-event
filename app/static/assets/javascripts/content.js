var filter_list = [];
$(function () {
    $('body').find('.module-element').each(function () {
        var element_id = "elements-" + $(this).attr('data-name');
        var element_html = $('#' + element_id).html();
        $(this).html(element_html);
    });
    if ($('#fliter-data').val() != '' && $('#fliter-data').val() != null && $('#fliter-data').val() != undefined && $('#fliter-data').val() != "None") {
        var filter_data = jQuery.parseJSON($('#fliter-data').val());
        filter_list = filter_data;
    }
    var $body = $('body');
    var base_url = window.location.origin;
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var hiddenDiv = $('#hidden-content');
    $body.on('click', '#btn-add-content', function () {
        var pageUrl = $('#page-url-txt').val();
        if (pageUrl.length == 0) {
            $.growl.error({message: "Page URL can't be blank"});
        }
        else {

            hiddenDiv.html($("#mainContent").html());
            hiddenDiv.find('.toolBox').remove();
            hiddenDiv.find('.element').removeClass('.element');
//            hiddenDiv.find('.element').children().unwrap();
            var allHtml = hiddenDiv.html().replace(/ui-sortable/g, '').replace(/(\r\n|\n|\r|\t)/gm, "").replace(/\s+/g, " ");
            $.ajax({
                url: base_url + '/admin/pages/',
                type: "POST",
                data: {
                    content: JSON.stringify({
                        page_url: pageUrl,
                        content: allHtml
                    }),
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.message});
                    } else {
                        $.growl.notice({message: result.message});
//                        setTimeout(function () {
//                            window.location.href = base_url + '/admin/pages/';
//                        }, 800);
                    }
                }
            });
        }
    });

    $body.on('change', '#settings-toggle', function () {
        if ($(this).is(":checked")) {
            $('#plugin-settings').addClass("visible")
        } else {
            $('#plugin-settings').removeClass("visible")
        }
    });
    $body.on('click', '.close-button', function () {
        $(this).closest('.left-menu').removeClass("visible");
        if ($(this).parent().is('#addQuestion')) {
            $("#addQuestionButton").toggleClass("active");
        }
        if ($(this).parent().is('#addModuleComponent')) {
            $("#addModuleButton").toggleClass("active");
        }
        if ($(this).parent().is('#upload-pop-up')) {
            $("#btn-show-upload").toggleClass("active");
        }
        if ($(this).parent().is('#image-pop-up')) {
            $("#btn-show-images").toggleClass("active");
        }
        if ($(this).parent().is('#addColumns')) {
            $("#addColumnsButton").toggleClass("active");
        }
    });

//    $body.on('click', '.btn-pencil', function(){
//
//    });


    $body.on('click', '#btn-update-content', function () {
        var pageUrl = $('#page-url-txt').val();
        var page_id = $('#btn-update-content').attr('data-id');
//        var page_id = window.location.pathname.split('/')[3];
//        console.log(page_id);

//        console.log($("#mainContent").html());
        if (pageUrl.length == 0) {
            $.growl.error({message: "Page URL can't be blank"});
        }
        else {
            hiddenDiv.html($("#mainContent").html());
            hiddenDiv.find('.toolBox').remove();
            hiddenDiv.find('.element').children().unwrap();
            var allHtml = hiddenDiv.html().replace(/ui-sortable/g, '').replace(/(\r\n|\n|\r|\t)/gm, "").replace(/\s+/g, " ");
            $.ajax({
                url: base_url + '/admin/pages/',
                type: "POST",
                data: {
                    content: JSON.stringify({
                        page_url: pageUrl,
                        content: allHtml
                    }),
                    id: page_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.message});
                    } else {
                        $.growl.notice({message: result.message});
//                        setTimeout(function () {
//                            window.location.href = base_url + '/admin/pages/';
//                        }, 800);
                    }
                }
            });
        }
    });


//    $("#mainContent").bind('DOMNodeInserted DOMNodeRemoved',function(){
//        var page_id = window.location.pathname.split('/')[3];
//        console.log(page_id);
//    });

//    $('#mainContent').mouseup(function () {
//
//        var html = $("#mainContent .col").find(".rendered-markdown").html();
//        $("#mainContent .col").find(".rendered-markdown").replaceWith("<div class='element'>" + html + "<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton btn-pencil'><i class='fa fa-pencil'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
//        saveOrUpdate();
//    });


    $body.on('click', '#btn-prerequisite-filter', function () {
        var box_id = $(this).attr('box');
        var filters = [];
        var action = $(this).siblings('.filter-nested-rule-form-group').find('.prerequisite-status').val();
        var match = $(this).siblings('.filter-nested-rule-form-group').find('.any-or-all').val();
        $body.find('.toolBoxContent').find('.questions-list').each(function () {
            var matchfor = $(this).find('.any-or-all').val();
            var $this = $(this);
            var filter_questions = [];
            $this.find('.prerequisite-item').each(function () {
                var question_id = $(this).find('.prerequisite-question').val();
                var question_answer = $(this).find('.prerequisite-option').val();
                if (question_id != "" && question_id != null && question_answer != "" && question_answer != null) {
                    var pre_req = {
                        'pre_question_id': question_id,
                        'pre_answers': question_answer
                    }
                    filter_questions.push(pre_req);
                }
            });
            if (filter_questions.length > 0) {
                var match_filter = {
                    'matchfor': matchfor,
                    'filter_questions': filter_questions
                }
                filters.push(match_filter);
            }
        });

        //var req_filter = {
        //    'matchfor': match,
        //    'action': action,
        //    'filters': filter_match
        //}
        //filters.push(req_filter);
        //console.log(filters);

        //$body.find('#prerequisite-popup').find('.prerequisite-item').each(
        //    function () {
        //        var action = $(this).find('.prerequisite-status').val();
        //        var question_id = $(this).find('.prerequisite-question').val();
        //        var question_answer = $(this).find('.prerequisite-option').val();
        //        if (action != "" && question_id != "" && question_answer != "") {
        //            var pre_req = {
        //                'action': action,
        //                'pre_question_id': question_id,
        //                'pre_answers': question_answer
        //            }
        //            filters.push(pre_req);
        //        }
        //    }
        //);
        var added = false;
        if (filters.length > 0) {
            $.map(filter_list, function (elementOfArray, indexInArray) {
                if (elementOfArray.box_id == box_id) {
                    elementOfArray.filters = filters;
                    elementOfArray.matchfor = match;
                    elementOfArray.action = action;
                    added = true;
                }
            });
            if (!added) {
                filter_list.push({
                    'box_id': box_id,
                    'matchfor': match,
                    'action': action,
                    'filters': filters
                });
            }
        }
        saveOrUpdate();
    });

    // Add custom classes ---- Start

    $body.find('.add-cms-custom-class').select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/pages/get-custom-classes/',
            dataType: "json",
            type: "POST",
            data: function (term, page) {
                return {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    q: term
                };
            },
            results: function (data, page) {
                lastResults = data.results;
                return data;
            }
        },
        //Allow manually entered text in drop down.
        createSearchChoice: function (term, data) {
            term = $.trim(term);
            if ($(data).filter(function () {
                    return this.text.localeCompare(term) === 0;
                }).length === 0 && term !='') {
                term = term.replace(/\s+/g, '-');
                return {id: term, text: term};
            }
        }
    });

    $body.on('click', '#add-custom-class', function () {
        var box_classes = $(this).closest('#custom-class').find('.add-cms-custom-class').select2('val');
        var page_id = window.location.pathname.split('/')[3];
        var box_id = $(this).closest('.toolBoxContent').attr('data-box-id');
        var data = {
            page_id: page_id,
            box_id: box_id,
            box_classes: JSON.stringify(box_classes),
            csrfmiddlewaretoken: csrf_token
        };
        var $this = $(this);
        $.ajax({
            url: base_url + '/admin/pages/set-custom-classes/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.message});
                } else {
                    $.growl.notice({message: result.message});
                    $this.closest('.left-menu').removeClass('visible');
                }
            }
        });
    });

    // Add custom classes ---- End

    var $imageContainer = $('#uploaded-image-container');

    $(document).on('click', '.edit #btn-show-images, #image-pop-up .floatingToolBoxClose', function () {
        $(".module-content2").css("background-color", $("#mainContent").css("background-color"));
        $('.tools').find('li:not(#btn-show-images)').removeClass("active");
        $("#btn-show-images").toggleClass("active");
        $('.left-menu:not(#image-pop-up)').removeClass('visible');
        $("#image-pop-up").toggleClass("visible");
        if ($("#btn-show-images").hasClass('active')) {
            retrieveImages();
        }
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
                '<span class="show-hide-flag" style="display: none;"><input type="text" value="' + images[i].url + '" style="width: 90%; float: left;">' +
                '<i class="fa fa-times cross-img-id" aria-hidden="true" style="margin-top:10px;margin-left:5px;"></i></span>' +
                '<button class="btn-copy-url" data-clipboard-text="' + images[i].url + '">Copy URL</button>' +
                '</div>';
        }
        $imageContainer.html(imageHtml);
        new Clipboard('.btn-copy-url');
    }

    var msg_editor;

    $body.on('click', '.msg-edit', function () {
        var message_content = toMarkdown($(this).prev('.msg-settings').html());
        $(this).prev('.msg-settings').html($('#elements-setting-message').html())
        $(this).css('display', 'none');
        msg_editor = CodeMirror.fromTextArea(document.getElementById('elements-setting-msg'), {
            mode: 'gfm',
            lineNumbers: false,
            matchBrackets: true,
            lineWrapping: false,
            theme: 'base16-light',
            extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"}
        });
        msg_editor.on('change', msgupdate);
        //var code_content = $.trim($('#elements-setting-msg').val());

        if (message_content != '') {
            msg_editor.setValue(message_content);
        }


    });
    $body.on('click', '#msg-save', function () {
        $(this).closest('.msg-settings').next('.msg-edit').css('display', 'inline-block');
        $(this).closest('.msg-settings').html($(this).next('#out_msg').html());
    });

    var hashtomsg;

    function msgupdate(e) {
        if (e != undefined) {
            setOutputmsg(e.getValue());
        }

        clearTimeout(hashto);
        hashtomsg = setTimeout(updateHashmsg, 1000);
    }

    function setOutputmsg(val) {
        val = val.replace(/<equation>((.*?\n)*?.*?)<\/equation>/ig, function (a, b) {
            return '<img src="http://latex.codecogs.com/png.latex?' + encodeURIComponent(b) + '" />';
        });

        var out = document.getElementById('out_msg');
        var old = out.cloneNode(true);
        out.innerHTML = md.render(val);
        emojify.run(out);

        var allold = old.getElementsByTagName("*");
        if (allold === undefined) return;

        var allnew = out.getElementsByTagName("*");
        if (allnew === undefined) return;

        for (var i = 0, max = Math.min(allold.length, allnew.length); i < max; i++) {
            if (!allold[i].isEqualNode(allnew[i])) {
                out.scrollTop = allnew[i].offsetTop;
                return;
            }
        }
    }

    function updateHashmsg() {
    }

    if (window.location.hash) {
        var h = window.location.hash.replace(/^#/, '');
        if (h.slice(0, 5) == 'view:') {
            setOutputmsg(decodeURIComponent(escape(RawDeflate.inflate(atob(h.slice(5))))));
            document.body.className = 'view';
        } else {
            editor.setValue(
                decodeURIComponent(escape(
                    RawDeflate.inflate(
                        atob(
                            h
                        )
                    )
                ))
            );
            msgupdate(msg_editor);
            if (msg_editor) {
                msg_editor.focus();
            }
        }
    } else {
        msgupdate(msg_editor);
        if (msg_editor) {
            msg_editor.focus();
        }
    }

    $body.on('click', '.save-element-settings', function () {
        var page_id = window.location.pathname.split('/')[3];
        var box_id = $(this).prev('.toolBoxContent').find('fieldset').attr('data-box-id');
        var element_settings = []
        var $this = $(this);
        $this.prev('.toolBoxContent').find('.settings-given-answer').each(function () {
            var tag_type = $(this).prop('tagName');
            if (tag_type == 'SELECT') {
                var setting_id = $(this).attr('data-setting-id');
                var setting_answer = $(this).val();
                if ($.trim(setting_answer) != '' || $.trim(setting_answer) != null || $.trim(setting_answer) != undefined) {
                    var setting_data = {
                        'setting_id': setting_id,
                        'setting_answer': setting_answer,
                        'type': 'setting'
                    }
                    element_settings.push(setting_data);
                }
            } else {
                var setting_type = $(this).attr('type');
                if (setting_type == 'checkbox') {
                    var setting_id = $(this).attr('data-setting-id');
                    var setting_answer = $(this).prop('checked');
                    if ($.trim(setting_answer) != '' || $.trim(setting_answer) != null || $.trim(setting_answer) != undefined) {
                        var setting_data = {
                            'setting_id': setting_id,
                            'setting_answer': setting_answer,
                            'type': 'setting'
                        }
                        element_settings.push(setting_data);
                    }
                } else {
                    var setting_id = $(this).attr('data-setting-id');
                    var setting_answer = $(this).val();
                    if ($.trim(setting_answer) != '' || $.trim(setting_answer) != null || $.trim(setting_answer) != undefined) {
                        var setting_data = {
                            'setting_id': setting_id,
                            'setting_answer': setting_answer,
                            'type': 'setting'
                        }
                        element_settings.push(setting_data);
                    }
                }
            }
        });
        var message_setting_id = $this.prev('.toolBoxContent').find('.msg-settings').attr('data-setting-id');
        var message_setting_answer = $this.prev('.toolBoxContent').find('.msg-settings').html();
        if ($.trim(message_setting_answer) != null || $.trim(message_setting_answer) != undefined) {
            var message_setting_data = {
                'setting_id': message_setting_id,
                'setting_answer': message_setting_answer,
                'type': 'message'
            }
            element_settings.push(message_setting_data);
        }
        var groups = []
        $this.prev('.toolBoxContent').find('.settings-given-groups').find('input').each(function () {
            var group_id = $(this).attr('data-group-id');
            if ($(this).prop('checked')) {
                groups.push(group_id);
            }
        });

        if (groups.length > 0) {
            var group_setting_id = $this.prev('.toolBoxContent').find('.settings-given-groups').attr('data-setting-id');
            var group_setting_answer = JSON.stringify(groups);
            var setting_group_data = {
                'setting_id': group_setting_id,
                'setting_answer': group_setting_answer,
                'type': 'setting'
            }
            element_settings.push(setting_group_data);
        }

        var data = {
            page_id: page_id,
            box_id: box_id,
            element_settings: JSON.stringify(element_settings),
            csrfmiddlewaretoken: csrf_token
        }



        $.ajax({
            url: base_url + '/admin/pages/set-element-settings/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.message});
                } else {
                    $.growl.notice({message: result.message});
                    $this.closest('.floatingToolBox').removeClass('visible');
                }
            }
        });


    });

    // copy image in iOS and Safari

    $body.on('click', '.btn-copy-url', function () {

        if (!(Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0)) {
            $(".show-hide-flag").hide();
            $(this).prev('span').show();
            $(this).prev('span').children('input').focus(function () {
                $(this).select();
            });
            $(this).prev('span').children('input').mouseup(function (e) {
                e.preventDefault();
            });
            $(".cross-img-id").click(function () {
                $(".show-hide-flag").hide();
            });
        }
    });


});

function saveOrUpdate() {
    var element_filters = [];
    $('body').find('.module-element:visible').each(
        function () {
            var box_id = $(this).attr('id');
            var element_id = $(this).attr('data-id');
            if (box_id != "" && element_id != "") {
                var element = {
                    'box_id': box_id,
                    'element_id': element_id
                };
                element_filters.push(element);
            }
        }
    );
    var base_url = window.location.origin;
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var hiddenDiv = $('#hidden-content');
    var page_id = window.location.pathname.split('/')[3];
    hiddenDiv.html($("#mainContent").html());
    hiddenDiv.find('.toolBox').remove();
    hiddenDiv.find('.element').removeClass('.element');
    hiddenDiv.find('.formQuestion').each(function () {
        $(this).html("{qid:" + $(this).attr('data-id') + "}");
    });
    hiddenDiv.find('.module-element').each(function () {
        var element_name = $(this).attr('data-name') + '-' + $(this).attr('id').split('-')[1];
        $(this).html("{element:" + element_name + "}");
    });
    var allHtml = hiddenDiv.html().replace(/ui-sortable/g, '').replace(/(\r\n|\n|\r|\t)/gm, "").replace(/\s+/g, " ");
    $.ajax({
        url: base_url + '/admin/pages/',
        type: "POST",
        data: {
            content: JSON.stringify({
                content: allHtml
            }),
            id: page_id,
            filter_list: JSON.stringify(filter_list),
            element_filters: JSON.stringify(element_filters),
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.error) {
                $.growl.error({message: result.message});
            } else {
                //if(result.page.filter != ''){
                //filter_list = jQuery.parseJSON(result.page.filter);
                //}

//                    $.growl.notice({ message: result.message });
//                    setTimeout(function () {
//                        window.location.href = base_url + '/admin/pages/';
//                    }, 800);
            }
        }
    });


}
