var filter_list = [];
var delete_title = "Delete";
var settings_title = "Class and Filter Settings";
var plugin_settings_title = "Plugin Settings";
var move_title = "Move";
var edit_title = "Edit Content";
var element_plugin_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "<li class='btn-plugin-setting'><i class='fa fa-cogs' aria-hidden='true' title='" + plugin_settings_title + "'></i></li>" +
    "<li class='move move-element'><i class='fa fa-arrows' aria-hidden='true' title='" + move_title + "'></i></li>" +
    "</ul>";
var element_question_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "<li class='move move-element'><i class='fa fa-arrows' aria-hidden='true' title='" + move_title + "'></i></li>" +
    "</ul>";
var element_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "<li class='edit'><i class='fa fa-pencil' aria-hidden='true' title='" + edit_title + "'></i></li>" +
    "<li class='move move-element'><i class='fa fa-arrows' aria-hidden='true' title='" + move_title + "'></i></li>" +
    "</ul>";
var col_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "</ul>";
var row_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "<li class='move move-row'><i class='fa fa-arrows' aria-hidden='true' title='" + move_title + "'></i></li>" +
    "</ul>";
var section_toolbox = "<ul class='admin-cms-toolbox' style='display: none;'>" +
    "<li class='delete'><i class='fa fa-trash' aria-hidden='true' title='" + delete_title + "'></i></li>" +
    "<li class='settings'><i class='fa fa-cog' aria-hidden='true' title='" + settings_title + "'></i></li>" +
    "<li class='move move-section'><i class='fa fa-arrows' aria-hidden='true' title='" + move_title + "'></i></li>" +
    "</ul>";
