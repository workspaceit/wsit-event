$(function () {

    attendee_details_load();

    $('.global-session-details-settings, .global-location-details-settings, .global-economy-order-table-settings').fancytree({
        checkbox: true,
        clickFolderMode: 2, //1:activate, 2:expand, 3:activate and expand, 4:activate/dblclick expands
        icon: false,
        aria: false,
        selectMode: 3, // 1:single, 2:multi, 3:multi-hier
        click: function (event, data) {
            if (data.targetType == 'title' && data.node.folder !== true) {
                data.node.toggleSelected();
            }
        }
    });
    $('.global-session-details-settings, .global-location-details-settings').fancytree("option", "selectMode", 2);

    $('body').on('click', '.add-group', function (event) {
        var groupClass = $(this).closest('.table-light').find('table').attr('id');
        clog(groupClass);
        var length = $("#" + groupClass).find('tbody tr').length + 1;
        var $groupList = JSON.parse($("#groupList").val());
        clog($groupList.length);
        var $groupListView = $("#" + groupClass).find('tbody');

        // this is for setting vat field type
        var input_type = 'text';
        var data_text_value = $(this).attr('data-text-value');
        if (data_text_value != undefined && data_text_value == 'vat') {
            input_type = 'number';
        }

        $groupListView.append('<tr>' +
            '<td><input type="checkbox"></td>' +
            '<td>' + length + '</td>' +
            '<td></td>' +
            '<td class="addSearchableGroup" data-grouplist="' + $groupList.length + '"><a href="#" class="' + groupClass + '" id="" data-type="' + input_type + '" data-pk="1" data-title="Name"></a></td>' +
            // '<td><input type="checkbox" class="addSearchableGroup" checked="" data-grouplist="' + $groupList.length + '"></td>' +
            '</tr>');

        $groupList[$groupList.length] = {};
        $("#groupList").val(JSON.stringify($groupList));

        $('.settings-attendee-group, .settings-session-group, .settings-hotel-group, .settings-filter-group, .settings-export_filter-group, .settings-payment-vat, .settings-question-group, .settings-location-group, .settings-travel-group, .settings-menu-group ,.settings-email-group').editable({
            type: 'text',
            name: 'Name',
            title: 'Name'
        });

    });
    // $('body').on('click', '.addSearchableGroup', function (event) {
    //     var name = $(this).closest('tr').find('td:nth-child(3)').find('a').html();
    //     console.log('-------------name------------');
    //     console.log(name);
    //     var type = $(this).closest('table').attr('id').split('-')[1];
    //     var visible = $(this).closest('tr').find('td:last').find('.addSearchableGroup').prop('checked');
    //     var index = $(this).closest('tr').find('td:last').find('.addSearchableGroup').attr('data-grouplist');
    //     var serial_id = $.trim($(this).closest('tr').find('td:nth(1)').html());
    //     groupQue(name, type, visible, index, serial_id);
    // });


    $('body').on('click', '.settings-groups-table .editable-submit', function (event) {
        var name = $(this).closest('div').siblings().children('.form-control').val();
        var type = $(this).closest('table').attr('id').split('-')[1];
        // var visible = $(this).closest('tr').find('td:last').find('.addSearchableGroup').prop('checked');
        var index = $(this).closest('tr').find('.addSearchableGroup').attr('data-grouplist');
        var id = $('.editable-submit').closest('td').find('a').attr('id');
        //if(id != null && id != undefined){
        //    groupQue(name, type, visible, index, id);
        //}else{
        //    groupQue(name, type, visible, index);
        //}
        var serial_id = $.trim($(this).closest('tr').find('td:nth(1)').html());
        clog(index);
        groupQue(name, type, index, serial_id, id);

//    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
//    $.ajax({
//        url: base_url + '/admin/search/',
//        type: "POST",
//        data: {
//            csrfmiddlewaretoken: csrf_token
//        },
//        success: function (result) {
//            if (result.error) {
//                $.growl.error({ message: result.error });
//            } else {
//                $.growl.notice({ message: result.success });
//                setTimeout(function () {
//                    window.location.href = '';
//                }, 3000);
//            }
//        }
//    });
    });

    $('body').on('click', '.delete-group', function (event) {
        var $this = $(this);
        var id = "";
        var pushArray = true;
        var $deleteGroupList = $("#deleteGroupList");
        var deleteGroupList = JSON.parse($deleteGroupList.val());
        //$('.checkGroup').each(function () {
        $(this).closest('.table-footer').siblings('table').find('.checkGroup').each(function () {
            if ($(this).prop('checked')) {
                id = $(this).attr('data-id');
                var deleteGroupListTemp = {id: id};
                if (pushArray) {
                    deleteGroupList.push(deleteGroupListTemp);
                }
                $deleteGroupList.val(JSON.stringify(deleteGroupList));
            }
        });
        if ($("#deleteGroupList").val().length > 2) {
            var groupList = $('#deleteGroupList').val();
            bootbox.confirm("Are you sure you want to delete this Groups?", function (result) {
                if (result) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/settings/delete/',
                        type: "POST",
                        data: {
                            groupList: groupList,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                            } else {
                                $.growl.notice({message: result.success});
                                for (var i = 0; i < deleteGroupList.length; i++) {
                                    $this.closest('.table-footer').prev('.settings-groups-table').find('tbody tr').each(function () {
                                        if ($(this).find('td:first input[class="checkGroup"]').data('id') == deleteGroupList[i]['id']) {
                                            $(this).remove();
                                        }
                                    });
                                }
                            }
                        }
                    });
                } else {
                    $("#deleteGroupList").val('[]');
                }
            });
        }

