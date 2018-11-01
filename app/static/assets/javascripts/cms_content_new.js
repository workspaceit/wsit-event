var base_url = window.location.origin;
var idCount = 0;
var inst = $('[data-remodal-id=modal]').remodal();
var cookie_expire = 0;
var cookie_counter = 0;
var cookie_expire_msg = 'You have been idle for too long and have been logged out. Click Okay to reload the page.';
$(document).ready(function () {
    var box_count = [];
    $('.box').each(function () {
        box_count.push($(this).attr('id').split('-')[1]);
    });
    if (box_count.length > 0) {
        idCount = Math.max.apply(Math, box_count);
    }
    clog(idCount)

    cookie_expire = $('#cookie-expire').val();
    cookie_counter = cookie_expire;
    var cookie_timer = setInterval(function() {
        cookie_counter -= 1;
        //clog(cookie_counter);
        if(cookie_counter <= -10) {
            alert(cookie_expire_msg);
            location.reload();
            /*$("<div></div>").html(cookie_expire_msg).dialog({
                modal: true,
                resizable: false,
                width: 'auto',
                close: function (event, ui) {
                    location.reload();
                },
                buttons: {
                    "OK" : function () {
                        location.reload();
                    }
                }
            });*/
            clearInterval(cookie_timer);
        }
    }, 1000);

    $(".event-question-country").each(function () {
        for(var i=0;i<country_list.length;i++) {
            $(this).append($('<option>', {
                value: country_list[i].id,
                text: country_list[i].text
            }));
        }
    });

    // TEMPORARY KENDO UI IMPLEMENTATIONS

    // Creates Calendar for Hotel Reservation

});

$(document).ajaxSuccess(function () {
    cookie_counter = cookie_expire;
    console.log("Triggered ajaxSuccess handler.");
});
// Session Scheduler

$(function () {
    var static_url = $('#static-url').val();
    // Add Question Start

    var dropdown_questions = [];

    var questionTreeView = $("#admin-questions-treeview").kendoTreeView({
        dataSource: JSON.parse($('#question-tree').val())
    });
    selectQuestion();
    function selectQuestion() {
        questionTreeView.each(function (i, el) {
            $(el).on("dblclick", function (event) {
                var treeview = $("#admin-questions-treeview").data("kendoTreeView");
                var question_id = treeview.dataItem(event.target).data_id;
                clog(question_id);
                if (question_id != '' && question_id != undefined) {
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
                            clog(pre_req_list);

                            var slug_title = slug(question.title);
                            if (question.description == null) {
                                question.description = ''
                            }
                            var description = '<span class="event-question-label-description">' + question.description + '</span>';

                            if (question.type == 'select') {
                                var option = '<option value="">- Select -</option>';
                                for (var i = 0; i < options.length; i++) {
                                    option += '<option value="' + options[i].option + '">' + options[i].option + '</option>';
                                }
                                var content = '<select id="attendee-question-' + question.id + '" class="given-answer event-question-select">' +
                                    '' + option + '' +
                                    '</select>';
                            } else if (question.type == 'radio_button') {
                                var option = '';
                                for (var i = 0; i < options.length; i++) {
                                    var counter = i + 1;
                                    option += '<div class="radio-wrapper"><input type="radio" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '" class="given-answer"><label class="radio-label" for="attendee-question-' + question.id + '-' + counter + '">' + options[i].option + '</label></div>';
                                }
                                var content = '<div class="event-question-radio">' + option + '</div>';

                            } else if (question.type == 'text') {
                                var content = '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                            } else if (question.type == 'checkbox') {
                                var option = '';
                                for (var i = 0; i < options.length; i++) {
                                    var counter = i + 1;
                                    option += '<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" name="attendee-question-' + question.id + '" value="' + options[i].option + '" id="attendee-question-' + question.id + '-' + counter + '"><label for="attendee-question-' + question.id + '-' + counter + '" class="checkbox-label">' + options[i].option + '</label></div>';
                                }
                                var content = '<div class="event-question-checkbox">' + option + '</div>';
                            } else if (question.type == 'textarea') {
                                var content = '<textarea id="attendee-question-' + question.id + '" class="given-answer"></textarea>';
                            } else if (question.type == 'date_range') {
                                var content = '<div style="overflow:hidden">' +
                                    '<input style="width:50%; display:inline; float:left" type="text" id="attendee-question-' + question.id + '" class="given-answer">' +
                                    '<input style="width:50%; display:inline; float:left" type="text" id="attendee-question-' + question.id + '" class="given-answer">' +
                                    '</div>';

                            } else if (question.type == 'time_range') {
                                var content = '<div style="overflow:hidden">' +
                                    '<input style="width:50%; display:inline; float:left" type="text" id="attendee-question-' + question.id + '" class="given-answer">' +
                                    '<input style="width:50%; display:inline; float:left" type="text" id="attendee-question-' + question.id + '" class="given-answer">' +
                                    '</div>';

                            } else if (question.type == 'date') {
                                var content = '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                            } else if (question.type == 'time') {
                                var content = '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                            }
                            else if (question.type == 'country') {
                                var option = '<option value="">- Select -</option>';
                                for (var i = 0; i < country_list.length; i++) {
                                    option += '<option value="' + country_list[i].id + '">' + country_list[i].text + '</option>';
                                }
                                var content = '<select id="attendee-question-' + question.id + '" class="given-answer event-question-country">' +
                                    '' + option + '' +
                                    '</select>';
                            }
                            else {
                                var content = '<input type="text" id="attendee-question-' + question.id + '" class="given-answer">';
                            }
                            var element = '<label for="attendee-question-' + question.id + '" class="event-question-label">' + question.title + description + '</label>' + content + '<div class="error-validating">Validation failed</div>' + element_question_toolbox;
                            idCount++;
                            if (question.question_class == null) {
                                question.question_class = '';
                            }
                            var question_element = "<div class='event-question element box " + question.question_class + "' data-id='" + question.id + "' data-req='" + required + "' data-def='" + definition + "' id='box-" + idCount + "' type='" + question.type + "'>" + element + "</div>";
                            if ($('#content_data').find('.temporary').length < 1) {
                                createTemporarySection();
                            }
                            $('.temporary').children('.row:last').children('.col:last').append(question_element);
                            $('html, body').animate({
                                scrollTop: $("#" + 'box-' + idCount).offset().top
                            }, 2000);
                            saveOrUpdate();
                        }
                    });
                }
            });
        });
    }

    $(".admin-question-search").on("input", function () {
        var query = this.value.toLowerCase();
        var dataSource = $("#admin-questions-treeview").data("kendoTreeView").dataSource;
        searchData(dataSource, query);
        selectQuestion();
    });

// Add Question End

// Add File Repository Start

    // var fileTreeView = $("#admin-file-repository-treeview").kendoTreeView({
    //     checkboxes: {
    //         checkChildren: true
    //     },
    //
    //     dataSource: JSON.parse($('#file-tree').html())
    // });
    //
    // selectFile();
    // function selectFile() {
    //     fileTreeView.each(function (i, el) {
    //         $(el).off("dblclick").on("dblclick", function (event) {
    //             var treeview = $("#admin-file-repository-treeview").data("kendoTreeView");
    //             var file_path = treeview.dataItem(event.target).path;
    //             var file_type = treeview.dataItem(event.target).spriteCssClass;
    //             if (file_type != 'folder' && file_type != 'rootfolder') {
    //                 file_path = file_path.replace(" ", "%20");
    //                 var $temp = $("<input>");
    //                 $("body").append($temp);
    //                 $temp.val(static_url + file_path).select();
    //                 file_path = static_url + file_path;
    //                 document.execCommand("copy");
    //                 $temp.remove();
    //                 if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
    //                     var codeview_editor = $('.CodeMirror')[0].CodeMirror;
    //                     codeview_editor.replaceSelection(file_path);
    //                 } else {
    //                     $('textarea#froala_content_editor').froalaEditor('html.insert', file_path, true);
    //                 }
    //             }
    //         });
    //     });
    //     fileTreeView.each(function (i, el) {
    //         $(el).off("click").on("click", function (event) {
    //             var treeview = $("#admin-file-repository-treeview").data("kendoTreeView");
    //             var file_path = treeview.dataItem(event.target).path;
    //             var file_type = treeview.dataItem(event.target).spriteCssClass;
    //             if (file_type == "image") {
    //                 file_path = static_url + file_path.replace(" ", "%20");
    //                 $('.show-image-file').html("<img src='" + file_path + "'/>");
    //             } else {
    //                 $('.show-image-file').html("");
    //             }
    //
    //         });
    //     });
    // }

    $(".admin-file-search").on("input", function () {
        var query = this.value.toLowerCase();
        var dataSource = $("#admin-file-repository-treeview").data("kendoTreeView").dataSource;
        searchData(dataSource, query);
        selectFile();
    });

// Add File Repository End

// Add Plugin Start

    var pluginTreeView = $("#admin-add-plugins-treeview").kendoTreeView({
        dataSource: JSON.parse($('#plugin-tree').val())
    });

    selectPlugin();
    function selectPlugin() {
        pluginTreeView.each(function (i, el) {
            $(el).off("dblclick").on("dblclick", function (event) {
                var treeview = $("#admin-add-plugins-treeview").data("kendoTreeView");
                var plugin_id = treeview.dataItem(event.target).data_id;
                var plugin_name = treeview.dataItem(event.target).text;
                if (plugin_id != '' && plugin_id != undefined) {
                    if (plugin_name == "Submit Button") {
                        $.ajax({
                            url: base_url + '/admin/pages/get-submit-button-name/',
                            type: "POST",
                            data: {
                                page_id: window.location.pathname.split('/')[3],
                                box_id: ++idCount,
                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                            },
                            success: function (result) {
                                clog(result.submit_button);

                                var plugin_content = plugin_name.replace(/ /g, "-");
                                var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                                var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "' data-submit-id='" + result.submit_button.id + "' data-submit-name='" + result.submit_button.name + "'>" + plugin_html + element_plugin_toolbox;
                                clog(plugin_element);
                                if ($('#content_data').find('.temporary').length < 1) {
                                    createTemporarySection();
                                }
                                $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                                $('html, body').animate({
                                    scrollTop: $("#" + 'box-' + idCount).offset().top
                                }, 2000);
                                saveOrUpdate();
                            }
                        });
                    } else if (plugin_name == "Photo Upload") {
                        $.ajax({
                            url: base_url + '/admin/pages/get-photo-group-name/',
                            type: "POST",
                            data: {
                                page_id: window.location.pathname.split('/')[3],
                                box_id: ++idCount,
                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                            },
                            success: function (result) {
                                clog(result.photo_group);

                                var plugin_content = plugin_name.replace(/ /g, "-");
                                var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                                var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "' data-photo-group-id='" + result.photo_group.id + "' data-photo-group-name='" + result.photo_group.name + "'>" + plugin_html + element_plugin_toolbox;
                                clog(plugin_element);
                                if ($('#content_data').find('.temporary').length < 1) {
                                    createTemporarySection();
                                }
                                $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                                $('html, body').animate({
                                    scrollTop: $("#" + 'box-' + idCount).offset().top
                                }, 2000);
                                saveOrUpdate();
                            }
                        });
                    } else if (plugin_name == 'Hotel Reservation') {
                        var plugin_content = plugin_name.replace(/ /g, "-");
                        idCount++;
                        var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                        var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "'>" + plugin_html + element_plugin_toolbox;
                        clog(plugin_element);
                        if ($('#content_data').find('.temporary').length < 1) {
                            createTemporarySection();
                        }
                        $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                        $('html, body').animate({
                            scrollTop: $("#" + 'box-' + idCount).offset().top
                        }, 2000);
                        // Creates Calendar for Hotel Reservation

                        $("#" + 'box-' + idCount).find(".hotel-reservation-calendar").kendoDatePicker();

                        var data = [
                            "Jakeem Pratt",
                            "Carter Abbott",
                            "Addison Glover",
                            "Roary Bray",
                            "Mercedes Merrill",
                            "Rooney Peterson",
                            "Zephr Mclean",
                            "September Good",
                            "Indigo Tucker",
                            "Liberty Fitzgerald",
                            "Tad Cameron",
                            "Yoko Mcleod",
                            "Alexis Madden",
                            "Gloria Guy",
                            "Simon Burton",
                            "Yael Bowen",
                            "Lunea Durham",
                            "Jane Richard",
                            "Alfonso Frost",
                            "Chava Mathews",
                            "Ryder Terry",
                            "Griffith Fuller",
                            "Chase Powers",
                            "Rae Alvarez",
                            "Farrah Parks",
                            "Sebastian Hester",
                            "Yuli Benjamin",
                            "Medge Watkins",
                            "Sybill Hays",
                            "Imogene Goodwin",
                            "Brendan Huffman",
                            "Fiona Kelley",
                            "Colorado Cochran",
                            "Burke Oneal",
                            "Daquan Padilla",
                            "Zena Sykes",
                            "Judith Oliver",
                            "Dieter Harrington",
                            "Jasper Dillon",
                            "Fatima Manning",
                            "Rana Walters",
                            "Hedda Chen",
                            "Ryan Poole",
                            "Carl Huff",
                            "Ferdinand Odonnell",
                            "Yuli Oneal",
                            "Cleo Owens",
                            "Jessamine Gallegos",
                            "Allistair English",
                            "MacKenzie Woodard",
                            "Imogene Barker",
                            "Hashim Key",
                            "Claire Jacobson",
                            "Arsenio Saunders",
                            "Lillith Vasquez",
                            "Serena Williamson",
                            "Joakim Svensson"
                        ];

                        $("#" + 'box-' + idCount).find(".hotel-room-buddy").kendoAutoComplete({
                            dataSource: data,
                            filter: "contains",
                            minLength: 3,
                            placeholder: "Select a room buddy",
                            separator: ", " // Only for rooms with more than one bed
                        });
                        saveOrUpdate();
                    } else if (plugin_name == 'Session Scheduler') {
                        var plugin_content = plugin_name.replace(/ /g, "-");
                        idCount++;
                        var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                        var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "'>" + plugin_html + element_plugin_toolbox;
                        clog(plugin_element);
                        if ($('#content_data').find('.temporary').length < 1) {
                            createTemporarySection();
                        }
                        $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                        $('html, body').animate({
                            scrollTop: $("#" + 'box-' + idCount).offset().top
                        }, 2000);
                        $("#" + 'box-' + idCount).find(".session-scheduler").kendoScheduler({
                            date: new Date("2013/6/13"),
                            startTime: new Date("2013/6/13 07:00 AM"),
                            height: 600,
                            views: [
                                {type: "day", selected: true},
                                "week",
                                "workWeek",
                                "agenda"
                            ],
                            timezone: "Etc/UTC",
                            dataSource: {
                                batch: true,
                                transport: {
                                    read: {
                                        url: "http://demos.telerik.com/kendo-ui/service/tasks",
                                        dataType: "jsonp"
                                    },
                                    update: {
                                        url: "http://demos.telerik.com/kendo-ui/service/tasks/update",
                                        dataType: "jsonp"
                                    },
                                    create: {
                                        url: "http://demos.telerik.com/kendo-ui/service/tasks/create",
                                        dataType: "jsonp"
                                    },
                                    destroy: {
                                        url: "http://demos.telerik.com/kendo-ui/service/tasks/destroy",
                                        dataType: "jsonp"
                                    },
                                    parameterMap: function (options, operation) {
                                        if (operation !== "read" && options.models) {
                                            return {models: kendo.stringify(options.models)};
                                        }
                                    }
                                },
                                schema: {
                                    model: {
                                        id: "taskId",
                                        fields: {
                                            taskId: {from: "TaskID", type: "number"},
                                            title: {
                                                from: "Title",
                                                defaultValue: "No title",
                                                validation: {required: true}
                                            },
                                            start: {type: "date", from: "Start"},
                                            end: {type: "date", from: "End"},
                                            startTimezone: {from: "StartTimezone"},
                                            endTimezone: {from: "EndTimezone"},
                                            description: {from: "Description"},
                                            recurrenceId: {from: "RecurrenceID"},
                                            recurrenceRule: {from: "RecurrenceRule"},
                                            recurrenceException: {from: "RecurrenceException"},
                                            ownerId: {from: "OwnerID", defaultValue: 1},
                                            isAllDay: {type: "boolean", from: "IsAllDay"}
                                        }
                                    }
                                },
                                filter: {
                                    logic: "or",
                                    filters: [
                                        {field: "ownerId", operator: "eq", value: 1},
                                        {field: "ownerId", operator: "eq", value: 2}
                                    ]
                                }
                            },
                            resources: [
                                {
                                    field: "ownerId",
                                    title: "Owner",
                                    dataSource: [
                                        {text: "Alex", value: 1, color: "#f8a398"},
                                        {text: "Bob", value: 2, color: "#51a0ed"},
                                        {text: "Charlie", value: 3, color: "#56ca85"}
                                    ]
                                }
                            ]
                        });
                        saveOrUpdate();
                    } else if (plugin_name == "Pdf Button") {
                        $.ajax({
                            url: base_url + '/admin/pages/get-pdf-button-name/',
                            type: "POST",
                            data: {
                                page_id: window.location.pathname.split('/')[3],
                                box_id: ++idCount,
                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                            },
                            success: function (result) {
                                console.log(result.pdf_button);

                                var plugin_content = plugin_name.replace(/ /g, "-");
                                var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                                var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "' data-pdf-button-id='" + result.pdf_button.id + "' data-pdf-button-name='" + result.pdf_button.name + "'>" + plugin_html + element_plugin_toolbox;
                                clog(plugin_element);
                                if ($('#content_data').find('.temporary').length < 1) {
                                    createTemporarySection();
                                }
                                $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                                $('html, body').animate({
                                    scrollTop: $("#" + 'box-' + idCount).offset().top
                                }, 2000);
                                saveOrUpdate();
                            }
                        });
                    } else {
                        var plugin_content = plugin_name.replace(/ /g, "-");
                        idCount++;
                        var plugin_html = $('#elements-' + plugin_content.toLowerCase()).find('.element').html();
                        var plugin_element = "<div class='event-plugin element event-plugin-" + plugin_content.toLowerCase() + " box' id='box-" + idCount + "' data-id='" + plugin_id + "' data-name='" + plugin_content.toLowerCase() + "'>" + plugin_html + element_plugin_toolbox;
                        clog(plugin_element);
                        if ($('#content_data').find('.temporary').length < 1) {
                            createTemporarySection();
                        }
                        $('.temporary').children('.row:last').children('.col:last').append(plugin_element);
                        $('html, body').animate({
                            scrollTop: $("#" + 'box-' + idCount).offset().top
                        }, 2000);
                        saveOrUpdate();
                    }
                }
            });
        });
    }

    $(".admin-plugin-search").on("input", function () {
        var query = this.value.toLowerCase();
        var dataSource = $("#admin-add-plugins-treeview").data("kendoTreeView").dataSource;
        searchData(dataSource, query);
        selectPlugin();
    });

