$(function () {
    var $body = $('body');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();

    //   Email View Start
    setTotalSelectedAndUnselectedReceiver();

    $(".email-template-selector").select2({
        placeholder: "Select a Template"
    });
    //$(".email-filter-selector").select2({
    //    placeholder: "Select a Template"
    //});
    $body.on('click', '.new-email', function () {
        $('#email-modal').find('.modal-title').html('<i class="fa fa-lg fa-envelope-o"></i> Add New Email');
        $('#btn-save-email').css('display', 'inline');
        $('#btn-update-email').css('display', 'none');
        $('#email-sender').val($('.event-sender-email').val());
        $('#email-template').select2('val', '');
    });
    $body.on('click', '.email-settings', function () {
        var email_id = $(this).attr('data-id');
        getEmailDetails(email_id);
    });
    $body.on('click', '.view-email-settings', function () {
        var email_id = $(this).attr('data-id');
        getEmailDetails(email_id);
        $("body #email-modal").find("input, select").attr('disabled', 'disabled');
    });

    $body.on('click', '#btn-save-email', function () {
        addOrUpdateEmail($(this));
    });

    $body.on('click', '#btn-update-email', function () {
        addOrUpdateEmail($(this));
    });

    // Get Email Details
    function getEmailDetails(email_id) {
        $.ajax({
            url: base_url + '/admin/emails/' + email_id + '/',
            type: "GET",
            success: function (response) {
                if (response.error) {
                    $.growl.error({message: response.error});
                } else {
                    var email_data = response.email;
                    $('#email-modal').find('.modal-title').html('<i class="fa fa-lg fa-envelope-o"></i> ' + email_data.name);
                    $('#email-id').val(email_data.id);
                    $('#email-template').select2('val', email_data.template.id);
                    $('#email-name').val(email_data.name);
                    $('#email-subject').val(email_data.subject);
                    $('#email-sender').val(email_data.sender_email);
                    $('#btn-save-email').css('display', 'none');
                    $('#btn-update-email').css('display', 'inline');
                    $('#email-modal').modal();
                }
            }
        });
    }

    function addOrUpdateEmail($this) {
        var name = $('#email-name').val(),
            template_id = $('#email-template').select2('val'),
            subject = $('#email-subject').val(),
            email_sender = $('#email-sender').val();

        var requiredFields = [
            {fieldId: 'email-name', message: 'Name'},
            {fieldId: 'email-template', message: 'Template'},
            {fieldId: 'email-subject', message: 'Subject'}
        ];
        if (!requiredEmailFieldValidator(requiredFields)) {
            return;
        }
        var data = {
            name: name,
            template_id: template_id,
            subject: subject,
            email_sender: email_sender,
            csrfmiddlewaretoken: csrf_token
        };
        if ($this.attr('id') == 'btn-update-email') {
            var email_id = $('#email-id').val();
            data['id'] = email_id;
        }
        $.ajax({
            url: base_url + '/admin/emails/',
            type: 'POST',
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.message});
                    var updated_email = response.email;
                    var receivers_url = base_url + '/admin/emails-receivers/' + updated_email.id + '/';
                    var content_url = base_url + '/admin/emails-content/' + updated_email.id + '/';
                    var row = '' +
                        '<td>' + updated_email.id + '</td>' +
                        '<td>' + updated_email.name + '</td>' +
                        '<td>' + response.sent_receiver + '/' + response.total_receiver + '</td>' +
                        '<td>' +
                        '    <a href="' + receivers_url + '" class="btn btn-xs btn-info" data-toggle="tooltip" data-placement="top" title="" data-original-title="Receivers"> <i class="dropdown-icon fa fa-users"></i> </a>' +
                        '    <button class="btn btn-xs email-settings" data-id="' + updated_email.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Setting"> <i class="dropdown-icon fa fa-cog"></i> </button>' +
                        '    <a href="' + content_url + '" class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Email Content" target = _blank> <i class="dropdown-icon fa fa-pencil"></i> </a>' +
                        '    <button class="btn btn-xs btn-warning duplicate-email" data-id="' + updated_email.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"> <i class="dropdown-icon fa fa-files-o"></i> </button>' +
                        '    <button class="btn btn-xs btn-danger delete-email" data-id="' + updated_email.id + '" data-toggle="tooltip"data-placement="top" title=""data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>' +
                        '</td>';
                    if ($this.attr('id') === 'btn-update-email') {
                        $('body .email-table tbody tr').each(function () {
                            if ($(this).find('td:first-child').html() == updated_email.id) {
                                $(this).html(row);
                            }
                        });

                    } else {
                        $('body').find('.email-table').find('tbody').append('<tr>' + row + '</tr>');
                    }
                    $('#email-modal').modal('hide');
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

    function requiredEmailFieldValidator(requiredFields) {
        var message = '';
        var valid = true;
        for (var i = 0; i < requiredFields.length; i++) {
            var Id = requiredFields[i].fieldId;
            if ($.trim($('#' + Id).val()) == '') {
                message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
                valid = false;
            }
        }
        var sender = $.trim($('#email-sender').val());
        if (sender == null || sender == '') {
            message += "*Sender can't be blank" + "<br>";
            valid = false;
        }
        else if (!validateEmail(sender)) {
            message += "*Sender email is not valid" + "<br>";
            valid = false;
        }
        if (!valid) {
            $.growl.warning({message: message});
        }
        return valid;
    }

    $body.on('click', '.duplicate-email', function () {
        var email_id = $(this).data('id');
        var data = {
            email_id: email_id,
            csrfmiddlewaretoken: csrf_token
        }
        $.ajax({
            url: base_url + '/admin/emails-duplicate/',
            type: "POST",
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.success});
                    var email = response.email;
                    var receivers_url = base_url + '/admin/emails-receivers/' + email.id + '/';
                    var content_url = base_url + '/admin/emails-content/' + email.id + '/';
                    var row = '' +
                        '<td>' + email.id + '</td>' +
                        '<td>' + email.name + '</td>' +
                        '<td>' + response.sent_receiver + '/' + response.total_receiver + '</td>' +
                        '<td>' +
                        '    <a href="' + receivers_url + '" class="btn btn-xs btn-info" data-toggle="tooltip" data-placement="top" title="" data-original-title="Receivers"> <i class="dropdown-icon fa fa-users"></i> </a>' +
                        '    <button class="btn btn-xs email-settings" data-id="' + email.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Setting"> <i class="dropdown-icon fa fa-cog"></i> </button>' +
                        '    <a href="' + content_url + '" class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Email Content" target = _blank> <i class="dropdown-icon fa fa-pencil"></i> </a>' +
                        '    <button class="btn btn-xs btn-warning duplicate-email" data-id="' + email.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"> <i class="dropdown-icon fa fa-files-o"></i> </button>' +
                        '    <button class="btn btn-xs btn-danger delete-email" data-id="' + email.id + '" data-toggle="tooltip"data-placement="top" title=""data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>' +
                        '</td>';
                    $('body').find('.email-table').find('tbody').append('<tr>' + row + '</tr>');
                } else {
                    $.growl.warning({message: response.error});
                }
            }
        });
    });
    $body.on('click', '.delete-email', function (event) {
        var $this = $(this);
        bootbox.confirm("Are you sure you want to delete this Email?", function (result) {
            if (result) {
                var id = $this.attr('data-id');
                $.ajax({
                    url: base_url + '/admin/emails-delete/',
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

    // Email View End

    // Email Receivers View Start

    // Open Add receiver modal

    $body.on('click', '#open-email-filter-form', function () {
        $('#filter').select2('val', '');
    });

    // Select receivers using Status

    $body.on('click', '.select-status', function () {
        var status = $(this).attr('data-status');
        $('body').find('.select-all-receiver').prop('checked', false);
        var $receivers = $('.receivers-table').find('tbody tr');
        if (status == 'sent') {
            clearSelection();
            $receivers.each(function () {
                var $this = $(this);
                if ($.trim($this.find('.receiver-status').attr('data-status')) == 'sent') {
                    $this.find('input[type=checkbox]').prop('checked', true);
                    $this.find('input[type=checkbox]').onclick = false;
                }
            });
        }
        else if (status == 'not_sent') {
            clearSelection();
            $receivers.each(function () {
                var $this = $(this);
                if ($.trim($this.find('.receiver-status').attr('data-status')) == 'not_sent') {
                    $this.find('input[type=checkbox]').prop('checked', true);
                    $this.find('input[type=checkbox]').onclick = false;
                }
            });
        }
        else if (status == 'invert') {
            $receivers.each(function () {
                var $this = $(this);
                if ($this.find('input[type=checkbox]').prop('checked')) {
                    $this.find('input[type=checkbox]').prop('checked', false);
                } else {
                    $this.find('input[type=checkbox]').prop('checked', true);
                }
                //$this.find('input[type=checkbox]').trigger('click');
                $this.find('input[type=checkbox]').onclick = false;
            });
        }
        setTotalSelectedAndUnselectedReceiver();
    });

    // Select/DeSelect All receiver

    $body.on('click', '.select-all-receiver', function () {
        var $isChecked = this.checked;
        $('body').find('.receivers-table').find('tbody tr').each(function () {
            $(this).find('input[type=checkbox]').prop('checked', $isChecked);
        });
        setTotalSelectedAndUnselectedReceiver();
    });

    // Search Receiver

    // $body.on('keyup', '.search-email-receiver', function (e) {
    //     var $this = $(this);
    //     var search_key = $(this).val();
    //     var email_id = window.location.pathname.split('/')[3];
    //     var data = {
    //         search_key: search_key,
    //         email_id: email_id
    //     }
    //     $.ajax({
    //         url: base_url + '/admin/emails/search-receiver/',
    //         type: "GET",
    //         data: data,
    //         success: function (result) {
    //             $('.receivers-table').find('tbody').html(result);
    //         }
    //     });
    // });

    $body.on('keyup', '.search-email-receiver', function (e) {
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
                    var email = $this_tr.find('td:nth-child(5)').text().toUpperCase();
                    $this_tr.find('td').each(function () {
                        if (firstname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (lastname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (fullname.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        } else if (email.indexOf(search_key.toUpperCase()) != -1) {
                            found_receiver = true;
                        }
                    });
                    if (found_receiver) {
                        $this_tr.show();
                    }
                    // else {
                    //     $this_tr.find('td:first input').prop('checked', false);
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

    $body.on('click', '.change-email-receiver-selected', function () {
        var selected_receivers = [];
        var status = $.trim($(this).attr('data-status'));
        $('body').find('.receivers-table').find('tbody tr').each(function () {
            var $thisChecbox = $(this).find('input[type=checkbox]');
            if ($thisChecbox.prop('checked')) {
                selected_receivers.push($thisChecbox.attr('data-id'));
            }
        });
        if (selected_receivers.length > 0) {
            if (status == 'sent' || status == 'not_sent') {
                changeEmailReceiversStatus(selected_receivers, status);
            } else if (status == 'delete') {
                bootbox.confirm("Are you sure you want to delete selected receivers?", function (result) {
                    if (result) {
                        deleteEmailReceivers(selected_receivers);
                    }
                });
            }
        } else {
            $.growl.warning({message: 'Pls select a receivers first'});
        }

        clog(selected_receivers);
    });

    // Change receiver status

    $body.on('click', '.change-email-receiver-status', function () {
        var selected_receivers = [];
        var receiver_id = $.trim($(this).closest('tr').find('input[type=checkbox]').attr('data-id'));
        var current_status = $.trim($(this).closest('tr').find('.receiver-status').attr('data-status'));
        if (receiver_id != '' && receiver_id != undefined && current_status != '' && current_status != undefined) {
            selected_receivers.push(receiver_id);
            var status = "not_sent";
            if (current_status == 'not_sent') {
                status = "sent";
            }
            changeEmailReceiversStatus(selected_receivers, status);
        }
    });

    // Delete Email Receiver

    $body.on('click', '.delete-email-receiver', function () {
        var selected_receivers = [];
        var receiver_id = $.trim($(this).closest('tr').find('input[type=checkbox]').attr('data-id'));
        if (receiver_id != '' && receiver_id != undefined) {
            selected_receivers.push(receiver_id);
            bootbox.confirm("Are you sure you want to delete this receiver?", function (result) {
                if (result) {
                    deleteEmailReceivers(selected_receivers);
                }
            });
        }
    });

    // Select receiver to send mail

    $body.on('click', '.send-email', function () {
        var selected_receivers = [];
        var status = $.trim($(this).attr('data-status'));
        var $allReceiver = $('body').find('.receivers-table').find('tbody tr');
        if (status == 'not_sent') {
            $allReceiver.each(function () {
                var receiver_status = $(this).find('.receiver-status').attr('data-status');
                if ($.trim(receiver_status) == status) {
                    var receiver_id = $.trim($(this).find('input[type=checkbox]').attr('data-id'));
                    // selected_receivers.push({id: receiver_id});
                    selected_receivers.push(receiver_id);
                }
            });
            if (selected_receivers.length > 0) {
                bootbox.confirm("You are about to send this email to " + selected_receivers.length + " receivers. Are you sure you want to continue?", function (result) {
                    if (result) {
                        sendEmail(selected_receivers);
                    }
                });
            } else {
                $.growl.warning({message: 'There is no receiver to send mail'});
            }
        } else if (status == 'selected') {
            $allReceiver.each(function () {
                var $thisChecbox = $(this).find('input[type=checkbox]');
                if ($thisChecbox.prop('checked')) {
                    // selected_receivers.push({id: $thisChecbox.attr('data-id')});
                    selected_receivers.push($thisChecbox.attr('data-id'));
                }
            });
            if (selected_receivers.length > 0) {
                bootbox.confirm("You are about to send this email to " + selected_receivers.length + " receivers. Are you sure you want to continue?", function (result) {
                    if (result) {
                        sendEmail(selected_receivers);
                    }
                });
            } else {
                $.growl.warning({message: 'There is no receiver to send mail'});
            }
        } else {
            $.growl.warning({message: 'something went wrong'});
        }

    });

    // import receivers using filter

    $body.on('click', '.add-email-filer-receiver', function () {
        var filter_id = $('#filter').select2('val');
        if (filter_id != '' && filter_id != null && filter_id != undefined) {
            $('body .loader').show();
            $('.add-email-filer-receiver').prop("disabled", true);
            var email_id = window.location.pathname.split('/')[3];
            $.ajax({
                url: base_url + '/admin/emails/import-filter-receiver/',
                type: "POST",
                data: {
                    email_id: email_id,
                    filter_id: filter_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $('body .loader').hide();
                    $('.add-email-filer-receiver').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var email_receivers = result.email_receivers;
                        var receiver_rows = addEmailAttendeetoReceiverTable(admin_permission, email_receivers);
                        $('#email-from-filter').modal('hide');
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


    // import receivers using Clipboard

    $body.on('click', '.add-email-receivers-clipboard', function () {
        var clipboard_data = $.trim($('.clipboard-data').val());
        if (clipboard_data != '' && clipboard_data != null && clipboard_data != undefined) {
            $('body .loader').show();
            $('.add-email-receivers-clipboard').prop("disabled", true);
            var email_id = window.location.pathname.split('/')[3];
            $.ajax({
                url: base_url + '/admin/emails/import-clipboard-receiver/',
                type: "POST",
                data: {
                    email_id: email_id,
                    clipboard_data: clipboard_data,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $('body .loader').hide();
                    $('.add-email-receivers-clipboard').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var email_receivers = result.email_receivers;
                        var receiver_rows = addEmailAttendeetoReceiverTable(admin_permission, email_receivers);
                        $('#email-from-clipboard').modal('hide');
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


    $body.on('click', '#btn-import-mail-excel', function () {
        try {
            $('body .loader').show();
            $('#btn-import-mail-excel').prop("disabled", true);
            var email_id = window.location.pathname.split('/')[3];
            var formdata = new FormData();
            formdata.append('upload_file', $('#upload_excel_file')[0].files[0]);
            formdata.append('csrfmiddlewaretoken', csrf_token);
            formdata.append('email_id', email_id);
            $.ajax({
                url: base_url + '/admin/emails/import-excel-receiver/',
                type: 'POST',
                data: formdata,
                async: false,
                cache: false,
                contentType: false,
                processData: false,
                success: function (result) {
                    $('body .loader').hide();
                    $('#btn-import-mail-excel').prop("disabled", false);
                    if (result.success) {
                        var admin_permission = result.admin_permission;
                        var email_receivers = result.email_receivers;
                        var receiver_rows = addEmailAttendeetoReceiverTable(admin_permission, email_receivers);
                        $('#email-from-excel-import').modal('hide');
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

    // Change Total Selectd And Unselected Receiver By clicking Checkbox

    $body.on('click', '.receivers-table tbody tr input[type=checkbox]', function (e) {
        //console.log(e.originalEvent.isTrusted);
        //if(e.originalEvent.isTrusted){
        setTotalSelectedAndUnselectedReceiver();
        //}
    });


    // Clear receiver selection function

    function clearSelection() {
        $('body').find('.receivers-table').find('tbody tr').each(function () {
            $(this).find('input[type=checkbox]').prop('checked', false);
        });
    }

    // Delete receiver function

    function deleteEmailReceivers(selected_receivers) {
        $.ajax({
            url: base_url + '/admin/emails/delete-receiver/',
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
                            if (receiver_id == selected_receivers[i]) {
                                $(this).remove();
                            }
                        }
                    });
                    setTotalSelectedAndUnselectedReceiver();
                } else {
                    $.growl.error({message: result.message});
                }

            }
        });
    }

    // Change receivers status

    function changeEmailReceiversStatus(selected_receivers, status) {
        $.ajax({
            url: base_url + '/admin/emails/change-receiver-status/',
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
                            if (receiver_id == selected_receivers[i]) {
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

    // Send mail Function

    function sendEmail(selected_receivers) {
        $('body .loader').show();
        $('.send-dropdown').prop("disabled", true);
        var email_id = window.location.pathname.split('/')[3];
        $.ajax({
            url: base_url + '/admin/emails/send-email/',
            type: "POST",
            data: {
                status: status,
                email_id: email_id,
                receivers: JSON.stringify(selected_receivers),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                $('body .loader').hide();
                $('.send-dropdown').prop("disabled", false);
                if (result.success) {
                    $.growl.notice({message: result.message});
                    var updated_receivers = result.updated_receivers;
                    var last_received = result.last_received;
                    var status = result.status;
                    $('.select-all-receiver').prop('checked', false);
                    $('body').find('.receivers-table').find('tbody tr').each(function () {
                        var receiver_id = $(this).find('input[type=checkbox]').attr('data-id');
                        for (var i = 0; i < updated_receivers.length; i++) {
                            if (receiver_id == updated_receivers[i].id) {
                                $(this).find('input[type=checkbox]').prop('checked', false);
                                $(this).find('.receiver-status').attr('data-status', status).html('Sent');
                                $(this).find('.last-received').html(moment(last_received, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm'));
                                // if (updated_receivers[i].status == 'sent') {
                                //     $(this).find('.receiver-status').attr('data-status', updated_receivers[i].status).html('Sent');
                                // } else if (updated_receivers[i].status == 'not_sent') {
                                //     $(this).find('.receiver-status').attr('data-status', updated_receivers[i].status).html('Not Sent');
                                // }
                                // $(this).find('.last-received').html(moment(updated_receivers[i].last_received, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm'));
                            }
                        }
                    });
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


    // Email Receivers View End

});

function addEmailAttendeetoReceiverTable(admin_permission, email_receivers) {
    var all_rows = '';
    for (var i = 0; i < email_receivers.length; i++) {
        var count = i + 1;
        var receiver_status = "Not Sent";
        if (email_receivers[i].status == "sent") {
            receiver_status = "Sent";
        }
        var action_buttons = '<a href="' + base_url + '/admin/emails/receiver-preview/' + email_receivers[i].id + '" class="btn btn-xs preview-receiver-email-content" data-toggle="tooltip" data-placement="top" title="" data-original-title="Preview" target="_blank"><i class="fa fa-share-square-o" aria-hidden="true"></i></a>' +
            ' <a href="' + base_url + '/admin/emails/download-receiver-email/' + email_receivers[i].id + '" class="btn btn-xs btn-warning download-email-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Download" target="_blank"> <i class="fa fa-download" aria-hidden="true"></i> </a>';
        if (admin_permission) {
            action_buttons = '<button class="btn btn-xs btn-info change-email-receiver-status" data-toggle="tooltip" data-placement="top" title="" data-original-title="Change Status"><i class="fa fa-refresh" aria-hidden="true"></i></button>' +
                ' <a href="' + base_url + '/admin/emails/receiver-preview/' + email_receivers[i].id + '" class="btn btn-xs preview-receiver-email-content" data-toggle="tooltip" data-placement="top" title="" data-original-title="Preview" target="_blank"><i class="fa fa-share-square-o" aria-hidden="true"></i> </a>' +
                ' <a href="' + base_url + '/admin/emails/download-receiver-email/' + email_receivers[i].id + '" class="btn btn-xs btn-warning download-email-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Download" target="_blank"> <i class="fa fa-download" aria-hidden="true"></i> </a>' +
                ' <button class="btn btn-xs btn-danger delete-email-receiver" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"> <i class="dropdown-icon fa fa-times-circle"></i> </button>';
        }
        all_rows += '<tr>' +
            '<td><input type="checkbox" data-id="' + email_receivers[i].id + '"></td>' +
            '<td>' + count + '</td>' +
            '<td>' + email_receivers[i].firstname + '</td>' +
            '<td>' + email_receivers[i].lastname + '</td>' +
            '<td>' + email_receivers[i].email + '</td>' +
            '<td data-status="' + email_receivers[i].status + '" class="receiver-status"> ' + receiver_status + ' </td>' +
            '<td class="last-received">' + moment(email_receivers[i].last_received).format('YYYY-MM-DD  HH:mm') + '</td>' +
            '<td>' + action_buttons + '</td>' +
            '</tr>';
    }
    return all_rows;
}