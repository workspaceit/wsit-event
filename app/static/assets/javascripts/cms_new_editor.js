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
    // "<li class='edit'><i class='fa fa-pencil' aria-hidden='true' title='" + edit_title + "'></i></li>" +
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

    $body.on('click', '.msg-edit', function () {
        // var message_content = toMarkdown($(this).siblings('.hidden-msg').html());
        var message_content = $(this).siblings('.hidden-msg').html();
        //clog(message_content);
        $(this).prev('.msg-settings').html($('#elements-setting-message').html())
        $(this).css('display', 'none');
        var $msg_editor = $('#admin-plugin-settings').find('textarea#elements-setting-msg');
        // $msg_editor.froalaEditor('destroy');
        $msg_editor.froalaEditor({
            toolbarButtons: ['bold', 'italic', 'underline', 'insertHR', 'paragraphFormat', 'undo', 'redo', 'selectAll', 'html'],
            heightMax: 100,
            width: '200'
        });
        if ($msg_editor.froalaEditor('codeView.isActive')) {
            $msg_editor.froalaEditor('codeView.toggle');
        }
        $msg_editor.froalaEditor('html.set', message_content);
    });
    $body.on('click', '#msg-save', function () {
        //clog(msg_editor.getValue());
        $(this).closest('.msg-settings').next('.msg-edit').css('display', 'inline-block');
        //$(this).closest('.msg-settings').html($(this).next('#out_msg').html());
        // $(this).closest('.msg-settings').siblings('.hidden-msg').html($(this).next('#out_msg').html());
        $(this).closest('.msg-settings').siblings('.hidden-msg').html($('#admin-plugin-settings').find('textarea#elements-setting-msg').froalaEditor('html.get'));
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

    // var hashtomsg;
    //
    // function msgupdate(e) {
    //     if (e != undefined) {
    //         setOutputmsg(e.getValue());
    //     }
    //
    //     clearTimeout(hashto);
    //     hashtomsg = setTimeout(updateHashmsg, 1000);
    // }
    //
    // function setOutputmsg(val) {
    //     val = val.replace(/<equation>((.*?\n)*?.*?)<\/equation>/ig, function (a, b) {
    //         return '<img src="http://latex.codecogs.com/png.latex?' + encodeURIComponent(b) + '" />';
    //     });
    //
    //     var out = document.getElementById('out_msg');
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
    // function updateHashmsg() {
    // }
    //
    // if (window.location.hash) {
    //     var h = window.location.hash.replace(/^#/, '');
    //     if (h.slice(0, 5) == 'view:') {
    //         setOutputmsg(decodeURIComponent(escape(RawDeflate.inflate(atob(h.slice(5))))));
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
    //         msgupdate(msg_editor);
    //         if (msg_editor) {
    //             msg_editor.focus();
    //         }
    //     }
    // } else {
    //     msgupdate(msg_editor);
    //     if (msg_editor) {
    //         msg_editor.focus();
    //     }
    // }

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
                    $('#element-settings-title-data').val(result.element_title_settings);
                    $('#page-class-list').val(result.class_list);
                    $('#all-plugins').html(result.all_plugins);
                    onLoadCmsJs();
                    $('.loader').hide();
                }
                $('.loader').hide();

            }
        });

    });
    // $body.find('div.editor-inline-box').on('froalaEditor.buttons.refresh', function (e, editor) {
    //     getInlineEditorHtml($(this));
    //     saveOrUpdate();
    // });
    // $body.find('div.editor-inline-box').on('froalaEditor.contentChanged', function (e, editor) {
    //     console.log('ypyo');
    //     getInlineEditorHtml($(this));
    //     saveOrUpdate();
    // });
});

