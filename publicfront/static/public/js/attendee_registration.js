jQuery(document).ready(function ($) {
    var base_url = window.location.origin + '/' + event_url;
    $(".travel").hide();
    $(".accommodation").hide();
    $(".stockholm").hide();
    $(".passport").hide();
    $("#attendee9").hide();

    $("#attendee-attend-1").change(function () {
        $(".contact").not("#attendee9").slideDown();
        $(".default").not("#attendee9").slideDown();
        $('#contact-office-where-emloyed :nth-child(1)').prop('selected', true);
    });

// If attendee is not attendeing
    $("#attendee-attend-2").change(function () {
        clearAttendee();
        clearFlights()
        clearAccommodation()
        clearPassport()
        clearStockholm()
        $("#travel1").slideUp();
        $('#contact-office-where-emloyed :nth-child(1)').prop('selected', true);
    });

// ATTENDEE //

// Office where employed
    $("#contact-office-where-emloyed").change(function () {
        // When changing option
        var currentOffice = $(this).find(':selected').attr('data-office-selected');
        $("#travel-need-flight-1, #travel-need-flight-2").removeAttr("checked");
        clearFlights()
        clearAccommodation()
        clearPassport()
        clearStockholm()

        // If none is selected
        if (currentOffice == "none") {
            clearFlights();
            $(".travel").slideUp();

            // If Barcelone is selected
        } else if (currentOffice == "Stockholm") {
            $("#travel2").slideUp();
            $("#travel1").slideUp();

            if ($("#attendee-attend-1").is(':checked')) {
                $(".stockholm.main").slideDown("fast");
                $("[data-stockholm='no']").slideUp();
                $(".travel.title").not(".sub").slideDown();
            }

            // All other cases
        }
        // else if (currentOffice == "Activision / Blizzard") {
        //    clearFlights();
        //    $(".travel").slideUp();
        //    $("#travel2").slideUp();
        //    $("#travel1").slideUp();
        //    $(".title.accommodation").slideDown();
        //    $("#accommodation1").slideDown();
        //}
        else {
            $("#flights_table tbody tr").hide();
            $("#flights_table .outbound." + currentOffice + ", .other").show();

            // If attendee is attending
            if ($("#attendee-attend-1").is(':checked')) {
                $("#travel1").show();
                $(".travel.title").not(".sub").slideDown();
                $(".title.accommodation").slideDown();
                $("#accommodation1").slideDown();
            }
        }
    });


// Shows "Specify dietary needs" when needed
    $("#contact-food-requirements").change(function () {
        if ($(this).val() == "Other") {
            $("#attendee9").slideDown("fast");
        } else {
            $("#attendee9").slideUp("fast");
            $("#contact-specify-dietary-needs").val("")
        }
    });

// STOCKHOLM //

// Lives within city limits
    $("#stockholm-live-in-stockholm-1").change(function () {
        $("#stockholm2").slideDown("fast");
        $("#stockholm3").slideUp("fast");
        $("#stockholm3").find("input[type='radio']").removeAttr("checked");
        $("#stockholm4").slideUp("fast");
        $("#stockholm4").find("input[type='text']").val("");
        clearAccommodation()
    });

// Lives outside city limits
    $("#stockholm-live-in-stockholm-2").change(function () {
        $("#stockholm3").slideDown("fast");
        $("#stockholm2").slideUp("fast");
        $("#stockholm2").find("input[type='radio']").removeAttr("checked");
        $("#stockholm4").slideUp("fast");
        $("#stockholm4").find("input[type='text']").val("");
        clearAccommodation()
    });


// OUTSIDE stockholm CITY LIMITS //

// Attende wants Taxi
    $("#stockholm-accommodation-arrangment-1").change(function () {
        $("#stockholm4").slideDown("fast");
        clearAccommodation();
        clearPassport();
    });

// Attende wants hotel
    $("#stockholm-accommodation-arrangment-2").change(function () {
        $("#stockholm4").slideUp("fast");
        $("#stockholm4").find("input[type='text']").val("");
        $(".accommodation").not("[data-stockholm='no']").slideDown("fast");
        $(".passport").slideDown("fast");
        $("#accommodation-check-in").val("2016-05-20");
        $("#accommodation-check-out").val("2016-05-21");
        //$("#attendee-preferred-room-buddy").select2({
        //    tags: true,
        //    tokenSeparators: [","],
        //    maximumSelectionSize: 1,
        //    ajax: {
        //        multiple: true,
        //        url: base_url + '/attendee/getattendees_alt/',
        //        dataType: "json",
        //        type: "POST",
        //        data: function (term, page) {
        //            console.log(term);
        //            return {
        //                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //                q: term
        //                //f: $('#attendee-first-name').val(),
        //                //l: $('#attendee-last-name').val()
        //            };
        //        },
        //        results: function (data, page) {
        //            lastResults = data.results;
        //            return data;
        //        }
        //    },
        //    //Allow manually entered text in drop down.
        //    createSearchChoice: function (term, data) {
        //        if ($(data).filter(function () {
        //                return this.text.localeCompare(term) === 0;
        //            }).length === 0) {
        //            return {id: term, text: term};
        //        }
        //    }
        //});
    });

// Attende wants nothing
    $("#stockholm-accommodation-arrangment-3").change(function () {
        $("#stockholm4").slideUp("fast");
        $("#stockholm4").find("input[type='text']").val("");
        clearAccommodation();
        clearPassport();
    });


// FLIGHTS //

// If attendee want a flight
    $("#travel-need-flight-1").change(function () {
        var city = $('#contact-office-where-emloyed').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/flight/outbound/',
            type: "POST",
            data: {'city': city, csrfmiddlewaretoken: csrf_token},
            success: function (response) {
                c(response);
                var travels = response.travel_groups;
                var html = '';
                for (var i = 0; i < travels.length; i++) {
                    console.log(travels[i]);
                    html += '' +
                        '<tr class="titleOrigin Stockholm">' +
                        '   <td colspan="4"><strong>' + travels[i].group.name + ' (Outbound)</strong></td>' +
                        '</tr>';
                    var travels2 = travels[i].travels;
                    for (var j = 0; j < travels2.length; j++) {
                        var trClass = '';
                        if (travels2[j].full) {
                            trClass = 'full';
                        }
                        start_date = moment(travels2[j].departure, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD')
                        end_date = moment(travels2[j].arrival, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD')
                        var departure_time = moment(travels2[j].departure, 'YYYY-MM-DD HH:mm').format('HH:mm')
                        var arrival_time = moment(travels2[j].arrival, 'YYYY-MM-DD HH:mm').format('HH:mm')
                        var start_time = '';
                        var end_time = '';
                        if (departure_time != '00:00') {
                            start_time = departure_time
                        }
                        if (arrival_time != '00:00') {
                            end_time = arrival_time
                        }
                        html += '' +
                            '<tr class="Stockholm outbound outbound outbound-item-' + travels[i].group.id + ' ' + trClass + '">' +
                            '   <td>' +
                            '       <input type="radio" class="outbound-checkbox" name="outbound" data-group=' + travels[i].group.id + ' value=' + travels2[j].id + ' id="" data-homebound="#stockholm_homebound_1" data-start_date=' + start_date + ' data-start_time = ' + departure_time + ' data-end_time = ' + arrival_time + '>' +
                            '   </td>' +
                            '   <td>' +
                            '<label for="stockholm_outbound_1">' + travels2[j].name + '</label>' +
                            '   </td>' +
                            '   <td>' +
                            '<span class="date_checkin">' + start_date + ' ' + start_time + '</span>' +
                            '   </td>' +
                            '   <td>' + end_date + ' ' + end_time + '</td>' +
                            '</tr>';
                    }
                }

                $('#flights_table').find('tbody').html(html);
                var other = '' +
                    '<tr class="titleOrigin other"> ' +
                    '   <td colspan="4"><strong>Other</strong></td> ' +
                    '	    </tr> ' +
                    '		<tr class="other"> ' +
                    '           <td> ' +
                    '				<input type="radio" name="no_suitable_flight" value="I can\'t find any suitable flights" id="no_suitable_flight"> ' +
                    '			</td> ' +
                    '			<td>' +
                    '				<label for="no_suitable_flight">I can\'t find any suitable flights</label>' +
                    '			</td> ' +
                    '			<td></td> ' +
                    '			<td></td> ' +
                    '		</tr> ';
                $('#flights_table').find('tfoot').html(other);
                $('#travel-cannot-find').slideDown();
            }

        });


        $("#travel2").slideDown("fast");
        $("#travel4").slideDown("fast");
        $(".sub.title.travel").slideDown("fast");
        $(".passport").slideDown("fast");
        if ($('#contact-office-where-emloyed').val() == 'San Francisco' || $('#contact-office-where-emloyed').val() == 'Seattle' || $('#contact-office-where-emloyed').val() == 'Seoul' || $('#contact-office-where-emloyed').val() == 'Shanghai' || $('#contact-office-where-emloyed').val() == 'Singapore' || $('#contact-office-where-emloyed').val() == 'Tokyo') {
            $("#accommodation-check-in").val("2016-05-17");
            $("#accommodation-check-out").val("2016-05-21");
        }
        else {
            $("#accommodation-check-in").val("2016-05-18");
            $("#accommodation-check-out").val("2016-05-21");
        }

    });

// If attendee does not want a flight
    $("#travel-need-flight-2").change(function () {
        $("#travel2, #travel3, .sub.title.travel").slideUp("fast");
        clearFlights()
        if (!$("#accommodation-need-accommodation-1").prop('checked')) {
            clearPassport()
        }
        if ($('#contact-office-where-emloyed').val() == 'San Francisco' || $('#contact-office-where-emloyed').val() == 'Seattle' || $('#contact-office-where-emloyed').val() == 'Seoul' || $('#contact-office-where-emloyed').val() == 'Shanghai' || $('#contact-office-where-emloyed').val() == 'Singapore' || $('#contact-office-where-emloyed').val() == 'Tokyo') {
            $("#accommodation-check-in").val("2016-05-18");
            $("#accommodation-check-out").val("2016-05-21");
        }
        else {
            $("#accommodation-check-in").val("2016-05-18");
            $("#accommodation-check-out").val("2016-05-21");
        }
        $('#travel-cannot-find').slideUp();
    });

//If "I can't find a suitable flight" view "Comments regarding flight reservations / Special requests"
    $('body').on('change', "#no_suitable_flight", function () {
        $("#flights_table").find("input[type='radio'], input[type='checkbox']").not("#no_suitable_flight").removeAttr("checked");
        $("#travel3").slideDown("fast")
        $("tr.homebound").hide();
        $("tr.homebound").prev('.titleOrigin').hide();
    });

//If a specific flight is selected uncheck "I can't find a suitable flight" and hide "Comments regarding flight reservations / Special requests"
    $("#flights_table input[type='radio']").not("#no_suitable_flight").change(function () {
        $("#no_suitable_flight").removeAttr("checked");
        $("#travel3").find("textarea").val("");
        $("#travel3").slideUp("fast");
    });

// When selecting an outbound flight
    $("[name='outbound']").not("#no_suitable_flight").change(function () {
        $("[name='homebound']").removeAttr("checked");
        var currentAvailableHomebound = $(this).attr('data-homebound');
        $("tr.homebound").hide();
        var currentDestination = $("#contact-office-where-emloyed").find(':selected').attr('data-office-selected');
        $(currentAvailableHomebound).closest("tr").show();
        $(".titleOrigin." + currentDestination + ".homebound").show();
    });


//Marketing-Team

    $('body').on('change', "#marketing_team", function () {
        $("#flights_table").find("input[type='radio'], input[type='checkbox']").not("#marketing_team").removeAttr("checked");
        $("#travel3").slideDown("fast")
        $("tr.homebound").hide();
    });

//If a specific flight is selected uncheck "I can't find a suitable flight" and hide "Comments regarding flight reservations / Special requests"
    $("#flights_table input[type='radio']").not("#marketing_team").change(function () {
        $("#marketing_team").removeAttr("checked");
        $("#travel3").find("textarea").val("");
        $("#travel3").slideUp("fast");
    });

// When selecting an outbound flight
    $("[name='outbound']").not("#marketing_team").change(function () {
        $("[name='homebound']").removeAttr("checked");
        var currentAvailableHomebound = $(this).attr('data-homebound');
        $("tr.homebound").hide();
        var currentDestination = $("#contact-office-where-emloyed").find(':selected').attr('data-office-selected');
        $(currentAvailableHomebound).closest("tr").show();
        $(".titleOrigin." + currentDestination + ".homebound").show();
    });

// ACCOMMODATION //

// If the attendee want a hotel
    $("#accommodation-need-accommodation-1").change(function () {
        $(".accommodation").slideDown("fast");
        if ($('#travel-need-flight-1').prop('checked') && ($('#contact-office-where-emloyed').val() == 'San Francisco' || $('#contact-office-where-emloyed').val() == 'Seattle' || $('#contact-office-where-emloyed').val() == 'Seoul' || $('#contact-office-where-emloyed').val() == 'Shanghai' || $('#contact-office-where-emloyed').val() == 'Singapore' || $('#contact-office-where-emloyed').val() == 'Tokyo')) {
            $("#accommodation-check-in").val("2016-05-17");
            $("#accommodation-check-out").val("2016-05-21");
        }
        else if ($('#travel-need-flight-2').prop('checked') && ($('#contact-office-where-emloyed').val() == 'San Francisco' || $('#contact-office-where-emloyed').val() == 'Seattle' || $('#contact-office-where-emloyed').val() == 'Seoul' || $('#contact-office-where-emloyed').val() == 'Shanghai' || $('#contact-office-where-emloyed').val() == 'Singapore' || $('#contact-office-where-emloyed').val() == 'Tokyo')) {
            $("#accommodation-check-in").val("2016-05-18");
            $("#accommodation-check-out").val("2016-05-21");
        } else {
            $("#accommodation-check-in").val("2016-05-18");
            $("#accommodation-check-out").val("2016-05-21");
        }

        $(".passport").slideDown("fast");
        //$("#attendee-preferred-room-buddy").select2({
        //    tags: true,
        //    tokenSeparators: [","],
        //    maximumSelectionSize: 1,
        //    ajax: {
        //        multiple: true,
        //        url: base_url + '/attendee/getattendees_alt/',
        //        dataType: "json",
        //        type: "POST",
        //        data: function (term, page) {
        //            console.log(term);
        //            return {
        //                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //                q: term
        //                //f: $('#attendee-first-name').val(),
        //                //l: $('#attendee-last-name').val()
        //            };
        //        },
        //        results: function (data, page) {
        //            lastResults = data.results;
        //            return data;
        //        }
        //    },
        //    //Allow manually entered text in drop down.
        //    createSearchChoice: function (term, data) {
        //        if ($(data).filter(function () {
        //                return this.text.localeCompare(term) === 0;
        //            }).length === 0) {
        //            return {id: term, text: term};
        //        }
        //    }
        //});

        //set checkin and out
        if ($('#travel-need-flight-1').prop('checked')) {
            if ($('.outbound-checkbox').prop('checked')) {
                var date1 = $('.outbound-checkbox:checked').closest('tr').find('td:last').html();
                var arrival = moment(date1, 'YYYY-MM-DD, HH:mm').format('YYYY-MM-DD');
                $('#accommodation-check-in').val(arrival);
                console.log(arrival);
            }
            if ($('.homebound-checkbox').prop('checked')) {
                var date1 = $('.homebound-checkbox:checked').closest('tr').find('td:nth-child(3)').find('span').html();
                var departure = moment(date1, 'YYYY-MM-DD, HH:mm').format('YYYY-MM-DD');
                $('#accommodation-check-out').val(departure);
            }
        }
    });

// If the attendee does not want a hotel
    $("#accommodation-need-accommodation-2").change(function () {
        $(".accommodation").find("input[type='text'], input[type='date'], textarea").val("");
        $(".accommodation").not("#accommodation1").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".accommodation").not("#accommodation1, .title.accommodation").slideUp("fast");
        if (!$("#travel-need-flight-1").prop('checked')) {
            clearPassport()
        }
    });

// CLEARS //

// Clears the different question categories as functions

    function clearFlights() {
        $("#travel3").slideUp("fast");
        $("#travel3").find("textarea").val("");
        $("#flights_table input[type='radio']").removeAttr("checked");
        $(".travel").not(".travel.title, #travel1").slideUp("fast");
    }

    function clearAccommodation() {
        $(".accommodation").find("input[type='text'], input[type='date'], textarea").val("");
        $(".accommodation").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".accommodation").slideUp("fast");
    }

    function clearPassport() {
        $(".passport").find("input[type='text'], input[type='date'], textarea").val("");
        $(".passport").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".passport").slideUp("fast");
    }

    function clearStockholm() {
        $(".stockholm").find("input[type='text'], input[type='date'], textarea").val("");
        $(".stockholm").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".stockholm").slideUp();
        $(".travel.title").slideUp();
    }

    function clearAttendee() {
        $(".default").not("[data-not-attending='yes']").find("input[type='text'], input[type='date'], textarea").val("");
        $(".default").not("[data-not-attending='yes']").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".default").not("[data-not-attending='yes']").find("select :nth-child(1)").prop('selected', true);
        $(".default").not("[data-not-attending='yes']").slideUp("fast");
        $(".contact").not("[data-not-attending='yes']").find("input[type='text'], input[type='date'], textarea").val("");
        $(".contact").not("[data-not-attending='yes']").find("input[type='radio'], input[type='checkbox']").removeAttr("checked");
        $(".contact").not("[data-not-attending='yes']").find("select :nth-child(1)").prop('selected', true);
        $(".contact").not("[data-not-attending='yes']").slideUp("fast");
    }

    $('body').on('click', '.outbound-checkbox', function (e) {
        $('input[name="no_suitable_flight"]').prop('checked', false);
        $("#travel3").slideUp("fast");
        $("#travel3").find("textarea").val("");
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var outbound_id = $(this).val();
        var group_id = $(this).data('group');
        var $currentRow = $(this).closest('tr');
        $.ajax({
            url: base_url + '/flight/homebound/',
            type: "POST",
            data: {'outbound_id': outbound_id, csrfmiddlewaretoken: csrf_token},
            success: function (response) {
                console.log(response);
                var travels = response.travel_groups;
                var html = '';
                for (var i = 0; i < travels.length; i++) {
                    console.log(travels[i]);
                    html += '' +
                        '<tr class="titleOrigin Stockholm outbound homebound-item">' +
                        '   <td colspan="4"><strong>' + travels[i].group.name + ' (Homebound)</strong></td>' +
                        '</tr>';
                    var travels2 = travels[i].travels;
                    for (var j = 0; j < travels2.length; j++) {
                        var trClass = '';
                        if (travels2[j].full) {
                            trClass = 'full';
                        }
                        start_date = moment(travels2[j].departure, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD')
                        end_date = moment(travels2[j].arrival, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD')
                        var departure_time = moment(travels2[j].departure, 'YYYY-MM-DD HH:mm').format('HH:mm')
                        var arrival_time = moment(travels2[j].arrival, 'YYYY-MM-DD HH:mm').format('HH:mm')
                        var start_time = '';
                        var end_time = '';
                        if (departure_time != '00:00') {
                            start_time = departure_time
                        }
                        if (arrival_time != '00:00') {
                            end_time = arrival_time
                        }
                        html += '' +
                            '<tr class="Stockholm homebound  homebound-item ' + trClass + '">' +
                            '   <td>' +
                            '       <input type="radio" class="homebound-checkbox" name="homebound" data-group=' + travels[i].group.id + ' value=' + travels2[j].id + ' id="" data-homebound="#stockholm_homebound_1" data-start_date=' + start_date + ' data-start_time = ' + departure_time + ' data-end_time = ' + arrival_time + '>' +
                            '   </td>' +
                            '   <td>' +
                            '       <label for="stockholm_outbound_1">' + travels2[j].name + '</label>' +
                            '   </td>' +
                            '   <td>' +
                            '<span class="date_checkin">' + start_date + ' ' + start_time + '</span>' +
                            '   </td>' +
                            '   <td>' + end_date + ' ' + end_time + '</td>' +
                            '</tr>';
                    }
                }
                $('#flights_table').find('.homebound-item').remove();
                $(html).insertAfter($('#flights_table').find('.outbound-item-' + group_id + ':last'));
            }
        });

        if ($('#accommodation-need-accommodation-1').prop('checked')) {
            var date1 = $(this).closest('tr').find('td:last').html();
            var arrival = moment(date1, 'YYYY-MM-DD, HH:mm').format('YYYY-MM-DD');
            $('#accommodation-check-in').val(arrival);
        }

    });

    $('body').on('click', '.homebound-checkbox', function (e) {
        if ($('#accommodation-need-accommodation-1').prop('checked')) {
            var date1 = $(this).closest('tr').find('td:nth-child(3)').find('span').html();
            var departure = moment(date1, 'YYYY-MM-DD, HH:mm').format('YYYY-MM-DD');
            $('#accommodation-check-out').val(departure);
        }
    });


    $('body').on('click', '#btn-register-attendee', function (e) {
        e.preventDefault();
        var validated = true;
        var answers = [];
        var firstName = '';
        var lastName = '';
        var email = '';
        var phone = '';
        var data = {};
        var outbound = '';
        var homebound = '';
        var hasFlight = false;

        $('.formQuestion').removeClass('notValidated');

        if ($('input[name="travel-need-flight"]').prop('checked') && !($('input[name="no_suitable_flight"]:checked').length > 0 )) {

            if ($('input[name="outbound"]:checked').val() == undefined) {
                $('#travel2').addClass('notValidated');
                validated = false;
            }
            else if ($('input[name="homebound"]:checked').val() == undefined) {
                $('#travel2').addClass('notValidated');
                validated = false;
            }
            else {
                hasFlight = true;
                outbound = $('input[name="outbound"]:checked').val();
                homebound = $('input[name="homebound"]:checked').val();
                var outbound_answer = $('input[name="outbound"]:checked').attr('data-start_date') + ' ' + $('input[name="outbound"]:checked').parent().next('td').find('label').html() + ' ' + $('input[name="outbound"]:checked').attr('data-start_time') + '-' + $('input[name="outbound"]:checked').attr('data-end_time')
                var homebound_answer = $('input[name="homebound"]:checked').attr('data-start_date') + ' ' + $('input[name="homebound"]:checked').parent().next('td').find('label').html() + ' ' + $('input[name="homebound"]:checked').attr('data-start_time') + '-' + $('input[name="homebound"]:checked').attr('data-end_time')
                answers.push({
                    id: 184,
                    answer: outbound_answer
                });
                answers.push({
                    id: 185,
                    answer: homebound_answer
                });
            }
        }

        $('.formQuestion').each(function () {
            var row = $(this);
            if (row.css('display') != 'none') {
                var answer = '';
                var valid = true;
                var include = true;
                var element = row.find('.given-answer');
                var type = element.prop('type');
                if (type == 'text' || type == 'select-one' || type == 'textarea' || type == 'date') {
                    answer = element.val();
                    if ((answer == '' || answer == 'not selected') && row.data('req') == 1) {
                        valid = false;
                    }
                    else if ((answer == '' || answer == 'not selected') && row.data('req') == 0) {
                        include = false;
                    }
                    else if (element.attr('id') == 'passport-date-of-birth' || element.attr('id') == 'passport-date-of-issue' || element.attr('id') == 'accommodation-check-in' || element.attr('id') == 'accommodation-check-out') {
                        if (!dateValidate(element.val())) {
                            valid = false;
                        }
                    }
                    else if (element.attr('id') == 'passport-date-of-expire') {
                        if (!expDateValidate(element.val())) {
                            valid = false;
                        }
                    }
                    else if (element.attr('id') == 'default-king-email') {
                        if (!validateEmail(element.val())) {
                            valid = false;
                        }
                    }
                    else if (element.attr('id') == 'default-mobile-phone-number') {
                        if (!phoneValidate(element.val())) {
                            valid = false;
                        }
                    }
                }
                else if (type == 'radio') {
                    if (!element.is(':checked') && row.data('req') == 1) {
                        valid = false;
                    }
                    else {
                        var elemName = element.attr('name');
                        answer = $('input[name="' + elemName + '"]:checked').val();
                    }
                }
                else if (type == 'checkbox') {
                    if (!element.is(':checked') && row.data('req') == 0) {
                        include = false;
                    }
                    else {
                        answer = element.prop('checked');
                    }
                }
                if (!valid) {
                    validated = false;
                    row.addClass('notValidated');
                }
                else {
                    if (include) {
                        var id = row.data('id');
                        answers.push({
                            id: id,
                            answer: answer
                        });
                    }
                }
            }
        });
        var group = $('input[name="attendee-attend"]:checked').val();
        if (group == 'Yes') {
            var group_id = 95;
        }
        else if (group == 'No') {
            var group_id = 96;
        }

        var checkIn = $('#accommodation-check-in').val();
        var checkOut = $('#accommodation-check-out').val();
        var roomBuddy = $('#accommodation-preferred-room-buddy').val();
        var rooms = [];
        if ($('#accommodation-need-accommodation-1').prop('checked')) {
            var room = {room_id: 8, check_in: checkIn, check_out: checkOut, buddy: [roomBuddy]};
            rooms.push(room);
        }


        //if (roomBuddy !='' && !validateEmail(roomBuddy)) {
        //    $('#accommodation-preferred-room-buddy').parent().addClass('notValidated');
        //}

        if (validated) {
            $('#registration-loader').show();
            $(this).prop("disabled", true);
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            var noSuitableFlight = false;
            if ($('#no_suitable_flight').prop('checked')) {
                noSuitableFlight = true;
                answers.push({
                    id: 184,
                    answer: 'I can’t find a suitable flight'
                });
                answers.push({
                    id: 185,
                    answer: 'I can’t find a suitable flight'
                });
            }
            console.log(answers);
            data = {
                answers: JSON.stringify(answers),
                rooms: JSON.stringify(rooms),
                sessions: JSON.stringify([]),
                group_id: group_id,
                event_id: 11,
                email: $('#default-king-email').val(),
                no_suitable_flight: noSuitableFlight,
                csrfmiddlewaretoken: csrf_token
            };
            if (hasFlight) {
                data['hasFlight'] = true;
                data['flight'] = JSON.stringify([outbound, homebound]);
            }
            else {
                data['hasFlight'] = false;
                data['flight'] = JSON.stringify([]);
            }
            $.ajax({
                url: base_url + '/attendee-registration/',
                type: "POST",
                data: data,
                success: function (result) {
                    $('#registration-loader').hide();
                    $('#btn-register-attendee').prop('disabled', false);
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        setTimeout(function () {
                            window.location.href = base_url + '/?uid=' + result.key;
                        }, 500);
                    }
                }
            });
        }
        else {
            $('html, body').animate({
                scrollTop: $('.notValidated:visible:first').offset().top
            }, 300);
        }

    });

    function dateValidate(dateValue) {
        console.log(dateValue);
        console.log(moment(dateValue, 'YYYY-MM-DD', true).isValid());
        var momentDate = moment(dateValue, 'YYYY-MM-DD', true);
        console.log(momentDate.month());
        console.log(momentDate.date());
        if (!momentDate.isValid()) {
            return false;
        }
        else {
            if (momentDate.year() < 1900 || momentDate.year() > 2016 || momentDate.month() > 11 || momentDate.date() > 31) {
                return false;
            }
        }
        return true;
    }

    function expDateValidate(dateValue) {
        console.log(moment(dateValue, 'YYYY-MM-DD').isValid());
        var momentDate = moment(dateValue, 'YYYY-MM-DD', true);
        console.log(momentDate.month());
        console.log(momentDate.date());
        if (!momentDate.isValid()) {
            return false;
        }
        else {
            var firstDay = moment('2016-01-02', 'YYYY-MM-DD');
            if (moment(momentDate).isBefore(firstDay)) {
                return false;
            }
        }
        return true;
    }

    function phoneValidate(phone) {
        var re = /^[0-9+-\\(\\) ]*$/;
        return re.test(phone);
    }

    function validateEmail(email) {
        emails = [];
        $.ajax({
            url: base_url + '/get-allowed-emails/',
            type: "get",
            async: false,
            success: function (result) {
                result.forEach(function (entry) {
                    emails.push(entry.name);
                });
            }
        });
        validEmail = [];
        validDomain = [];
        emails.forEach(function (entry) {

            if (entry.indexOf("*") >= 0) {
                var domain = entry.substring(entry.lastIndexOf("@") + 1);
                validDomain.push(domain)
            } else {
                validEmail.push(entry);
            }
        });

        regularExp = ""
        validDomain.forEach(function (entry) {
            regularExp += "\\b";
            regularExp += entry;
            regularExp += "|";
        });
        var regex = regularExp.slice(0, -1)
        //console.log(validEmail);
        //console.log(regex);
        //var validEmail = ['lxj.isabella@gmail.com', 'JakobGraff@web.de', 'terrence.marriott@live.com', 'bjorn@toftmadsen.org', 'laridk@gmail.com', 'paulkreshchenko@gmail.com', 'xric@hotmail.co.uk', 'algernon@gmail.com', 'ben@todomedia.co.uk', 'andytomlinson@hotmail.co.uk', 'lxj.isabella@gmail.com', 'helenamoreira21@gmail.com']
        //var re = /^([\w-]+(?:\.[\w-]+)*)@(\bworkspaceit|\bspringconf|\bking).([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        if (emails.length > 0) {
            if (jQuery.inArray(email, validEmail) !== -1) {
                return true;
            } else {
                //var re = /^([\w-]+(?:\.[\w-]+)*)@(\bworkspaceit.com|\bspringconf.com|\bking.com|\btailwind.se|\bactivision.com|\bblizzard.com)$/;
                var re = new RegExp("^([\\w-]+(?:\\.[\\w-]+)*)@(" + regex + ")$");
                //console.log(re);
                return re.test(email);
            }
        }else{
            return true;
        }

    }

});