// Add Plugin End


// Add Filter Start
    var filterTreeView = $("#add-filter-treeview").kendoTreeView({
        dataSource: JSON.parse($('#filter-tree').val()),
        change: function (e) {
            $("#clear-filter").remove();
        }
    });

    selectFilter();
    function selectFilter() {
        filterTreeView.each(function (i, el) {
            $(el).off("click").on("click", function (event) {
                var treeview = $("#add-filter-treeview").data("kendoTreeView");
                var filter_type = treeview.dataItem(event.target).data_type;
                if (filter_type == "quick-filter") {
                    $.ajax({
                        url: base_url + '/admin/filters/quick_filter_exists/',
                        success: function (response) {
                            if (response.status) {
                                var modal_class = 'filters-add-filter';
                                $('#quick-save-div').show();
                                $('#filter-grp-div').hide();
                                $('#preset-name-div').hide();
                                var name = "page";
                                showQuickFilterData(response.filter.id, modal_class, name);
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
                                //$('#dialoge').addClass('visible');
                                $('[data-remodal-id=modal]').remodal().open();
                                //inst.open();
                                $('#preset_name').attr('data-id', '');
                                var rowCount = 0;
                                $('.filter-list').html($('#filter-li-html').html());
                                activeDatePicker();


                            }
                        }
                    });
                }


            });
        });
    }

    $(".admin-filter-search").on("input", function () {
        var query = this.value.toLowerCase();
        var dataSource = $("#add-filter-treeview").data("kendoTreeView").dataSource;
        searchData(dataSource, query);
        selectFilter();
    });
// Add Filter End

//Add Tag Start

    // var tagTreeview = $("#add-tag-treeview").kendoTreeView({
    //         dataSource: [
    //             {
    //                 text: "General", spriteCssClass: "folder", expanded: true,
    //                 items: [
    //                     {text: "UID Link {uid_link}", spriteCssClass: "tag", tag: 'uid_link'},
    //                     {text: "First Name {first_name}", spriteCssClass: "tag", tag: 'first_name'},
    //                     {text: "Last Name {last_name}", spriteCssClass: "tag", tag: 'last_name'},
    //                     {text: "Email Address {email_address}", spriteCssClass: "tag", tag: 'email_address'},
    //                     {text: "Registration Date {registration_date}", spriteCssClass: "tag", tag: 'registration_date'},
    //                     {text: "Last Updated Date {updated_date}", spriteCssClass: "tag", tag: 'updated_date'},
    //                     {text: "Uid {uid}", spriteCssClass: "tag", tag: 'uid'},
    //                     {text: "Calendar {calendar}", spriteCssClass: "tag", tag: 'calendar'}
    //                 ]
    //             },
    //             {
    //                 text: "Group", spriteCssClass: "folder", expanded: true,
    //                 items: [
    //                     {text: "Attendee Groups {attendee_groups}", spriteCssClass: "tag", tag: 'attendee_groups'},
    //                     {text: "Tags {tags}", spriteCssClass: "tag", tag: 'tags'},
    //                     {text: "Hotels {hotels}", spriteCssClass: "tag", tag: 'hotels'},
    //                     {text: "Sessions {sessions}", spriteCssClass: "tag", tag: 'sessions'},
    //                     {text: "Travels {travels}", spriteCssClass: "tag", tag: 'travels'},
    //                     {text: "Questions {questions}", spriteCssClass: "tag", tag: 'questions'},
    //                     {text: "Photos {photos}", spriteCssClass: "tag", tag: 'photos'}
    //                 ]
    //             },
    //             {
    //                 text: "Economy Tags", spriteCssClass: "folder", expanded: true,
    //                 items: [
    //                     {text: "Order Table {order_table}", spriteCssClass: "tag", tag: 'order_table'},
    //                     {
    //                         text: "Multiple Order Table {multiple_order_table}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_table'
    //                     },
    //                     {text: "Balance Table {balance_table}", spriteCssClass: "tag", tag: 'balance_table'},
    //                     {
    //                         text: "Order value paid order {order_value_paid_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'order_value_paid_order'
    //                     },
    //                     {
    //                         text: "Multiple Order value paid order {multiple_order_value_paid_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_value_paid_order'
    //                     },
    //                     {
    //                         text: "Order value pending order {order_value_pending_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'order_value_pending_order'
    //                     },
    //                     {
    //                         text: "Multiple Order value pending order {multiple_order_value_pending_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_value_pending_order'
    //                     },
    //                     {
    //                         text: "Order value open order {order_value_open_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'order_value_open_order'
    //                     },
    //                     {
    //                         text: "Multiple Order value open order {multiple_order_value_open_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_value_open_order'
    //                     },
    //                     {
    //                         text: "Order value all order {order_value_all_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'order_value_all_order'
    //                     },
    //                     {
    //                         text: "Multiple Order value all order {multiple_order_value_all_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_value_all_order'
    //                     },
    //                     {
    //                         text: "Order value credit order {order_value_credit_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'order_value_credit_order'
    //                     },
    //                     {
    //                         text: "Multiple Order value credit order {multiple_order_value_credit_order}",
    //                         spriteCssClass: "tag",
    //                         tag: 'multiple_order_value_credit_order'
    //                     },
    //                     {text: "Receipt {receipt}", spriteCssClass: "tag", tag: 'receipt'},
    //                 ]
    //             }
    //         ]
    //     }).data("kendoTreeView"),
    //     handleTextBox = function (callback) {
    //         return function (e) {
    //             if (e.type != "keypress" || kendo.keys.ENTER == e.keyCode) {
    //                 callback(e);
    //             }
    //         };
    //     };
    // selectTag();
    // function selectTag() {
    // tagTreeview.items().each(function (i, el) {
    //     $(el).on("dblclick", function (event) {
    //         var treeview = $("#add-tag-treeview").data("kendoTreeView");
    //         var tag = treeview.dataItem(event.target).tag;
    //         clog(tag);
    //         if (tag != '' && tag != undefined) {
    //             if (tag == 'hotels') {
    //                 editor.replaceSelection('{"hotels":[{"id":"","group-id":"","columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"Y.M.d"}]}', 'end');
    //             } else if (tag == 'sessions') {
    //                 editor.replaceSelection('{"sessions":[{"id":"","group-id":"","columns":"name,start,end", "sort-column":"start",  "status":"attending","time-date":"Y.M.d H:i"}]}', 'end');
    //             }
    //             else if (tag == 'travels') {
    //                 editor.replaceSelection('{"travels":[{"id":"","group-id":"","columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"Y.M.d H:i"}]}', 'end');
    //             }
    //             else if (tag == 'questions') {
    //                 editor.replaceSelection('{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"Y.M.d H:i"}]}', 'end');
    //             }
    //             else if (tag == 'photos') {
    //                 editor.replaceSelection('{"photo":[{ "group":""}]}', 'end');
    //             }
    //             else {
    //                 editor.replaceSelection('{' + tag + '}', 'end');
    //             }
    //         }
    //     });
    // });
    // }

    // $(".admin-tag-search").on("input", function () {
    //     var query = this.value.toLowerCase();
    //     var dataSource = $("#add-tag-treeview").data("kendoTreeView").dataSource;
    //     searchData(dataSource, query);
    //     selectTag();
    // });

// Add Tag End


// sets "hidden" field on items matching query
// Kendo Search
    function searchData(dataSource, query) {
        var hasVisibleChildren = false;
        var data = dataSource instanceof kendo.data.HierarchicalDataSource && dataSource.data();

        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            var text = item.text.toLowerCase();
            var itemVisible =
                query === true // parent already matches
                || query === "" // query is empty
                || text.indexOf(query) >= 0; // item text matches query

            var anyVisibleChildren = searchData(item.children, itemVisible || query); // pass true if parent matches

            hasVisibleChildren = hasVisibleChildren || anyVisibleChildren || itemVisible;

            item.hidden = !itemVisible && !anyVisibleChildren;
        }

        if (data) {
            // re-apply filter on children
            dataSource.filter({field: "hidden", operator: "neq", value: true});
        }

        return hasVisibleChildren;
    }

// Date selector for settings
//    $(".plugin-setting-calendar").kendoDatePicker();
//    $(".plugin-setting-time").kendoTimePicker();

// Add Custom Class Start

    var newItem = "";

    function onDataBound() {
        if ((newItem || this._prev) && newItem !== this._prev) {
            var ds = this.dataSource,
                datas = ds.data(),
                lastItem = datas[datas.length - 1];
            newItem = this._prev;
            if (datas.length > 0) {
                if (/\(Add New\)$/i.test(lastItem.text)) {
                    ds.remove(lastItem);
                }
            }
            var newEntryFound = _.findWhere(datas, {text: newItem}) != null;

            if (newItem.length > 2 && !newEntryFound) {
                ds.add({text: newItem + " (Add New)", id: newItem});
                this.open();
            }
        }
    }

    function onSelect(e) {
        var dataItem = this.dataSource.view()[e.item.index()],
            datas = this.dataSource.data(),
            lastData = datas[datas.length - 1];

        clog(parseInt(dataItem.value))
        if (parseInt(dataItem.value) > 0) {
            clog(parseInt(dataItem.value))
            //this.dataSource.remove(lastData);
        } else {
            clog("onselect :" + dataItem.text)
            dataItem.text = dataItem.text.replace(" (Add New)", "");
        }
    }


    var CustomClass = $("#admin-element-settings-classes").kendoMultiSelect({
        dataSource: {
            transport: {
                read: {
                    url: base_url + '/admin/pages/get-custom-classes/',
                    dataType: "json",
                }
            },
            schema: {
                data: function (data) { //specify the array that contains the data
                    return data.results;
                }
            }
        },
        animation: false,
        dataBound: onDataBound,
        select: onSelect,
        dataTextField: "text",
        dataValueField: "id"
    });

// Add Custom Class End

    // Show Rebate List End

    $(document).ready(scrollWrapperHeight);
    $(window).on('resize', scrollWrapperHeight);

    function scrollWrapperHeight() {
        $(".admin-menu-scrollable").each(function () {
            var totalHeight = 0
            $(this).closest("fieldset").children(".admin-menu-group").not(this, "this > .admin-menu-group").each(function (index) {
                totalHeight += $(this).outerHeight(true);
            });

            $(this).innerHeight(
                $(this).closest("fieldset").height() - ($(this).siblings("legend").outerHeight(true)) - totalHeight);
        });
    }

// REMOVE CURRENT SEARCH

    $(".admin-search-wrapper .admin-clear-search").click(function () {
        $(this).parent().find(".admin-search").val('').focus();
    });

// ADD COLUMN

// Add columns to preview

    function createCol(newColumns) {
        $.each(newColumns, function (index, value) {
            $("#admin-columns-preview").append("<div class='admin-columns-add-col' data-admin-columns-col-width='" + value + "'>" + value + "<i class='admin-columns-delete-current-col fa fa-trash'></i></div>");
        });
    }

// Clicking a predefined column layout

    $(".admin-columns-add-predefined-col").click(function () {
        var newColumns = $(this).attr('data-admin-columns-cols').split("+");
        $("#admin-columns-preview").html("")
        createCol(newColumns);
    });

