$(function () {
    $body.on('click', '#btn-add-admin', function () {
        var fieldsToClear = [
            'firstname', 'lastname', 'company', 'email', 'password', 'phonenum'
        ];
        clearForm(fieldsToClear);
        $('#permissions').html('');
        $('#btn-save-admin').show();
        $('#btn-update-admin').hide();
        $('.add-event-permission').select2("val", "");
        $('#admins-edit-admin').find('.modal-title').html('Add Admin');
        $('#admins-edit-admin').modal();

    });

    function clearForm(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).val('');
        }
    }

    $body.on('click', '.btn-edit-admin', function () {
        var admin_id = $(this).data('id');
        $('#admin-id').val(admin_id);
        $('#permissions').html('');
        $.ajax({
            url: base_url + '/admin/admins/' + admin_id + '/',
            type: "GET",
            success: function (response) {
                clog(response);

                if (response.success) {
                    console.log(response)
                    var admin = response.user;
                    var events = response.events;
                    var content_permission = response.content_permission;
                    var group_permission = response.group_permission;
                    clog(group_permission);

                    $('#firstname').val(admin.firstname);
                    $('#lastname').val(admin.lastname);
                    $('#email').val(admin.email);
                    $('#company').val(admin.company);
                    $('#password').val("");
                    $('#phonenum').val(admin.phonenumber);
                    $('.add-event-permission').select2('data', events);

                    $('#btn-save-admin').hide();
                    $('#btn-update-admin').show();
                    $('#admins-edit-admin').find('.modal-title').html('Edit Admin');
                    $('#admins-edit-admin').modal();

                    for (var i = 0; i < events.length; i++) {
                        var event_id = events[i]['id'];
                        $.ajax({
                            url: base_url + '/admin/admin-render-permission-eventwise/',
                            type: "POST",
                            async:false,
                            data: {
                                id: event_id,
                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                            },
                            success: function (data) {

                                var write_count=0;
                                var read_count=0;
                                var group_write_count=0;
                                var group_read_count=0;
                                $('#permissions').append(data);
                                for (var j = 0; j < content_permission.length; j++) {
                                    $('#collapseOne' + content_permission[j].event.id).find('input[name=' + content_permission[j].content + ']').each(function () {
                                        if ($(this).val() == content_permission[j].access_level) {
                                            $(this).prop('checked', true);
                                        }
                                    });
                                }
                                for (var k = 0; k < group_permission.length; k++) {
                                    $('input[name=' + group_permission[k].group.id + ']').each(function () {
                                        if ($(this).val() == group_permission[k].access_level) {
                                            $(this).prop('checked', true);
                                        }
                                    });
                                }

                                if($('#admins-edit-admin #permissions').find('.permission-read-'+event_id+':not(:checked)').length > 0){
                                    $(".permission-read-all"+event_id).prop('checked', false);
                                }else{
                                    $(".permission-read-all"+event_id).prop('checked', true);
                                }
                                if($('#admins-edit-admin #permissions').find('.permission-write-'+event_id+':not(:checked)').length > 0){
                                    $(".permission-write-all"+event_id).prop('checked', false);
                                }else{
                                    $(".permission-write-all"+event_id).prop('checked', true);
                                }
                                if($('#admins-edit-admin #permissions').find('.group-permission-read-'+event_id+':not(:checked)').length > 0){
                                    $(".group-permission-read-all"+event_id).prop('checked', false);
                                }else{
                                    $(".group-permission-read-all"+event_id).prop('checked', true);
                                }
                                if($('#admins-edit-admin #permissions').find('.group-permission-write-'+event_id+':not(:checked)').length > 0){
                                    $(".group-permission-write-all"+event_id).prop('checked', false);
                                }else{
                                    $(".group-permission-write-all"+event_id).prop('checked', true);
                                }
                            }
                        });
                    }
                }
                else {
                    var errors = response.message;
                }
            },
            error: function () {
                //alert();
            }
        });
    });
    function addOrUpdateAdmin(button) {
        var firstname = $('#firstname').val(),
            lastname = $('#lastname').val(),
            company = $('#company').val(),
            email = $('#email').val(),
            password = $('#password').val(),
            phonenumber = $('#phonenum').val(),
            events = $('#event_access').val(),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val();

        var requiredFields = [
            {fieldId: 'firstname', message: 'Firstname'},
            {fieldId: 'lastname', message: 'Lastname'},
            {fieldId: 'company', message: 'company'},
            {fieldId: 'email', message: 'email'}

        ];
        var data = {
            firstname: firstname,
            lastname: lastname,
            company: company,
            email: email,
            password: password,
            phonenumber: phonenumber,
            events: events,
            csrfmiddlewaretoken: csrfToken
        };
        if (button.attr('id') == 'btn-update-admin') {
            var admin_id = $('#admin-id').val();
            data['id'] = admin_id;
        }
        else {
            requiredFields.push({fieldId: 'password', message: 'Password'})
        }
        if (!requiredFieldValidator(requiredFields)) {
            return;
        }


        if (!validateEmail(email)) {
            $.growl.warning({message: "Please enter a valid email" + "\n"});
            return;
        }


        var events = [];
        $('.event').each(
            function () {
                var event_id = $(this).attr('id');
                var contents = []
                $(this).find('.content').each(
                    function () {
                        var content = $(this).attr('name');

                        if ($(this).prop("checked")) {

                            var access = $(this).val();
                            if (access != undefined) {
                                dataCont = {
                                    "content": content,
                                    "access": access
                                }
                                contents.push(dataCont)
                            }
                        }


                    }
                );
                var questions_group = []
                $(this).find('.qn_group').each(
                    function () {
                        var group_id = $(this).attr('name');

                        if ($(this).prop("checked")) {

                            var access = $(this).val();
                            if (access != undefined) {
                                dataCont = {
                                    "group_id": group_id,
                                    "access": access
                                }
                                questions_group.push(dataCont)
                            }
                        }


                    }
                );

                evnt_obj = {
                    "event_id": event_id,
                    "contents": contents,
                    "questions": questions_group
                }

                events.push(evnt_obj);

            }
        );

//        var permissions={
//            "events":events
//        }
        clog(events);
        data['permissions'] = JSON.stringify(events)

        $.ajax({
            url: base_url + '/admin/admin/',
            type: 'POST',
            data: data,
            dataType: "json",
            success: function (response) {

                if (response.success) {
                    $.growl.notice({message: response.success});
                    var updated_admin = response.admin;
                    var actionbutton;
                    if (updated_admin.status == "inactive") {
                        actionbutton = '    <button class="btn btn-xs btn-primary btn-active-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="active"><i class="dropdown-icon fa fa-unlock"></i></button>'
                    }
                    if (updated_admin.status == "active") {
                        actionbutton = '    <button class="btn btn-xs btn-warning btn-inactive-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="inactive"><i class="dropdown-icon fa fa-lock"></i></button>'
                    }
                    var row = '' +
                        '<td>' + updated_admin.id + '</td>' +
                        '<td>' + updated_admin.firstname + '</td>' +
                        '<td>' + updated_admin.lastname + '</td>' +
                        '<td>' + updated_admin.email + '</td>' +
                        '<td>' + updated_admin.company + '</td>' +
                        '<td>' + updated_admin.phonenumber + '</td>' +
                        '<td>' + updated_admin.status + '</td>' +
                        '<td>' +
                        '    <button class="btn btn-xs btn-edit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        actionbutton +

                        '    <button class="btn btn-xs btn btn-permit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Permission"><i class="dropdown-icon fa fa-cogs"></i></button>' +
                        '</td>';
                    if (button.attr('id') === 'btn-update-admin') {
                        $('body .admin-table tbody tr').each(function () {
                            if ($(this).find('td:first-child').html() == updated_admin.id) {
                                $(this).html(row);
                            }
                        });

                    } else {
                        $('body .admin-table').find('tbody').append('<tr>' + row + '</tr>');
                    }

                    $('#admins-edit-admin').modal('hide');
                }
                else {
                    var errors = response.error;
                    $.growl.warning({message: errors});
                }
            },
            error: function (e) {
                clog(e);
            }
//            complete : function(){
//            }
        });
    }

    $body.on('click', '#btn-save-admin', function () {
        addOrUpdateAdmin($(this));
    });

    $body.on('click', '#btn-update-admin', function () {
        addOrUpdateAdmin($(this));
    });

    $body.on('click', '.btn-active-admin', function () {
        csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var admin_id = $(this).data('id');
        $('#admin-id').val(admin_id);
        $.ajax({
            url: base_url + '/admin/admin-change-status/',
            type: "POST",
            dataType: "json",
            data: {
                status: "active",
                id: admin_id,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                if (response.success) {
                    clog(response.admin.status)
                    var updated_admin = response.admin;
                    var actionbutton;
                    if (updated_admin.status == "inactive") {
                        actionbutton = '    <button class="btn btn-xs btn-primary btn-active-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="active"><i class="dropdown-icon fa fa-unlock"></i></button>'
                    }
                    if (updated_admin.status == "active") {
                        actionbutton = '    <button class="btn btn-xs btn-warning btn-inactive-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="inactive"><i class="dropdown-icon fa fa-lock"></i></button>'
                    }
                    var row = '' +
                        '<td>' + updated_admin.id + '</td>' +
                        '<td>' + updated_admin.firstname + '</td>' +
                        '<td>' + updated_admin.lastname + '</td>' +
                        '<td>' + updated_admin.email + '</td>' +
                        '<td>' + updated_admin.company + '</td>' +
                        '<td>' + updated_admin.phonenumber + '</td>' +
                        '<td>' + updated_admin.status + '</td>' +
                        '<td>' +
                        '    <button class="btn btn-xs btn-edit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        actionbutton +

                        '    <button class="btn btn-xs btn btn-permit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Permission"><i class="dropdown-icon fa fa-cogs"></i></button>' +
                        '</td>';

                    $('body .admin-table tbody tr').each(function () {
                        if ($(this).find('td:first-child').html() == updated_admin.id) {
                            $(this).html(row);
                        }
                    });

                    $('#admins-edit-admin').modal('hide');
                }
                else {
                    var errors = response.error;
                    $.growl.warning({message: errors});
                }
            },
            error: function () {
                //alert();
            }
        });
    });

    $body.on('click', '.btn-inactive-admin', function () {
        csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var admin_id = $(this).data('id');
        $('#admin-id').val(admin_id);
        $.ajax({
            url: base_url + '/admin/admin-change-status/',
            type: "POST",
            dataType: "json",
            data: {
                status: "inactive",
                id: admin_id,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                if (response.success) {
                    var updated_admin = response.admin;

                    var actionbutton;
                    if (updated_admin.status == "inactive") {
                        clog(response.admin.status)
                        actionbutton = '    <button class="btn btn-xs btn-primary btn-active-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="active"><i class="dropdown-icon fa fa-unlock"></i></button>'
                    }
                    if (updated_admin.status == "active") {
                        actionbutton = '    <button class="btn btn-xs btn-warning btn-inactive-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="inactive"><i class="dropdown-icon fa fa-lock"></i></button>'
                    }
                    var row = '' +
                        '<td>' + updated_admin.id + '</td>' +
                        '<td>' + updated_admin.firstname + '</td>' +
                        '<td>' + updated_admin.lastname + '</td>' +
                        '<td>' + updated_admin.email + '</td>' +
                        '<td>' + updated_admin.company + '</td>' +
                        '<td>' + updated_admin.phonenumber + '</td>' +
                        '<td>' + updated_admin.status + '</td>' +
                        '<td>' +
                        '    <button class="btn btn-xs btn-edit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        actionbutton +

                        '    <button class="btn btn-xs btn btn-permit-admin" data-id="' + updated_admin.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-cogs"></i></button>' +
                        '</td>';

                    $('body .admin-table tbody tr').each(function () {
                        if ($(this).find('td:first-child').html() == updated_admin.id) {
                            clog(updated_admin.id)
                            $(this).html(row);
                        }
                    });

                    $('#admins-edit-admin').modal('hide');
                }
                else {
                    var errors = response.error;
                    $.growl.warning({message: errors});
                }
            },
            error: function () {
                //alert();
            }
        });
    });

    $(".add-event-permission").select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/get-events/',
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
                clog(lastResults);

                return data;
            }
        }
