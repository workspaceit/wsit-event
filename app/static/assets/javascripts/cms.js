jQuery(document).ready(function ($) {

        var base_url = window.location.origin;
        var $prereqPopup = $('#prerequisite-popup');
        var $popupContainer = $prereqPopup.find('div.outer');
        var $hiddenQuestionItem = $('#hidden_question_item');
        var dropdown_questions = [];

        $("#files").kendoUpload({
            async: {
                saveUrl: base_url + '/admin/upload-page-image/',
                //                removeUrl: "remove",
                autoUpload: true
            },
            upload: function (e) {
                e.data = {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()}
            },
            success: function (e) {
                if (e.response.success) {
                    $.growl.notice({message: e.response.msg});
                } else {
                    $.growl.error({message: e.response.msg});
                }


            }
        });

        var is_update = $('#hidden-content').attr('data-content');
        if (is_update == "update") {
            $('#hidden-content .row').find('.col').each(function () {
                var $this = $(this);
                //$this.children().each(function () {
                $this.find('.box').each(function () {
                    $(this).addClass('element');
                    var $html = $(this);
                    var html = $(this).html();
                    if ($(this).hasClass('formQuestion')) {
                        $html.append("<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                        //$html.html(html+"<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                    } else if ($(this).hasClass('module-element')) {
                        $html.append("<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton btn-element-setting'><i class='fa fa-tasks'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                        //$html.html(html+"<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                    } else if ($(this).hasClass('general-element')) {
                        $html.append("<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                        //$html.html(html+"<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                    } else {
                        $html.append("<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton btn-pencil'><i class='fa fa-pencil'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div>");
                    }
                });
            });

            $("#mainContent").html($('#hidden-content').html());
            $("#mainContent > .row").append('<div class="toolBox" style="display: none;"><div class="toolButton delete"><i class="fa fa-trash"></i></div><div class="toolButton filter"><i class="fa fa-gear"></i></div><div class="toolButton customClass"><i class="fa fa-css3"></i></div><div class="toolButton handle"><i class="fa fa-arrows"></i></div></div>');
            $("#mainContent > .row .row").append("<div class='toolBox' style='display: none;'><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton delete'><i class='fa fa-trash'></i></div></div>");
            var question_ids = [];
            var $questions = $('.formQuestion:visible');
            $questions.each(function () {
                if (($(this).attr('type') === 'select') || ($(this).attr('type') === 'checkbox') || ($(this).attr('type') === 'radio_button')) {
                    question_ids.push($(this).data('id'));
                }
            });

            $.ajax({
                url: base_url + '/admin/questions/all-options/',
                type: "POST",
                data: {
                    question_ids: JSON.stringify(question_ids),
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.message});
                    } else {
                        var all_questions = result.all_question_list;
                        for (var i = 0; i < all_questions.length; i++) {
                            dropdown_questions.push({
                                'question': all_questions[i].question,
                                'options': all_questions[i].options
                            });
                        }
                    }
                }
            });
        }


        var idCount = 0;
        var box_count = [];
        $('.box').each(function () {
            box_count.push($(this).attr('id').split('-')[1]);
        });
        if (box_count.length > 0) {
            idCount = Math.max.apply(Math, box_count);
        }

        $('body').addClass('edit');
        $('.toggle-menu').jPushMenu();

        $(".toolBox").hide();

        $('.floatingToolBox').draggable({
            handle: ".floatingToolBoxTitleRow",
            containment: "body",
            snap: ".floatingToolBox"
        }).disableSelection();

        $(document).on('mousedown', '.floatingToolBox', function () {
            $(".floatingToolBox").css("z-index", "999")
            $(this).css("z-index", "1000")
        });

        $("#ui-accordion").accordion({
            animate: 100,
            collapsible: true,
            heightStyle: "content",
            header: "> div > h3",
            beforeActivate: function (event, ui) {
                // The accordion believes a panel is being opened
                if (ui.newHeader[0]) {
                    var currHeader = ui.newHeader;
                    var currContent = currHeader.next('.ui-accordion-content');
                    // The accordion believes a panel is being closed
                } else {
                    var currHeader = ui.oldHeader;
                    var currContent = currHeader.next('.ui-accordion-content');
                }
                // Since we've changed the default behavior, this detects the actual status
                var isPanelSelected = currHeader.attr('aria-selected') == 'true';

                // Toggle the panel's header
                currHeader.toggleClass('ui-corner-all', isPanelSelected).toggleClass('accordion-header-active ui-state-active ui-corner-top', !isPanelSelected).attr('aria-selected', ((!isPanelSelected).toString()));

                // Toggle the panel's icon
                currHeader.children('.ui-icon').toggleClass('ui-icon-triangle-1-e', isPanelSelected).toggleClass('ui-icon-triangle-1-s', !isPanelSelected);

                // Toggle the panel's content
                currContent.toggleClass('accordion-content-active', !isPanelSelected)
                if (isPanelSelected) {
                    currContent.slideUp();
                } else {
                    currContent.slideDown();
                }

                return false; // Cancels the default action
            }
        });

        function sortCol() {
            $("#mainContent .col").sortable({
                handle: ".handle",
                connectWith: ".col",
                placeholder: "ui-state-highlight",
                cursor: "move",
                helper: 'clone',
                opacity: '.5',
                revert: "invalid",
                receive: function (event, ui) {
                    var $this = $(this);
                    var question_html = $(this).find(".question-markdown").html();
                    var module_html = $(this).find(".module-markdown").html();
                    var general_html = $(this).find(".general-markdown").html();
                    if (question_html != "" && question_html != undefined) {
                        var question_id = $(this).find(".question-markdown").attr('data-id');

                        var $this = $(this);
                        $.ajax({
                            url: base_url + '/admin/questions/option/',
                            type: "POST",
                            data: {
                                question_id: question_id,
                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                            },
                            success: function (result) {
                                var options = result.options;
                                var question = result.question;
                                if (question.type == 'select' || question.type == 'radio_button' || question.type == 'checkbox') {
                                    dropdown_questions.push({
                                        'question': question,
                                        'options': options
                                    });
                                }
                                var required = 0;
                                if (result.question.required == true) {
                                    required = 1;
                                }
                                var definition = result.question.actual_definition;
                                var pre_req_questions = result.pre_req_questions;
                                var pre_req_list = [];
                                for (var p = 0; p < pre_req_questions.length; p++) {
                                    var pre_req = {
                                        pre_ques: pre_req_questions[p].pre_req_question.id,
                                        pre_ans: pre_req_questions[p].pre_req_answer.option,
                                        pre_action: pre_req_questions[p].action
                                    };
                                    pre_req_list.push(pre_req);
                                }

                                var slug_title = slug(question.title);
                                var description = '';
                                if (question.description != '') {
                                    description = '<span class="questionDescription">' + question.description + '</span>';
                                }

                                if (question.type == 'select') {
                                    var option = '<option value="">- Select -</option>';
                                    for (var i = 0; i < options.length; i++) {
                                        option += '<option value="' + options[i].option + '">' + options[i].option + '</option>';
                                    }
                                    var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                        '<div class="validationBorder">' +
                                        '<select id="attendee-question-' + question.id + '" class="given-answer">' +
                                        '' + option + '' +
                                        '</select>' +
                                        '</div>';
                                } else if (question.type == 'radio_button') {
                                    var option = '';
                                    for (var i = 0; i < options.length; i++) {
                                        var counter = i + 1;
                                        option += '<input type="radio" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '" class="given-answer"><label for="attendee-question-' + question.id + '-' + counter + '">' + options[i].option + '</label>';
                                    }
                                    var content = '<label class="fontLarge">' + question.title + description + '</label><br/>' +
                                        '' + option + '';

                                } else if (question.type == 'text') {
                                    var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                        '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                                } else if (question.type == 'checkbox') {
                                    var option = '';
                                    for (var i = 0; i < options.length; i++) {
                                        var counter = i + 1;
                                        option += '<input class="given-answer" type="checkbox" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '"><label for="attendee-question-' + question.id + '-' + counter + '">' + options[i].option + '</label>';
                                    }
                                    var content = '<label for="attendee-' + slug_title + '">' + question.title + description + '</label><br/>' +
                                        '' + option + '';
                                } else if (question.type == 'textarea') {
                                    var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                        '<textarea id="attendee-question-' + question.id + '" class="given-answer"></textarea>';
                                } else {
                                    var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                        '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                                }
                                var element = '' + content + '' +
                                    '<div class="error-validating noMargin">Please select your ' + question.title + '</div>' +
                                    '<div class="toolBox">' +
                                    '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                    '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                    '<div class"toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                    '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                    '</div>';
                                //$this.find(".question-markdown").replaceWith("<div class='element formQuestion " + question.question_class + "' data-id='" + question.id + "' data-pre-req='" + JSON.stringify(pre_req_list) + "'>" + element + "</div>");
                                idCount++;
                                $this.find(".question-markdown").replaceWith("<div class='element formQuestion box " + question.question_class + "' data-id='" + question.id + "' data-req='" + required + "' data-def='" + definition + "' id='box-" + idCount + "' type='" + question.type + "'>" + element + "</div>");
                                saveOrUpdate();
                                dissableQuestionDraggable();
                            }
                        });
                        //$(this).find(".question-markdown").replaceWith("<div class='element'>" + question_html + "<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton btn-pencil'><i class='fa fa-pencil'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
                    } else if (module_html != "" && module_html != undefined) {
                        var module_id = $(this).find(".module-markdown").attr('data-id');
                        //var module_content = $(this).find(".module-markdown").html().replace(/\_/g, ' ');
                        var module_content = $(this).find(".module-markdown").html().replace(/ /g, "-");
                        ;
                        idCount++;
                        var module_html = $('#elements-' + module_content.toLowerCase()).html();
                        $(this).find(".module-markdown").replaceWith("<div class='element module-element box' id='box-" + idCount + "' data-id='" + module_id + "' data-name='" + module_content.toLowerCase() + "'><b>" + module_html + "</b><div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton btn-element-setting'><i class='fa fa-tasks'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
                        saveOrUpdate();
                        //dissableElementDraggable();
                    } else if (general_html != "" && general_html != undefined) {
                        var html = $(this).find(".general-markdown").attr('data-id');
                        var general_content = html.replace(/ /g, "_").toLowerCase();
                        idCount++;
                        $(this).find(".general-markdown").replaceWith("<div class='element general-element box' id='box-" + idCount + "'>{" + general_content + "}<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
                        saveOrUpdate();
                    } else {
                        var html = $(this).find(".rendered-markdown").html();
                        //var session_table = html.match(/\{"sessions":(.|\s)*]}/g);
                        var session_table = html.match(/\{"sessions":(.)*]}/g);
                        if (session_table != null) {
                            for (var s = 0; s < session_table.length; s++) {
                                var session_element = '' + session_table[s] + '' +
                                    '<div class="toolBox">' +
                                    '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                    '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                    '<div class="toolButton btn-pencil"><i class="fa fa-pencil"></i></div>' +
                                    '<div class="toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                    '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                    '</div>';
                                idCount++;
                                html = html.replace(session_table[s], "<div class='regex-table box element' id='box-" + idCount + "'>" + session_element + "</div>");
                            }
                        }
                        var travel_table = html.match(/\{"travels":(.)*]}/g);
                        if (travel_table != null) {
                            for (var t = 0; t < travel_table.length; t++) {
                                var travel_element = '' + travel_table[t] + '' +
                                    '<div class="toolBox">' +
                                    '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                    '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                    '<div class="toolButton btn-pencil"><i class="fa fa-pencil"></i></div>' +
                                    '<div class="toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                    '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                    '</div>';
                                idCount++;
                                html = html.replace(travel_table[t], "<div class='regex-table box element' id='box-" + idCount + "'>" + travel_element + "</div>");
                            }
                        }
                        var hotel_table = html.match(/\{"hotels":(.)*]}/g);
                        if (hotel_table != null) {
                            for (var h = 0; h < hotel_table.length; h++) {
                                var hotel_element = '' + hotel_table[h] + '' +
                                    '<div class="toolBox">' +
                                    '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                    '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                    '<div class="toolButton btn-pencil"><i class="fa fa-pencil"></i></div>' +
                                    '<div class="toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                    '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                    '</div>';
                                idCount++;
                                html = html.replace(hotel_table[h], "<div class='regex-table box element' id='box-" + idCount + "'>" + hotel_element + "</div>");
                            }
                        }
                        var question_table = html.match(/\{"questions":(.)*]}/g);
                        if (question_table != null) {
                            for (var q = 0; q < question_table.length; q++) {
                                var question_element = '' + question_table[q] + '' +
                                    '<div class="toolBox">' +
                                    '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                    '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                    '<div class="toolButton btn-pencil"><i class="fa fa-pencil"></i></div>' +
                                    '<div class="toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                    '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                    '</div>';
                                idCount++;
                                html = html.replace(question_table[q], "<div class='regex-table box element' id='box-" + idCount + "'>" + question_element + "</div>");
                            }
                        }
                        var res = html.match(/\{qid:(.*?)}/g);
                        var question_array = [];
                        if (res != null) {
                            for (var i = 0; i < res.length; i++) {
                                var tag_question_id = res[i].split("{qid:")[1].split("}")
                                if ($.inArray(tag_question_id[0], question_array) == -1) {
                                    question_array.push(tag_question_id[0]);
                                }
                            }
                        }
                        if (question_array.length > 0) {
                            $.ajax({
                                url: base_url + '/admin/questions/all-options/',
                                type: "POST",
                                data: {
                                    question_ids: JSON.stringify(question_array),
                                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                                },
                                success: function (result) {
                                    var all_questions = result.all_question_list;
                                    for (var j = 0; j < all_questions.length; j++) {
                                        var options = all_questions[j].options;
                                        var question = all_questions[j].question;
                                        if (question.type == 'select' || question.type == 'radio_button' || question.type == 'checkbox') {
                                            dropdown_questions.push({
                                                'question': question,
                                                'options': options
                                            });
                                        }
                                        var required = 0;
                                        if (question.required == true) {
                                            required = 1;
                                        }
                                        var definition = all_questions[j].question.actual_definition;
                                        var pre_req_questions = all_questions[j].pre_req_questions;
                                        var pre_req_list = [];
                                        for (var p = 0; p < pre_req_questions.length; p++) {
                                            var pre_req = {
                                                pre_ques: pre_req_questions[p].pre_req_question.id,
                                                pre_ans: pre_req_questions[p].pre_req_answer.option,
                                                pre_action: pre_req_questions[p].action
                                            };
                                            pre_req_list.push(pre_req);
                                        }

                                        var slug_title = slug(question.title);
                                        var description = '';
                                        if (question.description != '') {
                                            description = '<span class="questionDescription">' + question.description + '</span>';
                                        }

                                        if (question.type == 'select') {
                                            var option = '<option value="">- Select -</option>';
                                            for (var i = 0; i < options.length; i++) {
                                                option += '<option value="' + options[i].option + '">' + options[i].option + '</option>';
                                            }
                                            var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                                '<div class="validationBorder">' +
                                                '<select id="attendee-question-' + question.id + '" class="given-answer">' +
                                                '' + option + '' +
                                                '</select>' +
                                                '</div>';
                                        } else if (question.type == 'radio_button') {
                                            var option = '';
                                            for (var i = 0; i < options.length; i++) {
                                                var counter = i + 1;
                                                option += '<input type="radio" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '" class="given-answer"><label for="attendee-question-' + question.id + '-' + counter + '">' + options[i].option + '</label>';
                                            }
                                            var content = '<label class="fontLarge">' + question.title + description + '</label><br/>' +
                                                '' + option + '';

                                        } else if (question.type == 'text') {
                                            var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                                '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                                        } else if (question.type == 'checkbox') {
                                            var option = '';
                                            for (var i = 0; i < options.length; i++) {
                                                var counter = i + 1;
                                                option += '<input class="given-answer" type="checkbox" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '"><label for="attendee-question-' + question.id + '-' + counter + '">' + options[i].option + '</label>';
                                            }
                                            var content = '<label for="attendee-' + slug_title + '">' + question.title + description + '</label><br/>' +
                                                '' + option + '';
                                        } else if (question.type == 'textarea') {
                                            var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                                '<textarea id="attendee-question-' + question.id + '" class="given-answer"></textarea>';
                                        } else {
                                            var content = '<label for="attendee-question-' + question.id + '">' + question.title + description + '</label>' +
                                                '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                                        }
                                        var element = '' + content + '' +
                                            '<div class="error-validating noMargin">Please select your ' + question.title + '</div>' +
                                            '<div class="toolBox">' +
                                            '<div class="toolButton delete"><i class="fa fa-trash"></i></div>' +
                                            '<div class="toolButton filter"><i class="fa fa-gear"></i></div>' +
                                            '<div class="toolButton customClass"><i class="fa fa-css3"></i></div>' +
                                            '<div class="toolButton handle"><i class="fa fa-arrows"></i></div>' +
                                            '</div>';
                                        idCount++;
                                        var qid = '{qid:' + question.id + '}';
                                        var re = new RegExp(qid, 'g');
                                        html = html.replace(re, "<div class='element formQuestion box " + question.question_class + "' data-id='" + question.id + "' data-req='" + required + "' data-def='" + definition + "' id='box-" + idCount + "' type='" + question.type + "'>" + element + "</div>");
                                    }
                                    idCount++;
                                    $this.find(".rendered-markdown").replaceWith("<div class='element box' id='box-" + idCount + "'>" + html + "<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton btn-pencil'><i class='fa fa-pencil'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
                                    saveOrUpdate();
                                }
                            });
                        } else {
                            idCount++;
                            $(this).find(".rendered-markdown").replaceWith("<div class='element box' id='box-" + idCount + "'>" + html + "<div class='toolBox' style='display: none;'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton btn-pencil'><i class='fa fa-pencil'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle ui-sortable-handle'><i class='fa fa-arrows'></i></div></div></div>");
                            saveOrUpdate();
                        }
                        $(this).find(".element").find('.row').each(function () {
                            $(this).append("<div class='toolBox' style='display: none;'><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton delete'><i class='fa fa-trash'></i></div></div>");
                        });

                    }
                },
                stop: function (event, ui) {
                    saveOrUpdate();
                }
            });
            $(".row").disableSelection();
        }

        var slug = function (str) {
            var $slug = '';
            var trimmed = $.trim(str);
            $slug = trimmed.replace(/[^a-z0-9-]/gi, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
            return $slug.toLowerCase();
        }

        function sortRow() {
            $("#mainContent").sortable({
                handle: ".handle",
                placeholder: "ui-state-highlight",
                cursor: "move",
                helper: 'clone',
                opacity: '.5',
                stop: function (event, ui) {
                    saveOrUpdate();
                }
            });
            $(".row").disableSelection();
        };

        $(".rendered-markdown").draggable({
            connectToSortable: "#mainContent .col",
            helper: "clone",
            revert: "invalid"
        });

        $(".question-markdown").draggable({
            connectToSortable: "#mainContent .col",
            helper: "clone",
            revert: "invalid"

        });

        $(".module-markdown").draggable({
            connectToSortable: "#mainContent .col",
            helper: "clone",
            revert: "invalid"

        });

        $(".general-markdown").draggable({
            connectToSortable: "#mainContent .col",
            helper: "clone",
            revert: "invalid"

        });

        function dissableQuestionDraggable() {
            $('body').find('.formQuestion:visible').each(function () {
                var $this = $(this);
                $(".question-markdown").each(function () {
                    if ($this.attr('data-id') == $(this).attr('data-id')) {
                        $(this).draggable('disable');
                    }
                });
            });
        }

        function dissableElementDraggable() {
            $('body').find('.module-content:visible').each(function () {
                var $this = $(this);
                $(".module-markdown").each(function () {
                    if ($this.attr('data-id') == $(this).attr('data-id')) {
                        $(this).draggable('disable');
                    }
                });
            });
        }

        dissableQuestionDraggable();
        dissableElementDraggable();

        sortCol();
        sortRow();

        $("body")
            .on("mouseenter", (".row > .col > .element > .formQuestion"), function () {
                if ($("body").hasClass("edit")) {
                    $(".toolBox").hide();
                    $(this).closest(".row").find(".toolBox").hide();
                    $(this).children('.toolBox').show();
                }
            })
            .on("mouseleave", (".row > .col > .element > .formQuestion"), function () {
                if ($("body").hasClass("edit")) {
                    $(this).closest(".row").find(".toolBox").show();
                    $(this).closest(".row").find(".element > .toolBox").hide();
                }
            });
        $("body")
            .on("mouseenter", (".row > .col > .element > .regex-table"), function () {
                if ($("body").hasClass("edit")) {
                    $(".toolBox").hide();
                    $(this).closest(".row").find(".toolBox").hide();
                    $(this).children('.toolBox').show();
                }
            })
            .on("mouseleave", (".row > .col > .element > .regex-table"), function () {
                if ($("body").hasClass("edit")) {
                    $(this).closest(".row").find(".toolBox").show();
                    $(this).closest(".row").find(".element > .toolBox").hide();
                }
            });

        $("body")
            .on("mouseenter", (".row > .col > .element"), function () {
                if ($("body").hasClass("edit")) {
                    $(".toolBox").hide();
                    $(this).closest(".row").find(".toolBox").hide();
                    $(this).children('.toolBox').show();
                }
            })
            .on("mouseleave", (".row > .col > .element"), function () {
                if ($("body").hasClass("edit")) {
                    $(this).closest(".row").find(".toolBox").show();
                    $(this).closest(".row").find(".element > .toolBox").hide();
                }
            });

        $("body")
            .on("mouseenter", (".row"), function () {
                if ($("body").hasClass("edit")) {
                    $(this).children('.toolBox').show();
                }
            })
            .on("mouseleave", (".row"), function () {
                if ($("body").hasClass("edit")) {
                    $(".toolBox").hide();
                }
            });
        /*        $("body")
         .on("mouseenter", (".row > .col"), function () {
         if ($("body").hasClass("edit")) {
         $(this).children('.toolBox').show();
         }
         })
         .on("mouseleave", (".row > .col"), function () {
         if ($("body").hasClass("edit")) {
         $(".toolBox").hide();
         }
         });*/


        //

        $(document).on('click', '.row > .toolBox > .delete', function () {
            if (confirm("Are you sure you want to delete this row and all of it's content?")) {
                $(this).closest(".row").remove();
                $(".question-markdown").each(function () {
                    $(this).draggable('enable');
                });
                $(".module-markdown").each(function () {
                    $(this).draggable('enable');
                });
                saveOrUpdate();
            }

        });
        /*        $(document).on('click', '.col > .toolBox > .delete', function () {
         if (confirm("Are you sure you want to delete this row and all of it's content?")) {
         $(this).closest(".col").remove();
         saveOrUpdate();
         }

         });*/

        $(document).on('click', '.element > .toolBox > .delete', function () {
            if (confirm("Are you sure you want to delete this element? This action can not be undone.")) {
                var id = $(this).closest(".element").attr('data-id');
                if ($(this).closest(".element").hasClass('formQuestion')) {
                    $(".question-markdown").each(function () {
                        if (id == $(this).attr('data-id')) {
                            $(this).draggable('enable');
                        }
                    });
                } else if ($(this).closest(".element").hasClass('module-content')) {
                    $(".module-markdown").each(function () {
                        if (id == $(this).attr('data-id')) {
                            $(this).draggable('enable');
                        }
                    });
                }
                $(this).closest(".element").remove();
                saveOrUpdate();
            }
        });

        $(document).on('click', 'div.row > .toolBox > .filter', function () {
            var boxId = ($(this).closest('.box').attr('id'));
            $('.left-menu:not(#prerequisite-popup)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $('#prerequisite-popup').addClass("visible").find('#btn-prerequisite-filter').attr('box', boxId);
            $hiddenQuestionItem.find('.prerequisite-question').html('');
            $hiddenQuestionItem.find('.prerequisite-option').html('');
            $popupContainer.html('');
            $popupContainer.attr('data-id', '');
            var found_box = false;
            var element;
            $.map(filter_list, function (elementOfArray, indexInArray) {
                if (elementOfArray.box_id == boxId) {
                    found_box = true;
                    element = elementOfArray;
                }
            });
            addPrerequisiteFilter();
            if (found_box) {
                updatePrerequisiteFilter(element);
            } else {
                $('body').find('#prerequisite-popup').find('.outer').html($('#filter-nested-html').html());
            }
        });

        $(document).on('click', 'div.element > .toolBox > .filter', function () {
            var boxId = ($(this).closest('.box').attr('id'));
            var question_id = $(this).closest('.box').attr('data-id');
            $('.left-menu:not(#prerequisite-popup)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $('#prerequisite-popup').addClass("visible").find('#btn-prerequisite-filter').attr('box', boxId);
            $hiddenQuestionItem.find('.prerequisite-question').html('');
            $hiddenQuestionItem.find('.prerequisite-option').html('');
            $popupContainer.html('');
            $popupContainer.attr('data-id', question_id);
            var found_box = false;
            var element;
            $.map(filter_list, function (elementOfArray, indexInArray) {
                if (elementOfArray.box_id == boxId) {
                    found_box = true;
                    element = elementOfArray;

                }
            });
            addPrerequisiteFilter(question_id);
            if (found_box) {
                updatePrerequisiteFilter(element);
            } else {
                $('body').find('#prerequisite-popup').find('.outer').html($('#filter-nested-html').html());
            }

        });
        $(document).on('click', 'div.row > .toolBox > .customClass', function () {
            $('.left-menu:not(#custom-class)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $('#custom-class').addClass("visible");
            var box_id = $(this).closest('.box').attr('id').split('-')[1];
            $('#custom-class').find('.toolBoxContent').attr('data-box-id', box_id);
            getBoxClasses(box_id);
        });
        $(document).on('click', 'div.element > .toolBox > .customClass', function () {
            $('.left-menu:not(#custom-class)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $('#custom-class').addClass("visible");
            var box_id = $(this).closest('.box').attr('id').split('-')[1];
            $('#custom-class').find('.toolBoxContent').attr('data-box-id', box_id);
            getBoxClasses(box_id);
        });
        $(document).on('click', '.btn-add-pre-filter', function () {
            $(this).closest('.outer').append($hiddenQuestionItem.html());
        });

        $(document).on('click', '.btn-delete-pre-filter', function () {
            if ($(this).closest('.outer').find('.prerequisite-item').length == 1) {
                if ($('.editor').find('.questions-list').length == 1) {
                    alert('Rule set needs at least one rule to match');
                } else {
                    $(this).closest('.questions-list').remove();
                }
            } else {
                $(this).closest('.prerequisite-item').remove();
            }
        });

        $(document).on('click', 'div.row > .toolBox > .btn-element-setting', function () {
            $('.left-menu:not(#element-setting-toolbox)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $("#element-setting-toolbox").addClass("visible");
            var element_name = $(this).closest('.module-element').attr('data-name');
            var box_id = $(this).closest('.box').attr('id').split('-')[1];
            $('#element-setting-toolbox').find('.toolBoxContent').html($('#elements-' + element_name + '-setting').html());
            $('#element-setting-toolbox').find('.toolBoxContent').find('fieldset').attr('data-box-id', box_id);
            getElementSettings($('#element-setting-toolbox'), box_id);

        });

        $(document).on('click', 'div.element > .toolBox > .btn-element-setting', function () {
            $('.left-menu:not(#element-setting-toolbox)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $("#element-setting-toolbox").addClass("visible");
            var element_name = $(this).closest('.module-element').attr('data-name');
            var box_id = $(this).closest('.box').attr('id').split('-')[1];
            $('#element-setting-toolbox').find('.toolBoxContent').html($('#elements-' + element_name + '-setting').html());
            $('#element-setting-toolbox').find('.toolBoxContent').find('fieldset').attr('data-box-id', box_id);
            getElementSettings($('#element-setting-toolbox'), box_id);
        });

        function getBoxClasses(box_id){
            var page_id = window.location.pathname.split('/')[3];
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/pages/get-box-classes/',
                type: "POST",
                data: {
                    page_id: page_id,
                    box_id: box_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        var class_list = result.class_list;
                        var classList = [];
                        for (var i = 0; i < class_list.length; i++) {
                            classList.push({id: class_list[i].classname.id, text: class_list[i].classname.classname});
                        }
                        $('#custom-class').find('.add-cms-custom-class').select2('data', classList);
                    }
                }
            });
        }

        function getElementSettings(toolbox, box_id) {
            var page_id = window.location.pathname.split('/')[3];
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            //console.log($(toolbox).find('.toolBoxContent').find('fieldset').attr('data-box-id',14));
            $.ajax({
                url: base_url + '/admin/pages/get-element-settings/',
                type: "POST",
                data: {
                    page_id: page_id,
                    box_id: box_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.message});
                    } else {
                        var element_settings = result.element_settings;
                        var message_setting = result.message_setting;
                        $(toolbox).find('.msg-settings').html(message_setting);
                        for (var i = 0; i < element_settings.length; i++) {
                            $(toolbox).find('.settings-given-answer').each(function () {
                                var setting_id = $(this).attr('data-setting-id');
                                if (setting_id == element_settings[i].element_question.id) {
                                    if ($(this).attr('type') == 'checkbox') {
                                        if (element_settings[i].answer == 'True') {
                                            $(this).prop('checked', true);
                                        } else {
                                            $(this).prop('checked', false);
                                        }
                                    } else {
                                        $(this).val(element_settings[i].answer);
                                    }
                                }
                            });
                            $(toolbox).find('.settings-given-groups').each(function () {
                                var $this = $(this);
                                var setting_id = $(this).attr('data-setting-id');
                                if (setting_id == element_settings[i].element_question.id) {
                                    var groups = JSON.parse(element_settings[i].answer);
                                    for (var j = 0; j < groups.length; j++) {
                                        $this.find('input').each(function () {
                                            var group_id = $(this).attr('data-group-id');
                                            if (group_id == groups[j]) {
                                                $(this).prop('checked', true);
                                            }
                                        });
                                    }
                                }
                            });
                        }
                    }
                }
            });
        }

        function addPrerequisiteFilter(question_id) {
            for (var i = 0; i < dropdown_questions.length; i++) {
                if (question_id) {
                    if (question_id != dropdown_questions[i].question.id) {
                        var questionTitle = dropdown_questions[i].question.title;
                        $hiddenQuestionItem.find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
                    }
                } else {
                    var questionTitle = dropdown_questions[i].question.title;
                    $hiddenQuestionItem.find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
                }

            }
            if (dropdown_questions.length > 0) {
                var first_question;
                if (question_id) {
                    for (var j = 0; j < dropdown_questions.length; j++) {
                        if (question_id != dropdown_questions[j].question.id) {
                            first_question = dropdown_questions[j];
                            break;
                        }
                    }
                    if (first_question != undefined) {
                        var optionsFirstQuestion = first_question.options;
                        for (var j = 0; j < optionsFirstQuestion.length; j++) {
                            $hiddenQuestionItem.find('.prerequisite-option:last').append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
                        }
                    }
                } else {
                    first_question = dropdown_questions[0];
                    var optionsFirstQuestion = first_question.options;
                    for (var j = 0; j < optionsFirstQuestion.length; j++) {
                        $hiddenQuestionItem.find('.prerequisite-option:last').append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
                    }
                }
            }
            $('body').find('#filter-nested-html').find('.outer').html($hiddenQuestionItem.html());
        }

        function updatePrerequisiteFilter(element) {
            var $status = $('body').find('#prerequisite-popup').find('.filter-nested-rule-form-group:first');
            $status.find('.prerequisite-status').val(element.action);
            $status.find('.any-or-all').val(element.matchfor);
            for (var i = 0; i < element.filters.length; i++) {
                $('#updated-filter').html($('#filter-nested-html').html());
                var $nested_html = $('#updated-filter');
                var $outer_first = $('body').find('#prerequisite-popup').find('.outer:first');
                if (i == 0) {
                    $outer_first.html($nested_html.html());
                } else {
                    $outer_first.append($nested_html.html());
                }
                $outer_first.find('.any-or-all:last').val(element.filters[i].matchfor);
                for (var j = 0; j < element.filters[i].filter_questions.length; j++) {
                    var $qusetionItem = $nested_html.find('.questions-list:last').find('.outer')
                    if (j != 0) {
                        $('body').find('#prerequisite-popup').find('.outer:first').find('.questions-list:last').find('.outer:first').append($qusetionItem.html());
                    }
                    var $item = $('body')
                        .find('#prerequisite-popup')
                        .find('.outer:first')
                        .find('.questions-list:last')
                        .find('.outer:first')
                        .find('.prerequisite-item:last');

                    $item.find('.prerequisite-question').val(element.filters[i].filter_questions[j].pre_question_id);
                    $item.find('.prerequisite-question').change();
                    $item.find('.prerequisite-option').val('' + element.filters[i].filter_questions[j].pre_answers + '');
                }

            }

        }

//function addPrerequisiteFilter(question_id) {
//    console.log(question_id);
//    var item = $hiddenQuestionItem.html();
//    $popupContainer.append(item);
//    for (var i = 0; i < dropdown_questions.length; i++) {
//        if (question_id) {
//            if (question_id != dropdown_questions[i].question.id) {
//                var questionTitle = dropdown_questions[i].question.title;
//                console.log(questionTitle);
//                                                $popupContainer.find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
//                $('#hidden-question').find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
//            }
//        } else {
//            var questionTitle = dropdown_questions[i].question.title;
//            console.log(questionTitle);
//                                        $popupContainer.find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
//            $('#hidden-question').find('.prerequisite-question:last').append('<option value=' + dropdown_questions[i].question.id + '>' + questionTitle + '</option>');
//        }
//
//    }
//    if (dropdown_questions.length > 0) {
//        var first_question;
//        if (question_id) {
//            for (var j = 0; j < dropdown_questions.length; j++) {
//                if (question_id != dropdown_questions[j].question.id) {
//                    first_question = dropdown_questions[j];
//                    break;
//                }
//            }
//            var optionsFirstQuestion = first_question.options;
//            for (var j = 0; j < optionsFirstQuestion.length; j++) {
//                console.log(optionsFirstQuestion[j].option);
//                                                $popupContainer.find('.prerequisite-option:last')
//                                                        .append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
//                $('#hidden-question').find('.prerequisite-option:last')
//                        .append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
//            }
//        } else {
//            first_question = dropdown_questions[0];
//            var optionsFirstQuestion = first_question.options;
//            console.log(optionsFirstQuestion);
//            for (var j = 0; j < optionsFirstQuestion.length; j++) {
//                console.log(optionsFirstQuestion[j].option);
//                                                $popupContainer.find('.prerequisite-option:last')
//                                                        .append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
//                $('#hidden-question').find('.prerequisite-option:last')
//                        .append('<option value=' + optionsFirstQuestion[j].option + '>' + optionsFirstQuestion[j].option + '</option>');
//            }
//        }
//    }
//}

        $(document).on('change', '.prerequisite-question', function () {
            $(this).closest('.prerequisite-item')
                .find('.prerequisite-option')
                .html('')
            var questionId = $(this).val();
            var matchedIndex = -1;
            for (var i = 0; i < dropdown_questions.length; i++) {
                if (dropdown_questions[i].question.id == questionId) {
                    matchedIndex = i;
                }
            }
            var question = dropdown_questions[matchedIndex];
            var optionsQuestion = question.options;
            for (var j = 0; j < optionsQuestion.length; j++) {
                $(this).closest('.prerequisite-item')
                    .find('.prerequisite-option')
                    .append('<option value=' + optionsQuestion[j].option + '>' + optionsQuestion[j].option + '</option>');
            }
        });


        $(document).on('click', '.element > .toolBox > .btn-pencil', function () {
            $('form').find('.CodeMirror').remove();
            var hiddenDiv = $('#hidden-content');
            hiddenDiv.html($(this).closest('.element').html());
            hiddenDiv.find('.toolBox').remove();
            var allHtml = hiddenDiv.html();
            var new_html = toMarkdown(allHtml);
            $("#code").html(new_html);
            editor = CodeMirror.fromTextArea(document.getElementById('code'), {
                mode: 'gfm',
                lineNumbers: false,
                matchBrackets: true,
                lineWrapping: true,
                theme: 'base16-light',
                extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"}
            });

            update(editor);
            $("#code").html("");
            var data = btoa( // base64 so url-safe
                RawDeflate.deflate( // gzip
                    unescape(encodeURIComponent( // convert to utf8
                        editor.getValue()
                    ))
                )
            );
            var h = data.replace(/^#/, '');
            setOutput(decodeURIComponent(escape(RawDeflate.inflate(atob(h)))));
            $('#addContentButton').click();
            editor.on('change', update);
        });


// ADD COLUMN

// Add columns to preview

        function createCol(newColumns) {
            $.each(newColumns, function (index, value) {
                $("#currentCol").append("<div class='addCol' data-colWidth='" + value + "'>" + value + "<i class='delete fa fa-trash'></i></div>");
            });
        }

// Clicking a predefined column layout

        $(".addColPreDefined").click(function () {
            var newColumns = $(this).attr('data-cols').split("+");
            $("#currentCol").html("")
            createCol(newColumns);
        });

// Clicking the Add button

        $("#addCol").click(function () {
            currentColTotal = 0;
            $('#currentCol').children().each(function () {
                currentColTotal += parseInt($(this).attr('data-colWidth'));
            });

            currentColAdding = $("#addColValue").val();
            newColTotal = parseInt(currentColAdding) + parseInt(currentColTotal);

            if (newColTotal > 12) {
                alert("There is not enough space to add " + currentColAdding + " column(s). You have " + (12 - currentColTotal) + "/12 columns remaining in the current row.")
            }
            else {
                var newColumns = jQuery.makeArray(currentColAdding);
                createCol(newColumns);
            }
        });


// Clicking the Delete-button

        $(document).on('click', '.addCol .delete', function () {
            $(this).closest(".addCol").remove();
        });

// Clicking the Add to page-button

        $("#addColToPage").click(function () {
            currentColTotal = 0;
            $('#currentCol').children().each(function () {
                currentColTotal += parseInt($(this).attr('data-colWidth'));
            });

            if (currentColTotal > 0) {

                idCount++;

                // Adds the first (row) appending code
                if ($("#rowHasGutters").val() == "gutter") {
                    colHTML = "<div class='row gutters box' id=box-" + idCount + ">"
                } else {
                    colHTML = "<div class='row box' id=box-" + idCount + ">"
                }

                // Adds the columns to the appeding code
                $('#currentCol').children().each(function () {
                    currentColToAdd = $(this).attr('data-colWidth');
                    //colHTML = colHTML + "<div class='col span_" + currentColToAdd + "'><div class='toolBox'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton handle'><i class='fa fa-arrows'></i></div></div></div>"
                    colHTML = colHTML + "<div class='col span_" + currentColToAdd + "'></div>"
                });

                // Adds the last (row) appending code
                colHTML = colHTML + "<div class='toolBox'><div class='toolButton delete'><i class='fa fa-trash'></i></div><div class='toolButton filter'><i class='fa fa-gear'></i></div><div class='toolButton customClass'><i class='fa fa-css3'></i></div><div class='toolButton handle'><i class='fa fa-arrows'></i></div></div>"
                $("#mainContent").append(colHTML);

                // Updates the sorting on rows and columns
                sortCol();
                sortRow();
            } else {

                alert("The row has no columns. Add more columns and try again.");

            }

        });


// TOOLBOX BUTTONS


        $(document).on('click', '.edit #addColumnsButton, #addColumns .floatingToolBoxClose', function () {
            $('.tools').find('li:not(#addColumnsButton)').removeClass("active");
            $("#addColumnsButton").toggleClass("active");
            $('.left-menu:not(#addColumns)').removeClass('visible');
            $("#addColumns").toggleClass("visible");
        });

        $(document).on('click', '.edit #addContentButton, #addContent .floatingToolBoxClose', function () {
            $(".entry-preview-content").css("background-color", $("#mainContent").css("background-color"))
            $('.tools').find('li:not(#addContentButton)').removeClass("active");
            $("#addContentButton").toggleClass("active");
            $('.left-menu:not(#addContent)').removeClass('visible');
            $("#addContent").toggleClass("visible");
        });

        $(document).on('click', '.edit #addQuestionButton, #addQuestion .floatingToolBoxClose', function () {
            $(".question-content").css("background-color", $("#mainContent").css("background-color"))
            $('.tools').find('li:not(#addQuestionButton)').removeClass("active");
            $("#addQuestionButton").toggleClass("active");
            $('.left-menu:not(#addQuestion)').removeClass('visible');
            $("#addQuestion").toggleClass("visible");
        });

        $(document).on('click', '#prerequisite-popup .floatingToolBoxClose', function () {
            $('.left-menu:not(#prerequisite-popup)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $("#prerequisite-popup").toggleClass("visible");
        });

        $(document).on('click', '#element-setting-toolbox .floatingToolBoxClose', function () {
            $('.left-menu:not(#element-setting-toolbox)').removeClass('visible');
            $('.tools').find('li').removeClass("active");
            $("#element-setting-toolbox").toggleClass("visible");
        });

// moduleComponent Start
        $(document).on('click', '.edit #addModuleButton, #addModuleComponent .floatingToolBoxClose', function () {
            $(".module-content").css("background-color", $("#mainContent").css("background-color"))
            $('.tools').find('li:not(#addModuleButton)').removeClass("active");
            $("#addModuleButton").toggleClass("active");
            $('.left-menu:not(#addModuleComponent)').removeClass('visible');
            $("#addModuleComponent").toggleClass("visible");
        });

        $(document).on('click', '.edit #btn-show-upload, #upload-pop-up .floatingToolBoxClose', function () {
            $(".module-content1").css("background-color", $("#mainContent").css("background-color"));
            $('.tools').find('li:not(#btn-show-upload)').removeClass("active");
            $("#btn-show-upload").toggleClass("active");
            $('.left-menu:not(#upload-pop-up)').removeClass('visible');
            $("#upload-pop-up").toggleClass("visible");
        });


// moduleComponent End

        $(document).on('click', '#editForm', function () {
            $(".tools").toggle("");
            $("#editForm").toggleClass("active");
            $("body").toggleClass("edit");
            $("#editForm i").toggleClass("fa-2x");
            $("#editForm i").toggleClass("fa-lg");
            $('.floatingToolBox').not("#tools").each(function () {
                if ($(this).hasClass("visible")) {
                    $(this).removeClass("visible").addClass("notvisible");
                } else if ($(this).hasClass("notvisible")) {
                    $(this).removeClass("notvisible").addClass("visible");
                }
            });
        });


        $(window).on("scroll touchmove", function () {
            $('.header').toggleClass('tiny', $(document).scrollTop() > 25);
        });

        $('.btn-add-nested-rule').on('click', function () {
            $('#filter-nested-html').find('.outer').html($('#hidden-question').html())
            $(this).closest('.filter-nested-rule-form-group').siblings('.outer').append($('#filter-nested-html').html());
        })


        $(function () {
            $("#currentCol").sortable({
                placeholder: "addCol-drag",
                cursor: "move",
                opacity: '0',
                helper: "clone"
            });
            $("#currentCol").disableSelection();
        });

    }
)
;