// Clicking the Add button

    $("#admin-columns-add-col-button").click(function () {
        currentColTotal = 0;
        $('#admin-columns-preview').children().each(function () {
            currentColTotal += parseInt($(this).attr('data-admin-columns-col-width'));
        });

        currentColAdding = $("#admin-columns-add-col-value").val();
        clog(currentColAdding);
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

    $(document).on('click', '.admin-columns-add-col .admin-columns-delete-current-col', function () {
        $(this).closest(".admin-columns-add-col").remove();

    });

// Checked Row Has Section

    $(document).on('click', '#admin-columns-toggle', function () {
        //$('#rowHasSection').prop('checked', true);

    });

// Clicking the Add to page-button

    $("#admin-columns-add-col-to-page").click(function () {
        currentColTotal = 0;
        $('#admin-columns-preview').children().each(function () {
            currentColTotal += parseInt($(this).attr('data-admin-columns-col-width'));
        });

        if (currentColTotal > 0) {
            var row_has_section = $('#rowHasSection').prop("checked");
            //if (row_has_section) {
            //    idCount++;
            //    var section_id = idCount;
            //    idCount++;
            //    var row_id = idCount;
            //    colHTML = "<div class='section section-box box' id=box-" + section_id + ">" +
            //        section_toolbox +
            //        "<div class='row box' id=box-" + row_id + ">";
            //} else {
            //    idCount++;
            //    var row_id = idCount;
            //    colHTML = "<div class='row box section-box' id=box-" + row_id + ">";
            //}

            idCount++;
            var section_id = idCount;
            idCount++;
            var row_id = idCount;
            if (row_has_section) {
                colHTML = "<div class='section section-box box' id=box-" + section_id + ">" +
                    section_toolbox +
                    "<div class='row box' id=box-" + row_id + ">";
            } else {
                if ($("#content_data").find('.section').length == 0) {
                    colHTML = "<div class='section-box box' id=box-" + section_id + ">" +
                        section_toolbox +
                        "<div class='row box' id=box-" + row_id + ">";
                } else {
                    colHTML = "<div class='row box' id=box-" + row_id + ">";
                }
            }

            // Adds the columns to the appeding code
            $('#admin-columns-preview').children().each(function () {
                idCount++;
                var col_id = idCount;
                currentColToAdd = $(this).attr('data-admin-columns-col-width');
                colHTML = colHTML + "<div class='col span-" + currentColToAdd + " box' id=box-" + col_id + ">" + col_toolbox + "</div>"
            });

            // Adds the last (row) appending code
            colHTML = colHTML + row_toolbox + "</div>";
            if (row_has_section || $("#content_data").find('.section').length == 0) {
                $("#content_data").append(colHTML);
            } else {
                $("#content_data").find('.section:last').append(colHTML);
            }


            // Updates the sorting on rows and columns
            sortCol();
            sortRow();
            sortSection();


        } else {

            alert("The row has no columns. Add more columns and try again.");

        }

    });


    function sortCol() {
        $("#content_data .col").sortable({
            handle: ".move-element",
            connectWith: ".col",
            //placeholder: "ui-state-highlight",
            cursor: "move",
            helper: 'clone',
            opacity: '.5',
            revert: "invalid",
            start: function (event, ui) {
                $("#content").addClass("dragging");
            },
            receive: function (event, ui) {
            },
            stop: function (event, ui) {
                $("#content").removeClass("dragging");
                saveOrUpdate();
            }
        });
    }

    function sortRow() {
        $("#content_data .section-box").sortable({
            handle: ".move-row",
            connectWith: ".section-box",
            cursor: "move",
            helper: 'clone',
            opacity: '.5',
            revert: "invalid",
            start: function (event, ui) {
                $("#content").addClass("dragging");
            },
            receive: function (event, ui) {
            },
            stop: function (event, ui) {
                $("#content").removeClass("dragging");
                saveOrUpdate();
            }
        });
    }

    function sortSection() {
        $("#content_data").sortable({
            handle: ".move-section",
            cursor: "move",
            helper: 'clone',
            opacity: '.5',
            revert: "invalid",
            start: function (event, ui) {
                $("#content").addClass("dragging");
            },
            receive: function (event, ui) {
            },
            stop: function (event, ui) {
                $("#content").removeClass("dragging");
                saveOrUpdate();
            }
        });
    }

    var slug = function (str) {
        var $slug = '';
        var trimmed = $.trim(str);
        $slug = trimmed.replace(/[^a-z0-9-]/gi, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
        return $slug.toLowerCase();
    }

    $(document).ready(function () {
        sortCol();
        sortRow();
        sortSection();
        $('#dialoge .dialogue-content').on('click', '.close-dialouge', function () {
            $("#dialoge").removeClass("visible");
        });
        $("#dialoge").not($(this).find('.dialogue-content')).click(function () {
            $(this).removeClass("visible");
        }).children().click(function (e) {
            e.stopPropagation();
        });

        $('.dialoge .dialogue-content').on('click', '.close-dialouge', function () {
            $(".dialoge").removeClass("visible");
        });
        $(".dialoge").not($(this).find('.dialogue-content')).click(function () {
            $(this).removeClass("visible");
        }).children().click(function (e) {
            e.stopPropagation();
        });

        $(function () {
            $("#admin-columns-preview").sortable({
                placeholder: "admin-columns-add-col-drag",
                cursor: "move",
                opacity: '0.5',
                helper: "clone",
            });
            $("#admin-columns-preview").disableSelection();
        });
    });

// ADMIN TOGGLE WRAPPER

    $("#admin-toggle-wrapper").draggable({
        handle: "#admin-toggle-wrapper-titlebar",
        containment: "window"
    });

// Handles menu visibility
    $("#admin-toggle-wrapper :checkbox").change(function () {
        var menu = $(this).attr("data-admin-menu");
        if(menu != "admin-editor") {
            if ($("#" + menu).hasClass("visible")) {
                // If menu is visble
                $(".admin-menu").removeClass("visible");
                if (menu == "admin-file-repository") {
                    $('#admin-editor').addClass("visible");
                }
                // else if (menu == "admin-editor") {
                //     // $('#admin-file-repository').removeClass("visible");
                //     // $("#admin-toggle-wrapper #admin-file-repository-toggle").prop('checked', false);
                // }
            } else {
                // If menu is not visible
                $(".admin-menu").removeClass("visible");
                $("#" + menu).addClass("visible");
                $("#admin-toggle-wrapper :checkbox").not(this).prop('checked', false);
                // if (menu == "admin-file-repository") {
                //     $('#admin-editor').addClass("visible");
                //     $("#admin-toggle-wrapper #admin-editor-toggle").prop('checked', true);
                // }
                // else if (menu == "admin-editor") {
                //     // $('#admin-file-repository').addClass("visible");
                //     $("#admin-toggle-wrapper #admin-file-repository-toggle").prop('checked', true);
                // }
            }
        }else{
            $("#admin-toggle-wrapper #admin-editor-toggle").prop('checked', false);
        }

    });

// Closes .admin-menu (x)
    $(".admin-menu .admin-close-button").click(function () {
        if ($(this).closest('.admin-menu').attr('id') == 'admin-file-repository') {
            $(this).closest('.admin-menu').removeClass("visible");
            $("#admin-toggle-wrapper #admin-file-repository-toggle").prop('checked', false);
        } else {
            $(".admin-menu").removeClass("visible");
            $("#admin-toggle-wrapper :checkbox").prop('checked', false);
        }
    });

// CMS TOOLBOX

    $(".admin-cms-toolbox").hide();
    $('#content_data').on("mouseenter", (".row, .col, .element"), function () {
        enter($(this));
    }).on("mouseleave", (".row, .col, .element"), function () {
        exit($(this));
    });
    function enter(element) {
        var child = element.children('.admin-cms-toolbox:first');
        child.show();
        $(".admin-cms-toolbox").not(child).hide();
    }

    function exit(element) {
        element.children('.admin-cms-toolbox:first').hide();
        var parent = element.parent().children(".admin-cms-toolbox:first");
        if (parent.length !== 0)
            parent.show();
    }


// CMS ACTIVE ELEMENT

    // $(".section-box .col:first").addClass("column-preview");
    //
    // $("body").on("click", ".col", function () {
    //     $(".col").removeClass("column-preview");
    //     $(this).addClass("column-preview");
    // });
    //
    // $("body").on("click", ".element", function () {
    //     $(".element").not(this).removeClass("current-element");
    //     $(this).toggleClass("current-element");
    // });

    $("body").on("click", ".element", function () {
        $(".element").removeClass("selected");
        $(".col").removeClass("selected");
        $(".row").removeClass("selected");
        $(this).addClass("selected");
        $(this).closest('.col').addClass("selected");
        $(this).closest('.row').addClass("selected");
    });

    $("#admin-editor-toggle").on("click", function () {
        // if ($("#admin-toggle-wrapper #admin-editor-toggle").is(':checked')) {
        // var scrollHeight = $("#content_data").height() + $("#admin-editor").height();
        // $("#content_data").height(scrollHeight);
        // if ($('#admin-editor.visible').length > 0) {
        //     saveEditorHtml();
        // }
        if ($('#content_data').find('.temporary').length < 1) {
            createTemporarySection();
        }
        idCount++;
        var element = "<div class='element form-editor box' id=box-" + idCount + ">" +
            element_toolbox + "<div class='editor-inline-box'></div>" +
            "</div>";
        $('.temporary').children('.row:last').children('.col:last').append(element);
        var $this_editor = $('.temporary').children('.row:last').children('.col:last').find('div.form-editor').find('.editor-inline-box');
        initInlineFroala($this_editor);
        $('#current-editor-box').val('box-' + idCount);
        $('html, body').animate({
            scrollTop: $("#" + 'box-' + idCount).offset().top
        }, 'fast');
        $body.find('div.editor-inline-box').off('froalaEditor.buttons.refresh');
        $body.find('div.editor-inline-box').off('froalaEditor.contentChanged');
        $body.find('div.editor-inline-box').on('froalaEditor.buttons.refresh', function (e, editor) {
            getInlineEditorHtml($(this));
            saveOrUpdate();
        });
        $body.find('div.editor-inline-box').on('froalaEditor.contentChanged', function (e, editor) {
            console.log('ypyo');
            getInlineEditorHtml($(this));
            saveOrUpdate();
        });
        // $this_editor.on('froalaEditor.buttons.refresh', function (e, editor) {
        //     getInlineEditorHtml($(this));
        //     saveOrUpdate();
        // });
        // $this_editor.on('froalaEditor.contentChanged', function (e, editor) {
        //     console.log('ypyo');
        //     getInlineEditorHtml($(this));
        //     saveOrUpdate();
        // });
        // if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
        //     $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        // }
        // $('textarea#froala_content_editor').froalaEditor('html.set', '');
        // editor.setValue("");
        // } else {
        //     // var scrollHeight = $("#content_data").height() - $("#admin-editor").height();
        //     // $("#content_data").height(scrollHeight);
        //     saveEditorHtml();
        // }
    });
    // $("#admin-file-repository-toggle").on("click", function () {
    //     if ($('#admin-editor.visible').length == 0) {
    //         if ($('#content_data').find('.temporary').length < 1) {
    //             createTemporarySection();
    //         }
    //         idCount++;
    //         var element = "<div class='element form-editor box' id=box-" + idCount + ">" +
    //             element_toolbox + "<div class='editor-inline-box'></div>"+
    //             "</div>";
    //         $('.temporary').children('.row:last').children('.col:last').append(element);
    //         $('#current-editor-box').val('box-' + idCount);
    //         $('html, body').animate({
    //             scrollTop: $("#" + 'box-' + idCount).offset().top
    //         }, 'fast');
    //         if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
    //             $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
    //         }
    //         $('textarea#froala_content_editor').froalaEditor('html.set', '');
    //         // editor.setValue("");
    //     } else {
    //         saveEditorHtml();
    //     }
    // });
    function createTemporarySection() {
        idCount++;
        var section_id = idCount;
        idCount++;
        var row_id = idCount;
        idCount++;
        var col_id = idCount;
        var temporarySection = "<div class='section section-box temporary box' id=box-" + section_id + ">" +
            section_toolbox +
            "<div class='row box' id=box-" + row_id + ">" +
            row_toolbox +
            "<div class='col span-12 box' id=box-" + col_id + ">" +
            col_toolbox +
            "</div>" +
            "</div></div>"
        $("#content_data").append(temporarySection);

        // Updates the sorting on rows and columns
        sortCol();
        sortRow();
        sortSection();

    }

    // $(document).on('click', '.element > .admin-cms-toolbox > .edit', function () {
    //     if ($('#admin-editor.visible').length > 0) {
    //         saveEditorHtml();
    //     }
    //     var box_id = $(this).closest('.element').attr('id');
    //     var page_id = window.location.pathname.split('/')[3];
    //     // $('form').find('.CodeMirror').remove();
    //     var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    //     var new_html = "";
    //     var language_id = $("#admin-languages-toggle").val();
    //     $.ajax({
    //         url: base_url + '/admin/pages/get-element-html/',
    //         dataType: "json",
    //         type: "POST",
    //         data: {
    //             box_id: box_id.split("-")[1],
    //             page_id: page_id,
    //             language_id: language_id,
    //             csrfmiddlewaretoken: csrf_token
    //         },
    //         async: false,
    //         success: function (result) {
    //             if (result.success) {
    //                 if (result.element_html != "") {
    //                     // new_html = result.element_html.uncompiled;
    //                     new_html = result.element_html.compiled;
    //                 }
    //             }
    //         }
    //     });
    //     //var hiddenDiv = $('#hidden-content');
    //     //hiddenDiv.html($(this).closest('.element').html());
    //     //hiddenDiv.find('.admin-cms-toolbox').remove();
    //     //var allHtml = hiddenDiv.html();
    //     ////var new_html = toMarkdown(allHtml);
    //     // $("#code").html(new_html);
    //     // clog(new_html);
    //     // editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    //     //     mode: 'gfm',
    //     //     lineNumbers: false,
    //     //     matchBrackets: true,
    //     //     lineWrapping: true,
    //     //     theme: 'base16-light',
    //     //     extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"}
    //     // });
    //     // //editor.display.wrapper.style.fontSize = "1.2em";
    //     //
    //     // update(editor);
    //     // $("#code").html("");
    //     // clog(editor.getValue());
    //     // var data = btoa( // base64 so url-safe
    //     //     RawDeflate.deflate( // gzip
    //     //         unescape(encodeURIComponent( // convert to utf8
    //     //             editor.getValue()
    //     //         ))
    //     //     )
    //     // );
    //     // clog(data);
    //     // var h = data.replace(/^#/, '');
    //     // setOutput(decodeURIComponent(escape(RawDeflate.inflate(atob(h)))));
    //     if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
    //         $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
    //     }
    //     $('textarea#froala_content_editor').froalaEditor('html.set', new_html);
    //     $('#current-editor-box').val(box_id);
    //     $(".admin-menu").removeClass("visible");
    //     $('#admin-editor').addClass('visible');
    //     // $('#admin-file-repository').addClass('visible');
    //     // $("#admin-toggle-wrapper #admin-file-repository-toggle").prop('checked', true);
    //     $("#admin-toggle-wrapper #admin-editor-toggle").prop('checked', true);
    //     // editor.on('change', function () {
    //     //     update(editor);
    //     //     updateData();
    //     // });
    //     // var scrollHeight = $("#content_data").height() + $("#admin-editor").height();
    //     // $("#content_data").height(scrollHeight);
    //     console.log('yes');
    //     $('html, body').animate({
    //         scrollTop: $("#" + box_id).offset().top
    //         // scrollTop: scrollHeight
    //     }, 2000);
    //     //editor.on('blur', function () {
    //     //    getEditorHtml();
    //     //    saveOrUpdate();
    //     //});
    // });
    $(document).on('click', '#admin-save-cms', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        saveOrUpdate();
    });
    $(document).on('click', '#admin-editor .admin-close-button', function () {
        // var scrollHeight = $("#content_data").height() - $("#admin-editor").height();
        // $("#content_data").height(scrollHeight);
        saveEditorHtml();
    });
    //editor.on('blur', function () {
    //    getEditorHtml();
    //    saveOrUpdate();
    //});
    // $('textarea#froala_content_editor').on('froalaEditor.contentChanged', function (e, editor) {
    //     updateData();
    // });
    // $body.find('div.editor-inline-box').on('froalaEditor.contentChanged', function (e, editor) {
    //     getInlineEditorHtml($(this));
    //     saveOrUpdate();
    // });
    // $('textarea#froala_content_editor').on('froalaEditor.focus', function (e, editor) {
    //     updateData();
    // });
    // $('textarea#froala_content_editor').on('froalaEditor.click', function (e, editor) {
    //     updateData();
    // });
    // $('textarea#froala_content_editor').on('froalaEditor.blur', function (e, editor) {
    //     getEditorHtml();
    //     saveOrUpdate();
    // });

    // $(document).on('froalaEditor.buttons.refresh','.editor-inline-box', function (e, editor) {
    //     getInlineEditorHtml($(this));
    //     saveOrUpdate();
    // });
    // $(document).on('froalaEditor.contentChanged','.editor-inline-box', function (e, editor) {
    //     console.log('ypyo');
    //     getInlineEditorHtml($(this));
    //     saveOrUpdate();
    // });

    function saveEditorHtml() {
        getEditorHtml();
        saveOrUpdate();
    }

    function getEditorHtml() {
        var box = $('#current-editor-box').val();
        if ($.trim(box) != "" && $.trim(box) != undefined) {
            var box_id = box.split("-")[1];
            var page_id = window.location.pathname.split('/')[3];
            // var compiled_html = $('#out').html();
            var compiled_html = $('textarea#froala_content_editor').froalaEditor('html.get');
            // var uncompiled_html = editor.getValue();
            var uncompiled_html = compiled_html;
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            var language_id = $("#admin-languages-toggle").val();
            $.ajax({
                url: base_url + '/admin/pages/set-element-html/',
                dataType: "json",
                type: "POST",
                data: {
                    box_id: box_id,
                    page_id: page_id,
                    compiled_html: compiled_html,
                    uncompiled_html: uncompiled_html,
                    language_id: language_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    clog(result);
                }
            });
        }
    }

    function updateData() {
        clog("ok");
        var editor_box = $('#current-editor-box').val();
        if ($.trim(editor_box) != "") {
            // clog(editor_box);
            var content = $('textarea#froala_content_editor').froalaEditor('html.get');
            // clog($('#content_data').find('#' + editor_box).html());
            // $('#content_data').find('#' + editor_box).html(element_toolbox + content);
            // clog(element_toolbox + content);
            // $('#' + editor_box).html(element_toolbox + content);
            // $('#' + editor_box).froalaEditor('html.set', element_toolbox + content);
            console.log(editor_box);
            console.log(content);
            $body.find('#' + editor_box).find('.editor-inline-box').froalaEditor('html.set', content);
        }
    }

// language dropdown change language event

    $(document).on('change', '#admin-languages-toggle', function () {
        clog("Change event called");
        if ($('#admin-editor.visible').length > 0) {
            var box = $('#current-editor-box').val();
            if ($.trim(box) != "" && $.trim(box) != undefined) {
                var box_id = box.split("-")[1];
                var page_id = window.location.pathname.split('/')[3];
                //var compiled_html = $('#out').html();
                //var uncompiled_html = editor.getValue();
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                var language_id = $("#admin-languages-toggle").val();
                $.ajax({
                    url: base_url + '/admin/pages/get-element-html/',
                    dataType: "json",
                    type: "POST",
                    data: {
                        box_id: box_id,
                        page_id: page_id,
                        language_id: language_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    async: false,
                    success: function (result) {
                        if (result.success) {
                            // new_html = result.element_html.uncompiled;
                            new_html = result.element_html.compiled;
                        } else {
                            new_html = "";
                        }
                    }
                });
                // $("#code").html(new_html);
                // clog(new_html);
                // editor = CodeMirror.fromTextArea(document.getElementById('code'), {
                //     mode: 'gfm',
                //     lineNumbers: false,
                //     matchBrackets: true,
                //     lineWrapping: true,
                //     theme: 'base16-light',
                //     extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"}
                // });
                //editor.display.wrapper.style.fontSize = "1.2em";

                // update(editor);
                // $("#code").html("");
                // clog(editor.getValue());
                // var data = btoa( // base64 so url-safe
                //     RawDeflate.deflate( // gzip
                //         unescape(encodeURIComponent( // convert to utf8
                //             editor.getValue()
                //         ))
                //     )
                // );
                // clog(data);
                // var h = data.replace(/^#/, '');
                // setOutput(decodeURIComponent(escape(RawDeflate.inflate(atob(h)))));
                if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                    $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
                }
                $('textarea#froala_content_editor').froalaEditor('html.set', new_html);
                $('#current-editor-box').val(box);
                $(".admin-menu").removeClass("visible");
                $('#admin-editor').addClass('visible');
                // $('#admin-file-repository').addClass('visible');
                updateData();
                clog($('#current-editor-box').val());
                // editor.on('change', function () {
                //     update(editor);
                //     updateData();
                // });
                //$('html, body').animate({
                //    scrollTop: $("#" + box_id).offset().top
                //}, 2000);
            }
        }
    });


// Delete section, row, col, element


    $(document).on('click', '.section > .admin-cms-toolbox > .delete', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        if (confirm("Are you sure you want to delete this section and all of it's content?")) {
            var box_id = $(this).closest(".section").attr('id');
            $(this).closest(".section").remove();
            removeFilterAndElement(box_id);
            saveOrUpdate();
        }
    });

    $(document).on('click', '.row > .admin-cms-toolbox > .delete', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        if (confirm("Are you sure you want to delete this row and all of it's content?")) {
            var box_id = $(this).closest(".row").attr('id');
            $(this).closest(".row").remove();
            removeFilterAndElement(box_id);
            saveOrUpdate();
        }
    });

    $(document).on('click', '.col > .admin-cms-toolbox > .delete', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        if (confirm("Are you sure you want to delete this Col and all of it's content?")) {
            var box_id = $(this).closest(".col").attr('id');
            $(this).closest(".col").remove();
            removeFilterAndElement(box_id);
            saveOrUpdate();
        }
    });

    $(document).on('click', '.element > .admin-cms-toolbox > .delete', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        if (confirm("Are you sure you want to delete this element and all of it's content?")) {
            var box_id = $(this).closest(".element").attr('id');
            $(this).closest(".element").remove();
            if ($(this).closest(".element").hasClass("form-editor")) {
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                var page_id = window.location.pathname.split('/')[3];
                var box = box_id.split("-")[1]
                $.ajax({
                    url: base_url + '/admin/pages/delete-element-html/',
                    type: "POST",
                    data: {
                        page_id: page_id,
                        box_id: box,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                    }
                });
            }
            removeFilterAndElement(box_id);
            saveOrUpdate();
        }
    });


