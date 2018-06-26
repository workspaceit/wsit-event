$(function () {
    $('#travel-departure-date').datepicker('setDate', new Date());
    $('#travel-arrival-date').datepicker('setDate', new Date());
    $('#travel-reg-between-start').datepicker('setDate', new Date());
    $('#travel-reg-between-end').datepicker('setDate', new Date());

    var $body = $('body');

    function clearTravelForm(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).val('');
        }
        $('#travel-departure-date').data('datepicker').setDate(null);
        $('#travel-arrival-date').data('datepicker').setDate(null);
        $('#travel-reg-between-start').data('datepicker').setDate(null);
        $('#travel-reg-between-end').data('datepicker').setDate(null);
        $('#travel-location').select2("val", "");
        $('#travel-group').select2("val", "");
        //$('#travel-tags').select2("val", "");
        $('#travel-bound').val("");
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('html.set', '');
        $('.travel-language-preset-selector').select2("val", "");
        $('.language-preset-selector').hide();
        // setTimeout(function () {
        //     editor.setValue('');
        // }, 400);
    }

    function prepareTravelValidationMessage(errors) {
        var msg = '';
        for (var key in errors) {
            msg += key + ': ' + errors[key][0] + '<br>';
        }
        $.growl.warning({message: msg});
    }

    function requiredTravelFieldValidator(requiredFields) {
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

    $body.on('click', '#btn-add-travel', function () {
        var fieldsToClear = [
            'travel-name', 'travel-group', 'travel-max-attendees', 'travel-departure-city', 'travel-arrival-city'
        ];
        clearTravelForm(fieldsToClear);
        $('#btn-save-travel').show();
        $('#btn-update-travel').hide();
//        $('#btn-remove-queue').hide();
        $('#travels-edit-travel').find('.modal-title').html('Add Travel');
        $('#travels-edit-travel').modal();

    });

    $body.on('click', '.btn-edit-travel', function () {
        var travel_id = $(this).data('id');
        var modal_class = 'travels-edit-travel';
        showTravel(travel_id, modal_class);
        $('#travels-edit-travel').find('.modal-title').html('Edit Travel');
    });

    $body.on('click', '.btn-delete-travel', function () {
        var $this = $(this);
        bootbox.confirm("Are you sure you want to delete this Travel?", function (result) {
            if (result) {
                var travel_id = $this.attr('data-id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/travels/delete/',
                    type: "POST",
                    data: {
                        id: travel_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.success) {
                            $.growl.notice({message: result.success});
                            $this.closest('tr').remove();
                        } else {
                            $.growl.warning({message: result.error});
                        }
                    }
                });
            }
        });
    });

    $body.on('click', '.btn-view-travel', function () {
        var travel_id = $(this).data('id');
        var modal_class = 'travels-view-travel';
        showTravel(travel_id, modal_class);
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('edit.off');
        // editor.setOption("readOnly", "nocursor");
    });

    function showTravel(travel_id, modal_class) {
        $('.travel-preset-selector').show();
        $('#travel-id').val(travel_id);
        $.ajax({
            url: base_url + '/admin/travels/' + travel_id + '/',
            type: "GET",
            success: function (response) {
                clog(response);
                if (response.success) {
                    var current_language_id = response.current_language_id;
                    default_language_id = current_language_id;
                    $('.travel-language-presets-selector').select2('val',current_language_id);
                    var travel = response.travel;
                    travel_language = response.travel;
                    var travel_bound_list = response.travel_bound_list;
                    var all_bound_list = response.all_bound_list;
                    var departure = travel.departure,
                        arrival = travel.arrival,
                        reg_between_start = travel.reg_between_start,
                        reg_between_end = travel.reg_between_end,
                        allow_attendees_queue = travel.allow_attendees_queue,
                        location = travel.location
                    //tags = response.tags;

                    var departure_date = moment(departure).format('MM/DD/YYYY'),
                        arrival_date = moment(arrival).format('MM/DD/YYYY'),
                        reg_between_start = moment(reg_between_start).format('MM/DD/YYYY'),
                        reg_between_end = moment(reg_between_end).format('MM/DD/YYYY');
                    var departure_time = moment(departure).format('HH:mm');
                    var arrival_time = moment(arrival).format('HH:mm');
                    $('#travel-name').val(getcontentByLanguage(travel.name, travel.name_lang, current_language_id));
                    //$('#travel-description').val(travel.description);
                    // $('#description').val(travel.description);
                    if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                        $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
                    }
                    $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(travel.description, travel.description_lang, current_language_id));
                    $('#travel-departure-city').val(travel.departure_city),
                        $('#travel-arrival-city').val(travel.arrival_city),
                        //$('.add-travel-tags').select2('data', tags);
                        $('#travel-bound').val(travel.travel_bound);
                    $('#travel-location').select2('val', travel.location.id);
                    $('#travel-group').select2('val', travel.group.id);
                    $('#travel-group').attr('data-id', travel.group.id);
                    $('#travel-departure-date').val(departure_date);
                    //$('#start-date').datepicker({dateFormat: 'mm/dd/yy'});
                    $('#travel-departure-date').datepicker('setDate', new Date(departure_date));

                    $('#travel-departure-time').val(departure_time);

                    $('#travel-arrival-date').val(arrival_date);
                    $('#travel-arrival-date').datepicker('setDate', new Date(arrival_date));

                    $('#travel-arrival-time').val(arrival_time);

                    $('#travel-reg-between-start').val(reg_between_start);
                    $('#travel-reg-between-start').datepicker('setDate', new Date(reg_between_start));

                    $('#travel-reg-between-end').val(reg_between_end);
                    $('#travel-reg-between-end').datepicker('setDate', new Date(reg_between_end));
                    var option = '';
                    for (var i = 0; i < all_bound_list.length; i++) {
                        option += '<option class="selected_column" value="' + all_bound_list[i].id + '">' + all_bound_list[i].name + '</option>';
                    }
                    var disabled = "";
                    if (modal_class == 'travels-view-travel') {
                        disabled = "disabled";
                    }

                    var html = '<label>' + response.bound_name + ' :</label>' +
                        '<div class="form-group show-travels">' +
                        '     <select name="travel-bound" class="selectpicker travel-bound-control" multiple data-live-search="true" data-live-search-placeholder="Search" data-actions-box="false" ' + disabled + '>' +
                        '         <optgroup label="' + travel.group.name + '">' +
                        '' + option + '' +
                        '         </optgroup>' +
                        '     </select>' +
                        ' </div>';
                    $('#travel_all_bounds').html(html);
                    $('body .travel-bound-control').selectpicker();
//                    var selected_bounds = '';
                    var total_bounds = [];
                    for (var j = 0; j < travel_bound_list.length; j++) {
                        if (travel.travel_bound == 'homebound') {
                            total_bounds.push(travel_bound_list[j].travel_outbound.id);
                        } else {
                            total_bounds.push(travel_bound_list[j].travel_homebound.id);
                        }
                    }
                    clog(total_bounds);
                    $('body .travel-bound-control').selectpicker('val', total_bounds);
                    $('#get_travel_id').val(travel.id);
//                    if (allow_attendees_queue == 1) {
//                        $('#travel-allow-attendees-queue').prop('checked', true);
//                    } else {
//                        $('#travel-allow-attendees-queue').prop('checked', false);
//                    }
                    $('#travel-max-attendees').val(travel.max_attendees);
                    $('#btn-save-travel').hide();
                    $('#btn-update-travel').show();
                    $('#' + modal_class).modal();
                    // setTimeout(function () {
                    //     var description_content = $.trim($('#description').val());
                    //     //if (description_content != '') {
                    //     editor.setValue(description_content);
                    //
                    //     //}
                    // }, 400);

                }
                else {
                    var errors = response.message;
                }
            },
            error: function () {
                //alert();
            }
        });
    }

    function addOrUpdateTravel(button) {
//        var allow_queue = $('#travel-allow-attendees-queue').prop('checked');
        var allow_attendees_queue = 0;
//        if (allow_queue == true) {
//            allow_attendees_queue = 1;
//        }
        var name = $('#travel-name').val(),
            group = $('#travel-group').select2('val'),
        //description = $('#travel-description').val(),
        //     description = $.trim($('#description_out').html()),
            description = $('textarea#froala_content_editor').froalaEditor('html.get'),
            departure_city = $('#travel-departure-city').val(),
            arrival_city = $('#travel-arrival-city').val(),
            start_date = $('#travel-departure-date').val(),
            start_time = $('#travel-departure-time').val(),
            end_date = $('#travel-arrival-date').val(),
            end_time = $('#travel-arrival-time').val(),
            reg_between_s = $('#travel-reg-between-start').val(),
            reg_between_e = $('#travel-reg-between-end').val(),
            max_attendees = $('#travel-max-attendees').val(),
            location = $('#travel-location').select2('val'),
        //tags = $('#travel-tags').val(),
            travel_bound = $('#travel-bound').val(),
            travel_bound_list = $('.travel-bound-control').val(),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var name_lang = valueWithSpecialCharacter(name);
        var description_lang = valueWithSpecialCharacter(description);
        var requiredFields = [
            {fieldId: 'travel-name', message: 'Name'},
            {fieldId: 'travel-group', message: 'Group'},
            {fieldId: 'travel-departure-city', message: 'Departure City'},
            {fieldId: 'travel-arrival-city', message: 'Arrival City'},
            {fieldId: 'travel-location', message: 'Location'},
            {fieldId: 'travel-departure-date', message: 'Start Date'},
            {fieldId: 'travel-arrival-date', message: 'End Date'},
            {fieldId: 'travel-speakers', message: 'Speakers'},
            {fieldId: 'travel-max-attendees', message: 'Max attendees'},
            {fieldId: 'travel-reg-between-start', message: 'Registration start date'},
            {fieldId: 'travel-reg-between-end', message: 'Registration end date'},
            {fieldId: 'travel-bound', message: 'Travel Bound'}
        ];
        clog(start_time);

        if (description == '') {
            $.growl.warning({message: "Description can't be blank"});
            return;
        }

        if (!requiredTravelFieldValidator(requiredFields)) {
            return;
        }
        if (travel_bound_list == null) {
            travel_bound_list = '';
        }

        var start = moment(start_date + ' ' + start_time, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD HH:mm:ss'),
            end = moment(end_date + ' ' + end_time, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD HH:mm:ss'),
            reg_between_start = moment(reg_between_s, 'MM/DD/YYYY').format('YYYY-MM-DD'),
            reg_between_end = moment(reg_between_e, 'MM/DD/YYYY').format('YYYY-MM-DD');
        var data = {
            name: name,
            group: group,
            description: description,
            name_lang: name_lang,
            description_lang: description_lang,
            departure_city: departure_city,
            arrival_city: arrival_city,
            location: location,
            departure: start,
            arrival: end,
            reg_between_start: reg_between_start,
            reg_between_end: reg_between_end,
            allow_attendees_queue: allow_attendees_queue,
            max_attendees: max_attendees,
            //tags: tags,
            travel_bound: travel_bound,
            travel_bound_list: JSON.stringify(travel_bound_list),
            csrfmiddlewaretoken: csrfToken
        };
        if (button.attr('id') == 'btn-update-travel') {
            var travel_id = $('#travel-id').val();
            data['id'] = travel_id;
            var current_language_id = $('.travel-language-presets-selector').select2('val');
            data['current_language_id'] = current_language_id;
        }

        $.ajax({
            url: base_url + '/admin/travels/',
            type: 'POST',
            data: data,
            success: function (responseText) {
                var response = JSON.parse(responseText);
                clog(response);

                if (response.success) {
                    clog('s');
                    $.growl.notice({message: response.message});
                    var updated_travel = response.travel;
                    var row = '' +
                        '<td>' + updated_travel.id + '</td>' +
                        '<td>' + updated_travel.name + '</td>' +
                        '<td>' + updated_travel.attending + ' / ' + updated_travel.max_attendees + '</td>' +
//                        '<td id="travel-queue-count-' + updated_travel.id + '">' + updated_travel.in_queue + '</td>' +
//                        '<td>' + updated_travel.not_attending + '</td>' +
                        '<td>' +
                        '    <button class="btn btn-xs btn-edit-travel" data-id="' + updated_travel.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
//                        '    <button class="btn btn-xs btn-edit-travel-queue" data-id="' + updated_travel.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Queue"><i class="dropdown-icon fa fa-users"></i></button>' +
//                        '    <button class="btn btn-xs btn-edit-travel-deciding" data-id="' + updated_travel.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Deciding List"><i class="dropdown-icon fa fa-user-secret"></i></button>' +
//                        '    <button class="btn btn-xs btn-duplicate-travel" data-id="' + updated_travel.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '    <button class="btn btn-xs btn-danger btn-delete-travel" data-id="' + updated_travel.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '</td>';
                    if (button.attr('id') === 'btn-update-travel') {
                        var old_group = $('#travel-group').attr('data-id');
                        if (old_group == updated_travel.group.id) {
                            $('body .travel-table tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_travel.id) {
                                    $(this).html(row);
                                }
                            });
                        } else {
                            $('body .travel-table tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_travel.id) {
                                    $(this).remove();
                                }
                            });
                            $('body #travel_group_' + updated_travel.group.id).next('.travel-table').find('tbody').append('<tr>' + row + '</tr>');
                        }

                    } else {
                        $('body #travel_group_' + updated_travel.group.id).next('.travel-table').find('tbody').append('<tr>' + row + '</tr>');
                    }
                    $('#travel_all_bounds').html('');

                    $('#travels-edit-travel').modal('hide');
                }
                else {
                    var errors = response.message;
                    clog(errors);
                    prepareTravelValidationMessage(errors);
                }
            },
            error: function (e) {
                clog(e);
            }
//            complete : function(){
//            }
        });
    }

    $body.on('click', '#btn-save-travel', function () {
        addOrUpdateTravel($(this));
    });

    $body.on('click', '#btn-update-travel', function () {
        addOrUpdateTravel($(this));
    });

    //$(".add-travel-tags").select2({
    //    tags: true,
    //    tokenSeparators: [","],
    //    ajax: {
    //        multiple: true,
    //        url: base_url + '/admin/travels/get-tags/',
    //        dataType: "json",
    //        type: "POST",
    //        data: function (term, page) {
    //            return {
    //                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    //                q: term
    //            };
    //        },
    //
    //        results: function (data, page) {
    //            lastResults = data.results;
    //            return data;
    //        }
    //    },
    //    //Allow manually entered text in drop down.
    //    createSearchChoice: function (term, data) {
    //        if($.trim(term) != '') {
    //            if ($(data).filter(function () {
    //                    return this.text.localeCompare(term) === 0;
    //                }).length === 0) {
    //                return {id: term, text: term};
    //            }
    //        }
    //    }
    //});