var file_upload_path;
var noOfFiles, fileCounter = 0;
var selectedNode;
var cms_temporary_classes = [];
var $body = $('body');
var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
$(function () {
    onLoadCmsJs();
    if ($('#fliter-data').val() != '' && $('#fliter-data').val() != null && $('#fliter-data').val() != undefined && $('#fliter-data').val() != "None") {
        var filter_data = jQuery.parseJSON($('#fliter-data').val());
        filter_list = filter_data;
    }

    var msg_editor;

    $body.on('click', '.msg-edit', function () {
        var message_content = toMarkdown($(this).siblings('.hidden-msg').html());
        //clog(message_content);
        $(this).prev('.msg-settings').html($('#elements-setting-message').html())
        $(this).css('display', 'none');
        msg_editor = CodeMirror.fromTextArea(document.getElementById('elements-setting-msg'), {
            mode: 'gfm',
            lineNumbers: false,
            matchBrackets: true,
            lineWrapping: true,
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
        //clog(msg_editor.getValue());
        $(this).closest('.msg-settings').next('.msg-edit').css('display', 'inline-block');
        //$(this).closest('.msg-settings').html($(this).next('#out_msg').html());
        $(this).closest('.msg-settings').siblings('.hidden-msg').html($(this).next('#out_msg').html());
        $(this).closest('.msg-settings').html("");
        //clog($(this).next('#out_msg').html());
    });

    $body.on('click', '#add-class-and-rule', function () {
        //var box_classes_data = $(this).closest('#admin-element-settings').find('#admin-element-settings-classes').select2('data');
        var box_classes_data = $(this).closest('#admin-element-settings').find("#admin-element-settings-classes").data("kendoMultiSelect").dataItems();
        var box_classes = [];
        var box_text = [];
        for (var i = 0; i < box_classes_data.length; i++) {
            if (box_classes_data[i].id != undefined && box_classes_data[i].id != '') {
                box_classes.push({id: String(box_classes_data[i].id), text: box_classes_data[i].text});
            } else {
                box_classes.push({text: box_classes_data[i].text});
            }
            box_text.push(box_classes_data[i].text);
        }
        var page_id = window.location.pathname.split('/')[3];
        var box_id = $(this).closest('fieldset').attr('data-box-id');

        var filterTreeView = $('#add-filter-treeview').data('kendoTreeView'),
            selected = filterTreeView.select(),
            filter_item = filterTreeView.dataItem(selected);
        var filter_id = '';
        clog(filter_item);
        if (filter_item) {
            if (filter_item.spriteCssClass == "filter") {
                filter_id = filter_item.data_id;
            }
        }
        clog(filter_id);
        if (filter_id != '') {
            var filter_box = "box-" + box_id;
            var action = $(this).closest("fieldset").find('.filter-action').val();
            clog("action : " + action);
            var added = false;
            $.map(filter_list, function (elementOfArray, indexInArray) {
                if (elementOfArray.box_id == filter_box) {
                    filter_list[indexInArray].action = action;
                    elementOfArray.filter_id = filter_id;
                    added = true;
                }
            });
            if (!added) {
                filter_list.push({
                    'box_id': filter_box,
                    'filter_id': filter_id,
                    'action': action
                });
            }
        }
        var data = {
            page_id: page_id,
            box_id: box_id,
            filter_list: JSON.stringify(filter_list),
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
                    //$.growl.error({message: result.message});
                } else {
                    //$.growl.notice({message: result.message});
                    if (result.page.filter != '') {
                        filter_list = jQuery.parseJSON(result.page.filter);
                    }
                    for (var k = 0; k < box_classes_data.length; k++) {
                        if (!$("#content_data").find("#box-" + box_id).hasClass(box_classes_data[k].text)) {
                            cms_temporary_classes.push({box_id: 'box-' + box_id, text: box_classes_data[k].text});
                        }
                    }
                    for (var j = 0; j < box_text.length; j++) {
                        $("#content_data").find("#box-" + box_id).addClass(box_text[j]);
                    }
                    $this.closest('#admin-element-settings').removeClass('visible');
                    saveOrUpdate();
                }
            }
        });
    });

    // Delete Files

    $body.on("click", "#admin-admin-file-repository-delete-selected-files", function () {
        //get reference to the TreeView widget
        var treeview = $("#admin-file-repository-treeview").data("kendoTreeView");
        //get the checked items
        var items = $("#admin-file-repository-treeview .k-item input[type=checkbox]:checked").closest(".k-item");
        //clog the text for each item
        var delete_files = []
        $(items).each(function () {

            var key = treeview.dataItem(this).path;
            var type = treeview.dataItem(this).spriteCssClass;
            if (type = "folder") {
                if (key.charAt(key.length - 1) != '/') {
                    key = key + "/";
                }
            }
            if (type != "rootfolder") {
                delete_files.push({"key": key, "type": type});
            }
        });
        clog(delete_files);
        if (delete_files.length > 0) {
            if (confirm("AAre you sure you want to delete these Files?")) {
                $.ajax({
                    url: base_url + '/admin/files/deletefolder/',
                    type: "POST",
                    data: {
                        delete_files: JSON.stringify(delete_files),
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (response) {
                        if (response.result) {

                            $(items).each(function () {
                                var data = treeview.dataItem(this);
                                if (data != undefined) {
                                    var item = treeview.findByUid(data.uid);
                                    treeview.remove(item);
                                }
                            });
                            //$.growl.notice({message: response.message});

                        }
                    }
                });
            }
        }
    });

    $body.on("click", "#admin-admin-file-repository-add-folder", function () {
        var folder_name = prompt("New Folder", "");
        var selectedNode;
        if ($.trim(folder_name) != null && $.trim(folder_name) != '') {
            var file = $('#admin-file-repository-treeview').data('kendoTreeView'),
                selected = file.select(),
                item = file.dataItem(selected);
            selectedNode = selected;
            var folder_path = '';
            if (item) {
                if (item.spriteCssClass == 'folder' || item.spriteCssClass == 'rootfolder') {
                    folder_path = item.path;
                } else {
                    alert("pls select a folder");
                }

            } else {
                var items = $("#admin-file-repository-treeview .k-item");
                $(items).each(function () {
                    if (file.dataItem(this).spriteCssClass == 'rootfolder') {
                        var root = file.findByUid(file.dataItem(this).uid)
                        selectedNode = root;
                        folder_path = file.dataItem(this).path;
                    }
                });
            }
            if (folder_path != '') {
                $.ajax({
                    url: base_url + '/admin/files/newfolder/',
                    type: "POST",
                    data: {
                        name: folder_name,
                        key: folder_path,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (response) {
                        if (response.result) {
                            //$.growl.notice({message: response.message});
                            clog(selectedNode);
                            var filetree = $('#admin-file-repository-treeview').data('kendoTreeView');
                            filetree.append(
                                {
                                    text: response.folderName,
                                    spriteCssClass: "folder",
                                    path: response.key
                                }, selectedNode
                            );

                        }
                    }
                });
            }
        }
    });

    $body.on("click", "#admin-admin-file-repository-upload-file", function () {
        var file = $('#admin-file-repository-treeview').data('kendoTreeView'),
            selected = file.select(),
            item = file.dataItem(selected);
        selectedNode = selected;
        if (item) {
            if (item.spriteCssClass == 'folder' || item.spriteCssClass == 'rootfolder') {
                file_upload_path = item.path;
                //$('.dialoge').addClass('visible');
                $('[data-remodal-id=upload-modal]').remodal().open();
            } else {
                alert("pls select a folder");
            }

        } else {
            var items = $("#admin-file-repository-treeview .k-item");
            $(items).each(function () {
                if (file.dataItem(this).spriteCssClass == 'rootfolder') {
                    var root = file.findByUid(file.dataItem(this).uid)
                    selectedNode = root;
                    file_upload_path = file.dataItem(this).path;
                    //$('.dialoge').addClass('visible');
                    $('[data-remodal-id=upload-modal]').remodal().open();
                }
            });
        }
    });
    $("#upload-files").kendoUpload({
        async: {
            saveUrl: base_url + '/admin/files/fileupload/',
            autoUpload: true
        },
        upload: function (e) {
            e.data = {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                key: file_upload_path
            }
        },
        select: function (e) {
            noOfFiles = e.files.length;
        },
        success: function (e) {
            if (e.response.success) {
                var filetree = $('#admin-file-repository-treeview').data('kendoTreeView');
                filetree.append(
                    {
                        text: e.response.file_name,
                        spriteCssClass: e.response.spriteCssClass,
                        path: e.response.key
                    }, selectedNode
                );
                $(".k-upload-files.k-reset").find("li").remove();
                //$('.dialoge').removeClass('visible');
                $('[data-remodal-id=upload-modal]').remodal().close();

                //if (fileCounter == noOfFiles) {
                //    $('#modal-upload').modal('hide');
                //    $.growl.notice({message: e.response.msg});
                //    fileCounter = 0;
                //    noOfFiles = 0;
                //}
            } else {
                //$.growl.error({message: e.response.msg});
                //$('.dialoge').removeClass('visible');
                $('[data-remodal-id=upload-modal]').remodal().close();
            }
        }


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

    $body.on("change", "#admin-languages-toggle", function () {
        var language_id = $(this).val();
        var page_id = window.location.pathname.split('/')[3];
        $('.loader').show();
        $.ajax({
            url: base_url + '/admin/get-page-with-language/',
            type: "POST",
            data: {
                language_id: language_id,
                page_id: page_id,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (result) {
                if (result.success) {
                    $('#hidden-content').html(result.content);
                    $('.menu').html(result.menu);
                    $('#element-settings-data').val(result.element_settings);
                    $('#page-class-list').val(result.class_list);
                    $('#all-plugins').html(result.all_plugins);
                    onLoadCmsJs();
                    $('.loader').hide();
                }
                $('.loader').hide();

            }
        });

    });


});

function onLoadCmsJs() {
    $body.find('#hidden-content').find('.form-plugin').each(function () {
        console.log('ok');
        var element_id = "elements-" + $(this).attr('data-name');
        var element_html = $('#' + element_id).find('.element').html();
        $(this).html(element_html);
    });
    var is_update = $('#hidden-content').attr('data-content');
    if (is_update == "update") {
        $('#hidden-content').find('.row').each(function () {
            var $row = $(this);
            $row.find('.col').each(function () {
                var $col = $(this);
                $col.find('.element').each(function () {
                    var $element = $(this);
                    var html = $element.html();
                    if ($element.hasClass("form-plugin")) {
                        $element.html(element_plugin_toolbox + html);
                    } else if ($element.hasClass("form-question")) {
                        $element.html(element_question_toolbox + html);
                    } else {
                        $element.html(element_toolbox + html);
                    }
                });
                $col.append(col_toolbox);

            });
            $row.append(row_toolbox);
        });
        $('#hidden-content').find('.section').each(function () {
            var $section = $(this);
            $section.append(section_toolbox);
        })
        $("#content_data").html($('#hidden-content').html());
        var element_settings = JSON.parse($("#element-settings-data").val());
        var element_title_settings = JSON.parse($("#element-settings-title-data").val());
        clog("element_settings");
        clog(element_settings);
        showPluginUsingSettings(element_settings, element_title_settings);
        //var question_ids = [];
        //var $questions = $('.formQuestion:visible');
        //$questions.each(function () {
        //    if (($(this).attr('type') === 'select') || ($(this).attr('type') === 'checkbox') || ($(this).attr('type') === 'radio_button')) {
        //        question_ids.push($(this).data('id'));
        //    }
        //});

        //$.ajax({
        //    url: base_url + '/admin/questions/all-options/',
        //    type: "POST",
        //    data: {
        //        question_ids: JSON.stringify(question_ids),
        //        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        //    },
        //    success: function (result) {
        //        if (result.error) {
        //            $.growl.error({message: result.message});
        //        } else {
        //            var all_questions = result.all_question_list;
        //            for (var i = 0; i < all_questions.length; i++) {
        //                dropdown_questions.push({
        //                    'question': all_questions[i].question,
        //                    'options': all_questions[i].options
        //                });
        //            }
        //        }
        //        clog(dropdown_questions);
        //    }
        //});
    }
    var page_classes = $('#page-class-list').val();
    page_classes = page_classes.replace(/'/g, '"');
    if (page_classes != "" && page_classes != "None") {
        var class_list = JSON.parse(page_classes);
        for (var c = 0; c < class_list.length; c++) {
            if (!$("#content_data").find("#box-" + class_list[c].box_id).hasClass(class_list[c].class_name)) {
                cms_temporary_classes.push({box_id: 'box-' + class_list[c].box_id, text: class_list[c].class_name});
            }
            $("#content_data").find('#box-' + class_list[c].box_id).addClass(class_list[c].class_name);
        }
    }


    //$('body').find('.module-element').each(function () {
    //    var element_id = "elements-" + $(this).attr('data-name');
    //    var element_html = $('#' + element_id).html();
    //    $(this).html(element_html);
    //});


    $("#content_data").find(".hotel-reservation-calendar").kendoDatePicker();

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

    $("#content_data").find(".hotel-room-buddy").kendoAutoComplete({
        dataSource: data,
        filter: "contains",
        minLength: 3,
        placeholder: "Select a room buddy",
        separator: ", " // Only for rooms with more than one bed
    });

    $("#content_data").find(".session-scheduler").kendoScheduler({
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
                        title: {from: "Title", defaultValue: "No title", validation: {required: true}},
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
}

function saveOrUpdate() {
    var element_filters = [];
    $('body').find('.form-plugin:visible').each(
        function () {
            var plugin_name = $.trim($(this).attr('data-name'));
            var box_id = $(this).attr('id');
            var element_id = $(this).attr('data-id');
            if (box_id != "" && element_id != "") {
                var element = {
                    'box_id': box_id,
                    'element_id': element_id
                };
                if (plugin_name == "submit-button") {
                    var button_id = $.trim($(this).attr('data-submit-id'));
                    element['button_id'] = button_id;
                } else if (plugin_name == "photo-upload") {
                    var photo_group_id = $.trim($(this).attr('data-photo-group-id'));
                    element['button_id'] = photo_group_id;
                }
                else if (plugin_name == "pdf-button") {
                    var pdf_button_id = $.trim($(this).attr('data-pdf-button-id'));
                    element['button_id'] = pdf_button_id;
                }
                element_filters.push(element);
            }
        }
    );
    var base_url = window.location.origin;
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var hiddenDiv = $('#hidden-content');
    var page_id = window.location.pathname.split('/')[3];
    hiddenDiv.html($("#content_data").html());
    hiddenDiv.find('.admin-cms-toolbox').remove();
    hiddenDiv.find('.section-box').each(function () {
        if ($(this).find('.row').length < 1) {
            $(this).remove();
        }
        if ($(this).hasClass('temporary')) {
            if ($(this).find('.element').length < 1) {
                $(this).remove();
            }
        }
    });
    hiddenDiv.find('.section.box').each(function () {
        var box_id = $(this).attr('id').split('-')[1];
        var section_content = $(this).html();
        var temp_class = ""
        if ($(this).hasClass("temporary")) {
            temp_class = "temporary"
        }
        $(this).replaceWith("{section:" + temp_class + ",box:" + box_id + "}" + section_content + "{end_div}");
    });
    hiddenDiv.find('.row.box').each(function () {
        var box_id = $(this).attr('id').split('-')[1];
        var row_content = $(this).html();
        $(this).replaceWith("{row:,box:" + box_id + "}" + row_content + "{end_div}");
    });
    hiddenDiv.find('.col.box').each(function () {
        var box_id = $(this).attr('id').split('-')[1];
        var col_content = $(this).html();
        var span_class = getSpanClass($(this).attr('class'))
        $(this).replaceWith("{col:" + span_class + ",box:" + box_id + "}" + col_content + "{end_div}");
    });
    hiddenDiv.find('.form-question.box').each(function () {
        var q_id = $(this).attr('data-id');
        var box_id = $(this).attr('id').split('-')[1];
        $(this).replaceWith("{questionid:" + q_id + ",box:" + box_id + "}");
    });
    hiddenDiv.find('.form-plugin.box').each(function () {
        var plugin_name = $.trim($(this).attr('data-name'));
        var box_id = $(this).attr('id').split('-')[1];
        var plugin_id = $(this).attr('id').split('-')[1];
        if (plugin_name == 'submit-button') {
            var button_id = $.trim($(this).attr('data-submit-id'));
            $(this).replaceWith("{element:" + plugin_name + ",box:" + box_id + ",button_id:" + button_id + "}");
        } else if (plugin_name == 'photo-upload') {
            var button_id = $.trim($(this).attr('data-photo-group-id'));
            $(this).replaceWith("{element:" + plugin_name + ",box:" + box_id + ",button_id:" + button_id + "}");
        } else if (plugin_name == 'pdf-button') {
            var button_id = $.trim($(this).attr('data-pdf-button-id'));
            $(this).replaceWith("{element:" + plugin_name + ",box:" + box_id + ",button_id:" + button_id + "}");
        } else {
            $(this).replaceWith("{element:" + plugin_name + ",box:" + box_id + "}");
        }
    });
    hiddenDiv.find('.form-editor.box').each(function () {
        var box_id = $(this).attr('id').split('-')[1];
        $(this).replaceWith("{editor:html,box:" + box_id + "}");
    });
    //hiddenDiv.find('.form-question').each(function () {
    //    $(this).html("{qid:" + $(this).attr('data-id') + "}");
    //});
    //hiddenDiv.find('.form-plugin').each(function () {
    //    var plugin_name = $(this).attr('data-name') + '-' + $(this).attr('id').split('-')[1];
    //    $(this).html("{element:" + plugin_name + "}");
    //});
    $.map(cms_temporary_classes, function (elementOfArray, indexInArray) {
        hiddenDiv.find('#' + elementOfArray.box_id).removeClass(elementOfArray.text);
    });
    //cms_temporary_classes = [];
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
                //$.growl.error({message: result.message});
            } else {
                if (result.page.filter != '') {
                    filter_list = jQuery.parseJSON(result.page.filter);
                }

//                    $.growl.notice({ message: result.message });
//                    setTimeout(function () {
//                        window.location.href = base_url + '/admin/pages/';
//                    }, 800);
            }
        }
    });
    clog(allHtml);


}

function showPluginUsingSettings(element_settings, element_title_settings) {
    for (var i = 0; i < element_settings.length; i++) {
        var $elem = $("#content_data").find("#box-" + element_settings[i].box_id).find(".plugin-" + element_settings[i].element_question.group_slug + "-" + element_settings[i].element_question.id);
        if (element_settings[i].element_question.id == 213) {
            console.log(element_settings[i].answer);
        }
        // Should be dynamic

        // var title_array = [69, 343];
        var title_array = [];
        // var message_array = [2, 5, 10, 20, 30, 48, 67, 72, 77, 80, 84, 146, 148, 149, 188, 200, 207, 209, 232, 237];
        var message_array = [];

        if ($.inArray(element_settings[i].element_question.id, title_array) != -1) {
            $elem.html(element_settings[i].answer);
        }
        if ($.inArray(element_settings[i].element_question.id, message_array) != -1) {
            $elem.html(element_settings[i].description);
        } else if (element_settings[i].answer == "True") {
            $elem.show();
            $elem.addClass('visible');
            if ($elem.parent().prop("tagName") == "SPAN") {
                $elem.parent().show();
                if ($elem.parent().parent().prop("tagName") == "TD") {
                    $elem.closest('tr').show();
                }
            }
            else if ($elem.parent().prop("tagName") == "TD") {
                $elem.closest('tr').show();
            }
            if (element_settings[i].element_question.question_key == 'attendee_logout_button') {
                $elem.parent().find('.plugin-automatic-log-out').hide();
                $elem.parent().find('.plugin-automatic-log-out').removeClass('visible');
            }
        }
        else if (element_settings[i].answer == "False" || element_settings[i].answer == "do-not-show") {
            $elem.hide();
            $elem.removeClass('visible');
            if (!$elem.hasClass('form-plugin-description')) {
                if ($elem.parent().prop("tagName") == "SPAN" && $.trim($elem.parent().children(".settings-plugin-element.visible").text()) == '') {
                    $elem.parent().hide();
                    if ($elem.parent().parent().prop("tagName") == "TD" && $.trim($elem.parent().parent().find(".settings-plugin-element.visible").text()) == '') {
                        $elem.closest('tr').hide();
                    }
                }
                else if ($elem.parent().prop("tagName") == "TD" && $.trim($elem.parent().find(".settings-plugin-element.visible").text()) == '') {
                    $elem.closest('tr').hide();
                }
            }
            if (element_settings[i].element_question.question_key == 'attendee_logout_button') {
                $elem.parent().find('.plugin-automatic-log-out').show();
                $elem.parent().find('.plugin-automatic-log-out').addClass('visible');
            }
        } else if (element_settings[i].answer == "loop") {
            $elem.parent().find('.loop-registration-form').show();
            $elem.parent().find('.inline-registration-form').hide();
        } else if (element_settings[i].answer == "inline") {
            $elem.parent().find('.inline-registration-form').show();
            $elem.parent().find('.loop-registration-form').hide();
        } else {
            $elem.show();
        }
        //else if (element_settings[i].element_question.question_key == "hotel_reservation_allow_partial_stays"){
        //    var $item = $("#content_data").find("#box-" + element_settings[i].box_id).find(".form-plugin-list").find(".form-plugin-item:first");
        //    $("#content_data").find("#box-" + element_settings[i].box_id).find(".form-plugin-list").find(".form-plugin-item").not('.form-plugin-item:first').remove();
        //    for(var item_stay = 1; item_stay<parseInt(element_settings[i].answer); item_stay++){
        //        $item.clone().appendTo($item.closest(".form-plugin-list"));
        //    }
        //}
    }
    for (var j = 0; j < element_title_settings.length; j++) {
        var $title_elem = $("#content_data").find("#box-" + element_title_settings[j].box_id).find(".plugin-" + element_title_settings[j].element_question.group_slug + "-" + element_title_settings[j].element_question.id);
        // Should be dynamic

        var title_array = [69, 343];


        if ($.inArray(element_title_settings[j].element_question.id, title_array) != -1) {
            $title_elem.html(element_title_settings[j].answer);
        }
    }
}

function removeFilterAndElement(box_id) {
    $.map(filter_list, function (elementOfArray, indexInArray) {
        if (elementOfArray.box_id == box_id) {
            filter_list.splice(indexInArray, 1);
        }
    });
}

function getSpanClass($classes) {
    var regex = /span-?\d*/g;
    var match = regex.exec($classes)
    var match_data = "";
    if (match.length > 0) {
        match_data = match[0];
    }
    return match_data;
}
function clog(message) {
    if (window.location.hostname != 'eventdobby.com') {
        console.log(message);
    }
}