//    clog($("#deleteGroupList").val());

    });


    function groupQue(name, type, index, serial_id, id) {
        var pushArray = true;
        var groupType = type;
        var $groupList = $("#groupList");
        if (name != "" && name != "Empty") {
            var groupList = JSON.parse($groupList.val());
            if (id != "" && id != undefined) {
                var groupListTemp = {
                    name: valueWithSpecialQuote(name),
                    type: groupType,
                    serial_id: serial_id,
                    id: id
                };
            } else {
                var groupListTemp = {name: valueWithSpecialQuote(name), type: groupType, serial_id: serial_id};
            }
            clog(groupListTemp)
            if (pushArray) {
                groupList[index] = groupListTemp;
            }
            $groupList.val(JSON.stringify(groupList));
        }
//    clog($("#groupList").val());
    }

    $('body').on('click', '.createGroup', function (event) {
        var groups = $("#groupList").val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var event = 1;
        var session_searchable_List = [];
        $('.searchableGroup').each(function () {
            var id = $(this).attr('data-id');
            var group_name = valueWithSpecialQuote($(this).find('a').html());
            // var group_name = valueWithSpecialCharacter($(this).closest('td').prev('td').find('a').html());
            var group_lang = $(this).find('a').attr('data-lang');
            if (group_lang == null || group_lang == "None") {
                group_lang = "";
            }
            // else{
            //     group_lang = valueWithSpecialCharacter(group_lang);
            // }
            var group_prev_name = valueWithSpecialCharacter($(this).find('a').attr('data-prev-name'));
            var group_type = $(this).closest('table').attr('id').split('-')[1]
            // if ($(this).prop('checked')) {
            session_searchable_List.push({
                id: id,
                group_name: group_name,
                group_name_lang: group_lang,
                group_prev_name: group_prev_name,
                group_type: group_type
            });
            //
            // else {
            //     session_searchable_List.push({
            //         id: id,
            //         group_name: group_name,
            //         group_name_lang: group_lang,
            //         group_prev_name: group_prev_name,
            //         group_type: group_type
            //     });
            // }
        });

        var default_answers = [];
        $('#default-answer a[name="questions\\[\\]"]').each(function () {
            if ($(this).attr('data-title') == 'date-range-to' || $(this).attr('data-title') == 'time-range-to') {
                return;
            }
            var value = $(this).html();
            var tr = $(this).parent().parent('tr');
            if ($(this).hasClass('date-question-default')) {
                if ($(this).html() != 'Empty') value = $(this).editable('getValue')['undefined'];
            }
            else if ($(this).attr('data-title') == 'date-range-from') {
                var values = ['', ''];
                if ($(this).html() != 'Empty') values[0] = $(this).editable('getValue')['undefined'];
                if (tr.find('.date-range-to-default').html() != "Empty") values[1] = tr.find('.date-range-to-default').editable('getValue')['undefined'];
                value = JSON.stringify(values);
            }
            else if ($(this).attr('data-title') == 'time-range-from') {
                var values = ['', ''];
                if ($(this).html() != 'Empty') values[0] = $(this).html();
                if (tr.find('.time-range-to-default').html() != "Empty") values[1] = tr.find('.time-range-to-default').html();
                value = JSON.stringify(values);
            }
            else if ($(this).hasClass('country-question-default')) {
                value = $(this).editable('getValue');
                if ($.isEmptyObject(value)) value = 'Empty';
                else value = value['undefined'];
            }
            var default_answer_status = tr.find("td").eq(0).find(".answer-status").val();
            var default_answer = {
                id: $(this).attr('data-pk'),
                value: valueWithSpecialQuote(value),
                status: default_answer_status
            };
            default_answers.push(default_answer);
        });

        var travels = [];
        var sessions = [];
        var all_rooms = [];

        $(".default-hotel").each(function () {
            var room = {id: $(this).attr("data-room"), value: $(this).val()};
            all_rooms.push(room);
        });

        $('#default-answer a[name="travel\\[\\]"]').each(function () {
            var tr = $(this).parent().parent('tr');
            var default_answer_status = tr.find("td").eq(0).find(".answer-status").val();
            var default_answer = {
                id: $(this).attr('data-pk'),
                value: $(this).editable('getValue').undefined,
                status: default_answer_status
            };
            travels.push(default_answer);

        });

        $('#default-answer a[name="session\\[\\]"]').each(function () {
            var tr = $(this).parent().parent('tr');
            var default_answer_status = tr.find("td").eq(0).find(".answer-status").val();
            var default_answer = {
                id: $(this).attr('data-pk'),
                value: $(this).editable('getValue').undefined,
                status: default_answer_status
            };
            sessions.push(default_answer);

        });


        var session_color_List = [];
        $('.group_color').each(function () {
            var group_id = $(this).attr('data-id');
            var color = $(this).val();
            session_color_List.push({
                id: group_id,
                color: color
            });
        });
        var location_keys = [];
        var session_keys = [];
        var economy_order_table_columns = [];
        var attendee_details = "";
        var timeout = $('#notification_timeout').val();
        var appear_next_up_setting = $('#appear_next_up_setting').val();
        var disappear_next_up_setting = $('#disappear_next_up_setting').val();
        var appear_evaluation_setting = $('#appear_evaluation_setting').val();
        // var disappear_evaluation_setting = $('#disappear_evaluation_setting').val();
        var sender_email = $.trim($('#sender_email').val());
        var timezone = $('#timezone').val();
        var uid_length = $('#uid-length').val();
        var week_start_day = $('#week_start_day').val();
        var plugin_language = $('#plugin_language').val();
        var default_date_format = $('#default_date_format').val();
        var temporary_attendee_time_expire = $('#temporary_attendee_time_expire').val();
        var duration = $('#slider-duration').val();
        var default_project = $('#default_project').select2('val');
        var default_language = $('#default_language').select2('val');
        var attendee_add_confirmation = $("#attendee-add-confirmation").select2("val");
        var attendee_edit_confirmation = $("#attendee-edit-confirmation").select2("val");
        var session_conflict_confirmation = $("#session-conflict-confirmation").select2("val");
        var session_no_conflict_confirmation = $("#session-no-conflict-confirmation").select2("val");
        var start_order_number = $('#start-order-number').val();
        var due_date = $('#due-date').val();
        var current_language_id = $('.group-language-presets-selector').select2('val');

        var message = '';
        var valid = true;
        // Cookie Settings
        var cookie_expire = 864000;
        var cookie_expire_in_year = $("#session_cookie_expire_year").prop("checked");
        if (cookie_expire_in_year) {
            cookie_expire = 31536000;
        } else {
            var cookie_expire_hour = $("#session_cookie_expire_hour").val();
            if (cookie_expire_hour.split(':').length > 1) {
                cookie_expire = cookie_expire_hour;
            } else {
                if ($.trim(cookie_expire_hour) != '' && $.trim(cookie_expire_hour) != null && $.trim(cookie_expire_hour) != undefined) {
                    var time_regex = new RegExp('^[0-9:]+$');
                    if (time_regex.test(cookie_expire_hour)) {
                        cookie_expire = cookie_expire_hour;
                    } else {
                        message += "*Session Cookie Settings" + " is not valid" + "<br>";
                        valid = false;
                    }
                }
                cookie_expire = 60 * cookie_expire;
            }
        }
        if (timeout == '' || timeout == undefined) {
            message += "*Notification timeout" + " can't be blank" + "<br>";
            valid = false;
        }
        if (sender_email == '' || sender_email == undefined) {
            message += "*Senders email" + " can't be blank" + "<br>";
            valid = false;
        }
        else if (!validateEmail(sender_email)) {
            message += "*Senders email" + " is not valid" + "<br>";
            valid = false;
        }
        /*$('.global-location-details-settings input[type=checkbox]').each(function () {
         if (this.checked) {
         var details_key = $.trim($(this).attr('data-setting-key'));
         location_keys.push(details_key);
         }
         });*/
        //var location_global_settings = '{"location_details":[{"key":"'+location_keys.join(",")+'"}]}';
        /*$('.global-session-details-settings input[type=checkbox]').each(function () {
         if (this.checked) {
         var details_key = $.trim($(this).attr('data-setting-key'));
         session_keys.push(details_key);
         }
         });*/
        var session_details_settings = $('.global-session-details-settings').fancytree('getTree').getSelectedNodes();
        var location_details_settings = $('.global-location-details-settings').fancytree('getTree').getSelectedNodes();
        var session_global_settings = $('.global-settings-attendee-list-visible-columns').fancytree('getTree').getSelectedNodes();
        var order_table_settings = $('.global-economy-order-table-settings').fancytree('getTree').getSelectedNodes();
        var selected_question_id = [];
        for (var i = 0; i < session_details_settings.length; i++) {
            session_keys.push(session_details_settings[i].data.settingKey);
        }
        for (var i = 0; i < location_details_settings.length; i++) {
            location_keys.push(location_details_settings[i].data.settingKey);
        }
        for (var i = 0; i < session_global_settings.length; i++) {
            if (session_global_settings[i].folder == false && session_global_settings[i].data.data_id) {
                selected_question_id.push(session_global_settings[i].data.data_id);
            }
        }
        attendee_details = '{"question":[{"id":"' + selected_question_id.join(',') + '"}]}';
        for (var i = 0; i < order_table_settings.length; i++) {
            economy_order_table_columns.push(order_table_settings[i].data.settingKey);
        }
        // $('.global-economy-order-table-settings input[type=checkbox]').each(function () {
        //     if (this.checked) {
        //         var details_key = $.trim($(this).attr('data-setting-key'));
        //         economy_order_table_columns.push(details_key);
        //     }
        // });
        //var session_global_settings = '{"session_details":[{"key":"'+session_keys.join(",")+'"}]}';
        // $('.global-attendee-details-settings ul').find('input:checkbox').each(function () {
        //     var selected_questions = attendee_treeview.getCheckedItems();
        //     var selected_questions_id = [];
        //     for (var i = 0; i < selected_questions.length; i++) {
        //         if (selected_questions[i].data_id != undefined) {
        //             selected_questions_id.push(selected_questions[i].data_id);
        //         }
        //     }
        //     attendee_details = '{"question":[{"id":"' + selected_questions_id.join(',') + '"}]}';
        // });

        if (uid_length != '') {
            if (uid_length > 256 || uid_length < 4) {
                clog('value err in uid_length');
                message += "*Set UID length between 4 and 256" + "<br>";
                valid = false;
            }
        } else {
            clog('not set uid_length');
            message += "*UID length is not set" + "<br>";
            valid = false;
        }

        if (temporary_attendee_time_expire != '') {
            if (temporary_attendee_time_expire < 1) {
                clog('value err in temporary_attendee_time_expire');
                message += "*Set Temporary attendee expire time > 0" + "<br>";
                valid = false;
            }
        } else {
            clog('value err in temporary_attendee_time_expire');
            message += "*Set Temporary attendee expire time" + "<br>";
            valid = false;
        }
        var allow_same_email_multiple_registration = $("#allow-same-email-registered-more-than-once").prop('checked');
        // console.log(groups);
        if (valid) {
            $.ajax({
                url: base_url + '/admin/settings/',
                type: "POST",
                data: {
                    groups: groups,
                    event: event,
                    timeout: timeout,
                    appear_next_up_setting: appear_next_up_setting,
                    disappear_next_up_setting: disappear_next_up_setting,
                    appear_evaluation_setting: appear_evaluation_setting,
                    // disappear_evaluation_setting: disappear_evaluation_setting,
                    sender_email: sender_email,
                    duration: duration,
                    timezone: timezone,
                    uid_length: uid_length,
                    week_start_day: week_start_day,
                    plugin_language: plugin_language,
                    default_date_format: default_date_format,
                    temporary_attendee_expire_time: temporary_attendee_time_expire,
                    default_project: default_project,
                    default_language: default_language,
                    attendee_add_confirmation: attendee_add_confirmation,
                    attendee_edit_confirmation: attendee_edit_confirmation,
                    session_conflict_confirmation: session_conflict_confirmation,
                    session_no_conflict_confirmation: session_no_conflict_confirmation,
                    default_tags: $(".attendee-question-attendee-tags").select2('val'),
                    default_group: $("#default-answer-group-selection").editable('getValue')['default-answer-group-selection'],
                    defaults_answers: JSON.stringify(default_answers),
                    default_travels: JSON.stringify(travels),
                    default_sessions: JSON.stringify(sessions),
                    group_searchable_List: JSON.stringify(session_searchable_List),
                    session_color_List: JSON.stringify(session_color_List),
                    rooms: JSON.stringify(all_rooms),
                    cookie_expire: cookie_expire,
                    location_global_settings: JSON.stringify(location_keys),
                    session_global_settings: JSON.stringify(session_keys),
                    economy_order_table_global_settings: JSON.stringify(economy_order_table_columns),
                    attendee_global_settings: JSON.stringify(attendee_details),
                    start_order_number: start_order_number,
                    due_date: due_date,
                    current_language_id: current_language_id,
                    allow_same_email_multiple_registration: allow_same_email_multiple_registration,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $("#groupList").val('[]');
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        //var all_new_groups = JSON.parse(groups);
                        if (result.group_response) {
                            var all_new_groups = result.group_response;
                            for (var new_group = 0; new_group < all_new_groups.length; new_group++) {
                                var new_group_type = all_new_groups[new_group].type;
                                var group_elem = $('#settings-' + new_group_type + '-group').find('tr:nth(' + all_new_groups[new_group].serial_id + ')');
                                if (all_new_groups[new_group].group_id) {
                                    group_elem.find('td:nth(2)').html(all_new_groups[new_group].group_id);
                                    group_elem.find('td:nth(0)').find('input').attr('name', 'checkGroup');
                                    group_elem.find('td:nth(0)').find('input').addClass('checkGroup');
                                    group_elem.find('td:nth(0)').find('input').attr('data-id', all_new_groups[new_group].group_id);
                                    group_elem.find('td:nth(3)').find('a').attr('id', all_new_groups[new_group].group_id);
                                    group_elem.find('td:nth(3)').attr('data-id', all_new_groups[new_group].group_id);
                                    group_elem.find('td:nth(3)').find('a').attr('data-lang', all_new_groups[new_group].group_name_lang);
                                    group_elem.find('td:nth(3)').find('a').attr('data-prev-name', all_new_groups[new_group].group_name);
                                    group_elem.find('td:nth(3)').removeClass('addSearchableGroup');
                                    group_elem.find('td:nth(3)').addClass('searchableGroup');
                                } else {
                                    group_elem.remove();
                                }
                            }
                        }
                        var old_group_list = result.updated_group_list;
                        for (var old_group = 0; old_group < old_group_list.length; old_group++) {
                            var old_group_elem = $('.settings-' + old_group_list[old_group].type + '-group#' + old_group_list[old_group].group_id);
                            old_group_elem.attr('data-lang', old_group_list[old_group].group_name_lang);
                            old_group_elem.attr('data-prev-name', old_group_list[old_group].group_name);
                        }
                        //clog(JSON.parse(groups));
//                setTimeout(function () {
//                    window.location.href = base_url + '/admin/settings/';
//                }, 3000);
                    }

                    if (result.warnings.length > 0) {
                        for (var warn_i = 0; warn_i < result.warnings.length; warn_i++) {
                            $.growl.warning({message: result.warnings[warn_i]});
                        }
                    }
                }
            });
        } else {
            $.growl.warning({message: message});
        }

    });

    $('body').on('click', '.checkAllGroup', function (event) {
        clog($(this));
        $this = $(this)[0];
        $(this).closest('table').find('.checkGroup').each(function () {
            $(this).prop('checked', $this.checked);
        });
        //$(':checkbox', table.rows().nodes()).prop('checked', this.checked);
        //$('#filter-search-table tbody input[type="checkbox"]').prop('checked', this.checked);
    });

    $('body').on('change', '#session_cookie_expire_year', function () {
        var session_cookie_expire_year = $('#session_cookie_expire_year').prop('checked');
        if (session_cookie_expire_year) {
            $('.cookie_time').hide();
        } else {
            $('.cookie_time').show();
            //$('.cookie_time').find('#session_cookie_expire_hour').val("");
        }
    });

    function attendee_details_load() {
        // global-settings-attendee-list-visible-columns
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $(".global-settings-attendee-list-visible-columns").fancytree({
            source: {
                url: base_url + '/admin/settings/settings-attendee-global-details/'
            },
            checkbox: true,
            clickFolderMode: 2, //1:activate, 2:expand, 3:activate and expand, 4:activate/dblclick expands
            icon: false,
            aria: false,
            selectMode: 3, // 1:single, 2:multi, 3:multi-hier
            click: function (event, data) {
                if (data.targetType == 'title' && data.node.folder !== true) {
                    data.node.toggleSelected();
                }
            }
        });
        // $.ajax({
        //     url: base_url + '/admin/settings/settings-attendee-global-details/',
        //     type: "GET",
        //     data: {
        //         csrfmiddlewaretoken: csrf_token
        //     },
        //     success: function (result) {
        //         var question_groups = result.question_groups;
        //         attendee_treeview = $(".global-settings-attendee-list-visible-columns").kendoTreeView({
        //             checkboxes: {
        //                 checkChildren: true
        //             },
        //             checked: true,
        //             dataSource: question_groups
        //         }).data("kendoTreeView");
        //         select_custom_attendee_colomns(result.attendee_global_settings, question_groups)
        //
        //     }
        // });
    }

    function select_custom_attendee_colomns(custom_attendee_selected_columns, all_attendee_columns) {
        try {
            custom_attendee_selected_columns = JSON.parse(custom_attendee_selected_columns);
        } catch (exception) {
            custom_attendee_selected_columns = [];
        }
        if (custom_attendee_selected_columns.length > 0) {
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

    // kendo.ui.TreeView.prototype.getCheckedItems = (function () {
    //     function getCheckedItems() {
    //         var nodes = this.dataSource.view();
    //         return getCheckedNodes(nodes);
    //     }
    //
    //     function getCheckedNodes(nodes) {
    //         var node, childCheckedNodes;
    //         var checkedNodes = [];
    //
    //         for (var i = 0; i < nodes.length; i++) {
    //             node = nodes[i];
    //             if (node.checked) {
    //                 checkedNodes.push(node);
    //             }
    //
    //             // to understand recursion, first
    //             // you must understand recursion
    //             if (node.hasChildren) {
    //                 childCheckedNodes = getCheckedNodes(node.children.view());
    //                 if (childCheckedNodes.length > 0) {
    //                     checkedNodes = checkedNodes.concat(childCheckedNodes);
    //                 }
    //             }
    //
    //         }
    //
    //         return checkedNodes;
    //     }
    //
    //     return getCheckedItems;
    // })();

});