// Plugin Settings
    $(document).on('click', '.element > .admin-cms-toolbox > .btn-plugin-setting', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        var plugin_name = $(this).closest('.element').attr('data-name');
        var box_id = $(this).closest('.box').attr('id').split('-')[1];
        $(".admin-menu").removeClass("visible");
        $('#admin-plugin-settings').find('.scroll-wrapper').html($('#elements-' + plugin_name + '-setting').html());
        $('#admin-plugin-settings').find('.scroll-wrapper').find('fieldset').attr('data-box-id', box_id);
        $("#admin-plugin-settings").find('.scroll-wrapper').find('fieldset').find('.admin-menu-scrollable').append("<button class='save-element-settings'>Save</button>");
        $("#admin-plugin-settings").find('.save-element-settings').attr('disabled', true);
        getPluginSettings($('#admin-plugin-settings'), box_id, plugin_name);
        $("#admin-plugin-settings").addClass("visible");
        scrollWrapperHeight();
    });

    $(document).on('change', '.plugin-setting-session-checkbox-session-groups input', function () {
        getCheckboxSessionsPreselected();
    });

    $(document).on('change', '.plugin-setting-session-radio-button-session-groups input', function () {
        var selected_session = $('.settings-session-radio-button-preselected').find('select').val();
        if (selected_session != undefined) {
            getRadioSessionsPreselected(selected_session);
        } else {
            getRadioSessionsPreselected();
        }
    });

    function getCheckboxSessionsPreselected(preselect_session, checkbox_radio_preselect_session, session_checkbox_choose_min, session_checkbox_choose_max) {
        var groups = [];
        $('.plugin-setting-session-checkbox-session-groups').find('input').each(function () {
            var group_id = $(this).attr('data-group-id');
            if ($(this).prop('checked')) {
                groups.push(group_id);
            }
        });
        if (groups.length > 0) {
            getSessionsByGroups(groups, preselect_session, checkbox_radio_preselect_session, session_checkbox_choose_min, session_checkbox_choose_max);
        } else {
            var sessionList = $("#settings-session-checkbox-preselected-select").data('kendoMultiSelect');
            sessionList.dataSource.read();
            var dataSource = new kendo.data.DataSource({
                data: []
            });
            sessionList.setDataSource(dataSource);
            $('.settings-session-checkbox-radio-preselected').find('select').html("<option value=''>None</option>");
        }
    }

    function getRadioSessionsPreselected(radio_preselect_session) {
        var groups = [];
        $('.plugin-setting-session-radio-button-session-groups').find('input').each(function () {
            var group_id = $(this).attr('data-group-id');
            if ($(this).prop('checked')) {
                groups.push(group_id);
            }
        });
        if (groups.length > 0) {
            getRadioSessionsByGroups(groups, radio_preselect_session);
        } else {
            $('.settings-session-radio-button-preselected').find('select').html("<option value=''>None</option>");
        }
    }

    function getRadioSessionsByGroups(groups, radio_preselect_session) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/pages/get-sessions-by-groups/',
            dataType: "json",
            type: "POST",
            data: {
                groups: JSON.stringify(groups),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                var sessions = result.results;
                var options = "<option value=''>None</option>";
                for (var i = 0; i < sessions.length; i++) {
                    options += "<option value=" + sessions[i].id + ">" + sessions[i].text + "</option>";
                }
                var preselect_elem = $('.settings-session-radio-button-preselected').find('select');
                preselect_elem.html(options);
                if (radio_preselect_session) {
                    preselect_elem.val(radio_preselect_session);
                }
            }
        });
    }


    function getSessionsByGroups(groups, preselect_session, checkbox_radio_preselect_session, session_checkbox_choose_min, session_checkbox_choose_max) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/pages/get-sessions-by-groups/',
            dataType: "json",
            type: "POST",
            data: {
                groups: JSON.stringify(groups),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                var sessionList = $("#settings-session-checkbox-preselected-select").data('kendoMultiSelect');
                sessionList.dataSource.read();
                var dataSource = new kendo.data.DataSource({
                    data: result.results
                });
                sessionList.setDataSource(dataSource);
                clog(sessionList.dataSource.total());
                var total_session = sessionList.dataSource.total();
                var $session_min = $('.settings-session-checkbox-choose-min').find('select');
                var $session_max = $('.settings-session-checkbox-choose-max').find('select');
                var session_min_val = $session_min.val();
                var session_max_val = $session_max.val();
                var session_min_options = '<option value="0" selected>No minimum limit</option>';
                var session_max_options = '<option value="0" selected>No maximum limit</option>';
                for (var session_i = 1; session_i <= total_session; session_i++) {
                    session_min_options += '<option value="' + session_i + '">' + session_i + ' sessions</option>';
                    session_max_options += '<option value="' + session_i + '">' + session_i + ' sessions</option>';
                }
                $session_min.html(session_min_options);
                $session_max.html(session_max_options);
                if(session_min_val != null && session_min_val != undefined && session_min_val != ''){
                    $session_min.val(session_min_val);
                }else{
                    $session_min.val("0");
                }
                if(session_max_val != null && session_max_val != undefined && session_max_val != ''){
                    $session_max.val(session_max_val);
                }else{
                    $session_max.val("0");
                }
                if(session_checkbox_choose_min){
                    $session_min.val(session_checkbox_choose_min);
                }
                if(session_checkbox_choose_max){
                    $session_max.val(session_checkbox_choose_max);
                }
                //sessionList.trigger("change");

                if (preselect_session) {
                    sessionList.value(preselect_session);
                }

                // Checkbox when Act like radio
                var radio_sessions = result.results;
                var radio_options = "<option value=''>None</option>";
                for (var i = 0; i < radio_sessions.length; i++) {
                    radio_options += "<option value=" + radio_sessions[i].id + ">" + radio_sessions[i].text + "</option>";
                }
                var radio_preselect_elem = $('.settings-session-checkbox-radio-preselected').find('select');
                radio_preselect_elem.html(radio_options);
                console.log(radio_preselect_elem)
                if(checkbox_radio_preselect_session){
                    radio_preselect_elem.val(checkbox_radio_preselect_session);
                }
            }
        });
    }

    // checkbox change event for custom location

    $('body').on('click', '.settings-session-custom-location input[type=checkbox]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-location-list-display').show();
        } else {
            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-location-list-display').hide();
        }
    });

    // checkbox change event for session agenda search

    $('body').on('click', '.plugin-setting-session-agenda-is-searchable input[type=checkbox]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-agenda-searchable-property').show();
        } else {
            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-agenda-searchable-property').hide();
        }
    });

    // checkbox change event for Session Details in Session Radio

    $('body').on('click', '.settings-session-radio-button-show-details input[type=checkbox]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-radio-session-detail-display').show();
        } else {
            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-radio-session-detail-display').hide();
        }
    });

    // checkbox change event for Session Details in Session Checkbox

    $('body').on('click', '.settings-session-checkbox-show-details input[type=checkbox]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-checkbox-session-detail-display').show();
        } else {
            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-checkbox-session-detail-display').hide();
        }
    });
    
    // checkbox show session must choose option when act like radio button

    $('body').on('click', '.settings-session-checkbox-act-like-radio-button input[type=checkbox]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-session-must-choose').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-remove-conflict-session').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-radio-preselected').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-preselected').hide();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-choose-min').hide();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-choose-max').hide();
        } else {
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-choose-min').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-choose-max').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-preselected').show();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-radio-preselected').hide();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-session-must-choose').hide();
            $(this).closest('#admin-plugin-settings').find('.settings-session-checkbox-remove-conflict-session').hide();
        }
    });

    $('body').on('change', '.plugin-setting-hotel-reservation-hotel-groups input[type=checkbox]', function () {
        if ($('.plugin-setting-hotel-reservation-hotel-groups:visible').length > 0) {
            var $hrp_elem = $('.plugin-setting-hotel-reservation-hotel-groups:visible').closest('.settings-hotel-reservation');
            var hotel_groups = ['do-not-force'];
            $hrp_elem.find('.plugin-setting-hotel-reservation-hotel-groups').find('input:checkbox:checked').each(function () {
                hotel_groups.push($(this).attr('data-group-id'));
            });
            $hrp_elem.find('.plugin-setting-hotel-reservation-force-hotel-room').find('.settings-given-answer').find('option').each(function () {
                if ($.inArray($(this).attr('data-group'), hotel_groups) == -1) {
                    $(this).hide();
                } else {
                    $(this).show();
                }

            });
            // $hrp_elem.find('.plugin-setting-hotel-reservation-force-hotel-room').find('.settings-given-answer').find('select option[value="do-not-force"]');
        }
    });