//    $body.on('click', '#btn-remove-travel-queue', function () {
//        $this = $(this);
//        var travel_id = $('#edit-travel-queue').data('id');
//        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
//        $.ajax({
//            url: base_url + '/admin/travels/remove-queue/',
//            type: 'POST',
//            data: {
//                travel_id: travel_id,
//                travel_attendee_id: 'all',
//                csrfmiddlewaretoken: csrfToken
//            },
//            success: function (response) {
//                //var response = JSON.parse(responseText);
//                if (response.success) {
//                    $.growl.notice({message: response.success});
//                    $this.closest('.modal-body').find('#edit-travel-queue tbody').remove();
//                    var total_queue = response.total_queue;
//                    $('#travel-queue-count-' + session_id).html(total_queue);
//                    $('#travels-edit-cue').modal('hide');
//                }
//
//            },
//            error: function (e) {
//                clog(e);
//            }
//        });
//
//    });
//
//    $body.on('click', '#btn-remove-travel-queue', function () {
//        $this = $(this);
//        var travel_id = $('#edit-travel-queue').data('id');
//        var travel_attendee_id = $(this).data('id');
//        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
//        $.ajax({
//            url: base_url + '/admin/travels/remove-queue/',
//            type: 'POST',
//            data: {
//                travel_id: travel_id,
//                travel_attendee_id: travel_attendee_id,
//                csrfmiddlewaretoken: csrfToken
//            },
//            success: function (response) {
//                //var response = JSON.parse(responseText);
//                if (response.success) {
//                    $.growl.notice({message: response.success});
//                    $this.closest('tr').remove();
//                    var total_queue = response.total_queue;
//                    $('#travel-queue-count-' + session_id).html(total_queue);
//                }
//
//            },
//            error: function (e) {
//                clog(e);
//            }
//        });
//
//    });
//
//    $body.on('click', '.btn-edit-travel-queue', function () {
//        var travel_id = $(this).data('id');
//        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
//        var data = {
//            travel_id: travel_id,
//            csrfmiddlewaretoken: csrfToken
//        }
//        $.ajax({
//            url: base_url + '/admin/travels/queue/',
//            type: "POST",
//            data: data,
//            success: function (response) {
//                $('#travels-edit-cue').html(response);
//                $('#travels-edit-cue').modal();
//            }
//        });
//    });
//
//    $body.on('click', '.btn-edit-travel-deciding', function () {
//        var travel_id = $(this).data('id');
//        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
//        var data = {
//            travel_id: travel_id,
//            csrfmiddlewaretoken: csrfToken
//        }
//        $.ajax({
//            url: base_url + '/admin/travels/deciding/',
//            type: "POST",
//            data: data,
//            success: function (response) {
//                $('#travels-edit-deciding').html(response);
//                $('#travels-edit-deciding').modal();
//            }
//        });
//    });


    $('body').on('change', '#travel-bound', function () {
        var bound = $(this).val();
        var group = $('#travel-group').select2('val');
        if (group != '' && group != null) {
            retrieveTravels(bound, group);
        }
    });

    $('body').on('change', '#travel-group', function () {
        var group = $(this).select2('val');
        var bound = $('#travel-bound').val();
        if (bound != '' && bound != null) {
            retrieveTravels(bound, group);
        }
    });


    function retrieveTravels(bound, group) {
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        travel_id = $('#get_travel_id').val();
        var data = {
            bound: bound,
            group: group,
            travel_id: travel_id,
            csrfmiddlewaretoken: csrfToken
        }
        $.ajax({
            url: base_url + '/admin/travels/get-bound/',
            type: "POST",
            data: data,
            success: function (response) {
                $('#travel_all_bounds').html(response);
                $('body .travel-bound-control').selectpicker();
            }
        });
    }


});
