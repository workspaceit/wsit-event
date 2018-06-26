var $body = $('body');

$body.on('click', '.btn-add-hotel-to-attendee', function () {
    var div_id = $(this).closest('.fade').attr('id');
    var hotelSelector = $(this).parent().find('.add-attendee-hotel-selector');
    var selectedValue = hotelSelector.val();
    clog('selectedValue');
    clog(selectedValue);
    if (selectedValue == '' || selectedValue == null) {
        $.growl.warning({message: 'Please Select a hotel first'});
        return;
    }
    var selectedOption = hotelSelector.children().children('option:selected');
    var selectedText = selectedOption.html();
    //var vat = Number(selectedOption.data('vat'));
    var cost = Number(selectedOption.data('cost'));
    //var total = cost + ((cost / 100) * vat);
    var total = cost;
    //clog(vat + ' ' + cost);
    var allHotels = $('#hotel-selector').html();
    clog(allHotels);

    var row = '' +
        '<tr>' +
        '   <td>' +
        '       <button type="button" class="btn btn-sm btn-remove-attendee-hotel" data-id=' + '' + '><i class="fa fa-minus"></i></button>' +
        '   </td>' +
        '   <td>' + allHotels + '</td>' +
        '   <td>' +
        '       <div class="form-group">' +
        '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
        '               <input type="text" class="input-sm form-control start_date" name="start" data-date-format="dd/mm/yyyy" placeholder="Start date">' +
        '               <span class="input-group-addon">to</span>' +
        '               <input type="text" class="input-sm form-control end_date" name="end" placeholder="End date">' +
        '           </div>' +
        '       </div>' +
        '   </td>' +
        '   <td>' +
        '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies"></a>' +
        '   </td>';
//            '   <td class="cost">' + cost + '</td>' +
//            '   <td class="">€20 (Student)</td>' +
//            '   <td>' + cost + '</td>' +
//            '   <td>' + vat + '</td>' +
//            '   <td>' + total + '</td>' +
//            '</tr>';

    var lastRow = '';
//        +
//            '<td colspan="4">TOTAL</td>' +
//            '<td>$310</td>' +
//            '<td>$50</td>' +
//            '<td>$260</td>' +
//            '<td>25%</td>' +
//            '<td>€325</td>';

    var addTable = $(this).parent().parent().siblings('.attendee-add-hotels');
    addTable.find('.total').html(lastRow);
    addTable.find('tbody').append(row);
    addTable.find('tbody').children('tr:last').find('select').val(selectedValue);
    addTable.find('tbody').find('tr').each(function () {
        var allotment = $(this).find('.add-attendee-hotel-selector option:selected').attr('data-allotments');
        var availableDates = $.parseJSON(allotment);
        var d = new Date();
        if (availableDates.length > 0) {
            var dateStr = availableDates[0];
        } else {
            var currDate = d.getDate();
            var currMonth = d.getMonth();
            var currYear = d.getFullYear();

            var dateStr = currYear + "-" + currMonth + "-" + currDate;
        }
        $(this).find('.add-attendee-hotels-datepicker-range').datepicker({
            format: 'yyyy-mm-dd',
            beforeShowDay: function (date) {
                var dmy = date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2) + "-" + ("0" + date.getDate()).slice(-2);
                if ($.inArray(dmy, availableDates) != -1) {
                    return true;
                } else {
                    return false;

                }
            },
            startDate: dateStr
        });
    });
    activateAutoSuggestForBuddies(div_id);
});

$body.on('click', '.export-btn', function () {
    mn = $(this).attr('modalName');
    $("#" + mn).modal('hide');
});