// Get Pluging Settings

    function getPluginSettings(toolbox, box_id, plugin_name) {
        var page_id = window.location.pathname.split('/')[3];
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var selected_language = $('#admin-languages-toggle').val()
        //clog($(toolbox).find('.toolBoxContent').find('fieldset').attr('data-box-id',14));
        $.ajax({
            url: base_url + '/admin/pages/get-element-settings/',
            type: "POST",
            data: {
                page_id: page_id,
                box_id: box_id,
                csrfmiddlewaretoken: csrf_token,
                language_id: selected_language
            },
            async: false,
            success: function (result) {
                if (result.error) {
                    $("#admin-plugin-settings").find('.save-element-settings').attr('disabled', false);
                } else {
                    // Date selector for settings
                    $(toolbox).find(".plugin-setting-calendar").kendoDatePicker();
                    $(toolbox).find(".plugin-setting-time").kendoTimePicker();

                    var element_settings = result.element_settings;
                    //var message_setting = result.message_setting;

                    var message = result.message_setting;

                    //$(toolbox).find('.msg-settings').html(message_setting);
                    $(toolbox).find('.hidden-msg').html(message);
                    var data_submit_name = $.trim($('#box-' + box_id).attr('data-submit-name'));
                    if (data_submit_name != undefined && data_submit_name != '') {
                        $(toolbox).find('.plugin-setting-submit-button-name:visible').find('input').val(data_submit_name);
                    }
                    var data_pdf_button_name = $.trim($('#box-' + box_id).attr('data-pdf-button-name'));
                    if (data_pdf_button_name != undefined && data_pdf_button_name != '') {
                        $(toolbox).find('.plugin-setting-pdf-button-name:visible').find('input').val(data_pdf_button_name);
                    }
                    var data_photo_group_name = $.trim($('#box-' + box_id).attr('data-photo-group-name'));
                    var data_photo_group_id = $.trim($('#box-' + box_id).attr('data-photo-group-id'));
                    if (data_photo_group_name != undefined && data_photo_group_name != '') {
                        $(toolbox).find('.plugin-setting-photo-upload-group-name:visible').find('input').val(data_photo_group_name);
                        $(toolbox).find('.plugin-setting-photo-upload-group-name:visible').find('input').attr('data-id', data_photo_group_id);
                    }
                    var preselect_session = [];
                    var columns_show = false;
                    var setting_attendee_list_visible_columns = {};
                    var custom_attendee_selected_columns = "";
                    var radio_preselect_session = '';
                    var checkbox_radio_preselect_session = '';
                    //var sort_columns_answers = '';
                    var attendee_owner_registration_groups = [];
                    var attendee_registration_groups = [];
                    var attendee_owner_registration_questions = "";
                    var attendee_registration_questions = "";
                    var session_checkbox_choose_min = "0";
                    var session_checkbox_choose_max = "0";
                    clog(element_settings);
                    if(plugin_name == 'submit-button'){
                        var sessionSelectList1 = $("#submit-button-auto-add-session-select-no-filter").kendoMultiSelect({
                            dataSource: {},
                            dataTextField: "text",
                            dataValueField: "id"
                        });
                        var sessionSelectListElse = $("#submit-button-auto-add-session-select-1").kendoMultiSelect({
                            dataSource: {},
                            dataTextField: "text",
                            dataValueField: "id"
                        });
                        var sessionSelectListElse = $("#submit-button-auto-add-session-select-last").kendoMultiSelect({
                            dataSource: {},
                            dataTextField: "text",
                            dataValueField: "id"
                        });
                    }
                    for (var i = 0; i < element_settings.length; i++) {
                        $(toolbox).find('.settings-given-answer').each(function () {
                            var setting_id = $(this).attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                if ($(this).attr('type') == 'checkbox') {
                                    var dialog_location_details_settings = ['session_scheduler_custom_location_settings', 'session_checkbox_custom_location_settings', 'session_radio_custom_location_settings', 'next_up_custom_location_settings', 'session_agenda_custom_location_settings'];
                                    var dialog_attendee_details_settings = ['session_scheduler_custom_attendee_settings', 'session_checkbox_custom_attendee_settings', 'session_radio_custom_attendee_settings', 'next_up_custom_attendee_settings', 'session_agenda_custom_attendee_settings'];
                                    var dialog_session_details_settings = ['session_checkbox_show_link_to_session_details'];
                                    var searchable_property_settings = ['session_agenda_searchable'];
                                    if (element_settings[i].answer == 'True') {
                                        $(this).prop('checked', true);
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_location_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-location-list-display').show();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_attendee_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-attendee-question-display').show();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, searchable_property_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-agenda-searchable-property').show();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_session_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-checkbox-session-detail-display').show();
                                        }
                                    } else {
                                        $(this).prop('checked', false);
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_location_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-location-list-display').hide();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_attendee_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-attendee-question-display').hide();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, searchable_property_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-session-agenda-searchable-property').hide();
                                        }
                                        if ($.inArray(element_settings[i].element_question.question_key, dialog_session_details_settings) != -1) {
                                            $(this).closest('#admin-plugin-settings').find('.plugin-settings-session-checkbox-session-detail-display').hide();
                                        }
                                    }
                                } else {
                                    $(this).val(element_settings[i].answer);
                                    if(element_settings[i].element_question.question_key == 'multiple_registration_form'){
                                        if(element_settings[i].answer == 'loop'){
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-multiple-registration-question-display').show();
                                        }else{
                                            $(this).closest('#admin-plugin-settings').find('.plugin-setting-multiple-registration-question-display').hide();
                                        }
                                    }
                                }
                            }
                        });
                        $('fieldset').find('.settings-submit-button-redirect:visible').each(function () {
                            var setting_id = $(this).attr('data-setting-id');
                            var $elem = $(this).closest('.settings-submit-button');
                            if (element_settings[i].answer.includes('"state":') && setting_id == element_settings[i].element_question.id) {
                                var submit_btn_setting = JSON.parse(element_settings[i].answer);
                                switch (submit_btn_setting[0].state) {
                                    case 1:
                                        clog('1');
                                        $elem.find('.plugin-setting-submit-button-select-page').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-button-custom-value').hide();
                                        break;
                                    case 2:
                                        clog('2');
                                        $(this).val('redirect-to-page');
                                        $elem.find('.plugin-setting-submit-button-select-page').css('display', 'block');
                                        $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-button-select-page select:visible').val(submit_btn_setting[0].data["page_id"]);
                                        $elem.find('.plugin-setting-submit-button-custom-value').show();
                                        break;
                                    case 3:
                                        clog('3');
                                        $(this).val('prerequisite-redirect');
                                        $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'block');
                                        $elem.find('.plugin-setting-submit-button-select-page').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-button-custom-value').show();
                                        var prerequisiteArray = submit_btn_setting[0].data;
                                        var ul = $elem.find('.plugin-setting-submit-button-create-prerequisite:visible ul');
                                        for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                            if (ii == 0) {
                                                ul.find('li:first select:first').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:first select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:first select:last').val(prerequisiteArray[ii]["page_id"]);
                                            } else if (ii == (prerequisiteArray.length - 1)) {
                                                ul.find('li:last select').val(prerequisiteArray[ii]["page_id"]);
                                            } else {
                                                var nestedli = ul.find('li:first').clone();
                                                nestedli.insertBefore(ul.find('li:last'));

                                                ul.find('li:nth-child(' + (ii + 1) + ') select:first').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') select:last').val(prerequisiteArray[ii]["page_id"]);
                                            }
                                        }
                                        break;
                                }
                            }
                        });

                        $('fieldset').find('.settings-submit-button-confirmation:visible').each(function () {
                            var setting_id = $(this).attr('data-setting-id');
                            var $elem = $(this).closest('.settings-submit-button');
                            if (element_settings[i].answer.includes('"state":') && setting_id == element_settings[i].element_question.id) {
                                var submit_btn_setting = JSON.parse(element_settings[i].answer);
                                switch (submit_btn_setting[0].state) {
                                    case 1:
                                        clog('1');
                                        $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'none');
                                        break;
                                    case 2:
                                        clog('2');
                                        $(this).val('send-confirmation');
                                        $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'block');
                                        $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'none');
                                        $elem.find('.plugin-setting-submit-confirmation-select-confirmation select:visible').val(submit_btn_setting[0].data["email_id"]);
                                        break;
                                    case 3:
                                        clog('3');
                                        $(this).val('prerequisite-confirmation');
                                        $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'block');
                                        $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'none');

                                        // previous submit button may not have new settings data, that's why we kept previous code.
                                        if (submit_btn_setting[0].data['attendee'] == undefined) {
                                            var prerequisiteArray = submit_btn_setting[0].data;
                                            var ul = $elem.find('.plugin-setting-submit-confirmation-create-prerequisite:visible ul');
                                            for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                                if (ii == 0) {
                                                    ul.find('li[data-setting-for="attendee"]:first select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="attendee"]:first select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="attendee"]:first select:last').val(prerequisiteArray[ii]["email_id"]);
                                                } else if (ii == (prerequisiteArray.length - 1)) {
                                                    ul.find('li[data-setting-for="attendee"]:last select').val(prerequisiteArray[ii]["email_id"]);
                                                } else {
                                                    var nestedli = ul.find('li[data-setting-for="attendee"]:first').clone();
                                                    nestedli.insertBefore(ul.find('li[data-setting-for="attendee"]:last'));

                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:last').val(prerequisiteArray[ii]["email_id"]);
                                                }
                                            }
                                        } else {
                                            var ul = $elem.find('.plugin-setting-submit-confirmation-create-prerequisite:visible ul');
                                            var prerequisiteArray = submit_btn_setting[0].data['attendee'];
                                            for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                                if (ii == 0) {
                                                    ul.find('li[data-setting-for="attendee"]:first select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="attendee"]:first select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="attendee"]:first select:last').val(prerequisiteArray[ii]["email_id"]);
                                                } else if (ii == (prerequisiteArray.length - 1)) {
                                                    ul.find('li[data-setting-for="attendee"]:last select').val(prerequisiteArray[ii]["email_id"]);
                                                } else {
                                                    var nestedli = ul.find('li[data-setting-for="attendee"]:first').clone();
                                                    nestedli.insertBefore(ul.find('li[data-setting-for="attendee"]:last'));

                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="attendee"]:nth-child(' + (ii + 1) + ') select:last').val(prerequisiteArray[ii]["email_id"]);
                                                }
                                            }
                                            prerequisiteArray = submit_btn_setting[0].data['owner'];
                                            for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                                if (ii == 0) {
                                                    ul.find('li[data-setting-for="owner"]:first select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="owner"]:first select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="owner"]:first select:last').val(prerequisiteArray[ii]["email_id"]);
                                                } else if (ii == (prerequisiteArray.length - 1)) {
                                                    ul.find('li[data-setting-for="owner"]:last select').val(prerequisiteArray[ii]["email_id"]);
                                                } else {
                                                    var nestedli = ul.find('li[data-setting-for="owner"]:first').clone();
                                                    nestedli.insertBefore(ul.find('li[data-setting-for="owner"]:last'));

                                                    ul.find('li[data-setting-for="owner"]:nth-child(' + (ii + 1) + ') select:first').val(prerequisiteArray[ii]["match"]);
                                                    ul.find('li[data-setting-for="owner"]:nth-child(' + (ii + 1) + ') select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                    ul.find('li[data-setting-for="owner"]:nth-child(' + (ii + 1) + ') select:last').val(prerequisiteArray[ii]["email_id"]);
                                                }
                                            }


                                        }
                                        break;
                                }
                            }
                        });
                        
                        $('fieldset').find('.settings-submit-button-auto-add-session:visible').each(function () {
                            var setting_id = $(this).attr('data-setting-id');
                            var $elem = $(this).closest('.settings-submit-button');
                            if (element_settings[i].answer.includes('"state":') && setting_id == element_settings[i].element_question.id) {
                                var submit_btn_setting = JSON.parse(element_settings[i].answer);
                                console.log(submit_btn_setting)
                                switch (submit_btn_setting[0].state) {
                                    case 1:
                                        clog('1');
                                        $elem.find('.plugin-setting-submit-button-select-session').hide();
                                        $elem.find('.plugin-setting-submit-button-create-session-prerequisite').hide();
                                        $elem.find('.plugin-setting-submit-button-remove-conflict-session').hide();
                                        break;
                                    case 2:
                                        clog('2');
                                        $(this).val('add-session');
                                        $elem.find('.plugin-setting-submit-button-select-session').show();
                                        $elem.find('.plugin-setting-submit-button-remove-conflict-session').show();
                                        $elem.find('.plugin-setting-submit-button-create-session-prerequisite').hide();
                                        $elem.find('.plugin-setting-submit-button-select-session #submit-button-auto-add-session-select-no-filter').data("kendoMultiSelect").value(submit_btn_setting[0].data["session_id"]);
                                        break;
                                    case 3:
                                        clog('3');
                                        $(this).val('prerequisite-session');
                                        $elem.find('.plugin-setting-submit-button-create-session-prerequisite').show();
                                        $elem.find('.plugin-setting-submit-button-remove-conflict-session').show();
                                        $elem.find('.plugin-setting-submit-button-select-session').hide();
                                        var prerequisiteArray = submit_btn_setting[0].data;
                                        var ul = $elem.find('.plugin-setting-submit-button-create-session-prerequisite:visible>ul');
                                        for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                            if (ii == 0) {
                                                ul.find('li:first select:first').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:first select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:first #submit-button-auto-add-session-select-1').data("kendoMultiSelect").value(prerequisiteArray[ii]["session_id"]);
                                            } else if (ii == (prerequisiteArray.length - 1)) {
                                                ul.find('li:last #submit-button-auto-add-session-select-last').data("kendoMultiSelect").value(prerequisiteArray[ii]["session_id"]);
                                            } else {
                                                // var nestedli = ul.find('li:first').clone();
                                                // nestedli.insertBefore(ul.find('li:last'));

                                                var li_length = ul.children('li').length;
                                                var nestedli = $('.auto-add-session-prerequisite-list li').clone();
                                                nestedli.find('.submit-button-prerequisite-go').attr('id','submit-button-auto-add-session-select-'+li_length);
                                                var sessionsList = nestedli.find("#submit-button-auto-add-session-select-"+li_length).kendoMultiSelect({
                                                    dataSource: {},
                                                    dataTextField: "text",
                                                    dataValueField: "id"
                                                });
                                                nestedli.insertBefore(ul.children('li:last'));

                                                ul.find('li:nth-child(' + (ii + 1) + ') select:first').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') select:nth-child(2)').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') #submit-button-auto-add-session-select-'+li_length).data("kendoMultiSelect").value(prerequisiteArray[ii]["session_id"]);
                                            }
                                        }
                                        break;
                                }
                            }
                        });

                        $('fieldset').find('.settings-rebate-apply-prerequisite:visible').each(function () {
                            var setting_id = $(this).attr('data-setting-id');
                            var $elem = $(this).closest('.settings-rebate');
                            if (element_settings[i].answer.includes('"state":') && setting_id == element_settings[i].element_question.id) {
                                var submit_btn_setting = JSON.parse(element_settings[i].answer);
                                switch (submit_btn_setting[0].state) {
                                    case 1:
                                        clog('1');
                                        $(this).val('apply-filter-prerequisite');
                                        $elem.find('.plugin-setting-rebate-create-filter-prerequisite').css('display', 'block');
                                        $elem.find('.plugin-setting-rebate-create-date-prerequisite').css('display', 'none');
                                        var prerequisiteArray = submit_btn_setting[0].data;
                                        var ul = $elem.find('.plugin-setting-rebate-create-filter-prerequisite:visible ul');
                                        for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                            if (ii == 0) {
                                                ul.find('li:first .rebate-filter-prerequisite-match').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:first .rebate-prerequisite-filter').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:first select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            } else if (ii == (prerequisiteArray.length - 1)) {
                                                ul.find('li:last select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            } else {
                                                var nestedli = ul.find('li:first').clone();
                                                nestedli.insertBefore(ul.find('li:last'));

                                                ul.find('li:nth-child(' + (ii + 1) + ') .rebate-filter-prerequisite-match').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') .rebate-prerequisite-filter').val(prerequisiteArray[ii]["filter_id"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            }
                                        }
                                        break;
                                    case 2:
                                        clog('2');
                                        $(this).val('apply-date-prerequisite');
                                        $elem.find('.plugin-setting-rebate-create-date-prerequisite').css('display', 'block');
                                        $elem.find('.plugin-setting-rebate-create-filter-prerequisite').css('display', 'none');
                                        var prerequisiteArray = submit_btn_setting[0].data;
                                        var ul = $elem.find('.plugin-setting-rebate-create-date-prerequisite:visible ul');
                                        for (var ii = 0; ii < prerequisiteArray.length; ii++) {
                                            if (ii == 0) {
                                                ul.find('li:first .rebate-date-prerequisite-match').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:first .rebate-apply-from').val(prerequisiteArray[ii]["from"]);
                                                ul.find('li:first .rebate-apply-to').val(prerequisiteArray[ii]["to"]);
                                                ul.find('li:first select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            } else if (ii == (prerequisiteArray.length - 1)) {
                                                ul.find('li:last select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            } else {
                                                var nestedli = ul.find('li:first').clone();
                                                nestedli.insertBefore(ul.find('li:last'));

                                                ul.find('li:nth-child(' + (ii + 1) + ') .rebate-filter-prerequisite-match').val(prerequisiteArray[ii]["match"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') .rebate-apply-from').val(prerequisiteArray[ii]["from"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') .rebate-apply-to').val(prerequisiteArray[ii]["to"]);
                                                ul.find('li:nth-child(' + (ii + 1) + ') select.rebate-prerequisite-apply').val(prerequisiteArray[ii]["rebate_id"]);
                                            }
                                        }
                                        break;
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
                        $(toolbox).find('.settings-given-searchable-property:visible').each(function () {
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
                        $(toolbox).find('#settings-session-checkbox-preselected-select').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                var sessions = JSON.parse(element_settings[i].answer);
                                for (var s = 0; s < sessions.length; s++) {
                                    preselect_session.push({id: sessions[s]});
                                }
                            }
                        });
                        $(toolbox).find('.settings-session-radio-button-preselected').find('select').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                radio_preselect_session = element_settings[i].answer;
                            }
                        });
                        $(toolbox).find('.settings-session-checkbox-radio-preselected').find('select').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                checkbox_radio_preselect_session = element_settings[i].answer;
                            }
                        });

                        $(toolbox).find('#settings-attendee-list-visible-columns').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            clog(element_settings[i].element_question.id);
                            if (setting_id == element_settings[i].element_question.id) {
                                columns_show = true;
                                setting_attendee_list_visible_columns = result.question_groups;
                            }
                        });

                        $(toolbox).find('.plugin-setting-session-attendee-question-display').each(function () {
                            var $this = $(this);
                            var setting_id = $(this).find('ul:first').attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                custom_attendee_selected_columns = element_settings[i].answer;
                            }
                        });

                        // set owners group for multiple registration

                        $(toolbox).find('#settings-multiple-registration-group-to-use-owner').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                var groups = JSON.parse(element_settings[i].answer);
                                for (var s = 0; s < groups.length; s++) {
                                    attendee_owner_registration_groups.push({value: groups[s]});
                                }
                            }
                        });

                        // set attendee group for multiple registration

                        $(toolbox).find('#settings-multiple-registration-group-to-use-attendee').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                var groups = JSON.parse(element_settings[i].answer);
                                for (var s = 0; s < groups.length; s++) {
                                    attendee_registration_groups.push({value: groups[s]});
                                }
                            }
                        });

                        // set attendee table question for multiple registration

                        $(toolbox).find('.plugin-setting-multiple-registration-question-display').each(function () {
                            var $this = $(this);
                            var setting_id = $(this).find('ul:first').attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                attendee_owner_registration_questions = element_settings[i].answer;
                            }
                        });

                        // set inherit question for multiple registration

                        $(toolbox).find('.plugin-setting-multiple-registration-inherit-question-display').each(function () {
                            var $this = $(this);
                            var setting_id = $(this).find('ul:first').attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                attendee_registration_questions = element_settings[i].answer;
                            }
                        });
                        $(toolbox).find('#settings-session-checkbox-choose-min').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                session_checkbox_choose_min = element_settings[i].answer;
                            }
                        });
                        $(toolbox).find('#settings-session-checkbox-choose-max').each(function () {
                            var $this = $(this);
                            var setting_id = $this.attr('data-setting-id');
                            if (setting_id == element_settings[i].element_question.id) {
                                session_checkbox_choose_max = element_settings[i].answer;
                            }
                        });

                    }

                    if ($('.plugin-setting-hotel-reservation-hotel-groups:visible').length > 0) {
                        var $hrp_elem = $('.plugin-setting-hotel-reservation-hotel-groups:visible').closest('.settings-hotel-reservation');
                        var hotel_groups = ['do-not-force'];
                        $hrp_elem.find('.plugin-setting-hotel-reservation-hotel-groups').find('input:checkbox:checked').each(function () {
                            hotel_groups.push($(this).attr('data-group-id'));
                        });
                        $hrp_elem.find('.plugin-setting-hotel-reservation-force-hotel-room').find('.settings-given-answer').find('option').each(function () {
                            if ($.inArray($(this).attr('data-group'), hotel_groups) == -1) {
                                $(this).hide();
                            }
                        });
                    }

                    if (plugin_name == 'session-checkbox') {
                        if($(toolbox).find('#settings-session-checkbox-act-like-radio-button').is(":checked")){
                            $(toolbox).find('.settings-session-checkbox-session-must-choose').show();
                            $(toolbox).find('.settings-session-checkbox-remove-conflict-session').show();
                            $(toolbox).find('.settings-session-checkbox-radio-preselected').show();
                            $(toolbox).find('.settings-session-checkbox-preselected').hide();
                            $(toolbox).find('.settings-session-checkbox-choose-min').hide();
                            $(toolbox).find('.settings-session-checkbox-choose-max').hide();
                        }else {
                            $(toolbox).find('.settings-session-checkbox-session-must-choose').hide();
                            $(toolbox).find('.settings-session-checkbox-remove-conflict-session').hide();
                            $(toolbox).find('.settings-session-checkbox-radio-preselected').hide();
                            $(toolbox).find('.settings-session-checkbox-preselected').show();
                            $(toolbox).find('.settings-session-checkbox-choose-min').show();
                            $(toolbox).find('.settings-session-checkbox-choose-max').show();
                        }
                        var sessionsList = $("#settings-session-checkbox-preselected-select").kendoMultiSelect({
                            dataSource: {},
                            dataTextField: "text",
                            dataValueField: "id"
                        });
                        getCheckboxSessionsPreselected(preselect_session, checkbox_radio_preselect_session, session_checkbox_choose_min, session_checkbox_choose_max);
                        attendee_treeview = $('#admin-plugin-settings').find(".session-settings-attendee-list-visible-columns").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: JSON.parse($('#question-tree').val())
                        }).data("kendoTreeView");
                        if (custom_attendee_selected_columns != "") {
                            select_custom_attendee_colomns(custom_attendee_selected_columns);
                        }
                    }

                    if (plugin_name == 'session-radio-button') {
                        getRadioSessionsPreselected(radio_preselect_session);
                        attendee_treeview = $('#admin-plugin-settings').find(".session-settings-attendee-list-visible-columns").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: JSON.parse($('#question-tree').val())
                        }).data("kendoTreeView");
                        if (custom_attendee_selected_columns != "") {
                            select_custom_attendee_colomns(custom_attendee_selected_columns);
                        }
                    }
                    if (plugin_name == 'session-scheduler' || plugin_name == 'session-agenda') {
                        attendee_treeview = $('#admin-plugin-settings').find(".session-settings-attendee-list-visible-columns").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: JSON.parse($('#question-tree').val())
                        }).data("kendoTreeView");
                        if (custom_attendee_selected_columns != "") {
                            select_custom_attendee_colomns(custom_attendee_selected_columns);
                        }
                    }
                    if (plugin_name == 'next-up') {
                        clog("ok----");
                        attendee_treeview = $('#admin-plugin-settings').find(".session-settings-attendee-list-visible-columns").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: JSON.parse($('#question-tree').val())
                        }).data("kendoTreeView");
                        if (custom_attendee_selected_columns != "") {
                            select_custom_attendee_colomns(custom_attendee_selected_columns);
                        }
                    }

                    if (plugin_name == 'multiple-registration') {
                        clog(plugin_name);
                        var all_questions_display = JSON.parse($('#question-tree').val());
                        attendee_treeview = $('#admin-plugin-settings').find("#setting-multiple-registration-question").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: all_questions_display
                        }).data("kendoTreeView");
                        if (attendee_owner_registration_questions != "") {
                            select_custom_attendee_colomns(attendee_owner_registration_questions);
                        }
                        for (var g = 0; g < all_questions_display.length; g++) {
                            var mylist = [];
                            for (var q = 0; q < all_questions_display[g].items.length; q++) {
                                if (all_questions_display[g].items[q].is_default != 1) {
                                    mylist.push(all_questions_display[g].items[q]);
                                }
                            }
                            all_questions_display[g].items = mylist;
                        }

                        attendee_inherit_treeview = $('#admin-plugin-settings').find("#setting-multiple-registration-inherit-question").kendoTreeView({
                            checkboxes: {
                                checkChildren: true
                            },
                            dataSource: all_questions_display
                        }).data("kendoTreeView");
                        if (attendee_registration_questions != "") {
                            select_custom_attendee_inherit_colomns(attendee_registration_questions);
                        }

                        var registration_group_to_use_owner = $('#admin-plugin-settings').find("#settings-multiple-registration-group-to-use-owner").kendoMultiSelect({
                            select: onSelectKendoCustomOwner
                        }).data("kendoMultiSelect");
                        $(document).on("registration_group_to_use_owner", function (event) {
                            registration_group_to_use_owner.value([]);
                        });
                        if (attendee_owner_registration_groups.length > 0) {
                            registration_group_to_use_owner.value(attendee_owner_registration_groups);
                        }
                        var registration_group_to_use_attendee = $('#admin-plugin-settings').find("#settings-multiple-registration-group-to-use-attendee").kendoMultiSelect({
                            select: onSelectKendoCustomAttendee
                        }).data("kendoMultiSelect");

                        $(document).on("registration_group_to_use_attendee", function (event) {
                            registration_group_to_use_attendee.value([]);
                        });
                        if (attendee_registration_groups.length > 0) {
                            registration_group_to_use_attendee.value(attendee_registration_groups);
                        }

                    }

                    if (plugin_name == 'attendee-list') {
                        if (columns_show) {
                            attendeeListVisibleColumn(JSON.parse(setting_attendee_list_visible_columns));
                        } else {
                            attendeeListVisibleColumn(JSON.parse($('#question-tree').val()));
                        }
                    }
                    if (plugin_name == 'rebate') {
                        $("#admin-plugin-settings").find(".plugin-setting-rebate-calendar").kendoDatePicker();
                        $(".rebate-apply-prerequisite").trigger("change");
                        $("#admin-plugin-settings").find(".rebate-prerequisite-apply").kendoMultiSelect({
                            dataSource: {
                                transport: {
                                    read: {
                                        url: base_url + '/admin/pages/get-all-rebates/',
                                        dataType: "json"
                                    }
                                },
                                schema: {
                                    data: function (data) { //specify the array that contains the data
                                        return data.results;
                                    }
                                }
                            },
                            animation: false,
                            dataTextField: "text",
                            dataValueField: "id"
                        });
                    }
                    $("#admin-plugin-settings").find('.save-element-settings').attr('disabled', false);
                }
            }
        });
    }

    function onSelectKendoCustomOwner(e) {
        $(document).trigger("registration_group_to_use_owner");
    };
    function onSelectKendoCustomAttendee(e) {
        $(document).trigger("registration_group_to_use_attendee");
    };

    function select_custom_attendee_colomns(custom_attendee_selected_columns) {
        if (custom_attendee_selected_columns.length > 0) {
            var all_attendee_columns = JSON.parse($('#question-tree').val());
            var selected_node, expand_flag = true;
            attendee_treeview.expand(".k-item");
            for (var i = 0; i < all_attendee_columns.length; i++) {
                for (var j = 0; j < all_attendee_columns[i].items.length; j++) {
                    if (custom_attendee_selected_columns.indexOf(all_attendee_columns[i].items[j].data_id) > 0) {
                        selected_node = attendee_treeview.findByText(all_attendee_columns[i].items[j].text);
                        attendee_treeview.dataItem(selected_node).set("checked", true);
                        expand_flag = false;
                    }
                }
            }
            if (expand_flag) {
                attendee_treeview.collapse(".k-item");
            }
        }
    }

    function select_custom_attendee_inherit_colomns(custom_attendee_selected_columns) {
        if (custom_attendee_selected_columns.length > 0) {
            var all_attendee_columns = JSON.parse($('#question-tree').val());
            var selected_node, expand_flag = true;
            attendee_inherit_treeview.expand(".k-item");
            for (var i = 0; i < all_attendee_columns.length; i++) {
                for (var j = 0; j < all_attendee_columns[i].items.length; j++) {
                    if (custom_attendee_selected_columns.indexOf(all_attendee_columns[i].items[j].data_id) > 0) {
                        selected_node = attendee_inherit_treeview.findByText(all_attendee_columns[i].items[j].text);
                        attendee_inherit_treeview.dataItem(selected_node).set("checked", true);
                        expand_flag = false;
                    }
                }
            }
            if (expand_flag) {
                attendee_inherit_treeview.collapse(".k-item");
            }
        }
    }

    function setting_alv(datasource) {
        var settings_alvc_selected_sorted = []
        var settings_group_alvc = {}
        var settings_question_alvc = {}
        for (var key in datasource) {
            settings_group_alvc[datasource[key]['gp_data_id']] = {
                index: parseInt(key),
                checked: datasource[key]['checked'] !== undefined ? datasource[key]['checked'] : false
            }

            for (var key2 in datasource[key]['items']) {
                settings_question_alvc[datasource[key]['items'][key2]['data_id']] = {
                    index: parseInt(key2),
                    checked: datasource[key]['items'][key2]['checked'] !== undefined ? datasource[key]['items'][key2]['checked'] : false
                }
                if (datasource[key]['items'][key2]['checked'] !== undefined && datasource[key]['items'][key2]['checked'] == true) {
                    settings_alvc_selected_sorted.push(datasource[key]['items'][key2]['data_id'])
                }
            }
        }
        return {
            group: settings_group_alvc,
            question: settings_question_alvc,
            selected_sorted: settings_alvc_selected_sorted
        };
    }


    function attendeeListVisibleColumn(questions) {
        var inlineDefault = new kendo.data.HierarchicalDataSource({
            sort: {field: "index", dir: "asc"},
            data: questions
        });
        var treeAsc = $("#settings-attendee-list-visible-columns").kendoTreeView({
                checkboxes: {
                    checkChildren: true
                },
                loadOnDemand: false,
                dataSource: inlineDefault,
                dragAndDrop: true,
                drag: function (e) {
                    if (e.statusClass == "denied") {
                        return;
                    } else if (e.statusClass == "add") {
                        e.setStatusClass("k-denied");
                    } else {
                        var sourceNode = this.dataItem(e.sourceNode);
                        var destination = this.dataItem(e.dropTarget);
                        if (sourceNode.level() == 1 && destination.level() == 0) {
                            e.setStatusClass("k-denied");
                        } else if (sourceNode.level() == 0 && destination.level() == 1) {
                            e.setStatusClass("k-denied");
                        } else if (sourceNode.level() != 0 || destination.level() != 0) {
                            var targetsRoot = $(e.dropTarget).parentsUntil(".k-treeview", ".k-item").length == 1;
                            if (targetsRoot && e.statusClass != "add") {
                                e.setStatusClass("k-denied");
                            }
                            if (this.dataItem(this.parent(e.sourceNode)) != undefined) {
                            }
                            if (this.dataItem(this.parent(e.sourceNode)) != undefined && this.dataItem(this.parent(e.sourceNode)) != undefined) {
                                if (this.dataItem(this.parent(e.sourceNode)).gp_data_id == undefined || this.dataItem(this.parent(e.dropTarget)).gp_data_id == undefined) {
                                    e.setStatusClass("k-denied");
                                } else {
                                    if (this.dataItem(this.parent(e.sourceNode)).gp_data_id != this.dataItem(this.parent(e.dropTarget)).gp_data_id) {
                                        e.setStatusClass("k-denied");
                                    }

                                }

                            }
                        }

                    }
                }
            }
        ).getKendoTreeView();
    }

