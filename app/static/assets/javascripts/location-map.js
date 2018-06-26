$(function () {
    $('#start-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1
    });
    $('#end-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1
    });
    $('#reg-between-start').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1
    });
    $('#reg-between-end').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1
    });
    $('#start-date').datepicker('setDate', $('#event-start-date').val());
    $('#end-date').datepicker('setDate', $('#event-end-date').val());
    $('#reg-between-start').datepicker('setDate', $('#now').val());
    $('#reg-between-end').datepicker('setDate', $('#event-end-date').val());

    var $body = $('body');
    //$($body).find('.data-table-location').dataTable();

    /* location */
    var map;
    markers = [];
    var locationSelected = false;

    function setMapOnAll(map) {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(map);
        }
    }

    function clearMarkers() {
        setMapOnAll(null);
    }

    function deleteMarkers() {
        clearMarkers();
        markers = [];
    }

    function placeMarkerAndPanTo(latLng, map) {
        deleteMarkers();
        var marker = new google.maps.Marker({
            position: latLng,
            map: map
        });
        map.panTo(latLng);
        map.setZoom(15);
        clog(latLng);
        markers.push(marker);
        clog(latLng);
        locationSelected = true;
    }

    function mapInitialize(point) {
        var myLatLng = {lat: -25.363, lng: 131.044};
        map = new google.maps.Map(document.getElementById('location-map-container'), {
            zoom: 4,
            center: myLatLng
        });
        map.addListener('click', function (e) {
            clog(e.latLng);
            placeMarkerAndPanTo(e.latLng, map);
        });
        google.maps.event.trigger(map, 'resize');
    }

    function mapInitializeEdit(point) {
        var myLatLng = {lat: point.lat, lng: point.lng};
        map = new google.maps.Map(document.getElementById('location-map-container'), {
            zoom: 15,
            center: myLatLng
        });
        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map
        });
        map.panTo(myLatLng);
        markers.push(marker);
        locationSelected = true;
        map.addListener('click', function (e) {
            placeMarkerAndPanTo(e.latLng, map);
        });
        google.maps.event.trigger(map, 'resize');
    }

    $('#location_maps_highlights').change(
        function () {
            var hightlight = $(this).val();
            if (hightlight.length > 0) {
                var url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + hightlight
                $.ajax({
                    url: url,
                    type: "GET",
                    dataType: "json",
                    success: function (data) {
                        clog(data)
                        if (data.status != "ZERO_RESULTS") {
                            var lat = data.results[0].geometry.location.lat;
                            var lng = data.results[0].geometry.location.lng;
                            clearMarkers();
                            var myLatLng = {lat: lat, lng: lng};
                            placeMarkerAndPanTo(myLatLng, map)
                        } else {
                            $.growl.warning({message: "Hight map not found"})
                            $('#location_maps_highlights').val("");
                        }


                    }
                })
            }

        }
    );
    $("#locations-edit-location").on("shown.bs.modal", function () {
        var point = $(this).data('point');
        if (point.from == 'edit' && point.lat && point.lat != '') {
            mapInitializeEdit($(this).data('point'));
        }
        else {
            mapInitialize($(this).data('point'));
        }
    });

    $("#locations-view-location").on("shown.bs.modal", function () {
        var point = $(this).data('point');
        if (point.from == 'edit' && point.lat && point.lat != '') {
            mapInitializeEdit($(this).data('point'));
        }
        else {
            mapInitialize($(this).data('point'));
        }
    });

    function clearForm() {
        $('#location_name').val('');
        //$('#location_description').val('');
        $('#location_address').val('');
        $('#location_group').select2('val', '');
        $('#location_maps_highlights').val('');
        $('#id_checkbox_location_maps_highlights').prop('checked', false);
        $('#contact_name').val('');
        $('#id_checkbox_location_name').prop('checked', false);
        $('#contact_web').val('');
        $('#id_checkbox_location_web').prop('checked', false);
        $('#contact_phone').val('');
        $('#id_checkbox_location_phone').prop('checked', false);
        $('#contact_email').val('');
        $('#id_checkbox_location_email').prop('checked', false);
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('html.set', '');
        $('.location-language-preset-selector').select2("val", "");
        $('.language-preset-selector').hide();
        // setTimeout(function () {
        //     editor.setValue('');
        // }, 400);
        mapInitialize();
    }

    $body.on('click', '#btn-add-location', function () {
        $('#btn-save-location').show();
        $('#btn-update-location').hide();
        $('#locations-edit-location').find('.modal-title').html('Add Location');
        clearForm();
        var point = {lat: -23.00, lng: 131.00, from: 'add'};
        $('#locations-edit-location').data('point', point).modal();
    });

    $body.on('click', '.btn-edit-location', function () {
        var locationId = $(this).data('id');
        modal_class = 'locations-edit-location';
        showLocationData(locationId, modal_class);
        $('#locations-edit-location').find('.modal-title').html('Edit Location');
    });

    $body.on('click', '.btn-view-location', function () {
        var locationId = $(this).data('id');
        modal_class = 'locations-view-location';
        showLocationData(locationId, modal_class);
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('edit.off');
        // editor.setOption("readOnly", "nocursor");
    });

    function showLocationData(locationId, modal_class) {
        $('.language-preset-selector').show();
        $.ajax({
            url: base_url + '/admin/locations/' + locationId + '/',
            type: "GET",
            success: function (response) {
                if (response.success) {
                    var current_language_id = response.current_language_id;
                    default_language_id = current_language_id;
                    $('.location-language-presets-selector').select2('val',current_language_id);
                    var location = response.location;
                    location_language = response.location;
                    var lat = Number(location.latitude);
                    var lon = Number(location.longitude);
                    $('#location_name').val(getcontentByLanguage(location.name, location.name_lang, current_language_id));
                    //$('#location_description').val(location.description);
                    // $('#description').val(location.description);
                    if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                        $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
                    }
                    $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(location.description, location.description_lang, current_language_id));
                    $('#location_address').val(getcontentByLanguage(location.address, location.address_lang, current_language_id));
                    $('#location_group').select2('val', location.group.id);
                    $('#location_group').attr('data-id', location.group.id);
                    $('#edit-location-id').val(location.id);

                    $('#location_maps_highlights').val(location.map_highlight);
                    $('#contact_email').val(location.contact_email);
                    $('#contact_name').val(getcontentByLanguage(location.contact_name, location.contact_name_lang, current_language_id));
                    $('#contact_web').val(location.contact_web);
                    $('#contact_phone').val(location.contact_phone);

                    if (location.show_map_highlight == 1) {
                        $('#id_checkbox_location_maps_highlights').prop('checked', true);
                    }
                    if (location.show_contact_name == 1) {
                        $('#id_checkbox_location_name').prop('checked', true);
                    }
                    if (location.show_contact_web == 1) {
                        $('#id_checkbox_location_web').prop('checked', true);
                    }
                    if (location.show_contact_email == 1) {
                        $('#id_checkbox_location_email').prop('checked', true);
                    }
                    if (location.show_contact_phone == 1) {
                        $('#id_checkbox_location_phone').prop('checked', true);
                    }
                    $('#btn-save-location').hide();
                    $('#btn-update-location').show();
                    var point = {lat: lat, lng: lon, from: 'edit'};
                    $('#' + modal_class).data('point', point).modal();
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
        $('#' + modal_class).modal();
    }

    function prepareValidationMessage(errors) {
        var msg = '';
        for (var key in errors) {
            msg += key + ': ' + errors[key][0] + '<br>';
        }
        $.growl.warning({message: msg});
    }

    function validated(name, address, group, description, mapHighlight, contact_name, contact_web, contact_phone, contact_email) {
        var valid = true,
            message = '';

        if (name.length === 0) {
            message += '*Location name can not be blank<br>';
            valid = false;
        }
//        if (description.length === 0) {
//            message += '*Location description can not be blank<br>';
//            valid = false;
//        }
        if (!group || group.length === 0) {
            message += '*Select a group for the location<br>';
            valid = false;
        }
//        if (address.length === 0) {
//            message += '*Location address can not be blank<br>';
//            valid = false;
//        }
        if ($('#id_checkbox_location_maps_highlights').prop('checked') && mapHighlight.length === 0) {
            message += '*Maps highlight can not be blank<br>';
            valid = false;
        }
        if ($('#id_checkbox_location_name').prop('checked') && contact_name.length === 0) {
            message += '*Contact name can not be blank<br>';
            valid = false;
        }
        if ($('#id_checkbox_location_web').prop('checked') && contact_web.length === 0) {
            message += '*Contact web can not be blank<br>';
            valid = false;
        }
        if ($('#id_checkbox_location_phone').prop('checked') && contact_phone.length === 0) {
            message += '*Contact phone can not be blank<br>';
            valid = false;
        }
        if ($('#id_checkbox_location_email').prop('checked') && contact_email.length === 0) {
            message += '**Contact email can not be blank<br>';
            valid = false;
        }
        if (!valid) {
            $.growl.warning({message: message});
        }
        return valid;
    }

    function addOrUpdateLocation(button) {
        var name = $('#location_name').val(),
            address = $('#location_address').val(),
            group = $('#location_group').select2('val'),
        //description = $('#location_description').val(),
        //     description = $.trim($('#description_out').html()),
            description = $('textarea#froala_content_editor').froalaEditor('html.get'),
            mapHighlight = $('#location_maps_highlights').val(),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val(),
            contact_name = $('#contact_name').val(),
            contact_web = $('#contact_web').val(),
            contact_phone = $('#contact_phone').val(),
            contact_email = $('#contact_email').val(),
            show_map_highlight = $('#id_checkbox_location_maps_highlights').prop('checked'),
            show_contact_name = $('#id_checkbox_location_name').prop('checked'),
            show_contact_web = $('#id_checkbox_location_web').prop('checked'),
            show_contact_phone = $('#id_checkbox_location_phone').prop('checked'),
            show_contact_email = $('#id_checkbox_location_email').prop('checked');
        var name_lang = valueWithSpecialCharacter(name);
        var description_lang = valueWithSpecialCharacter(description);
        var address_lang = valueWithSpecialCharacter(address);
        var contact_name_lang = valueWithSpecialCharacter(contact_name);
        if ($.trim(mapHighlight) != '') {
            mapHighlight = mapHighlight.replace(/ /g, '+');
        }

        if (!validated(name, address, group, description, mapHighlight, contact_name, contact_web, contact_phone, contact_email)) {
            return;
        }
        var lat, lon;
        if (locationSelected) {
//            lat = markers[0].position.G;
//            lon = markers[0].position.K;
            lat = markers[0].position.lat();
            lon = markers[0].position.lng();
        }

        var data = {
            name: name,
            address: address,
            group: group,
            description: description,
            name_lang: name_lang,
            description_lang: description_lang,
            latitude: lat,
            longitude: lon,
            map_highlight: mapHighlight,
            contact_name: contact_name,
            contact_web: contact_web,
            contact_phone: contact_phone,
            contact_email: contact_email,
            show_map_highlight: show_map_highlight,
            show_contact_name: show_contact_name,
            show_contact_web: show_contact_web,
            show_contact_phone: show_contact_phone,
            show_contact_email: show_contact_email,
            address_lang: address,
            contact_name_lang: contact_name_lang,
            csrfmiddlewaretoken: csrfToken
        };
        //if ($('#id_checkbox_location_maps_highlights').prop('checked')) {
        //    data['map_highlight'] = mapHighlight;
        //}
        //if ($('#id_checkbox_location_name').prop('checked')) {
        //    data['contact_name'] = contact_name;
        //}
        //if ($('#id_checkbox_location_web').prop('checked')) {
        //    data['contact_web'] = contact_web;
        //}
        //if ($('#id_checkbox_location_phone').prop('checked')) {
        //    data['contact_phone'] = contact_phone;
        //}
        //if ($('#id_checkbox_location_email').prop('checked')) {
        //    data['contact_email'] = contact_email;
        //}


        var ajaxUrl = '/admin/locations/',
            type = 'POST';

        if (button.attr('id') === 'btn-update-location') {
            data['id'] = $('#edit-location-id').val();
            var current_language_id = $('.location-language-presets-selector').select2('val');
            data['current_language_id'] = current_language_id;
        }

        $.ajax({
            url: base_url + ajaxUrl,
            type: type,
            data: data,
            success: function (responseText) {
                var response = JSON.parse(responseText);
                if (response.success) {
                    var updated_location = response.location;
                    var row = '' +
                        '<td>' + updated_location.id + '</td>' +
                        '      <td>' + updated_location.name + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs btn-edit-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '          <button class="btn btn-xs btn-duplicate-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '          <button class="btn btn-xs btn-danger btn-delete-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
                    if (button.attr('id') === 'btn-update-location') {
                        var old_group = $('#location_group').attr('data-id');
                        if (old_group == updated_location.group.id) {
                            $('body .data-table-location tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_location.id) {
                                    $(this).html(row);
                                }
                            });
                        } else {
                            $('body .data-table-location tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_location.id) {
                                    $(this).remove();
                                }
                            });
                            $('body #location_group_' + updated_location.group.id).next('.data-table-location').find('tbody').append('<tr>' + row + '</tr>');
                        }
                    } else {
                        $('body #location_group_' + updated_location.group.id).next('.data-table-location').find('tbody').append('<tr>' + row + '</tr>');
                    }

                    $.growl.notice({message: response.message});
                    $('#locations-edit-location').modal('hide');
                }
                else {
                    $.growl.warning({message: response.message});
                    // var errors = response.message;
                    // prepareValidationMessage(errors);
                }
            },
            error: function (e) {
                clog(e);
            }

        });
    }

    $body.on('click', '#btn-save-location', function () {
        addOrUpdateLocation($(this));
    });
    $body.on('click', '#btn-update-location', function () {
        addOrUpdateLocation($(this));
    });
    $body.on('click', '#allow-overlapping', function () {
        var session_id = $("#session-id").val()
        var checked = $(this).is(':checked');
        if (!checked) {
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/session-conflick-num/',
                type: "POST",
                data: {
                    session_id: session_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (response) {
                    if (response.success) {
                        if (response.number_of_attending_user_has_clash > 0 || response.number_of_queue_user_has_clash > 0) {
                            var session_name = $('#name').val();
                            bootbox.confirm(session_name + " will be removed from " + response.number_of_attending_user_has_clash + " ( attending ) and " + response.number_of_queue_user_has_clash + " ( in-queue ) attendees with conflicting sessions, are you sure you want to go through with this?", function (result) {
                                if (result) {
                                    $.ajax({
                                        url: base_url + "/admin/remove-session-for-conflict/",
                                        type: "POST",
                                        data: {
                                            session_id: session_id,
                                            csrfmiddlewaretoken: csrf_token
                                        },
                                        success: function (data) {
                                            if (data.success) {
                                                $('#allow-overlapping').prop('checked', false)
                                            }

                                        }
                                    });

                                } else {
                                    $('#allow-overlapping').prop('checked', true)
                                }
                            });
                        }

                    }
                }
            });

        }
    });

    $('body').on('click', '.btn-delete-location', function (event) {
        var $this = $(this);
        var locationId = $(this).data('id');
        bootbox.confirm("Are you sure you want to delete this attendee?", function (result) {
            if (result) {
                var id = locationId;
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/locations/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (response) {
                        if (response.success) {
                            $.growl.notice({message: response.message});
                            $this.closest('tr').remove();
                        }
                        else {

                        }
                    }
                });
            }
        });
    });

    $('body').on('click', '#btn-add-session-filter', function () {
        //var fieldsToClear = [
        //    'name', 'description', 'max-attendees'
        //];
        //clearForm1(fieldsToClear);
        $('#action').select2('val', '');
        $('#session').select2('val', '');
        $('#filter').select2('val', '');
        $('#btn-seminar-filter').show();
        //$('#btn-update-session').hide();
//        $('#btn-remove-queue').hide();
        $('#seminars-add-filter').find('.modal-title').html('Apply filter');
        $('#seminars-add-filter').modal();
    });

    /* location end */

    $.fn.serializeObject = function () {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    function clearForm1(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).val('');
        }
        $('#start-date').data('datepicker').setDate($('#event-start-date').val());
        $('#end-date').data('datepicker').setDate($('#event-end-date').val());
        $('#reg-between-start').data('datepicker').setDate($('#now').val());
        $('#reg-between-end').data('datepicker').setDate($('#event-end-date').val());
        $('#speakers').select2("val", "");
        $('#location').select2("val", "");
        $('#tags').select2("val", "");
        $('#session-custom-class').select2("val", "");
        $('#group').select2("val", "");
        $('.session-language-preset-selector').select2("val", "");
        $('.language-preset-selector').hide();
    }

    function requiredFieldValidator(requiredFields) {
        var message = '';
        for (var i = 0; i < requiredFields.length; i++) {
            var Id = requiredFields[i].fieldId;
            clog($('#' + Id).attr('type'))
            if ($('#' + Id).val() == '' || $('#' + Id).val() == null || $('#' + Id).val() == undefined) {
                message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
                valid = false;
            }
        }
        return message;
    }


    // START Added on 26-8-16    for selected date & time on datePicker tiemPicker
    var temp_start_time;
    var temp_end_time;
    $("#start-date").click(function () {
        $('#start-date').data('datepicker').setDate($('#start-date').val());
    });
    $("#end-date").click(function () {
        $('#end-date').data('datepicker').setDate($('#end-date').val());
    });
    $("#reg-between-start").click(function () {
        $('#reg-between-start').data('datepicker').setDate($('#reg-between-start').val());
    });
    $("#reg-between-end").click(function () {
        $('#reg-between-end').data('datepicker').setDate($('#reg-between-end').val());
    });

    $("#start-time").click(function () {
        $('#start-time').timepicker('setTime', temp_start_time);
    });
    $("#end-time").click(function () {
        $('#end-time').timepicker('setTime', temp_end_time);
    });

    // END


    /* session */

    $body.on('click', '#btn-add-session', function () {
        var fieldsToClear = [
            'name', 'max-attendees'
        ];
        clearForm1(fieldsToClear);
        $('#btn-save-session').show();
        $('#btn-update-session').hide();
//        $('#btn-remove-queue').hide();
        $('#seminars-edit-seminar').find('.modal-title').html('Add Session');
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('html.set', '');
        $('#seminars-edit-seminar').modal();
        // setTimeout(function () {
        //     // editor.setValue('');
        //
        //
        // }, 400);

    });


    $body.on('click', '.btn-edit-session', function () {
        var session_id = $(this).data('id');
        var modal_class = 'seminars-edit-seminar';
        showSession(session_id, modal_class);
        $('#seminars-edit-seminar').find('.modal-title').html('Edit Session');
    });

    $body.on('click', '.btn-view-session', function () {
        var session_id = $(this).data('id');
        var modal_class = 'seminars-view-seminar';
        showSession(session_id, modal_class);
        if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
            $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
        }
        $('textarea#froala_content_editor').froalaEditor('edit.off');
        // editor.setOption("readOnly", "nocursor");
    });
    $body.on('click', '#allow-all-day-session', function () {
        if ($(this).prop('checked')) {
            $('#start-time').val('00:00')
            $('#end-time').val('23:59')
            $('#start-time').prop('disabled', true);
            $('#end-time').prop('disabled', true);
        } else {
            $('#start-time').timepicker('setTime', temp_start_time);
            $('#end-time').timepicker('setTime', temp_end_time);
            $('#start-time').prop('disabled', false);
            $('#end-time').prop('disabled', false);
        }
    });


    function showSession(session_id, modal_class) {
        $('#session-id').val(session_id);
        $('.language-preset-selector').show();
        $.ajax({
            url: base_url + '/admin/sessions/' + session_id + '/',
            type: "GET",
            success: function (response) {
                clog(response);
                if (response.success) {
                    var current_language_id = response.current_language_id;
                    default_language_id = current_language_id;
                    $('.session-language-presets-selector').select2('val',current_language_id);
                    session_language = response.session;
                    var session = response.session;
                    var start = session.start,
                        end = session.end,
                        reg_between_start = session.reg_between_start,
                        reg_between_end = session.reg_between_end,
                        allow_attendees_queue = session.allow_attendees_queue,
                        allow_overlapping = session.allow_overlapping,
                        allow_all_day = session.all_day,
                        location = session.location,
                        speakers = session.speakers,
                        cost = session.cost,
                        vat = session.vat_rate;
                    var receive_answer = session.receive_answer;
                    var tags = response.tags;
                    var custom_classes = response.custom_classes;

                    var start_date = moment(start).format('YYYY-MM-DD'),
                        end_date = moment(end).format('YYYY-MM-DD'),
                        reg_between_start = moment(reg_between_start).format('YYYY-MM-DD'),
                        reg_between_end = moment(reg_between_end).format('YYYY-MM-DD');
                    if (session.has_time) {
                        var start_time = moment(start).format('HH:mm');
                        var end_time = moment(end).format('HH:mm');
                    } else {
                        var start_time = '';
                        var end_time = '';
                    }
                    temp_start_time = start_time;
                    temp_end_time = end_time;

                    $('#name').val(getcontentByLanguage(session.name, session.name_lang, current_language_id));
                    // $('#description').val(session.description);
                    if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                        $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
                    }
                    $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(session.description, session.description_lang, current_language_id));
                    //$('#group').val(session.group);
//                    $('#speakers').val(session.speakers);

                    $('.add-speakerss').select2('data', session.speakers);
                    $('.add-tags').select2('data', tags);
                    $('.add-session-custom-class').select2('data', custom_classes);

                    $('#location').select2('val', session.location.id);
                    $('#group').select2('val', session.group.id);
                    $('#group').attr('data-id', session.group.id);
                    $('#start-date').val(start_date);
                    //$('#start-date').datepicker({dateFormat: 'mm/dd/yy'});
                    $('#start-date').datepicker('setDate', new Date(start_date));

                    $('#start-time').val(start_time);

                    $('#end-date').val(end_date);
                    $('#end-date').datepicker('setDate', new Date(end_date));

                    $('#end-time').val(end_time);

                    $('#reg-between-start').val(reg_between_start);
                    $('#reg-between-start').datepicker('setDate', new Date(reg_between_start));

                    $('#reg-between-end').val(reg_between_end);
                    $('#reg-between-end').datepicker('setDate', new Date(reg_between_end));

                    $('#cost').val(cost);
                    $('#vat').val(vat);

                    if (allow_attendees_queue == 1) {
                        $('#allow-attendees-queue').prop('checked', true);
                    } else {
                        $('#allow-attendees-queue').prop('checked', false);
                    }

                    if (allow_overlapping) {
                        clog(allow_overlapping);
                        $('#allow-overlapping').prop('checked', true);
                    } else {
                        $('#allow-overlapping').prop('checked', false);
                    }

                    if (allow_all_day) {
                        $('#allow-all-day-session').prop('checked', true);
                        $('#start-time').prop('disabled', true);
                        $('#end-time').prop('disabled', true);
                    } else {
                        $('#allow-all-day-session').prop('checked', false);
                        $('#start-time').prop('disabled', false);
                        $('#end-time').prop('disabled', false);
                    }


                    if (receive_answer == 1) {
                        $('.receive-no-answer').prop('checked', true);
                    } else {
                        $('.receive-no-answer').prop('checked', false);
                    }
                    if (!session.show_on_evaluation) {
                        $('#not-show-evaluation').prop('checked', true);
                    } else {
                        $('#not-show-evaluation').prop('checked', false);
                    }
                    if (!session.show_on_next_up) {
                        $('#not-show-next-up').prop('checked', true);
                    } else {
                        $('#not-show-next-up').prop('checked', false);
                    }
                    if (session.max_attendees == 0) {
                        $('#max-attendees').val('');
                    } else {
                        $('#max-attendees').val(session.max_attendees);
                    }

                    $('#btn-save-session').hide();
                    $('#btn-update-session').show();
//                    $('#btn-remove-queue').show();
                    $('#' + modal_class).modal();
                    // setTimeout(function () {
                    //     var description_content = $.trim($('#description').val());
                    //     clog(description_content);
                    //     if (description_content != '') {
                    //         $('textarea#froala_content_editor').froalaEditor('html.set', description_content);
                    //         // editor.setValue(description_content);
                    //
                    //     }
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


    function addOrUpdateSession(button) {
        var receive_no_answer = $('.receive-no-answer').prop('checked');
        var receive_answer = 0;
        if (receive_no_answer == true) {
            receive_answer = 1;
        }
        var allow_queue = $('#allow-attendees-queue').prop('checked');
        var allow_attendees_queue = 0;
        if (allow_queue == true) {
            allow_attendees_queue = 1;
        }


        var not_show_evaluation = $('#not-show-evaluation').prop('checked');
        var not_show_next_up = $('#not-show-next-up').prop('checked');
        var allow_overlapping = $('#allow-overlapping').prop('checked');
        var name = $('#name').val(),
            group = $('#group').select2('val'),
        //description = $.trim(editor.getValue()),
        //     description = $.trim($('#description_out').html()),
            description = $('textarea#froala_content_editor').froalaEditor('html.get'),
            start_date = $('#start-date').val(),
            start_time = $('#start-time').val(),
            end_date = $('#end-date').val(),
            end_time = $('#end-time').val(),
            reg_between_s = $('#reg-between-start').val(),
            reg_between_e = $('#reg-between-end').val(),
            max_attendees = $('#max-attendees').val(),
            location = $('#location').val(),
            speakers = $('#speakers').val(),
            tags = $('#tags').val(),
            custom_classes = $('#session-custom-class').val(),
            cost = $('#cost').val(),
            vat = $('#vat').val(),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var allow_all_day = $('#allow-all-day-session').prop('checked');
        var name_lang = valueWithSpecialCharacter(name);
        var description_lang = valueWithSpecialCharacter(description);
        console.log('Cost: ' + cost);
        console.log('VAT: ' + vat);

        var requiredFields = [
            {fieldId: 'name', message: 'Name'},
            {fieldId: 'group', message: 'Group'},
            {fieldId: 'location', message: 'Location'},
            {fieldId: 'start-date', message: 'Start Date'},
            {fieldId: 'end-date', message: 'End Date'},
            //{fieldId: 'max-attendees', message: 'Max attendees'},
            {fieldId: 'reg-between-start', message: 'Registration start date'},
            {fieldId: 'reg-between-end', message: 'Registration end date'}
        ];
        clog(requiredFields);
        message = "";
        message += requiredFieldValidator(requiredFields);

        // if (description == '') {
        //     message += "*Description can't be blank";
        // }

        if (cost != 0) {
            if (vat == "") {
                message += "*Cost must have a vat rate" + "<br>";
            }
        }

        if (message != "") {
            $.growl.warning({message: message});
            return;
        }

        var start = moment(start_date + ' ' + start_time, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss'),
            end = moment(end_date + ' ' + end_time, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss'),
            reg_between_start = moment(reg_between_s, 'YYYY-MM-DD').format('YYYY-MM-DD'),
            reg_between_end = moment(reg_between_e, 'YYYY-MM-DD').format('YYYY-MM-DD');

        var data = {
            name: name,
            group: group,
            description: description,
            name_lang: name_lang,
            description_lang: description_lang,
            location: location,
            start: start,
            end: end,
            reg_between_start: reg_between_start,
            reg_between_end: reg_between_end,
            allow_attendees_queue: allow_attendees_queue,
            allow_overlapping: allow_overlapping,
            max_attendees: max_attendees,
            speakers: speakers,
            tags: tags,
            custom_classes: custom_classes,
            cost: cost,
            vat: vat,
            receive_answer: receive_answer,
            not_show_evaluation: not_show_evaluation,
            not_show_next_up: not_show_next_up,
            allow_all_day: allow_all_day,
            csrfmiddlewaretoken: csrfToken
        };
        if (start_time == '' && end_time == '') {
            data['hasTime'] = 0;
        } else {
            data['hasTime'] = 1;
        }
        clog(data['hasTime'])

        if (button.attr('id') == 'btn-update-session') {
            var session_id = $('#session-id').val();
            data['id'] = session_id;
            var current_language_id = $('.session-language-presets-selector').select2('val');
            data['current_language_id'] = current_language_id;
        }

        $.ajax({
            url: base_url + '/admin/sessions/',
            type: 'POST',
            data: data,
            success: function (responseText) {
                //var response = JSON.parse(responseText);
                var response = responseText;
                clog(response);

                if (response.success) {
                    clog('s');
                    $.growl.notice({message: response.message});
                    //setTimeout(function () {
                    //    window.location = ''
                    //}, 500);
                    if (response.speakerError.length > 0) {
                        $.each(response.speakerError, function (index, value) {
                            speaker_id = value[0].spk.id;
                            session_id = value[0].session_id;
                            bootbox.confirm(value[0].msg + " Are you want to forcefully add speaker in this session? ", function (result) {
                                if (result) {
                                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                                    $.ajax({
                                        url: base_url + '/admin/forcefully-add-speaker/',
                                        type: "POST",
                                        data: {
                                            attendee_id: speaker_id,
                                            session_id: session_id,
                                            csrfmiddlewaretoken: csrf_token
                                        },
                                        success: function (response2) {
                                            if (response2.success) {
                                                $.growl.notice({message: response2.message});
                                            }
                                            else {

                                            }
                                        }
                                    });
                                }
                            });

                        });
                    }
                    updated_session = response.session;
                    if (typeof (updated_session.average_rating) != 'undefined') {
                        var rating = updated_session.average_rating;
                        var no_of_attendees_evaluating = updated_session.no_of_attendees_evaluating;
                    } else {
                        var rating = 'N/A';
                        var no_of_attendees_evaluating = 'N/A';
                    }
                    if (updated_session.max_attendees == 0) {
                        max = '&#8734';
                    } else {
                        max = updated_session.max_attendees;
                    }

                    var selectedArr = $('.selectpicker').val();
                    var row = '' +
                        '<td>' + updated_session.id + '</td>' +
                        '<td>' + updated_session.name + '</td>';
                    if ($.inArray("2", selectedArr) != -1) {
                        row += '<td>' + updated_session.attending + '</td>';
                    }
                    if ($.inArray("3", selectedArr) != -1) {
                        row += '<td>' + max + '</td>';
                    }
                    if ($.inArray("4", selectedArr) != -1) {
                        row += '<td>' + updated_session.percentage + '</td>';
                    }
                    if ($.inArray("5", selectedArr) != -1) {
                        row += '<td id="session-queue-count-' + updated_session.id + '">' + updated_session.in_queue + '</td>';
                    }
                    if ($.inArray("6", selectedArr) != -1) {
                        row += '<td>' + updated_session.pending + '</td>';
                    }
                    if ($.inArray("7", selectedArr) != -1) {
                        row += '<td>' + updated_session.not_attending + '</td>';
                    }
                    if ($.inArray("8", selectedArr) != -1) {
                        row += '<td>' + updated_session.cost + '</td>';
                    }
                    if ($.inArray("9", selectedArr) != -1) {
                        if (updated_session.vat_rate != null) {
                            row += '<td>' + updated_session.vat_rate + '%' + '</td>';
                        } else {
                            row += '<td>' + 'N/A' + '</td>';
                        }

                    }
                    if ($.inArray("10", selectedArr) != -1) {
                        row += '<td>' + rating + '</td>';
                    }
                    if ($.inArray("11", selectedArr) != -1) {
                        row += '<td>' + no_of_attendees_evaluating + '</td>';
                    }
                    row += '<td>' +
                        '    <button class="btn btn-xs btn-edit-attending" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Participating"><i class="dropdown-icon fa fa-group"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-queue" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Queue"><i class="dropdown-icon fa fa-users"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-deciding" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Pending"><i class="dropdown-icon fa fa-user-secret"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-session-checkpoint" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Checkpoint"><i class="dropdown-icon fa fa-users"></i></button>' +
                        '</td><td>' +
                        '    <button class="btn btn-xs btn-edit-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '    <button class="btn btn-xs btn-duplicate-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '    <button class="btn btn-xs btn-danger btn-delete-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '    <a href="/admin/export-session/' + updated_session.id + '"> <button class="btn btn-xs btn-success btn-export-filter"data-original-title="Export"><i class="dropdown-icon fa fa-file-excel-o"></i></button> </a>' +
                        '</td>';
                    if (button.attr('id') === 'btn-update-session') {
                        var old_group = $('#group').attr('data-id');
                        if (old_group == updated_session.group.id) {
                            $('body .seminar-table tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_session.id) {
                                    $(this).html(row);
                                }
                            });
                        } else {
                            $('body .seminar-table tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_session.id) {
                                    $(this).remove();
                                }
                            });
                            var lists = '<button class="btn btn-xs btn-edit-attending" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Participating"><i class="dropdown-icon fa fa-users"></i></button>' +
                                '    <button class="btn btn-xs btn-edit-queue" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Queue"><i class="dropdown-icon fa fa-users"></i></button>' +
                                '    <button class="btn btn-xs btn-edit-deciding" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Pending"><i class="dropdown-icon fa fa-user-secret"></i></button>' +
                                '    <button class="btn btn-xs btn-edit-session-checkpoint" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Checkpoint"><i class="dropdown-icon fa fa-users"></i></button>';

                            var action = '    <button class="btn btn-xs btn-edit-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                                '    <button class="btn btn-xs btn-duplicate-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                                '    <button class="btn btn-xs btn-danger btn-delete-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                                '    <a href="/admin/export-session/' + updated_session.id + '"> <button class="btn btn-xs btn-success btn-export-filter"data-original-title="Export"><i class="dropdown-icon fa fa-file-excel-o"></i></button> </a>';

                            var t = $(".seminar-table-" + updated_session.group.id).DataTable();
                            t.row.add([
                                updated_session.id,
                                updated_session.name,
                                updated_session.attending,
                                max,
                                updated_session.percentage,
                                updated_session.in_queue,
                                updated_session.pending,
                                updated_session.not_attending,
                                updated_session.cost,
                                updated_session.vat_rate,
                                rating,
                                no_of_attendees_evaluating,
                                lists,
                                action

                            ]).draw(false);
                            //$('body #seminar_group_' + updated_session.group.id).next('.seminar-table').find('tbody').append('<tr>' + row + '</tr>');
                        }

                    } else {
                        //$('body #seminar_group_' + updated_session.group.id).next('.seminar-table').find('tbody').append('<tr>' + row + '</tr>');
                        var lists = '<button class="btn btn-xs btn-edit-attending" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Participating"><i class="dropdown-icon fa fa-users"></i></button>' +
                            '    <button class="btn btn-xs btn-edit-queue" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Queue"><i class="dropdown-icon fa fa-users"></i></button>' +
                            '    <button class="btn btn-xs btn-edit-deciding" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Pending"><i class="dropdown-icon fa fa-user-secret"></i></button>' +
                            '    <button class="btn btn-xs btn-edit-session-checkpoint" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Checkpoint"><i class="dropdown-icon fa fa-users"></i></button>';

                        var action = '    <button class="btn btn-xs btn-edit-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                            '    <button class="btn btn-xs btn-duplicate-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                            '    <button class="btn btn-xs btn-danger btn-delete-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                            '    <a href="/admin/export-session/' + updated_session.id + '"> <button class="btn btn-xs btn-success btn-export-filter"data-original-title="Export"><i class="dropdown-icon fa fa-file-excel-o"></i></button> </a>';
                        var t = $(".seminar-table-" + updated_session.group.id).DataTable();
                        t.row.add([
                            updated_session.id,
                            updated_session.name,
                            updated_session.attending,
                            max,
                            updated_session.percentage,
                            updated_session.in_queue,
                            updated_session.pending,
                            updated_session.not_attending,
                            updated_session.cost,
                            updated_session.vat_rate,
                            rating,
                            no_of_attendees_evaluating,
                            lists,
                            action

                        ]).draw(false);
                    }

                    $('#seminars-edit-seminar').modal('hide');
                }
                else {
                    clog(response);
                    var errors = response.message;
                    clog(errors);
                    prepareValidationMessage(errors);
                }
            },
            error: function (e) {
                clog(e);
            }
//            complete : function(){
//            }
        });
    }

    $body.on('click', '#btn-save-session', function () {
        addOrUpdateSession($(this));
    });

    $body.on('click', '#btn-update-session', function () {
        addOrUpdateSession($(this));
    });

    $body.on('click', '#btn-remove-queue', function () {
        $this = $(this);
        var session_id = $('#edit-session-queue').data('id');
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/sessions/remove-queue/',
            type: 'POST',
            data: {
                session_id: session_id,
                seminar_user_id: 'all',
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                //var response = JSON.parse(responseText);
                if (response.success) {
                    $.growl.notice({message: response.success});
                    $this.closest('.modal-body').find('#edit-session-queue tbody').remove();
                    var total_queue = response.total_queue;
                    $('#session-queue-count-' + session_id).html(total_queue);
                    $('#seminars-edit-cue').modal('hide');
                }

            },
            error: function (e) {
                clog(e);
            }
        });

    });

    $body.on('click', '#btn-remove-session-queue', function () {
        $this = $(this);
        var session_id = $('#edit-session-queue').data('id');
        var seminar_user_id = $(this).data('id');
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/sessions/remove-queue/',
            type: 'POST',
            data: {
                session_id: session_id,
                seminar_user_id: seminar_user_id,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                //var response = JSON.parse(responseText);
                if (response.success) {
                    $.growl.notice({message: response.success});
                    $this.closest('tr').remove();
                    var total_queue = response.total_queue;
                    $('#session-queue-count-' + session_id).html(total_queue);
                }

            },
            error: function (e) {
                clog(e);
            }
        });

    });

    /* session end*/

    /* rule */


    var lastResults = [];

    $(".add-speakerss").select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/attendee/getspeakers/',
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
//        createSearchChoice: function (term) {
//            var text = term + (lastResults.some(function(r) { return r.text == term }) ? "" : " (new)");
//            return { id: term, text: text };
//        },
    });


    $('body').on('hidden.bs.modal', '.modal', function () {
        $(this)
            .find("input,textarea,select")
            .val('')
            .end()
            .find("input[type=checkbox], input[type=radio]")
            .prop("checked", false)
            .end();
        $('#attendee_session_list').val('[]');
        $('#attendee_travel_list').val('[]');
        $('#travel_all_bounds').html('');
        $('#get_travel_id').val('');
        // $('textarea#froala_content_editor').froalaEditor('html.set', '');
//        $('#edit-attendee-question-attendee-groups').editable('setValue','');
    });

    $(".add-tags").select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/sessions/get-tags/',
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
        },
        //Allow manually entered text in drop down.
        createSearchChoice: function (term, data) {
            if ($.trim(term) != '') {
                if ($(data).filter(function () {
                        return this.text.localeCompare(term) === 0;
                    }).length === 0) {
                    return {id: term, text: term};
                }
            }
        }
    });

    $(".add-session-custom-class").select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/sessions/get-custom-class/',
            dataType: "json",
            type: "POST",
            data: function (term, page) {
                return {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    q: term
                };
            },

            results: function (data, page) {
                //lastResults = data.results;
                return data;
            }
        },
        //Allow manually entered text in drop down.
        createSearchChoice: function (term, data) {
            if ($.trim(term) != '') {
                if ($(data).filter(function () {
                        return this.text.localeCompare(term) === 0;
                    }).length === 0) {
                    return {id: term, text: term};
                }
            }
        }
    });

    $body.on('click', '.btn-edit-attending', function () {
        var session_id = $(this).data('id');
        var session_type = 'attending'
        createTempSessionFilter(session_type, session_id);
        //var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        //var data = {
        //    session_id: session_id,
        //    csrfmiddlewaretoken: csrfToken
        //}
        //$.ajax({
        //    url: base_url + '/admin/sessions/attending/',
        //    type: "POST",
        //    data: data,
        //    success: function (response) {
        //        $('#seminars-edit-attending').html(response);
        //        $('#seminars-edit-attending').modal();
        //    }
        //});
    });

    $body.on('click', '.btn-edit-session-checkpoint', function () {
        var session_id = $(this).data('id');
        var session_type = 'checkpoint';
        createTempSessionFilter(session_type, session_id);
        //var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        //var data = {
        //    session_id: session_id,
        //    csrfmiddlewaretoken: csrfToken
        //}
        //$.ajax({
        //    url: base_url + '/admin/sessions/checkpoint/',
        //    type: "POST",
        //    data: data,
        //    success: function (response) {
        //        $('#seminars-edit-attending').html(response);
        //        $('#seminars-edit-attending').modal();
        //    }
        //});
    });

    $body.on('click', '.btn-edit-queue', function () {
        var session_id = $(this).data('id');
        var session_type = 'in-queue';
        createTempSessionFilter(session_type, session_id);
        //var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        //var data = {
        //    session_id: session_id,
        //    csrfmiddlewaretoken: csrfToken
        //};
        //$.ajax({
        //    url: base_url + '/admin/sessions/queue/',
        //    type: "POST",
        //    data: data,
        //    success: function (response) {
        //        $('#seminars-edit-cue').html(response);
        //        $('#seminars-edit-cue').modal();
        //
        //        $('#edit-session-queue tbody').sortable({
        //            revert: true,
        //            connectWith: ".sortable",
        //            stop: function (event, ui) { /* do whatever here */
        //                var session_id = $(this).closest('#edit-session-queue').attr('data-id');
        //                queueRowOrder = [];
        //                var count = 0;
        //                $('#edit-session-queue tbody tr').each(function () {
        //                    var seminar_id = $(this).find('#btn-remove-session-queue').attr('data-id');
        //                    count++;
        //                    rowOrder = {'order': count, 'seminar_id': seminar_id};
        //                    queueRowOrder.push(rowOrder);
        //
        //                });
        //                clog(queueRowOrder);
        //                if (queueRowOrder.length > 0) {
        //                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        //                    $.ajax({
        //                        url: base_url + '/admin/sessions/queue_order/',
        //                        type: "POST",
        //                        data: {
        //                            queue_order: JSON.stringify(queueRowOrder),
        //                            session_id: session_id,
        //                            csrfmiddlewaretoken: csrf_token
        //                        },
        //                        success: function (result) {
        //                            if (result.error) {
        //                                $.growl.error({message: result.error});
        //                                setTimeout(function () {
        //                                    window.location.href = '';
        //                                }, 1000);
        //                            } else {
        //                                $.growl.notice({message: result.success});
        //
        //                            }
        //                        }
        //                    });
        //                }
        //            }
        //        });
        //    }
        //});
    });

    $body.on('click', '.btn-edit-deciding', function () {
        var session_id = $(this).data('id');
        var session_type = 'pending'
        createTempSessionFilter(session_type, session_id);
        //var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        //var data = {
        //    session_id: session_id,
        //    csrfmiddlewaretoken: csrfToken
        //}
        //$.ajax({
        //    url: base_url + '/admin/sessions/pending/',
        //    type: "POST",
        //    data: data,
        //    success: function (response) {
        //        $('#seminars-edit-deciding').html(response);
        //        $('#seminars-edit-deciding').modal();
        //    }
        //});
    });

    $body.on('click', '.btn-duplicate-session', function () {
        var session_id = $(this).data('id');
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            session_id: session_id,
            csrfmiddlewaretoken: csrfToken
        }
        $.ajax({
            url: base_url + '/admin/sessions/duplicate/',
            type: "POST",
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.success});
                    //setTimeout(function () {
                    //    window.location = ''
                    //}, 500);
                    var updated_session = response.session;
                    if (typeof (updated_session.average_rating) != 'undefined') {
                        var rating = updated_session.average_rating;
                        var no_of_attendees_evaluating = updated_session.no_of_attendees_evaluating;
                    } else {
                        var rating = 'N/A';
                        var no_of_attendees_evaluating = 'N/A';
                    }

                    if (updated_session.max_attendees == 0) {
                        max = '&#8734';
                    } else {
                        max = updated_session.max_attendees;
                    }

                    var lists = '<button class="btn btn-xs btn-edit-attending" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Participating"><i class="dropdown-icon fa fa-users"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-queue" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Queue"><i class="dropdown-icon fa fa-users"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-deciding" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Pending"><i class="dropdown-icon fa fa-user-secret"></i></button>' +
                        '    <button class="btn btn-xs btn-edit-session-checkpoint" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Checkpoint"><i class="dropdown-icon fa fa-users"></i></button>';

                    var action = '    <button class="btn btn-xs btn-edit-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '    <button class="btn btn-xs btn-duplicate-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '    <button class="btn btn-xs btn-danger btn-delete-session" data-id="' + updated_session.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '    <a href="/admin/export-session/' + updated_session.id + '"> <button class="btn btn-xs btn-success btn-export-filter"data-original-title="Export"><i class="dropdown-icon fa fa-file-excel-o"></i></button> </a>';

                    var t = $(".seminar-table-" + updated_session.group.id).DataTable();
                    t.row.add([
                        updated_session.id,
                        updated_session.name,
                        updated_session.attending,
                        max,
                        updated_session.percentage,
                        updated_session.in_queue,
                        updated_session.pending,
                        updated_session.not_attending,
                        updated_session.cost,
                        updated_session.vat_rate != null ? updated_session.vat_rate + "%" : "N/A",
                        rating,
                        no_of_attendees_evaluating,
                        lists,
                        action

                    ]).draw(false);

                } else {
                    $.growl.warning({message: response.error});
                }
            }
        });
    });

    $body.on('click', '.btn-duplicate-location', function () {
        var location_id = $(this).data('id');
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            location_id: location_id,
            csrfmiddlewaretoken: csrfToken
        }
        $.ajax({
            url: base_url + '/admin/locations/duplicate/',
            type: "POST",
            data: data,
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.success});
                    var updated_location = response.location;
                    var row = '' +
                        '<td>' + updated_location.id + '</td>' +
                        '      <td>' + updated_location.name + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs btn-edit-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '          <button class="btn btn-xs btn-duplicate-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '          <button class="btn btn-xs btn-danger btn-delete-location" data-id="' + updated_location.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
                    $('body #location_group_' + updated_location.group.id).next('.data-table-location').find('tbody').append('<tr>' + row + '</tr>');
                } else {
                    $.growl.warning({message: response.error});
                }
            }
        });
    });

    $('body').on('keyup', '#locations-edit-location #location_maps_highlights, #locations-edit-location #contact_name, #locations-edit-location #contact_web , #locations-edit-location #contact_phone, #locations-edit-location #contact_email', function () {
        var val = $(this).val();
        if (val.length >= 1) {
            $(this).parent().find('input[type=checkbox]').prop('checked', true);
        } else {
            $(this).parent().find('input[type=checkbox]').prop('checked', false);
        }
    });


});

function createTempSessionFilter(session_type, session_id) {
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        session_id: session_id,
        session_type: session_type,
        csrfmiddlewaretoken: csrfToken
    };
    //var response_data = false;
    $.ajax({
        url: base_url + '/admin/sessions/create-temp-session-filter/',
        type: "POST",
        data: data,
        async: false,
        success: function (response) {
            if (response.success) {
                showAttenddeBySessionType();
            }
            //if (response.success) {
            //    response_data = true;
            //    //showAttenddeBySessionType();
            //} else {
            //    response_data = false;
            //}
        },
        error: function () {
            //response_data = false;
        }
    });
    //return response_data;
}

function showAttenddeBySessionType() {
    var url = base_url + '/admin/attendee/';
    window.open(url, '_blank');
}