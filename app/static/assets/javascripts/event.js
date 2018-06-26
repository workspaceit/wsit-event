function changeEvent(event_id) {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: base_url + '/admin/change-event/',
        type: "POST",
        data: {
            event_id: event_id,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.error) {
                $.growl.error({message: result.error});
            } else {
                $.growl.notice({message: result.success});
                $('#change-event-modal').modal('hide');
                setTimeout(function () {
                    window.location.href = base_url + "/admin/";
                }, 500);
            }
        }
    });
}
$(function () {
    $('#event-start-date').datepicker('setDate', new Date());
    $('#event-end-date').datepicker('setDate', new Date());
    var $body = $('body');
    $body.on('click', '.get-all-events', function () {
        $.ajax({
            url: base_url + '/admin/get-all-events/',
            type: "GET",
            success: function (result) {
                $('#change-event-modal').html(result);
                $('#change-event-modal').modal();
            }
        });
    });
    $("#select2-manager").select2({
        maximumSelectionLength: 1,
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/get-managers/',
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
        }
    });

    $body.on('click', '.change-event', function () {
        var event_id = $('#choose_event').val();

        clog(event_id);
        if (event_id == "" || event_id == null) {
            $.growl.warning({message: "Please Select an Event"});
        } else {
            changeEvent(event_id)
        }
    });


    $body.on('click', '.add-project', function () {
        var fieldsToClear = [
            'event-name', 'event-description', 'event-url', 'event-address'
        ];
        clearEventForm(fieldsToClear);
        $('#event-url').prop("disabled", false);
        $('#event-start-date').data('datepicker').setDate(null);
        $('#event-end-date').data('datepicker').setDate(null);
        $('#select2-manager').select2('val', '');
        $('#add-project').find('.modal-title').html('Add Event');
        $('#add-project').modal();
    });

    $body.on('click', '#btn-save-event', function () {
        addOrUpdateEvent($(this));
    });

    $body.on('click', '#btn-update-event', function () {
        addOrUpdateEvent($(this));
    });

    $body.on('click', '.btn-edit-event', function () {
        var event_id = $(this).data('id');
        $('#edit-event-id').val(event_id);
        $.ajax({
            url: base_url + '/admin/events/' + event_id + '/',
            type: "GET",
            success: function (response) {
                if (response.success) {
                    var event = response.event;
                    var admin_list = response.admin_list;
                    clog(event)
                    $('#event-name').val(event.name);
                    $('#event-description').val(event.description);
                    $('#event-url').val(event.url);
                    $('#event-url').prop("disabled", true);
                    $('#select2-manager').select2('data', admin_list);
                    $('#event-address').val(event.address);
                    $('#event-start-date').val(moment(event.start).format('MM/DD/YYYY'));
                    $('#event-end-date').val(moment(event.end).format('MM/DD/YYYY'));
                    $('#btn-save-event').hide();
                    $('#btn-update-event').show();
                    $('#add-project').find('.modal-title').html('Edit Event');
                    $('#add-project').modal();
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

    $body.on('click', '.btn-delete-event', function (event) {
        var $this = $(this);
        var event_name = $this.closest('tr').find('td:eq(1)').html();
        bootbox.confirm({
            message: "You are about to delete all content and attendees of the event "+event_name+". This action can not be undone. Are you sure?",
            buttons: {
                confirm: {
                    label: 'Yes',
                    className: 'btn-success'
                },
                cancel: {
                    label: 'No',
                    className: 'btn-danger'
                }
            },
            callback: function (result) {
                if (result) {
                    var id = $this.attr('data-id');
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $('.loader').show();
                    $this.prop('disabled',true);
                    $.ajax({
                        url: base_url + '/admin/events/delete/',
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
                            $('.loader').hide();
                            $this.prop('disabled',false);
                        }
                    });
                }
            }
        });
    });

    $body.on('click', '.btn-view-logged-in-page', function () {
        var email = $(this).attr('data-email');
        var event_id = $(this).attr('data-event-id');
        var page_url = $(this).attr('data-url');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var $button = $(this);
        $button.prop('disabled', true);
        $.ajax({
            url: base_url + '/admin/events/logged-in/',
            type: "POST",
            async: false,
            data: {
                email: email,
                event_id: event_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                $button.prop('disabled', false);
                if (result.success) {
                    window.open(base_url + '/' + page_url, '_blank');
                }

            }
        });
    });

    $body.on('click', '.btn-view-logged-out-page', function () {
        var page_url = $(this).attr('data-url');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var $button = $(this);
        $button.prop('disabled', true);
        $.ajax({
            url: base_url + '/admin/events/logged-out/',
            type: "POST",
            async: false,
            data: {
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                $button.prop('disabled', false);
                if (result.success) {
                    window.open(base_url + '/' + page_url, '_blank');
                }
            }
        });
    });

    function addOrUpdateEvent(button) {

        var name = $('#event-name').val(),
            description = $('#event-description').val(),
            start_date = $('#event-start-date').val(),
            end_date = $('#event-end-date').val(),
            url = $('#event-url').val(),
            address = $('#event-address').val(),
            admin = $('#select2-manager').select2('val'),
            csrf_token = $('input[name=csrfmiddlewaretoken]').val();

        var requiredFields = [
            {fieldId: 'event-name', message: 'Name'},
            {fieldId: 'event-url', message: 'URL'},
            //{fieldId: 'event-description', message: 'Description'},
            {fieldId: 'event-start-date', message: 'Start Date'},
            {fieldId: 'event-end-date', message: 'End Date'},
            //{fieldId: 'select2-manager', message: 'Admin'},
            //{fieldId: 'event-address', message: 'Address'}
        ];

        if (!requiredEventFieldValidator(requiredFields)) {
            return;
        }

        var start = moment(start_date, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD');
        var end = moment(end_date, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD');
        var data = {
            name: name,
            description: description,
            start: start,
            end: end,
            address: address,
            url: url,
            admin: JSON.stringify(admin),
            csrfmiddlewaretoken: csrf_token
        }
        if (button.attr('id') == 'btn-update-event') {
            var event_id = $('#edit-event-id').val();
            data['id'] = event_id;
        }
        clog(data);

        $('.loader').show();
        $.ajax({
            url: base_url + '/admin/event/',
            type: "POST",
            data: data,
            success: function (result) {
                $('.loader').hide();
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    var updated_event = result.event;
                    var row = '' +
                        '<td>' + updated_event.id + '</td>' +
                        '      <td>' + updated_event.name + '</td>' +
                        '      <td>' + moment(updated_event.start, 'YYYY-MM-DD').format('YYYY-MM-DD') + '</td>' +
                        '      <td>' + moment(updated_event.end, 'YYYY-MM-DD').format('YYYY-MM-DD') + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs btn-edit-event" data-id="' + updated_event.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="EDIT Event"><i class="dropdown-icon fa fa-pencil"></i></button>' +
                        '          <button class="btn btn-xs btn-danger btn-delete-event" data-id="' + updated_event.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
                    if (button.attr('id') === 'btn-update-event') {
                        $('body .data-table-events tbody tr').each(function () {
                            if ($(this).find('td:first-child').html() == updated_event.id) {
                                $(this).html(row);
                            }
                        });
                    } else {
                        $('.data-table-events').find('tbody').append('<tr>' + row + '</tr>');
                        changeEvent(updated_event.id);
                    }
                    $('#add-project').modal('hide');
                }
            }
        });

    }

    function clearEventForm(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).val('');
        }
    }

    function requiredEventFieldValidator(requiredFields) {
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

});