// Set plugin settings

    $('body').on('click', '.save-element-settings', function () {
        var page_id = window.location.pathname.split('/')[3];
        var box_id = $(this).closest('fieldset').attr('data-box-id');
        var element_settings = [];
        var $this = $(this);
        $this.attr('disabled', true);
        $('.loader').show();
        $this.closest('fieldset').find('.settings-given-answer').each(function () {
            var tag_type = $(this).prop('tagName');
            if (tag_type == 'SELECT') {
                var setting_id = $(this).attr('data-setting-id');
                var setting_answer = $(this).val();
                if ($.trim(setting_answer) != undefined && setting_id != undefined) {
                    var setting_data = {
                        'setting_id': setting_id,
                        'setting_answer': setting_answer,
                        'type': 'setting'
                    };
                    //if(setting_id == 253){
                    //    setting_data['setting_answer'] = JSON.stringify(setting_answer);
                    //}
                    element_settings.push(setting_data);
                }
            } else {
                var setting_type = $(this).attr('type');
                if (setting_type == 'checkbox') {
                    var setting_id = $(this).attr('data-setting-id');
                    var setting_answer = $(this).prop('checked');
                    if ($.trim(setting_answer) != '' && $.trim(setting_answer) != null && $.trim(setting_answer) != undefined && setting_id != undefined) {
                        var setting_data = {
                            'setting_id': setting_id,
                            'setting_answer': setting_answer,
                            'type': 'setting'
                        };
                        element_settings.push(setting_data);
                    }
                } else {
                    var setting_id = $(this).attr('data-setting-id');
                    var setting_answer = $(this).val();
                    if ($.trim(setting_answer) != undefined && setting_id != undefined) {
                        var setting_data = {
                            'setting_id': setting_id,
                            'setting_answer': setting_answer,
                            'type': 'setting'
                        };
                        element_settings.push(setting_data);
                    }
                }
            }
        });
        var session_checkbox_preselected_elem = $this.closest('fieldset').find("#settings-session-checkbox-preselected-select");
        if (session_checkbox_preselected_elem.length > 0) {
            var session_checkbox_preselected = session_checkbox_preselected_elem.data("kendoMultiSelect").dataItems();
            var setting_id = session_checkbox_preselected_elem.attr('data-setting-id');
            var preselect_session = [];
            for (var preselect = 0; preselect < session_checkbox_preselected.length; preselect++) {
                preselect_session.push(session_checkbox_preselected[preselect].id);
            }
            //if (preselect_session.length > 0) {
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(preselect_session),
                'type': 'setting'
            };
            element_settings.push(setting_data);
            //}
        }

        $this.closest('fieldset').find('.settings-submit-button-redirect').each(function () {
            var setting_id = $(this).attr('data-setting-id');
            var setting_submit_answer = $(this).val();
            if ($.trim(setting_submit_answer) != undefined) {
                var redirect_array = [];
                if (setting_submit_answer == '') {
                    var redirect_data = {
                        'state': 1,
                        'data': ''
                    };
                    redirect_array.push(redirect_data);
                } else if (setting_submit_answer == 'redirect-to-page') {
                    var redirect_data = {
                        'state': 2,
                        'data': {'page_id': $('.plugin-setting-submit-button-select-page select').val()}
                    };
                    redirect_array.push(redirect_data);
                } else if (setting_submit_answer == 'prerequisite-redirect') {
                    var $elem = $this.parent().find('.plugin-setting-submit-button-create-prerequisite').find('.prerequisite li');
                    var elem_total = $elem.length;
                    var redirect_data = {
                        'state': 3,
                        'data': []
                    };
                    $elem.each(function (i) {
                        var $li = $(this);
                        if (i === (elem_total - 1)) {
                            var page_id = $li.find('.submit-button-prerequisite-go').val();
                            redirect_data['data'].push({'page_id': page_id});
                        } else {
                            var match = $li.find('.submit-button-prerequisite-match').val();
                            var filter_id = $li.find('.submit-button-prerequisite-filter').val();
                            var page_id = $li.find('.submit-button-prerequisite-go').val();
                            redirect_data['data'].push({'match': match, 'filter_id': filter_id, 'page_id': page_id});
                        }
                    });
                    redirect_array.push(redirect_data);
                }
                var setting_data = {
                    'setting_id': setting_id,
                    'setting_answer': JSON.stringify(redirect_array),
                    'type': 'setting'
                };
                element_settings.push(setting_data);
            }
        });

        $this.closest('fieldset').find('.settings-submit-button-auto-add-session').each(function () {
            var $autoAddSessionElem = $(this);
            var setting_id = $(this).attr('data-setting-id');
            var setting_submit_answer = $(this).val();
            if ($.trim(setting_submit_answer) != undefined) {
                var add_session_settings_array = [];
                if (setting_submit_answer == '') {
                    var session_data = {
                        'state': 1,
                        'data': ''
                    };
                    add_session_settings_array.push(session_data);
                } else if (setting_submit_answer == 'add-session') {
                    var selected_sessions = $autoAddSessionElem.closest('.settings-submit-button').find("#submit-button-auto-add-session-select-no-filter").data("kendoMultiSelect").value();
                    var selected_session_ids = [];
                    if(selected_sessions != undefined && selected_sessions != '' && selected_sessions != null){
                        selected_session_ids = selected_sessions;
                    }
                    var session_data = {
                        'state': 2,
                        'data': {'session_id': selected_session_ids}
                    };
                    add_session_settings_array.push(session_data);
                } else if (setting_submit_answer == 'prerequisite-session') {
                    var $elem = $this.parent().find('.plugin-setting-submit-button-create-session-prerequisite').find('.prerequisite>li');
                    var elem_total = $elem.length;
                    var session_data = {
                        'state': 3,
                        'data': []
                    };
                    $elem.each(function (i) {
                        var $li = $(this);
                        if (i === (elem_total - 1)) {
                            var selected_sessions = $li.find("#submit-button-auto-add-session-select-last").data("kendoMultiSelect").value();
                            var selected_session_ids = [];
                            if(selected_sessions != undefined && selected_sessions != '' && selected_sessions != null){
                                selected_session_ids = selected_sessions;
                            }
                            session_data['data'].push({'session_id': selected_session_ids});
                        } else {
                            var li_index = i+1;
                            var match = $li.find('.submit-button-prerequisite-match').val();
                            var filter_id = $li.find('.submit-button-prerequisite-filter').val();
                            var session_id = $li.find('.submit-button-prerequisite-go').val();
                            var selected_sessions = $li.find("#submit-button-auto-add-session-select-"+li_index).data("kendoMultiSelect").value();
                            var selected_session_ids = [];
                            if(selected_sessions != undefined && selected_sessions != '' && selected_sessions != null){
                                selected_session_ids = selected_sessions;
                            }
                            session_data['data'].push({'match': match, 'filter_id': filter_id, 'session_id': selected_session_ids});
                        }
                    });
                    add_session_settings_array.push(session_data);
                }
                var setting_data = {
                    'setting_id': setting_id,
                    'setting_answer': JSON.stringify(add_session_settings_array),
                    'type': 'setting'
                };
                console.log(setting_data);
                element_settings.push(setting_data);
            }
        });

        $this.closest('fieldset').find('.settings-rebate-apply-prerequisite').each(function () {
            var setting_id = $(this).attr('data-setting-id');
            var setting_submit_answer = $(this).val();
            if ($.trim(setting_submit_answer) != undefined) {
                var rebate_prequisite_array = [];
                if (setting_submit_answer == 'apply-filter-prerequisite') {
                    var $elem = $this.parent().find('.plugin-setting-rebate-create-filter-prerequisite').find('.prerequisite').find('.prerequisite-li');
                    var elem_total = $elem.length;
                    var rebate_prequisite_data = {
                        'state': 1,
                        'data': []
                    };
                    $elem.each(function (i) {
                        var $li = $(this);
                        var rebate_id = $li.find('select.rebate-prerequisite-apply').val();
                        if (rebate_id == null || rebate_id == undefined || rebate_id == "") {
                            rebate_id = [];
                        }
                        if (i === (elem_total - 1)) {
                            rebate_prequisite_data['data'].push({'rebate_id': rebate_id});
                        } else {
                            var match = $li.find('.rebate-filter-prerequisite-match').val();
                            var filter_id = $li.find('.rebate-prerequisite-filter').val();
                            rebate_prequisite_data['data'].push({
                                'match': match,
                                'filter_id': filter_id,
                                'rebate_id': rebate_id
                            });
                        }
                    });
                    rebate_prequisite_array.push(rebate_prequisite_data);
                }
                else if (setting_submit_answer == 'apply-date-prerequisite') {
                    var $elem = $this.parent().find('.plugin-setting-rebate-create-date-prerequisite').find('.prerequisite').find('.prerequisite-li');
                    var elem_total = $elem.length;
                    var rebate_prequisite_data = {
                        'state': 2,
                        'data': []
                    };
                    $elem.each(function (i) {
                        var $li = $(this);
                        var rebate_id = $li.find('select.rebate-prerequisite-apply').val();
                        if (rebate_id == null || rebate_id == undefined || rebate_id == "") {
                            rebate_id = [];
                        }
                        if (i === (elem_total - 1)) {
                            rebate_prequisite_data['data'].push({'rebate_id': rebate_id});
                        } else {
                            var match = $li.find('.rebate-date-prerequisite-match').val();
                            var from_date = $li.find('input.rebate-apply-from').val();
                            var to_date = $li.find('input.rebate-apply-to').val();
                            rebate_prequisite_data['data'].push({
                                'match': match,
                                'from': from_date,
                                'to': to_date,
                                'rebate_id': rebate_id
                            });
                        }
                    });
                    rebate_prequisite_array.push(rebate_prequisite_data);
                }
                var setting_data = {
                    'setting_id': setting_id,
                    'setting_answer': JSON.stringify(rebate_prequisite_array),
                    'type': 'setting'
                };
                element_settings.push(setting_data);
            }
        });

        $this.closest('fieldset').find('.settings-submit-button-confirmation').each(function () {
            var setting_id = $(this).attr('data-setting-id');
            var setting_submit_answer = $(this).val();
            if ($.trim(setting_submit_answer) != undefined) {
                var confirmation_array = [];
                if (setting_submit_answer == '') {
                    var confirmation_data = {
                        'state': 1,
                        'data': ''
                    };
                    confirmation_array.push(confirmation_data);
                } else if (setting_submit_answer == 'send-confirmation') {
                    var confirmation_data = {
                        'state': 2,
                        'data': {'email_id': $('.plugin-setting-submit-confirmation-select-confirmation select').val()}
                    };
                    confirmation_array.push(confirmation_data);
                } else if (setting_submit_answer == 'prerequisite-confirmation') {
                    var $elem = $this.parent().find('.plugin-setting-submit-confirmation-create-prerequisite').find('.prerequisite li');
                    var elem_total = $elem.length;
                    var confirmation_data = {
                        'state': 3,
                        'data': {
                            'attendee': [],
                            'owner': []
                        }
                    };
                    $elem.each(function (i) {
                        var $li = $(this);
                        if (i === (elem_total - 1)) {
                            var email_id = $li.find('.submit-button-prerequisite-go').val();
                            confirmation_data['data'][$li.attr('data-setting-for')].push({'email_id': email_id});
                        } else {
                            var match = $li.find('.submit-button-prerequisite-match').val();
                            var filter_id = $li.find('.submit-button-prerequisite-filter').val();
                            var email_id = $li.find('.submit-button-prerequisite-go').val();
                            confirmation_data['data'][$li.attr('data-setting-for')].push({
                                'match': match,
                                'filter_id': filter_id,
                                'email_id': email_id
                            });
                        }
                    });
                    confirmation_array.push(confirmation_data);
                }
                var setting_data = {
                    'setting_id': setting_id,
                    'setting_answer': JSON.stringify(confirmation_array),
                    'type': 'setting'
                };
                element_settings.push(setting_data);
            }
        });

        $this.closest('fieldset').find('.plugin-setting-session-attendee-question-display').each(function () {
            var setting_id = $(this).find('ul:first').attr('data-setting-id');
            var selected_questions = attendee_treeview.getCheckedItems();
            var selected_questions_id = [];
            for (var i = 0; i < selected_questions.length; i++) {
                if (selected_questions[i].data_id != undefined) {
                    selected_questions_id.push(selected_questions[i].data_id);
                }
            }
            var setting_answer = '{"question":[{"id":"' + selected_questions_id.join(',') + '"}]}';
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(setting_answer),
                'type': 'setting'
            };
            element_settings.push(setting_data);
        });

        var message_setting_id = $this.closest('fieldset').find('.msg-settings').attr('data-setting-id');
        $this.closest('fieldset').find('.msg-settings').find("#msg-save").trigger("click");
        var message_setting_answer = $this.closest('fieldset').find('.hidden-msg').html();
        var language_id = $("#admin-languages-toggle").val();
        if ($.trim(message_setting_answer) != '' && $.trim(message_setting_answer) != null && $.trim(message_setting_answer) != undefined) {
            // console.log(message_setting_answer);
            // message_setting_answer = message_setting_answer.replaceAll('"', "'");
            // console.log(message_setting_answer);
            var message_setting_data = {
                'setting_id': message_setting_id,
                'setting_answer': message_setting_answer,
                'type': 'message'
            }
            element_settings.push(message_setting_data);
        }

        var groups = []
        $this.closest('fieldset').find('.settings-given-groups').find('input').each(function () {
            var group_id = $(this).attr('data-group-id');
            if ($(this).prop('checked')) {
                groups.push(group_id);
            }
        });

        // if (groups.length > 0) {

        var group_setting_id = $this.closest('fieldset').find('.settings-given-groups').attr('data-setting-id');
        if (group_setting_id != undefined) {
            var group_setting_answer = JSON.stringify(groups);
            var setting_group_data = {
                'setting_id': group_setting_id,
                'setting_answer': group_setting_answer,
                'type': 'setting'
            }
            element_settings.push(setting_group_data);
            // }
        }
        $this.closest('fieldset').find('#settings-attendee-list-visible-columns').each(function () {
            var setting_id = $(this).attr('data-setting-id');
            var setting_alv_data = setting_alv(JSON.parse(JSON.stringify($("#settings-attendee-list-visible-columns").data("kendoTreeView").dataSource._data)));
            clog(setting_alv_data);
            var setting_group_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(setting_alv_data),
                'type': 'setting'
            }
            element_settings.push(setting_group_data);
        });

        $this.closest('fieldset').find('.settings-given-searchable-property:visible').each(function () {
            var seachable_property = [];
            var $thidSearch = $(this);
            $thidSearch.find('input[type="checkbox"]').each(function () {
                if ($(this).prop('checked')) {
                    var property_name = $(this).attr('data-group-id');
                    seachable_property.push(property_name);
                }
            });
            var setting_id = $thidSearch.attr('data-setting-id');
            var setting_data = JSON.stringify(seachable_property);
            var setting_search_data = {
                'setting_id': setting_id,
                'setting_answer': setting_data,
                'type': 'setting'
            };
            element_settings.push(setting_search_data);
        });

        // get owner group for Multiple registration

        var order_owner_group_elem = $this.closest('fieldset').find("#settings-multiple-registration-group-to-use-owner");
        if (order_owner_group_elem.length > 0) {
            var order_owner_group = order_owner_group_elem.data("kendoMultiSelect").dataItems();
            var setting_id = order_owner_group_elem.attr('data-setting-id');
            var owner_groups = [];
            for (var group = 0; group < order_owner_group.length; group++) {
                owner_groups.push(order_owner_group[group].value);
            }
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(owner_groups),
                'type': 'setting'
            };
            element_settings.push(setting_data);
        }

        // get attendee group for Multiple registration

        var attendee_group_elem = $this.closest('fieldset').find("#settings-multiple-registration-group-to-use-attendee");
        if (attendee_group_elem.length > 0) {
            var attendee_group = attendee_group_elem.data("kendoMultiSelect").dataItems();
            var setting_id = attendee_group_elem.attr('data-setting-id');
            var attendee_groups = [];
            for (var group = 0; group < attendee_group.length; group++) {
                attendee_groups.push(attendee_group[group].value);
            }
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(attendee_groups),
                'type': 'setting'
            };
            element_settings.push(setting_data);
        }

        // get attendee table visible question for Multiple registration

        $this.closest('fieldset').find('.plugin-setting-multiple-registration-question-display:visible').each(function () {
            var setting_id = $(this).find('ul:first').attr('data-setting-id');
            var selected_questions = attendee_treeview.getCheckedItems();
            var selected_questions_id = [];
            for (var i = 0; i < selected_questions.length; i++) {
                if (selected_questions[i].data_id != undefined) {
                    selected_questions_id.push(selected_questions[i].data_id);
                }
            }
            var setting_answer = '{"question":[{"id":"' + selected_questions_id.join(',') + '"}]}';
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(setting_answer),
                'type': 'setting'
            };
            element_settings.push(setting_data);
        });

        // get inherit question for Multiple registration

        $this.closest('fieldset').find('.plugin-setting-multiple-registration-inherit-question-display').each(function () {
            var setting_id = $(this).find('ul:first').attr('data-setting-id');
            var selected_questions = attendee_inherit_treeview.getCheckedItems();
            var selected_questions_id = [];
            for (var i = 0; i < selected_questions.length; i++) {
                if (selected_questions[i].data_id != undefined) {
                    selected_questions_id.push(selected_questions[i].data_id);
                }
            }
            var setting_answer = '{"question":[{"id":"' + selected_questions_id.join(',') + '"}]}';
            var setting_data = {
                'setting_id': setting_id,
                'setting_answer': JSON.stringify(setting_answer),
                'type': 'setting'
            };
            element_settings.push(setting_data);
        });


        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();

        var data = {
            page_id: page_id,
            box_id: box_id,
            element_settings: JSON.stringify(element_settings),
            'language_id': language_id,
            csrfmiddlewaretoken: csrf_token
        };
        $this.closest('fieldset').find('.plugin-setting-photo-upload-group-name').each(function () {
            var photo_group_name = $(this).find('input').val();
            var photo_group_id = $(this).find('input').attr('data-id');
            if (dataNotEmpty(photo_group_name)) {
                data['photo_group_name'] = $.trim(photo_group_name);
                data['photo_group_id'] = $.trim(photo_group_id);
            }
        });
        clog(element_settings);
        $.ajax({
            url: base_url + '/admin/pages/set-element-settings/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    //$.growl.error({message: result.message});
                    clog(result.message)
                } else {
                    //$.growl.notice({message: result.message});
                    clog(result.message)
                    $this.closest('#admin-plugin-settings').removeClass('visible');
                    var element_settings = result.element_settings;
                    var element_title_settings = result.element_title_settings;
                    clog(element_settings);
                    showPluginUsingSettings(element_settings, element_title_settings);
                    saveOrUpdate();
                }
                $this.attr('disabled', false);
                $('.loader').hide();
            }
        });
    });
    String.prototype.replaceAll = function (target, replacement) {
        return this.split(target).join(replacement);
    };


