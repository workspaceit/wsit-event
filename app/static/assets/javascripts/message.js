$(function () {
    var $body = $('body');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    //   Message View Start

    // message add modal
    $body.on('click', '.new-message', function () {
        $('#message-modal').find('.modal-title').html('<i class="fa fa-lg fa-envelope-o"></i> Add New Message');
        $('#btn-save-message').css('display', 'inline');
        $('#btn-update-message').css('display', 'none');
    });

    // message edit modal
    $body.on('click', '.message-settings', function () {
        var message_id = $(this).attr('data-id');
        getMessageDetails(message_id);
    });

    $body.on('click', '.view-message-settings', function () {
        var message_id = $(this).attr('data-id');
        getMessageDetails(message_id);
        $("body #message-modal").find("input, select").attr('disabled', 'disabled');
    });

    $body.on('click', '#btn-save-message', function () {
        addOrUpdateMessage($(this));
    });

    $body.on('click', '#btn-update-message', function () {
        addOrUpdateMessage($(this));
    });

    // Get message details
    function getMessageDetails(message_id) {
        $.ajax({
            url: base_url + '/admin/messages/' + message_id + '/',
            type: "GET",
            success: function (response) {
                if (response.error) {
                    $.growl.error({message: response.error});
                } else {
                    var message_data = response.message;
                    $('#message-modal').find('.modal-title').html('<i class="fa fa-lg fa-envelope-o"></i> ' + message_data.name);
                    $('#message-id').val(message_data.id);
                    $('#message-name').val(message_data.name);
                    $('#message-sender').val(message_data.sender_name);
                    $('#message-type').val(message_data.type);
                    $('#btn-save-message').css('display', 'none');
                    $('#btn-update-message').css('display', 'inline');
                    $('#message-modal').modal();
                }
            }
        });
    }

    // Add or update message function
    function addOrUpdateMessage($this) {
        var name = $('#message-name').val(),
            message_type = $('#message-type').val(),
            sender_name = $('#message-sender').val();

        var requiredFields = [
            {fieldId: 'message-name', message: 'Name'},
            {fieldId: 'message-type', message: 'Message Type'},
            {fieldId: 'message-sender', message: 'Sender Name'}
        ];
        if (!requiredMessageFieldValidator(requiredFields)) {
            return;
        }
        var data = {
            name: name,
            sender_name: sender_name,
            message_type: message_type,
            csrfmiddlewaretoken: csrf_token
        };
        if ($this.attr('id') == 'btn-update-message') {
            var message_id = $('#message-id').val();
            data['id'] = message_id;
        }
        $.ajax({
            url: base_url + '/admin/messages/',
            type: 'POST',
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.message});
                    var updated_message = response.message_data;
                    var receivers_url = base_url + '/admin/messages-receivers/' + updated_message.id + '/';
                    var content_url = base_url + '/admin/messages-content/' + updated_message.id + '/';
                    var row = '' +
                        '<td>' + updated_message.id + '</td>' +
                        '<td>' + updated_message.name + '</td>' +
                        '<td>' + response.sent_receiver + '/' + response.total_receiver + '</td>' +
                        '<td>' +
                        '    <a href="' + receivers_url + '" class="btn btn-xs btn-info" data-toggle="tooltip" data-placement="top" title="" data-original-title="Receivers"> <i class="dropdown-icon fa fa-users"></i> </a>' +
                        '    <button class="btn btn-xs message-settings" data-id="' + updated_message.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Setting"> <i class="dropdown-icon fa fa-cog"></i> </button>' +
                        '    <a href="' + content_url + '" class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Message Content" target = _blank> <i class="dropdown-icon fa fa-pencil"></i> </a>' +
                        '    <button class="btn btn-xs btn-warning duplicate-message" data-id="' + updated_message.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"> <i class="dropdown-icon fa fa-files-o"></i> </button>' +
                        '    <button class="btn btn-xs btn-danger delete-message" data-id="' + updated_message.id + '" data-toggle="tooltip"data-placement="top" title=""data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>' +
                        '</td>';
                    if ($this.attr('id') === 'btn-update-message') {
                        $('body .message-table tbody tr').each(function () {
                            if ($(this).find('td:first-child').html() == updated_message.id) {
                                $(this).html(row);
                            }
                        });

                    } else {
                        $('body').find('.message-table').find('tbody').append('<tr>' + row + '</tr>');
                    }
                    $('#message-modal').modal('hide');
                }
                else {
                    var errors = response.message;
                    $.growl.error({message: response.message});
                }
            },
            error: function (e) {
                clog(e);
                $.growl.error({message: 'Someting went wrong'});
            }
        });
    }

    function requiredMessageFieldValidator(requiredFields) {
        var message = '';
        var valid = true;
        for (var i = 0; i < requiredFields.length; i++) {
            var Id = requiredFields[i].fieldId;
            if ($.trim($('#' + Id).val()) == '') {
                message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
                valid = false;
            }
        }
        if ($.trim($('#message-sender').val()).length > 11) {
            message += "Message sender name must be between 1-11 characters" + "<br>";
            valid = false;
        }
        if (!valid) {
            $.growl.warning({message: message});
        }
        return valid;
    }

    // Duplicate Message
    $body.on('click', '.duplicate-message', function () {
        var message_id = $(this).data('id');
        var data = {
            message_id: message_id,
            csrfmiddlewaretoken: csrf_token
        }
        $.ajax({
            url: base_url + '/admin/messages-duplicate/',
            type: "POST",
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.success});
                    var message = response.message;
                    var receivers_url = base_url + '/admin/messages-receivers/' + message.id + '/';
                    var content_url = base_url + '/admin/messages-content/' + message.id + '/';
                    var row = '' +
                        '<td>' + message.id + '</td>' +
                        '<td>' + message.name + '</td>' +
                        '<td>' + response.sent_receiver + '/' + response.total_receiver + '</td>' +
                        '<td>' +
                        '    <a href="' + receivers_url + '" class="btn btn-xs btn-info" data-toggle="tooltip" data-placement="top" title="" data-original-title="Receivers"> <i class="dropdown-icon fa fa-users"></i> </a>' +
                        '    <button class="btn btn-xs message-settings" data-id="' + message.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Setting"> <i class="dropdown-icon fa fa-cog"></i> </button>' +
                        '    <a href="' + content_url + '" class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Message Content" target = _blank> <i class="dropdown-icon fa fa-pencil"></i> </a>' +
                        '    <button class="btn btn-xs btn-warning duplicate-message" data-id="' + message.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"> <i class="dropdown-icon fa fa-files-o"></i> </button>' +
                        '    <button class="btn btn-xs btn-danger delete-message" data-id="' + message.id + '" data-toggle="tooltip"data-placement="top" title=""data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>' +
                        '</td>';
                    $('body').find('.message-table').find('tbody').append('<tr>' + row + '</tr>');
                } else {
                    $.growl.warning({message: response.error});
                }
            }
        });
    });

    // Delete Message
    $body.on('click', '.delete-message', function (event) {
        var $this = $(this);
        bootbox.confirm("Are you sure you want to delete this Message?", function (result) {
            if (result) {
                var id = $this.attr('data-id');
                $.ajax({
                    url: base_url + '/admin/messages-delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else if (result.warning) {
                            $.growl.warning({message: result.warning});
                        } else {
                            $.growl.notice({message: result.success});
                            $this.closest('tr').remove();
                        }
                    }
                });
            }
        });
    });

    // Message View End

    // Message Receivers View Start

    // Open Add receiver modal

    $body.on('click', '#open-message-filter-form', function () {
        $('#filter').select2('val', '');
    });

    // Search Receiver

    // $body.on('keyup', '.search-message-receiver', function (e) {
    //     var $this = $(this);
    //     var search_key = $(this).val();
    //     var message_id = window.location.pathname.split('/')[3];
    //     var data = {
    //         search_key: search_key,
    //         message_id: message_id
    //     }
    //     $.ajax({
    //         url: base_url + '/admin/messages/search-receiver/',
    //         type: "GET",
    //         data: data,
    //         success: function (result) {
    //             $('.receivers-table').find('tbody').html(result);
    //         }
    //     });
    // });

    $body.on('keyup', '.search-message-receiver', function (e) {
            var search_key = $(this).val();
            $('.receivers-table tbody tr').hide();
            $('.receivers-table tbody').each(function () {
                var $this_tbody = $(this);
                $this_tbody.find('tr').each(function () {
                    var $this_tr = $(this);
                    var found_receiver = false;
                    var firstname = $this_tr.find('td:nth-child(3)').text().toUpperCase();
                    var lastname = $this_tr.find('td:nth-child(4)').text().toUpperCase();
                    var fullname = firstname + ' ' + lastname;
                    var phone = $this_tr.find('td:nth-child(5)').text().toUpperCase();
                    $this_tr.find('td').each(function () {
                        if (firstname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (lastname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (fullname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (phone.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        }
                    });
                    if (found_receiver) {
                        $this_tr.show();
                    }
                    // else{
                    //     $this_tr.find('td:first input').prop('checked',false);
                    // }
                });
                $('.receivers-table tbody tr:visible').each(function (index) {
                    $(this).find('td:nth-child(2)').html(index + 1);
                });
                setTotalSelectedAndUnselectedReceiver();
            })
        }
    );

    // Change selected receivers status and Delete

    $body.on('click', '.change-message-receiver-selected', function () {
        var selected_receivers = [];
        var status = $.trim($(this).attr('data-status'));
        $('body').find('.receivers-table').find('tbody tr').each(function () {
            var $thisChecbox = $(this).find('input[type=checkbox]');
            if ($thisChecbox.prop('checked')) {
                selected_receivers.push({id: $thisChecbox.attr('data-id')});
            }
        });
        if (selected_receivers.length > 0) {
            if (status == 'sent' || status == 'not_sent') {
                changeMessageReceiversStatus(selected_receivers, status);
            } else if (status == 'delete') {
                bootbox.confirm("Are you sure you want to delete selected receivers?", function (result) {
                    if (result) {
                        deleteMessageReceivers(selected_receivers);
                    }
                });
            }
        } else {
            $.growl.warning({message: 'Pls select a receivers first'});
        }

        clog(selected_receivers);
    });

    // Change receiver status

    $body.on('click', '.change-message-receiver-status', function () {
        var selected_receivers = [];
        var receiver_id = $.trim($(this).closest('tr').find('input[type=checkbox]').attr('data-id'));
        var current_status = $.trim($(this).closest('tr').find('.receiver-status').attr('data-status'));
        if (receiver_id != '' && receiver_id != undefined && current_status != '' && current_status != undefined) {
            selected_receivers.push({id: receiver_id});
            var status = "not_sent";
            if (current_status == 'not_sent') {
                status = "sent";
            }
            changeMessageReceiversStatus(selected_receivers, status);
        }
    });

    // Delete Email Receiver

    $body.on('click', '.delete-message-receiver', function () {
        var selected_receivers = [];
        var receiver_id = $.trim($(this).closest('tr').find('input[type=checkbox]').attr('data-id'));
        if (receiver_id != '' && receiver_id != undefined) {
            selected_receivers.push({id: receiver_id});
            bootbox.confirm("Are you sure you want to delete this receiver?", function (result) {
                if (result) {
                    deleteMessageReceivers(selected_receivers);
                }
            });
        }
    });

    // Select receiver to send mail

    $body.on('click', '.send-message', function () {
        var selected_receivers = [];
        var status = $.trim($(this).attr('data-status'));
        var $allReceiver = $('body').find('.receivers-table').find('tbody tr');
        if (status == 'not_sent') {
            $allReceiver.each(function () {
                var receiver_status = $(this).find('.receiver-status').attr('data-status');
                if ($.trim(receiver_status) == status) {
                    var receiver_id = $.trim($(this).find('input[type=checkbox]').attr('data-id'));
                    selected_receivers.push({id: receiver_id});
                }
            });
            if (selected_receivers.length > 0) {
                checkTotalReceivers(selected_receivers);
            } else {
                $.growl.warning({message: 'There is no receiver to send message'});
            }
        } else if (status == 'selected') {
            $allReceiver.each(function () {
                var $thisChecbox = $(this).find('input[type=checkbox]');
                if ($thisChecbox.prop('checked')) {
                    selected_receivers.push({id: $thisChecbox.attr('data-id')});
                }
            });
            if (selected_receivers.length > 0) {
                checkTotalReceivers(selected_receivers);
            } else {
                $.growl.warning({message: 'There is no receiver to send message'});
            }
        } else {
            $.growl.warning({message: 'something went wrong'});
        }

    });
    // import receivers using filter

    $body.on('click', '.add-message-filer-receiver', function () {
        var filter_id = $('#filter').select2('val');
        if (filter_id != '' && filter_id != null && filter_id != undefined) {
            $('body .loader').show();
            $('.add-message-filer-receiver').prop("disabled", true);
            var message_id = window.location.pathname.split('/')[3];
            $.ajax({
                url: base_url + '/admin/messages/import-filter-receiver/',
                type: "POST",
                data: {
                    message_id: message_id,
                    filter_id: filter_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $('body .loader').hide();
                    $('.add-message-filer-receiver').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var message_receivers = result.message_receivers;
                        var receiver_rows = addMessageAttendeetoReceiverTable(admin_permission, message_receivers);
                        $('#message-from-filter').modal('hide');
                        $('body').find('.receivers-table').find('tbody').html(receiver_rows);
                        $.growl.notice({message: result.message});
                        setTotalSelectedAndUnselectedReceiver();
                    } else {
                        $.growl.error({message: result.message});
                    }
                }
            });
        }

    });

    // import recievers using exeel

    $body.on('click', '#btn-import-message-excel', function () {
        try {
            var message_id = window.location.pathname.split('/')[3];
            var formdata = new FormData();
            formdata.append('upload_file', $('#upload_excel_file')[0].files[0]);
            formdata.append('csrfmiddlewaretoken', csrf_token);
            formdata.append('message_id', message_id);
            $('body .loader').show();
            $('#btn-import-message-excel').prop("disabled", true);
            $.ajax({
                url: base_url + '/admin/messages/import-excel-receiver/',
                type: 'POST',
                data: formdata,
                async: false,
                cache: false,
                contentType: false,
                processData: false,
                success: function (result) {
                    $('body .loader').hide();
                    $('#btn-import-message-excel').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var message_receivers = result.message_receivers;
                        var receiver_rows = addMessageAttendeetoReceiverTable(admin_permission, message_receivers);
                        $('#message-from-excel-import').modal('hide');
                        $('body').find('.receivers-table').find('tbody').html(receiver_rows);
                        $.growl.notice({message: result.message});
                        setTotalSelectedAndUnselectedReceiver();
                    } else {
                        $.growl.error({message: result.message});
                    }
                }
            });
        }
        catch (err) {
            clog(err);
        }
    });

    // import receivers using Clipboard

    $body.on('click', '.add-message-receivers-clipboard', function () {
        var clipboard_data = $.trim($('.clipboard-data').val());
        if (clipboard_data != '' && clipboard_data != null && clipboard_data != undefined) {
            $('body .loader').show();
            $('.add-message-receivers-clipboard').prop("disabled", true);
            var message_id = window.location.pathname.split('/')[3];
            $.ajax({
                url: base_url + '/admin/messages/import-clipboard-receiver/',
                type: "POST",
                data: {
                    message_id: message_id,
                    clipboard_data: clipboard_data,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $('body .loader').hide();
                    $('.add-message-receivers-clipboard').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var message_receivers = result.message_receivers;
                        var receiver_rows = addMessageAttendeetoReceiverTable(admin_permission, message_receivers);
                        $('#message-from-clipboard').modal('hide');
                        $('body').find('.receivers-table').find('tbody').html(receiver_rows);
                        $.growl.notice({message: result.message});
                        setTotalSelectedAndUnselectedReceiver();
                    } else {
                        $.growl.error({message: result.message});
                    }
                }
            });
        }

    });

    // Sort receiver columns

    $body.on('click', '.receivers-table thead th', function () {
        if (!$(this).hasClass('not-sortable')) {
            var n = $(this).prevAll().length;
            if(f_sl_receivier_n != 0 && f_sl_receivier_n != n){
                f_sl_receiver_list = 1;
            }
            f_sl_receivier_n = n;
            f_sl_receiver_list *= -1;
            var elem_tbody = $(this).closest('.receivers-table').find('tbody');
            var className = $.trim($(this).attr("class"));
            $(this).closest('.receivers-table thead').find('th').removeClass('asc desc');
            if (className == '' || className == undefined) {
                $(this).addClass('desc');
            } else if (className.indexOf('asc') != -1) {
                $(this).addClass('desc');
            } else if (className.indexOf('desc') != -1) {
                $(this).addClass('asc');
            } else {
                $(this).addClass('asc');
            }
            sortReceiverList(f_sl_receiver_list, n, elem_tbody);
        }
    });

    // Delete receiver function

    function deleteMessageReceivers(selected_receivers) {
        $.ajax({
            url: base_url + '/admin/messages/delete-receiver/',
            type: "POST",
            data: {
                receivers: JSON.stringify(selected_receivers),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.success) {
                    $.growl.notice({message: result.message});
                    $('body').find('.receivers-table').find('tbody tr').each(function () {
                        var receiver_id = $(this).find('input[type=checkbox]').attr('data-id');
                        for (var i = 0; i < selected_receivers.length; i++) {
                            if (receiver_id == selected_receivers[i]['id']) {
                                $(this).remove();
                            }
                        }
                    });
                } else {
                    $.growl.error({message: result.message});
                }

            }
        });
    }

    // Change receivers status

    function changeMessageReceiversStatus(selected_receivers, status) {
        $.ajax({
            url: base_url + '/admin/messages/change-receiver-status/',
            type: "POST",
            data: {
                status: status,
                receivers: JSON.stringify(selected_receivers),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.success) {
                    $.growl.notice({message: result.message});
                    $('body').find('.receivers-table').find('tbody tr').each(function () {
                        var receiver_id = $(this).find('input[type=checkbox]').attr('data-id');
                        for (var i = 0; i < selected_receivers.length; i++) {
                            if (receiver_id == selected_receivers[i]['id']) {
                                if (status == 'sent') {
                                    $(this).find('.receiver-status').attr('data-status', status).html('Sent');
                                } else if (status == 'not_sent') {
                                    $(this).find('.receiver-status').attr('data-status', status).html('Not Sent');
                                }
                            }
                        }
                    });
                } else {
                    $.growl.error({message: result.message});
                }
            }
        });
    }


    // Check total receivers

    function checkTotalReceivers(selected_receivers) {
        $.ajax({
            url: base_url + '/admin/messages/get-message-receivers/',
            type: "POST",
            data: {
                receivers: JSON.stringify(selected_receivers),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.success) {
                    if (result.total_receiver > 0) {
                        bootbox.confirm(result.message, function (result) {
                            if (result) {
                                sendMessage(selected_receivers);
                            }
                        });
                    } else {
                        $.growl.warning({message: 'There is no receiver to send message'});
                    }

                } else {
                    $.growl.error({message: result.message});
                }
            }
        });
    }

    // Send message Function

    function sendMessage(selected_receivers) {
        $('body .loader').show();
        $('.send-dropdown').prop("disabled", true);
        $.ajax({
            url: base_url + '/admin/messages/send-message/',
            type: "POST",
            data: {
                status: status,
                receivers: JSON.stringify(selected_receivers),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                $('body .loader').hide();
                $('.send-dropdown').prop("disabled", false);
                if (result.success) {
                    if (result.message_status) {
                        $.growl.notice({message: result.message});
                        var updated_receivers = result.updated_receivers;
                        $('.select-all-receiver').prop('checked', false);
                        $('body').find('.receivers-table').find('tbody tr').each(function () {
                            var receiver_id = $(this).find('input[type=checkbox]').attr('data-id');
                            for (var i = 0; i < updated_receivers.length; i++) {
                                if (receiver_id == updated_receivers[i].id) {
                                    $(this).find('input[type=checkbox]').prop('checked', false);
                                    if (updated_receivers[i].status == 'sent') {
                                        $(this).find('.receiver-status').attr('data-status', updated_receivers[i].status).html('Sent');
                                    } else if (updated_receivers[i].status == 'not_sent') {
                                        $(this).find('.receiver-status').attr('data-status', updated_receivers[i].status).html('Not Sent');
                                    }
                                    $(this).find('.last-received').html(moment(updated_receivers[i].last_received, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm'));
                                }
                            }
                        });
                    } else {
                        $.growl.error({message: "Something went wrong. please try again"});
                    }
                } else {
                    $.growl.error({message: result.message});
                }
                setTotalSelectedAndUnselectedReceiver();
            },
            error: function () {
                clog('something went wrong');
                $('body .loader').hide();
                $('.send-dropdown').prop("disabled", false);
            }
        });
    }


});