//        createSearchChoice: function (term) {
//            var text = term + (lastResults.some(function(r) { return r.text == term }) ? "" : " (new)");
//            return { id: term, text: text };
//        },
    });
    $('.add-event-permission').on("select2-selecting", function (e) {
        var event_id = e.object.id;
        $.ajax({
            url: base_url + '/admin/admin-render-permission-eventwise/',
            type: "POST",
            data: {
                id: event_id,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                $('#permissions').append(data);
            }
        });

    });
    $('.add-event-permission').on("select2-removed", function (e) {
        $('#' + e.val).remove()
    });

    $body.on('change', ':checkbox', function () {
        var th = $(this), name = th.prop('name');
        if (th.is(':checked')) {
            th.closest('.note').find(':checkbox[name="' + name + '"]').not($(this)).prop('checked', false);
        }
    });

    function prepareValidationMessage(errors) {
        var msg = '';
        for (var key in errors) {
            msg += key + ': ' + errors[key][0] + '<br>';
        }
        $.growl.warning({message: msg});
    }

    function requiredFieldValidator(requiredFields) {
        var message = '';
        var valid = true;
        for (var i = 0; i < requiredFields.length; i++) {
            var Id = requiredFields[i].fieldId;
            if ($('#' + Id).val() == '') {
                message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
                valid = false;
            }
        }
        if (!valid) {
            $.growl.warning({message: message});
        }
        return valid;
    }

    /**
     * Select all read or write checkbox
     */
    $body.on('click', '#permission-read-all', function () {
        var event_id=$(this).attr('event-id');
        var form_read_checkbox=".permission-read-"+event_id;
        var form_write_checkbox=".permission-write-"+event_id;
        if($(this).is(':checked')){
            $(form_read_checkbox).prop("checked", true);
            $(form_write_checkbox).prop("checked", false);
            $(".permission-write-all"+event_id).prop("checked", false);
        }
        else{
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", false);
        }
    });

    $body.on('click', '#permission-write-all', function () {
        var event_id=$(this).attr('event-id');
        var form_read_checkbox=".permission-read-"+event_id;
        var form_write_checkbox=".permission-write-"+event_id;
        if($(this).is(':checked')){
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", true);
            $(".permission-read-all"+event_id).prop("checked", false);
        }
        else{
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", false);
        }
    });

    /**
     * Select group all read or write checkbox
     */
    $body.on('click', '#group-permission-read-all', function () {
        var event_id=$(this).attr('event-id');
        var form_read_checkbox=".group-permission-read-"+event_id;
        var form_write_checkbox=".group-permission-write-"+event_id;
        if($(this).is(':checked')){
            $(form_read_checkbox).prop("checked", true);
            $(form_write_checkbox).prop("checked", false);
            $(".group-permission-write-all"+event_id).prop("checked", false);
        }
        else{
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", false);
        }
    });
    $body.on('click', '#group-permission-write-all', function () {
        var event_id=$(this).attr('event-id');
        var form_read_checkbox=".group-permission-read-"+event_id;
        var form_write_checkbox=".group-permission-write-"+event_id;
        if($(this).is(':checked')){
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", true);
            $(".group-permission-read-all"+event_id).prop("checked", false);
        }
        else{
            $(form_read_checkbox).prop("checked", false);
            $(form_write_checkbox).prop("checked", false);
        }
    });

});