// Plugin Submit button Redirect

    $('body').on('change', '.submit-button-redirect', function () {
        var selected_value = $.trim($(this).val());
        var $elem = $(this).closest('.settings-submit-button');
        if (selected_value == 'redirect-to-page') {
            $elem.find('.plugin-setting-submit-button-select-page').css('display', 'block');
            $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'none');
            $elem.find('.plugin-setting-submit-button-custom-value').show();
        } else if (selected_value == 'prerequisite-redirect') {
            $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'block');
            $elem.find('.plugin-setting-submit-button-select-page').css('display', 'none');
            $elem.find('.plugin-setting-submit-button-custom-value').show();
        } else {
            $elem.find('.plugin-setting-submit-button-select-page').css('display', 'none');
            $elem.find('.plugin-setting-submit-button-create-prerequisite').css('display', 'none');
            $elem.find('.plugin-setting-submit-button-custom-value').hide();
        }
    });

// Plugin Submit button Confirmation

    $('body').on('change', '.submit-button-confirmation', function () {
        var selected_value = $.trim($(this).val());
        var $elem = $(this).closest('.settings-submit-button');
        if (selected_value == 'send-confirmation') {
            $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'block');
            $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'none');
        } else if (selected_value == 'prerequisite-confirmation') {
            $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'block');
            $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'none');
        } else {
            $elem.find('.plugin-setting-submit-confirmation-select-confirmation').css('display', 'none');
            $elem.find('.plugin-setting-submit-confirmation-create-prerequisite').css('display', 'none');
        }
    })

    // Plugin Submit button Auto add session

    $('body').on('change', '.submit-button-auto-add-session', function () {
        var selected_value = $.trim($(this).val());
        var $elem = $(this).closest('.settings-submit-button');
        if (selected_value == 'add-session') {
            $elem.find('.plugin-setting-submit-button-select-session').show();
            $elem.find('.plugin-setting-submit-button-remove-conflict-session').show();
            $elem.find('.plugin-setting-submit-button-create-session-prerequisite').hide();
        } else if (selected_value == 'prerequisite-session') {
            $elem.find('.plugin-setting-submit-button-create-session-prerequisite').show();
            $elem.find('.plugin-setting-submit-button-remove-conflict-session').show();
            $elem.find('.plugin-setting-submit-button-select-session').hide();
        } else {
            $elem.find('.plugin-setting-submit-button-select-session').hide();
            $elem.find('.plugin-setting-submit-button-create-session-prerequisite').hide();
            $elem.find('.plugin-setting-submit-button-remove-conflict-session').hide();
        }
    });