// function saveEditorHtml() {
//    
// }

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
                        $element.html(element_toolbox + "<div class='editor-inline-box'>" + html + "</div>");
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
    initInlineFroala();
    $body.find('div.editor-inline-box').off('froalaEditor.buttons.refresh');
    $body.find('div.editor-inline-box').off('froalaEditor.contentChanged');
    $body.find('div.editor-inline-box').on('froalaEditor.buttons.refresh', function (e, editor) {
        getInlineEditorHtml($(this));
        saveOrUpdate();
    });
    $body.find('div.editor-inline-box').on('froalaEditor.contentChanged', function (e, editor) {
        getInlineEditorHtml($(this));
        saveOrUpdate();
    });
}
function initInlineFroala($this_div) {
    // var event_styles = $('#editor_event_stylesheet').val();
    // var min_height = parseInt($('#editor_min_height').val());
    // var max_height = parseInt($('#editor_max_height').val());
    // var editor_editor_iframe_style = $('#editor_editor_iframe_style').val();
    // var editor_toolbar_inline_data = $('#editor_toolbar_inline').val();
    // var editor_toolbar_inline = false;
    // if(editor_toolbar_inline_data == '1'){
    //     editor_toolbar_inline = true;
    // }
    // if (min_height == NaN) {
    //     min_height = 200;
    // }
    // if (max_height == NaN) {
    //     max_height = 200;
    // }
    // if (event_styles == undefined) {
    //     event_styles = '';
    // }
    // var editor_fullpage = $('#editor_fullpage').val();
    // var is_fullpage = false;
    // if (editor_fullpage == 'true') {
    //     is_fullpage = true;
    // }
    // console.log(is_fullpage);
    var static_url = $('#static-url').val();
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
            // $body.find('div.form-editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            console.log($btn);
            console.log('do refresh tag');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            console.log('do refresh when show tag');
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
            // $body.find('div.form-editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            console.log('do refresh economy');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            console.log('do refresh when show economy');
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
            // $body.find('div.form-editor').froalaEditor('events.trigger', 'contentChanged', [], true);
        },
        // Callback on refresh.
        refresh: function ($btn) {
            console.log('do refresh group');
        },
        // Callback on dropdown show.
        refreshOnShow: function ($btn, $dropdown) {
            console.log('do refresh when show group');
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
                    // $body.find('div.form-editor').froalaEditor('events.trigger', 'contentChanged', [], true);
                },
                // Callback on refresh.
                refresh: function ($btn) {
                    console.log('do refresh question');
                },
                // Callback on dropdown show.
                refreshOnShow: function ($btn, $dropdown) {
                    console.log('do refresh when show question');
                }
            });
        });
    }
    var toolbarButtons = ['bold', 'italic', 'underline', 'strikeThrough', 'subscript', 'superscript', 'fontFamily', 'fontSize', '|', 'specialCharacters', 'color', 'emoticons', 'paragraphStyle', '|', 'paragraphFormat', 'align', 'formatOL', 'formatUL', 'outdent', 'indent', '-', 'quote', 'insertHR', 'insertLink', 'insertImage', 'insertVideo', 'insertFile', 'insertTable', '|', 'undo', 'redo', 'clearFormatting', 'selectAll', 'html', 'applyFormat', 'removeFormat', 'fullscreen', 'print', 'help', '-', 'general_tags', 'economy_tags', 'group_tags'];
    toolbarButtons = $.merge(toolbarButtons, general_question_buttons);
    if ($this_div) {
        $this_div.on('froalaEditor.initialized', function (e, editor) {
            editor.toolbar.hide();
            // editor.events.bindClick($('body'), 'button#btn-reset-editor-content', function () {
            //     editor.html.set('');
            //     editor.events.focus();
            // }), editor.events.bindClick($('body'), 'button#btn-save-email-content', function (e) {
            //     addOrUpdateEmailContent(editor);
            // }), editor.events.bindClick($('body'), 'button#btn-save-email-template', function (e) {
            //     addOrUpdateTemplateContent(editor);
            // });
        }).on('froalaEditor.focus', function (e, editor) {
            editor.toolbar.show();
        }).on('froalaEditor.blur', function (e, editor) {
            editor.toolbar.hide();
        }).froalaEditor({
            // toolbarInline: true,
            charCounterCount: false,
            toolbarButtons: toolbarButtons,
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
            // iframe: true,
            // fullPage: is_fullpage,
            // iframeStyleFiles: [event_styles],
            // key: 'Lnzhf1F-10tB-7pqmC2uxu==',
            key: '9H4C3J3A5B-16D4E3C2C1C3I2C1B10C2C1phxjB-7evA-16vwoA1H-8vw==',
            htmlRemoveTags: [],
            // heightMin: min_height,
            // heightMax: max_height,
            // iframeStyle: editor_editor_iframe_style,
            // zIndex: 8000,
            // toolbarSticky: false,
            linkStyles: editor_link_styles,
            fontFamily: editor_font_familys,
            htmlExecuteScripts: false
            // enter: $.FroalaEditor.ENTER_P,
            // toolbarVisibleWithoutSelection: false
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
                // console.log(data);
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

    } else {

        $body.find('div.editor-inline-box').on('froalaEditor.initialized', function (e, editor) {
            editor.toolbar.hide();
            // editor.events.bindClick($('body'), 'button#btn-reset-editor-content', function () {
            //     editor.html.set('');
            //     editor.events.focus();
            // }), editor.events.bindClick($('body'), 'button#btn-save-email-content', function (e) {
            //     addOrUpdateEmailContent(editor);
            // }), editor.events.bindClick($('body'), 'button#btn-save-email-template', function (e) {
            //     addOrUpdateTemplateContent(editor);
            // });
        }).on('froalaEditor.focus', function (e, editor) {
            editor.toolbar.show();
        }).on('froalaEditor.blur', function (e, editor) {
            editor.toolbar.hide();
        }).froalaEditor({
            // toolbarInline: true,
            charCounterCount: false,
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
            // iframe: true,
            // fullPage: is_fullpage,
            // iframeStyleFiles: [event_styles],
            // key: 'Lnzhf1F-10tB-7pqmC2uxu==',
            key: '9H4C3J3A5B-16D4E3C2C1C3I2C1B10C2C1phxjB-7evA-16vwoA1H-8vw==',
            htmlRemoveTags: [],
            // heightMin: min_height,
            // heightMax: max_height,
            // iframeStyle: editor_editor_iframe_style,
            // zIndex: 8000,
            // toolbarSticky: false,
            linkStyles: editor_link_styles,
            fontFamily: editor_font_familys,
            htmlExecuteScripts: false
            // enter: $.FroalaEditor.ENTER_P
            // toolbarVisibleWithoutSelection: true
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
                // console.log(data);
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
    }
    // $('div.form-editor').froalaEditor({
    //   toolbarInline: true,
    //   toolbarButtons: ['bold', 'italic', 'underline', 'strikeThrough', 'color', 'emoticons', '-', 'paragraphFormat', 'align', 'formatOL', 'formatUL', 'indent', 'outdent', '-', 'insertImage', 'insertLink', 'insertFile', 'insertVideo', 'undo', 'redo']
    // })
}
function getInlineEditorHtml($this_div) {
    var box = $this_div.closest('.form-editor').attr('id');
    console.log(box);
    if ($.trim(box) != "" && $.trim(box) != undefined) {
        var box_id = box.split("-")[1];
        var page_id = window.location.pathname.split('/')[3];
        // var compiled_html = $('#out').html();
        // $this_div.find('.admin-cms-toolbox').remove();
        var compiled_html = $this_div.froalaEditor('html.get');
        // $this_div.froalaEditor('html.set',element_toolbox+compiled_html);
        // console.log(compiled_html);
        // compiled_html = compiled_html.replace(element_toolbox,'');
        // // var uncompiled_html = editor.getValue();
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

        var title_array = [];
        // var message_array = [2, 5, 10, 20, 30, 48, 67, 72, 77, 80, 84, 146, 148, 149, 188, 200, 207, 209, 232, 237];
        var message_array = [];

        if ($.inArray(element_settings[i].element_question.id, title_array) != -1) {
            $elem.html(element_settings[i].answer);
        }
        if ($.inArray(element_settings[i].element_question.id, message_array) != -1) {
            $elem.html(element_settings[i].description);
        } else if (element_settings[i].answer == "True" || element_settings[i].answer == true) {
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
        else if (element_settings[i].answer == "False" || element_settings[i].answer == false || element_settings[i].answer == "do-not-show") {
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