// Set Total Selected And Unselected Receiver

function setTotalSelectedAndUnselectedReceiver() {
    var total_selected = $('body').find('.receivers-table tbody tr:visible').find('input[type=checkbox]:checked').length;
    var total_unselected = $('body').find('.receivers-table tbody tr:visible').find('input[type=checkbox]:not(:checked)').length;
    $('body').find('#selected-receiver').html(total_selected);
    $('body').find('#unselected-receiver').html(total_unselected);
}

function addMessageAttendeetoReceiverTable(admin_permission, message_receivers) {
    var all_rows = '';
    for (var i = 0; i < message_receivers.length; i++) {
        var count = i + 1;
        var receiver_status = "Not Sent";
        if (message_receivers[i].status == "sent") {
            receiver_status = "Sent";
        }
        var phone_or_push = '';
        if(message_receivers[i].mobile_phone){
            phone_or_push += message_receivers[i].mobile_phone;
        }
        if(message_receivers[i].mobile_phone && message_receivers[i].push){
            phone_or_push += " / ";
        }
        if(message_receivers[i].push){
            phone_or_push += "Push";
        }
        var action_buttons = '<a href="' + base_url + '/admin/messages/receiver-preview/' + message_receivers[i].id + '" class="btn btn-xs preview-receiver-email-content" data-toggle="tooltip" data-placement="top" title="" data-original-title="Preview" target="_blank"><i class="fa fa-share-square-o" aria-hidden="true"></i></a>' +
            ' <a href="' + base_url + '/admin/messages/download-receiver-message/' + message_receivers[i].id + '" class="btn btn-xs btn-warning download-email-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Download" target="_blank"> <i class="fa fa-download" aria-hidden="true"></i> </a>';
        if (admin_permission) {
            action_buttons = '<button class="btn btn-xs btn-info change-message-receiver-status" data-toggle="tooltip" data-placement="top" title="" data-original-title="Change Status"><i class="fa fa-refresh" aria-hidden="true"></i></button>' +
                ' <a href="' + base_url + '/admin/messages/receiver-preview/' + message_receivers[i].id + '" class="btn btn-xs preview-receiver-email-content" data-toggle="tooltip" data-placement="top" title="" data-original-title="Preview" target="_blank"><i class="fa fa-share-square-o" aria-hidden="true"></i> </a>' +
                ' <a href="' + base_url + '/admin/messages/download-receiver-message/' + message_receivers[i].id + '" class="btn btn-xs btn-warning download-email-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Download" target="_blank"> <i class="fa fa-download" aria-hidden="true"></i> </a>' +
                ' <button class="btn btn-xs btn-danger delete-message-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>';
        }
        all_rows += '<tr>' +
            '<td><input type="checkbox" data-id="' + message_receivers[i].id + '"></td>' +
            '<td>' + count + '</td>' +
            '<td>' + message_receivers[i].firstname + '</td>' +
            '<td>' + message_receivers[i].lastname + '</td>' +
            '<td>' + phone_or_push + '</td>' +
            '<td data-status="' + message_receivers[i].status + '" class="receiver-status"> ' + receiver_status + ' </td>' +
            '<td class="last-received">' + moment(message_receivers[i].last_received).format('YYYY-MM-DD  HH:mm') + '</td>' +
            '<td>' + action_buttons + '</td>' +
            '</tr>';
    }
    return all_rows;
}