// Plugin Rebate Prerequisite Apply

    $('body').on('change', '.rebate-apply-prerequisite', function () {
        var selected_value = $.trim($(this).val());
        var $elem = $(this).closest('.settings-rebate');
        if (selected_value == 'apply-filter-prerequisite') {
            $elem.find('.plugin-setting-rebate-create-filter-prerequisite').css('display', 'block');
            $elem.find('.plugin-setting-rebate-create-date-prerequisite').css('display', 'none');
        } else if (selected_value == 'apply-date-prerequisite') {
            $elem.find('.plugin-setting-rebate-create-date-prerequisite').css('display', 'block');
            $elem.find('.plugin-setting-rebate-create-filter-prerequisite').css('display', 'none');
        }
    });

    $(document).on('click', '.rebate-filter-prequisite', function () {
        var $this = $(this);
        var prerequisite_type = "filter";
        addRebatePrerequisite($this, prerequisite_type);
    });

    $(document).on('click', '.rebate-date-prequisite', function () {
        var $this = $(this);
        var prerequisite_type = "date";
        addRebatePrerequisite($this, prerequisite_type);
    });

    $(document).on('click', '.delete-rebate-prerequisite', function () {
        $(this).closest('li.prerequisite-li').remove();
    });

    function addRebatePrerequisite($this, prerequisite_type) {
        var ul = $this.next(".prerequisite");
        var li = $('.clone-' + prerequisite_type + '-prerequisite').clone();
        li.removeClass('clone-' + prerequisite_type + '-prerequisite');
        li.find(".plugin-setting-rebate-calendar").kendoDatePicker();
        li.find(".rebate-prerequisite-apply").kendoMultiSelect({
            dataSource: {
                transport: {
                    read: {
                        url: base_url + '/admin/pages/get-all-rebates/',
                        dataType: "json"
                    }
                },
                schema: {
                    data: function (data) { //specify the array that contains the data
                        return data.results;
                    }
                }
            },
            animation: false,
            dataTextField: "text",
            dataValueField: "id"
        });
        li.find(".rebate-prerequisite-apply").val("");
        li.insertBefore(ul.find('li.prerequisite-li:last'));
    }

// Plugin Rebate Prerequisite End


// add prerequisite

    $(document).on('click', '.submit-button-prequisite', function () {
        var ul = $(this).next(".prerequisite");
        var li = ul.find('li:first').clone();
        li.insertBefore(ul.find('li:last'));
    });
    
    $(document).on('click', '.submit-button-prequisite-session', function () {
        var ul = $(this).next(".prerequisite");
        var li_length = ul.children('li').length;
        var li = $('.auto-add-session-prerequisite-list li').clone();
        li.find('.submit-button-prerequisite-go').attr('id','submit-button-auto-add-session-select-'+li_length);
        var sessionsList = li.find("#submit-button-auto-add-session-select-"+li_length).kendoMultiSelect({
            dataSource: {},
            dataTextField: "text",
            dataValueField: "id"
        });
        li.insertBefore(ul.children('li:last'));
    });

    $(document).on('click', '.delete-submit-button-prerequisite', function () {
        $(this).closest('li').remove();
    });


// Custom class

    $(document).on('click', '.element > .admin-cms-toolbox > .settings', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        var box_id = $(this).closest('.box').attr('id').split('-')[1];
        $(".admin-menu").removeClass("visible");
        $('#admin-element-settings').addClass("visible");
        $('#admin-element-settings').find('fieldset').attr('data-box-id', box_id);
        getCustomClassesAndFilter(box_id);
    });

    $(document).on('click', '.col > .admin-cms-toolbox > .settings', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        var box_id = $(this).closest('.box').attr('id').split('-')[1];
        $(".admin-menu").removeClass("visible");
        $('#admin-element-settings').addClass("visible");
        $('#admin-element-settings').find('fieldset').attr('data-box-id', box_id);
        getCustomClassesAndFilter(box_id);
    });

    $(document).on('click', '.row > .admin-cms-toolbox > .settings', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        var box_id = $(this).closest('.box').attr('id').split('-')[1];
        $(".admin-menu").removeClass("visible");
        $('#admin-element-settings').addClass("visible");
        $('#admin-element-settings').find('fieldset').attr('data-box-id', box_id);
        getCustomClassesAndFilter(box_id);
    });

    $(document).on('click', '.section > .admin-cms-toolbox > .settings', function () {
        if ($('#admin-editor.visible').length > 0) {
            saveEditorHtml();
        }
        var box_id = $(this).closest('.box').attr('id').split('-')[1];
        $(".admin-menu").removeClass("visible");
        $('#admin-element-settings').addClass("visible");
        $('#admin-element-settings').find('fieldset').attr('data-box-id', box_id);
        getCustomClassesAndFilter(box_id);
    });


    function getCustomClassesAndFilter(box_id) {
        var page_id = window.location.pathname.split('/')[3];
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var multiselect = $("#admin-element-settings-classes").data("kendoMultiSelect");
        multiselect.dataSource.read();
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

                } else {

                    $("#clear-filter").remove();
                    var class_list = result.class_list;
                    var classList = [];
                    for (var i = 0; i < class_list.length; i++) {
                        classList.push({id: class_list[i].classname.id, text: class_list[i].classname.classname});
                    }
                    var filterTree = $('#add-filter-treeview').data('kendoTreeView');
                    $("#add-filter-treeview")
                        .find(".k-state-selected")
                        .each(
                            function () {
                                var e = filterTree.dataItem(this);
                                e.set("selected", !1);
                                delete e.selected;
                            });
                    $("#add-filter-treeview")
                        .find(".k-state-hover")
                        .each(
                            function () {
                                var e = filterTree.dataItem(this);
                                e.set("selected", !1);
                                delete e.selected;
                            });
                    var items = $("#add-filter-treeview .k-item");
                    var found_box = false;
                    $.map(filter_list, function (elementOfArray, indexInArray) {
                        if (elementOfArray.box_id == "box-" + box_id) {
                            $(items).each(function () {
                                    if (filterTree.dataItem(this).data_id == elementOfArray.filter_id) {
                                        if (elementOfArray.action) {
                                            var action = elementOfArray.action;
                                            $('#admin-element-settings:visible').find('.filter-action').val(action);
                                        }
                                        var filter_uid = filterTree.dataItem(this).uid;
                                        if ($(this).attr('data-uid') == filter_uid) {
                                            $(this).find(".k-in").addClass('k-state-selected');
                                            if (!($(this).find(".k-in").parent().find('#clear-filter').length > 0)) {
                                                $(this).find(".k-in").parent().append('<span id="clear-filter" title="Clear Filter" style="color:#fff;cursor: pointer;font-weight: bold;padding-left: 6px;"><i class="fa fa-times-circle" aria-hidden="true"></i></span>');
                                            }
                                        }
                                    }
                                }
                            );
                        }
                    });
                    clog(classList)
                    var set_custom_class = $('#admin-element-settings').find('#admin-element-settings-classes').data("kendoMultiSelect")
                    set_custom_class.value(classList);
                    set_custom_class.trigger("change");
                }
            }
        })
        ;
    }

    $(document).on('click', '#clear-filter', function () {
        var $this = $(this);
        var filterTree = $('#add-filter-treeview').data('kendoTreeView');
        $("#add-filter-treeview")
            .find(".k-state-selected")
            .each(function () {
                var box_id = $(this).closest('fieldset').attr('data-box-id');
                var e = filterTree.dataItem(this);
                $(this).removeClass("k-state-focused");
                e.set("selected", !1);
                delete e.selected;
                $.map(filter_list, function (elementOfArray, indexInArray) {
                    if (elementOfArray.box_id == "box-" + box_id) {
                        filter_list.splice(indexInArray, 1);
                    }
                });
            });
        $this.remove();

    });

    kendo.ui.TreeView.prototype.getCheckedItems = (function () {
        function getCheckedItems() {
            var nodes = this.dataSource.view();
            return getCheckedNodes(nodes);
        }

        function getCheckedNodes(nodes) {
            var node, childCheckedNodes;
            var checkedNodes = [];

            for (var i = 0; i < nodes.length; i++) {
                node = nodes[i];
                if (node.checked) {
                    checkedNodes.push(node);
                }

                // to understand recursion, first
                // you must understand recursion
                if (node.hasChildren) {
                    childCheckedNodes = getCheckedNodes(node.children.view());
                    if (childCheckedNodes.length > 0) {
                        checkedNodes = checkedNodes.concat(childCheckedNodes);
                    }
                }

            }

            return checkedNodes;
        }

        return getCheckedItems;
    })();


    $('body').on('click', '.settings-session-custom-attendee input[type=checkbox]', function (e) {
        if (this.checked) {
            $('.plugin-setting-session-attendee-question-display').show();
        } else {
            $('.plugin-setting-session-attendee-question-display').hide();
        }

    });

    // Show or Hide Attendee question column settings of Multiple registration loop

    $('body').on('change', '.settings-multiple-registration-display-form select', function (e) {
        var value = $(this).val();
        if (value == 'loop') {
            $('.plugin-setting-multiple-registration-question-display').show();
        } else {
            $('.plugin-setting-multiple-registration-question-display').hide();
        }

    });

    //$(document).on('chenge','.settings-multiple-registration-default-attendee input',function(){
    //    var default_attendee = $(this).val();
    //    var min_attendee = $(this).closest('.settings-multiple-registration').find('.settings-multiple-registration-min-attendee input').val();
    //    if(default_attendee < min_attendee){
    //        $(this).closest('.settings-multiple-registration').find('.settings-multiple-registration-min-attendee input').val(default_attendee);
    //    }
    //
    //});

})
;


////////////////////////
// ADMIN JSCRIPT CODE //
////////////////////////

// TOOL TIP - Session Scheduler - Session
$(document).ready(function () {
    var tooltip = $(".session-section").kendoTooltip({
        filter: ".session-section-item",
        position: "top"
    }).data("kendoTooltip");

    // TOOL TIP - Session Scheduler - Session

    var tooltip = $(".event-plugin-next-up").kendoTooltip({
        filter: "tr",
        position: "top"
    }).data("kendoTooltip");

});

// SCROLLABLE ADMIN MENU

function dataNotEmpty(data) {
    var data = $.trim(data);
    if (data != '' && data != undefined && data != null) {
        return true;
    } else {
        return false;
    }
}

$(document).ready(function () {

});