$(document).ajaxSend(function () {
//    clog("Send");
    $('body .btn-save').prop('disabled', true);
});
$(document).ajaxComplete(function () {
    //clog("Complete");
    $('[data-toggle="tooltip"]').tooltip();
    $('body .btn-save').prop('disabled', false);
});
function check_export_status() {
    $.ajax({
        type: "GET",
        url: "/admin/get-export-state/",
        async: false
    }).success(function (result) {
        ajax_request = result.next_ajax_req;
        msg = result.msg;
        if (msg.length > 0) {
            $.each(msg, function (indx, item) {
                $.growl.notice({message: item.message});
            });
        }
        if (ajax_request == true) {
            setTimeout(function () {
                check_export_status();
            }, 5000);
        }
    });


}
function showAttendeeQuestions(questions, appendDiv, appendClass, outbound_flights, homebound_flights, answers) {
    $('.' + appendClass).html('');
    // if(date_format == null){
    //     date_format ='yyyy-mm-dd';
    // }
//    clog(appendClass);
//    clog(questions);
//    clog(answers);
//    alert("ok");
//    var allquestions = '';
    clog('questions');
    clog(questions);
    clog(questions.length);
    for (var i = 0; i < questions.length; i++) {
        var questionClass = "text-question-information";
        var dataType = "text";
        var value = "";
        var flights_value = "";
        var checkbox_value = [];
        if (answers) {
            for (var j = 0; j < answers.length; j++) {
                if ((typeof(answers[j]) != "undefined" && answers[j] !== null)) {
                    //if(answers[i].question)
                    if (answers[j].question.id == questions[i].question.id) {
                        if (questions[i].options.length > 0) {
                            if (questions[i].question.type == 'checkbox') {
                                var checkbox_answers = answers[j].value.split('<br>');
                                for (var l = 0; l < checkbox_answers.length; l++) {
                                    for (var k = 0; k < questions[i].options.length; k++) {
                                        if (checkbox_answers[l] == questions[i].options[k].option) {
                                            checkbox_value.push(questions[i].options[k].id);
                                        }
                                    }
                                }
                            } else {
                                for (var k = 0; k < questions[i].options.length; k++) {
                                    if (answers[j].value == questions[i].options[k].option) {
                                        value = questions[i].options[k].id;
                                    }
                                }
                            }
                        } else {
                            var range_types = ["date_range","time_range"];
                            if (questions[i].question.id == 104) {
                                value = answers[j].value.replace(/<(?:.|\n)*?>/gm, '')
                            }
                            else if (questions[i].question.id == 184 || questions[i].question.id == 185) {
                                flights_value = answers[j].value;
                            }
                            else if (range_types.indexOf(questions[i].question.type) != -1) {
                                value = answers[j].value;
                            }
                            else {
                                value = valueWithSpecialQuote(answers[j].value);
                                clog(questions[i].question.id + ': ' + value);
                            }
                        }
                    }
                }
            }
        }
        var req = questions[i].question.required;
        var options = [];
        clog(questions[i].question.type);
        if (questions[i].question.type == "select") {
            var option = {value: '', text: ""}
            options.push(option);
        }
        for (var j = 0; j < questions[i].options.length; j++) {
            var option = {value: questions[i].options[j].id, text: questions[i].options[j].option}
            options.push(option);
        }
        if (questions[i].question.type == "select") {
            questionClass = "select-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "radio_button") {
            questionClass = "radio-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "checkbox") {
            questionClass = "checkbox-question-information-" + questions[i].question.id;
            dataType = "checklist";
        } else if (questions[i].question.type == "date") {
            questionClass = "date-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "textarea") {
            questionClass = "textarea-question-information-" + questions[i].question.id;
            dataType = "textarea";
        } else if (questions[i].question.type == "rate") {
            questionClass = "rate-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "image_upload") {
            questionClass = "image_upload-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "password") {
            questionClass = "password-question-information-" + questions[i].question.id;
        }
        if (questions[i].question.id == 184) {
            for (var flight = 0; flight < outbound_flights.length; flight++) {
                var departure_date = moment(outbound_flights[flight].departure).format('YYYY-MM-DD'),
                    arrival_date = moment(outbound_flights[flight].arrival).format('YYYY-MM-DD');
                var departure_time = moment(outbound_flights[flight].departure).format('HH:mm');
                var arrival_time = moment(outbound_flights[flight].arrival).format('HH:mm');
                var text = departure_date + ' ' + outbound_flights[flight].name + ' ' + departure_time + '-' + arrival_time;
                var option = {value: 'flight_' + outbound_flights[flight].id, text: text}
                options.push(option);
                if (answers) {
                    if (flights_value == text) {
                        value = 'flight_' + outbound_flights[flight].id;
                    }

                }
            }
            questionClass = "select-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.id == 185) {
            for (var flight = 0; flight < homebound_flights.length; flight++) {
                var departure_date = moment(homebound_flights[flight].departure).format('YYYY-MM-DD'),
                    arrival_date = moment(homebound_flights[flight].arrival).format('YYYY-MM-DD');
                var departure_time = moment(homebound_flights[flight].departure).format('HH:mm');
                var arrival_time = moment(homebound_flights[flight].arrival).format('HH:mm');
                var text = departure_date + ' ' + homebound_flights[flight].name + ' ' + departure_time + '-' + arrival_time;
                var option = {value: 'flight_' + homebound_flights[flight].id, text: text}
                options.push(option);
                if (answers) {
                    if (flights_value == text) {
                        value = 'flight_' + homebound_flights[flight].id;
                    }
                    clog(flights_value);
                    clog(text);
                    clog(value);

                }
            }
            questionClass = "select-question-information-" + questions[i].question.id;
            dataType = "select";
        }
        if (questions[i].question.type == 'checkbox') {
            var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                '<td>' + questions[i].question.title + '</td>' +
                '<td><a href="#" class="' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + checkbox_value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                '</tr>';
        } else if (questions[i].question.type == 'date') {

            var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                '<td>' + questions[i].question.title + '</td>' +
                // '<td><a href="#" class="' + questionClass + ' date-question-attendee-info" name="questions[]" data-type="date" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                '<td><a href="#" id="' + questions[i].question.id + '_date" class="' + questionClass + ' date-question-attendee-info" name="questions[]" data-type="date" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req="' + req + '" data-range-from-date="' + questions[i].question.from_date + '" data-range-to-date="' + questions[i].question.to_date + '"></a></td>' +
                '</tr>';
        } else if (questions[i].question.type == 'time') {
            dataType = "time";
            questionClass = "time-question-information";
            var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                '<td>' + questions[i].question.title + '</td>' +
                '<td><a href="#" id="' + questions[i].question.id + '_time" class="' + questionClass + ' time-question-attendee-info" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                '</tr>';
        } else if (questions[i].question.type == 'date_range') {

            if (value != '') {
                var date_range_val = JSON.parse(value);
                var value_from = date_range_val[0];
                var value_to = date_range_val[1];
                var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                    '<td>' + questions[i].question.title + '</td>' +
                    '<td><a href="#" id="' + questions[i].question.id + '_from" class="date-range-question-attendee-info date_range" name="questions[]" data-type="date" data-pk="' + questions[i].question.id + '" data-value="' + value_from + '" data-title="' + questions[i].question.title + '" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a>' +
                    ' to <a href="#" id="' + questions[i].question.id + '_to" class="date-range-question-attendee-info date_range"  data-type="date" data-pk="' + questions[i].question.id + '" data-value="' + value_to + '" data-title="' + questions[i].question.title + '" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a></td>' +
                    '</tr>';
            } else {
                var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                    '<td>' + questions[i].question.title + '</td>' +
                    '<td><a href="#" id="' + questions[i].question.id + '_from" class="date-range-question-attendee-info date_range" name="questions[]" data-type="date" data-pk="' + questions[i].question.id + '"  data-title="' + questions[i].question.title + '" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a>' +
                    ' to <a href="#" id="' + questions[i].question.id + '_to" class="date-range-question-attendee-info date_range"  data-type="date" data-pk="' + questions[i].question.id + '" data-title="' + questions[i].question.title + '" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a></td>' +
                    '</tr>';
            }
        }
        else if (questions[i].question.type == 'time_range') {
            dataType = "time";
            questionClass = "time-range-question-information";
            if (value != '') {
                var date_range_val = JSON.parse(value);
                var value_from = date_range_val[0];
                var value_to = date_range_val[1];
                var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                    '<td>' + questions[i].question.title + '</td>' +
                    '<td><a href="#" id="' + questions[i].question.id + '_from" class="' + questionClass + ' time-range-question-attendee-info time_range" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value_from + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a>' +
                    ' to <a href="#" id="' + questions[i].question.id + '_to" class="' + questionClass + ' time-range-question-attendee-info time_range" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value_to + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                    '</tr>';
            } else {
                var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                    '<td>' + questions[i].question.title + '</td>' +
                    '<td><a href="#" id="' + questions[i].question.id + '_from" class="' + questionClass + ' time-range-question-attendee-info time_range" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '"  data-title="' + questions[i].question.title + '" data-req=' + req + '></a>' +
                    ' to <a href="#" id="' + questions[i].question.id + '_to" class="' + questionClass + ' time-range-question-attendee-info time_range"  data-type="' + dataType + '" data-pk="' + questions[i].question.id + '"  data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                    '</tr>';
            }
        }
        else if(questions[i].question.type == 'country') {
            dataType = 'select';
            questionClass = 'country-question-information select-question-information-' + questions[i].question.id;
            options = [];
            options.push({value: '', text: ''});
            for(var k=0;k<country_list.length;k++) {
                var option = {value: country_list[k].id, text: country_list[k].text};
                options.push(option);
            }
            var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                '<td>' + questions[i].question.title + '</td>' +
                '<td><a href="#" class="' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                '</tr>';
        }
        else {
            var allquestions = '<tr data-actual="' + questions[i].question.actual_definition + '">' +
                '<td>' + questions[i].question.title + '</td>' +
                '<td><a href="#" class="' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
                '</tr>';
        }
        $('#' + appendDiv).find('.' + appendClass).append(allquestions);
        if (typeof questions[i].access != "undefined" && questions[i].access == 'write') {
            $('.text-question-information').editable({
//            validate: function (value) {
//                if ($.trim(value) == '') return 'This field is required';
//            }
            });

            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            // $('.date-question-information-' + questions[i].question.id).editable({
            //    type : "date",
            //    format: 'yyyy-mm-dd',
            //    viewformat: 'dd/mm/yyyy',
            //    datepicker: {
            //        weekStart: 1
            //    }
            // });
            $('.textarea-question-information-' + questions[i].question.id).editable({
//            validate: function (value) {
//                if ($.trim(value) == '') return 'This field is required';
//            }
            });


        } else {
            $('.text-question-information').editable({
                disabled: true
            });

            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options,
                disabled: true
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.date-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
            $('.textarea-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
        }


    }
//    return allquestions;
}
function randomPassword(length) {
    var chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP1234567890";
    var pass = "";
    for (var x = 0; x < length; x++) {
        var i = Math.floor(Math.random() * chars.length);
        pass += chars.charAt(i);
    }
    return pass;
}
function clearAttendeeData(modal_id) {
    var modal = $('#' + modal_id);
    modal.find('.attendee-edit-sessions').find('tbody').html('');
    modal.find('.attendee-edit-travels').find('tbody').html('');
    modal.find('.attendee-add-hotels').find('tbody').html('');
    $('#add-attendee-questions').find('.attendee-question-attendee-tags').select2('val', '')
    // $('#add-attendee-question-attendee-groups').editable('setValue', null);
}
function changeBooking($html) {
    var div_id = $html.closest('.fade').attr('id');
    var allotment = $html.find('option:selected').attr('data-allotments');
    var $this = $html;
    var availableDates = $.parseJSON(allotment);
    clog('availableDates');
    clog(availableDates);
    var oldCheckIn = $html.closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=start]').val();
    var oldCheckOut = $html.closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=end]').val();
    clog(oldCheckIn);
    clog(oldCheckOut);
    clog($.inArray(oldCheckIn, availableDates));
    clog($.inArray(oldCheckOut, availableDates));
    $this.closest('tr').find('.add-attendee-hotels-datepicker-range').datepicker().remove();
    var data = '<div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
        '               <input type="text" class="input-sm form-control start_date" name="start" placeholder="Start date" value="" >' +
        '               <span class="input-group-addon">to</span>' +
        '               <input type="text" class="input-sm form-control end_date" name="end" placeholder="End date" value="" >' +
        '           </div>';
    $this.closest('tr').find('td:eq(2)').find('.form-group').append(data);
    var d = new Date();
    if (availableDates.length > 0) {
        var dateStr = availableDates[0];
    } else {
        var currDate = d.getDate();
        var currMonth = d.getMonth();
        var currYear = d.getFullYear();

        var dateStr = currYear + "-" + currMonth + "-" + currDate;
    }
    $this.closest('tr').find('.add-attendee-hotels-datepicker-range').datepicker({
        format: 'yyyy-mm-dd',
        beforeShowDay: function (date) {
            var dmy = date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2) + "-" + ("0" + date.getDate()).slice(-2);
            if ($.inArray(dmy, availableDates) != -1) {
                return true;
            } else {
                return false;

            }
        },
        startDate: dateStr

    });
    if ($.inArray(oldCheckIn, availableDates) != -1 && $.inArray(oldCheckOut, availableDates) != -1) {
        $html.closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=start]').val(oldCheckIn);
        $html.closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=end]').val(oldCheckOut);

    }
}
function checkIsBookingBreakUp(booking_id, room_id, check_in, check_out) {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    //var returnValue;
    $.ajax({
        url: base_url + '/admin/hotels/check-match/',
        type: "POST",
        data: {
            booking_id: booking_id,
            room_id: room_id,
            check_in: check_in,
            check_out: check_out,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            //clog(result);
            if (result.error) {
                $.growl.error({message: result.error});
            } else {
                return result;
            }
        }
    });
    //return false;

}
function decodeHTMLEntities(text) {
    var entities = [
        ['apos', '\''],
        ['amp', '&'],
        ['lt', '<'],
        ['gt', '>']
    ];

    for (var i = 0, max = entities.length; i < max; ++i)
        text = text.replace(new RegExp('&' + entities[i][0] + ';', 'g'), entities[i][1]);

    return text;
}
function attendeeSession(name, id, pushArray, $this, session_start, session_end) {
    var $sessionList = $("#attendee_session_list");
    if (name != "" && name != "Empty") {
        var sessionList = JSON.parse($sessionList.val());
        //clog(sessionList);
        for (var i = 0; i < sessionList.length; i++) {
            if (sessionList[i].id == id) {
                pushArray = false;
//                clog(sessionList);
//                var index = sessionList.indexOf(i);
//                clog(index);
//                sessionList.splice(index,1);
            }
        }
        clog("Reciving id " + id);
        $('.attendee-edit-sessions tbody').find('tr').each(
            function () {
                var button_id = $(this).find('td:nth(0)').find('button').attr('data-session');
                if (button_id == id) {
                    pushArray = false;
                }
                clog(button_id);
            });

        if (id != "" && id != undefined) {
            var sessionListTemp = {name: name, id: id};
        }
        if (pushArray) {
            sessionList.push(sessionListTemp);
            var date_format = moment_date_format + ' HH:mm:ss';
            $this.closest('.set-attendee-sessions').find('.attendee-sessions').append('<tr>' +
                '<td><button type="button" class="btn btn-sm btn-attendee-session-remove" data-id=' + id + ' data-session=' + id + '><i class="fa fa-minus"></i></button></td>' +
                '<td>' + name + '</td>' +
                '<td>' + moment(session_start, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                '<td>' + moment(session_end, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                '<td>Attending</td>' +
                '<td>' + moment(new Date()).format(date_format) + '</td>' +
//                '<td>€120</td>' +
//                '<td>€20 (Student)</td>' +
//                '<td>€100</td>' +
//                '<td>25%</td>' +
//                '<td>€125</td>' +
                '</tr>');
        }
        $sessionList.val(JSON.stringify(sessionList));
    }
//    clog($("#attendee_session_list").val());
}
function attendeeTravel(name, id, pushArray, $this, travel_departure, travel_arrival) {
    var $travelList = $("#attendee_travel_list");
    if (name != "" && name != "Empty") {
        var travelList = JSON.parse($travelList.val());
        //clog(sessionList);
        for (var i = 0; i < travelList.length; i++) {
            if (travelList[i].id == id) {
                pushArray = false;
//                clog(sessionList);
//                var index = sessionList.indexOf(i);
//                clog(index);
//                sessionList.splice(index,1);
            }
        }
        clog("Reciving id " + id);
        $('.attendee-edit-travels tbody').find('tr').each(
            function () {
                var button_id = $(this).find('td:nth(0)').find('button').attr('data-travel');
                if (button_id == id) {
                    pushArray = false;
                }
                clog(button_id);
            });

        if (id != "" && id != undefined) {
            var travelListTemp = {name: name, id: id};
        }
        if (pushArray) {
            travelList.push(travelListTemp);
            var date_format = moment_date_format + ' HH:mm:ss';
            $this.closest('.set-attendee-travels').find('.attendee-travels').append('<tr>' +
                '<td><button type="button" class="btn btn-sm btn-attendee-travel-remove" data-id=' + id + '  data-travel=' + id + '><i class="fa fa-minus"></i></button></td>' +
                '<td>' + name + '</td>' +
                '<td>' + moment(travel_departure, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                '<td>' + moment(travel_arrival, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                '<td>Attending</td>' +
                '<td>' + moment(new Date()).format(date_format) + '</td>' +
//                '<td>€120</td>' +
//                '<td>€20 (Student)</td>' +
//                '<td>€100</td>' +
//                '<td>25%</td>' +
//                '<td>€125</td>' +
                '</tr>');
        }
        $travelList.val(JSON.stringify(travelList));
    }
    clog($("#attendee_travel_list").val());
}
function showMultipleAttendeeQuestions(questions, appendDiv, appendClass) {
    $('.' + appendClass).html('');
//    var allquestions = '';
    for (var i = 0; i < questions.length; i++) {
        var questionClass = "text-question-information";
        var dataType = "text";
        var value = [];
        var options = [];
        for (var j = 0; j < questions[i].answers.length; j++) {
            if ((typeof(questions[i].answers[j]) != "undefined" && questions[i].answers[j] !== null)) {
                if (questions[i].answers[j].question.id == questions[i].question.id) {
                    if (questions[i].options.length > 0) {
                        for (var k = 0; k < questions[i].options.length; k++) {
                            if (questions[i].answers[j].value == questions[i].options[k].option) {
                                value = "[Multiple Values]";
                                options.push({value: '[Multiple Values]', text: '[Multiple Values]'})
//                                if (questions[i].question.type == 'select' || questions[i].question.type == 'radio_button') {
//                                    value = questions[i].options[k].id;
//                                } else {
//                                    value.push(questions[i].options[k].id);
//                                }
                            }
                        }
                    } else {
                        value = "[Multiple Values]";
                        options.push({value: '[Multiple Values]', text: '[Multiple Values]'})
//                        if (questions[i].question.id == 104) {
//                            value.push(questions[i].answers[j].value.replace(/<(?:.|\n)*?>/gm, ''));
//                        } else {
//                            value.push(questions[i].answers[j].value);
//                        }
                    }
//                        value.push(questions[i].answers[j].value);
                }
            }
        }
        for (var j = 0; j < questions[i].options.length; j++) {
            var option = {value: questions[i].options[j].id, text: questions[i].options[j].option}
            options.push(option);
        }
        if (questions[i].question.type == "select") {
            questionClass = "select-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "radio_button") {
            questionClass = "radio-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "checkbox") {
            questionClass = "checkbox-question-information-" + questions[i].question.id;
            dataType = "checklist";
        } else if (questions[i].question.type == "date") {
            questionClass = "date-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "textarea") {
            questionClass = "textarea-question-information-" + questions[i].question.id;
            dataType = "textarea";
        } else if (questions[i].question.type == "rate") {
            questionClass = "rate-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "image_upload") {
            questionClass = "image_upload-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "password") {
            questionClass = "password-question-information-" + questions[i].question.id;
        }
        var allquestions = '<tr>' +
            '<td>' + questions[i].question.title + '</td>' +
            '<td><a href="#" class="' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '"></a></td>' +
            '</tr>';
        $('#' + appendDiv).find('.' + appendClass).append(allquestions);
        if (typeof questions[i].access != "undefined" && questions[i].access == 'write') {
            $('.text-question-information').editable({
                //            validate: function (value) {
                //                if ($.trim(value) == '') return 'This field is required';
                //            }
            });
            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.date-question-information-' + questions[i].question.id).editable({
                //            format: 'yyyy-mm-dd',
                //            viewformat: 'dd/mm/yyyy',
                //            datepicker: {
                //                weekStart: 1
                //            }
            });
            $('.textarea-question-information-' + questions[i].question.id).editable({
                //            validate: function (value) {
                //                if ($.trim(value) == '') return 'This field is required';
                //            }
            });
        } else {
            $('.text-question-information').editable({
                disabled: true
            });
            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options,
                disabled: true
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.date-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
            $('.textarea-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
        }
    }
//    return allquestions;
}
function questionHead(questionType, action) {
    if (action == undefined) {
        action = 'add';
    }
    $('#add-question-country-group').hide();
    $('#edit-question-country-group').hide();
    $('#date-type-time-range').hide();
    $('#date-type-date-range').hide();
    $('#edit-date-type-date-range').hide();
    $('#edit-date-type-time-range').hide();
    $('#view-date-type-date-range').hide();
    $('#view-date-type-time-range').hide();
    $('#add-time-interval-group').hide();
    $('#edit-time-interval-group').hide();
    if (questionType == "text") {
        $('.question-panel-title').html('<i class="fa fa-font fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Text</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
    } else if (questionType == "select") {
        $('.question-panel-title').html('<i class="fa fa-check-square-o fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Select</strong>');
        $('#questions-add').find('#q_options').show();
        $('#questions-add').find('#options_table').html('<tbody></tbody>');
    } else if (questionType == "radio_button") {
        $('.question-panel-title').html('<i class="fa fa-dot-circle-o fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>RadioButton</strong>');
        $('#questions-add').find('#q_options').show();
        $('#questions-add').find('#options_table').html('<tbody></tbody>');
    } else if (questionType == "checkbox") {
        $('.question-panel-title').html('<i class="fa fa-check-square-o fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Checkbox</strong>');
        $('#questions-add').find('#q_options').show();
        $('#questions-add').find('#options_table').html('<tbody></tbody>');
    } else if (questionType == "date") {
        $('.question-panel-title').html('<i class="fa fa-calendar fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Date</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
        if (action == 'add') {
            $('#date-type-date-range').show();
        } else if (action == 'edit') {
            $('#edit-date-type-date-range').show();
        } else if (action == 'view') {
            $('#view-date-type-date-range').show();
        }

    } else if (questionType == "date_range") {
        clog('date_range');
        $('.question-panel-title').html('<i class="fa fa-calendar fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Date Range</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
        if (action == 'add') {
            $('#date-type-date-range').show();
        } else if (action == 'edit') {
            $('#edit-date-type-date-range').show();
        } else if (action == 'view') {
            $('#view-date-type-date-range').show();
        }
    } else if (questionType == "time") {
        $('.question-panel-title').html('<i class="fa fa-calendar fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Time</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
        $('#add-time-interval-group').show();
        $('#edit-time-interval-group').show();
        if (action == 'add') {
            $('#date-type-time-range').show();
        } else if (action == 'edit') {
            $('#edit-date-type-time-range').show();
        } else if (action == 'view') {
            $('#view-date-type-time-range').show();
        }
    } else if (questionType == "time_range") {
        $('.question-panel-title').html('<i class="fa fa-calendar fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Time Range</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
        $('#add-time-interval-group').show();
        $('#edit-time-interval-group').show();
        if (action == 'add') {
            $('#date-type-time-range').show();
        } else if (action == 'edit') {
            $('#edit-date-type-time-range').show();
        } else if (action == 'view') {
            $('#view-date-type-time-range').show();
        }
    }
    else if (questionType == "textarea") {
        $('.question-panel-title').html('<i class="fa fa-align-justify fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Textarea</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
    } else if (questionType == "rate") {
        $('.question-panel-title').html('<i class="fa fa-pie-chart fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Rate</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
    } else if (questionType == "image_upload") {
        $('.question-panel-title').html('<i class="fa fa-dot-circle-o fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Image Upload</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
    } else if (questionType == "password") {
        $('.question-panel-title').html('<i class="fa fa-dot-circle-o fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Password</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
    }
    else if(questionType == 'country') {
        $('.question-panel-title').html('<i class="fa fa-align-justify fa-lg"></i>&nbsp;&nbsp;&nbsp;<strong>Country</strong>');
        $('#questions-add').find('#options_table').find('tbody').remove();
        $('#questions-add').find('#q_options').hide();
        if(action == 'add') {
            $('#add-question-country-group').show();
        }
        else{
            $('#edit-question-country-group').show();
        }
    }
    $('#question_type').val(questionType);
    $('#questions-add').find('.filr').not('div:first').remove();
}
function validateEmail(email) {
    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    return re.test(email);
}
function phoneValidate(phone) {
    var re = /^[0-9+-\\(\\) ]*$/;
    return re.test(phone);
}
function fieldsInit() {

}
function getOptionList(className) {
    var optionsList = [];
    $('#' + className).find('#options_table tbody tr').each(function () {
        var title = $(this).find('.edit-button-label').html();
        var default_value = $(this).find('input[name="option_val"]').is(':checked')
        if (title != '' && title != 'Empty') {
            var id = $(this).attr('data-id');
            // if (id != undefined && id != '') {
            //     option = {'option': title, 'id': id, 'default_value': default_value, 'option_lang': valueWithSpecialQuote(title)};
            // } else {
            //     option = {'option': title, 'default_value': default_value, 'option_lang': valueWithSpecialQuote(title)};
            // }
            if (id != undefined && id != '') {
                option = {
                    'option': replaceSpecialCharacter(title),
                    'id': id,
                    'default_value': default_value,
                    'option_lang': valueWithSpecialQuote(replaceSpecialCharacter(title))
                };
            } else {
                option = {
                    'option': replaceSpecialCharacter(title),
                    'default_value': default_value,
                    'option_lang': valueWithSpecialQuote(replaceSpecialCharacter(title))
                };
            }
            optionsList.push(option);
        }
    });
    return optionsList;
}
function activateAutoSuggestForBuddies(id) {
    var addTable = $('#' + id).find('.attendee-add-hotels');
    var current_attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
    if (current_attendee_id == undefined) {
        current_attendee_id = 0;
    }
    var lastInsertedRow = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-select-room-buddies');
    var beds = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-selector option:selected').attr('data-beds');
    var maxbuddy = beds - 1;
    lastInsertedRow.select2({
        tags: true,
        tokenSeparators: [","],
        maximumSelectionSize: maxbuddy,
        ajax: {
            multiple: true,
            url: base_url + '/admin/attendee/getattendees/',
            dataType: "json",
            type: "POST",
            data: function (term, page) {
                return {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    q: term,
                    val: $('#add-attendee-hotel-select-room-buddies').val(),
                    current_attendee: current_attendee_id
                };
            },
            results: function (data, page) {
                lastResults = data.results;
                return data;
            }
        },
        //Allow manually entered text in drop down.
        createSearchChoice: function (term, data) {
            if ($(data).filter(function () {
                    return this.text.localeCompare(term) === 0;
                }).length === 0) {
                return {id: term, text: term};
            }
        }
    });
}