//$(function () {
//    $(".filter-rules-selector").select2({
//        placeholder: "Select a Rule"
//    });
//    $('body').on('click', '#bt-send-filter-message', function (e) {
//        e.preventDefault();
//        $this = $(this);
//        var rule_id = $('.filter-rules-selector option:selected').val();
//        var message = $('#session_message').val();
//        var subject = $('#message_subject').val();
//        var data = {
//            'rule_id': rule_id,
//            'message': message,
//            'type': 'message',
//            'subject': subject,
//            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//        }
//        if (rule_id != '' && message != '' && subject != '') {
//            $('#loader').show();
//            $this.prop("disabled", true);
//            $.ajax({
//                url: base_url + '/admin/get-message-recipients/',
//                type: "POST",
//                data: {
//                    'rule_id': rule_id,
//                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
//                },
//                success: function (response) {
//                    if (response.error) {
//                        $.growl.error({message: response.error});
//                    } else {
//                        var total_recipients = response.total_recipients;
//                        var push_notification_recipients = response.push_notification_recipients;
//                        console.log(total_recipients);
//                        //if (total_recipients > 0) {
//                        bootbox.confirm("This message will be sent to " + total_recipients + " attendees and " + push_notification_recipients + " push notifications. Are you sure you want to send?", function (result) {
//                            if (result) {
//                                send_mail_message(data);
//                            } else {
//                                $('#loader').hide();
//                                $this.prop("disabled", false);
//                            }
//                        });
//                        //}
//                        //else {
//                        //    send_mail_message(data);
//                        //}
//                    }
//                }
//            });
//        }
//    });
//    $('body').on('click', '#bt-send-filter-sms', function (e) {
//        e.preventDefault();
//        $this = $(this);
//        var rule_id = $('.filter-rules-selector option:selected').val();
//        var message = $('#session_message').val();
//        var subject = $('#message_subject').val();
//        var data = {
//            'rule_id': rule_id,
//            'message': message,
//            'type': 'sms',
//            'subject': subject,
//            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//        }
//        if (rule_id != '' && message != '' && subject != '') {
//            $('#loader').show();
//            $this.prop("disabled", true);
//            $.ajax({
//                url: base_url + '/admin/get-message-recipients/',
//                type: "POST",
//                data: {
//                    'rule_id': rule_id,
//                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
//                },
//                success: function (response) {
//                    if (response.error) {
//                        $.growl.error({message: response.error});
//                    } else {
//                        var total_recipients = response.total_recipients;
//                        var push_notification_recipients = response.push_notification_recipients;
//                        console.log(total_recipients);
//                        //if (total_recipients > 0) {
//                        bootbox.confirm("This message will be sent to " + total_recipients + " attendees and "+ push_notification_recipients +" push notifications. Are you sure you want to send?", function (result) {
//                            if (result) {
//                                send_mail_message(data);
//                            } else {
//                                $('#loader').hide();
//                                $this.prop("disabled", false);
//                            }
//                        });
//                        //}
//                        //else {
//                        //    send_mail_message(data);
//                        //}
//                    }
//                }
//            });
//        }
//    });
//});
//
//function send_mail_message(data) {
//    $.ajax({
//        url: base_url + '/admin/send-message/',
//        type: "POST",
//        data: data,
//        success: function (result) {
//            $('#loader').hide();
//            $('#bt-send-filter-message').prop('disabled', false);
//            $('#bt-send-filter-sms').prop('disabled', false);
//            if (result.error) {
//                $.growl.error({message: result.error});
//            } else {
//                $.growl.notice({message: result.success});
//                //setTimeout(function () {
////                            window.location.href = '';
////                }, 3000);
//            }
//        }
//    });
//}

//Sortable attendee list
var f_sl_receivier_n = 0;
var f_sl_receiver_list = 1;
function sortReceiverList(f, n, elem_tbody) {
    var rows = elem_tbody.find('tr').get();
    rows.sort(function (a, b) {

        var A = getVal(a);
        var B = getVal(b);
        if (A > B) {
            return -1 * f;
        }
        if (A < B) {
            return 1 * f;
        }
        return 0;
    });

    function getVal(elm) {
        var v = $(elm).children('td').eq(n).text().toUpperCase();
        //if ($.isNumeric(v)) {
        //    v = parseInt(v, 10);
        //}
        return v;
    }

    $.each(rows, function (index, row) {
        $(this).find('td:nth-child(2)').html(index + 1);
        elem_tbody.append(row);
    });
}