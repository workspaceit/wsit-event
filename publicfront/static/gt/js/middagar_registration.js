jQuery(document).ready(function ($) {

    Array.prototype.diff = function (a) {
        return this.filter(function (i) {
            return a.indexOf(i) < 0;
        });
    };

    init();

    var $gtSession = $('.gt-session');
    var $gtHotel = $('.gt-hotel');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var $formQuestion = $('.formQuestion');

    var previousSessions = [];
    var previousQuestions = [];
    var previousBookings = [];

    $('body').on('click', '#btn-middagar-attendee', function (e) {

        e.preventDefault();
        var validated = true;

        var answers = [];
        var sessions = [];
        var rooms = [];

        var questionsAnswered = [];
        var bookingSelected = [];

        $formQuestion.removeClass('notValidated');
        $formQuestion.each(function () {
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
                    else if (element.attr('id') == 'attendee-email') {
                        if (!validateEmail(element.val())) {
                            valid = false;
                        }
                    }
                    else if (element.attr('id') == 'attendee-mobiltelefon') {
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
                    if (!element.is(':checked') && row.data('req') == 1) {
                        valid = false;
                    }
                    else {
                        if (!element.is(':checked')) {
                            include = false;

                        }
                        else {
                            answer = element.val();
                        }
                    }
                }
                if (!valid) {
                    validated = false;
                    row.addClass('notValidated');
                }
                else {
                    if (include) {
                        questionsAnswered.push(row.data('id'));
                        var id = row.data('id');
                        answers.push({
                            id: id,
                            answer: answer
                        });
                    }
                }
            }
        });

        $gtSession.each(function () {
            var $row = $(this).closest('.attendee');
            if ($row.css('display') != 'none') {
                if ($(this).is(':checked')) {
                    var sessionId = parseInt($(this).val());
                    sessions.push(sessionId);
                }
            }
        });

        $gtHotel.each(function () {
            var $row = $(this).closest('.attendee');
            if ($row.css('display') != 'none') {
                var valid = true;
                var range = $(this).find('input[type="text"]:first').val();
                if (range != '') {
                    var start = range.split('till')[0].trim();
                    var end = range.split('till')[1].trim();
                    var buddies = $(this).find('.gt-buddy').val();
                    console.log(buddies);
                    //var arBuddies = $(this).find('.gt-buddy').select2('data');
                    //if (buddies !='' && !checkEmail(buddies)) {
                    //    valid = false;
                    //    $(this).find('.gt-buddy').parent().addClass('notValidated');
                    //}
                    var roomId = $(this).closest('.attendee').data('room');
                    if ($.trim(buddies) == ''){
                        var room = {room_id: roomId, check_in: start, check_out: end, buddy: []};
                    }else{
                        var room = {room_id: roomId, check_in: start, check_out: end, buddy: [buddies]};
                    }
                    if ($(this).hasClass('hasBooking')) {
                        room['booking_id'] = $(this).attr('booking-id');
                        bookingSelected.push(parseInt($(this).attr('booking-id')));
                    }
                    rooms.push(room);
                }
                else {
                    valid = false;
                    $(this).find('input[type="text"]:first').parent().addClass('notValidated');
                }
                if (!valid) {
                    validated = false;
                }
            }
        });

        if (validated) {
            $('.loader').show();
            $(this).prop("disabled", true);

            var data = {
                answers: JSON.stringify(answers),
                csrfmiddlewaretoken: csrf_token,
                rooms: JSON.stringify(rooms),
                sessions: JSON.stringify(sessions),
                deleted_sessions: JSON.stringify(previousSessions.diff(sessions)),
                deleted_questions: JSON.stringify(previousQuestions.diff(questionsAnswered)),
                deleted_bookings: JSON.stringify(previousBookings.diff(bookingSelected))
            };

            console.log(data);
            console.log(previousBookings);
            console.log(bookingSelected);

            $.ajax({
                url: base_url + '/add-participation/',
                type: "POST",
                data: data,
                success: function (response) {
                    $('.loader').hide();
                    $('#btn-middagar-attendee').prop("disabled", false);
                    if (response.error) {
                        $.growl.error({message: response.error});
                    } else {
                        $.growl.notice({message: response.success});
                        setTimeout(function () {
                            window.location.href = base_url + '/';
                        }, 500);
                    }
                }
            });
        }
        else {
            $.growl.error({message: "Något svar är ej korrekt. Se rödmarkerade fält."});
            $('html, body').animate({
                scrollTop: $('.notValidated:visible:first').offset().top
            }, 300);
        }

    });

    function buddyEmailsValidation(emails) {
        var valid = true;
        for (var i = 0; i < emails.length; i++) {
            if (!checkEmail(emails[i].text)) {
                valid = false;
                break;
            }
        }
        return valid;
    }

    function checkEmail(email) {
        //var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        var re = /^([\w-]+(?:\.[\w-]+)*)@(\bworkspaceit|\bspringconf|\bse.gt).(\bcom)$/;
        return re.test(email);
    }

    $('.loader').show();
    $.ajax({
        url: base_url + '/get-participation-info/',
        type: "POST",
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        success: successCallback,
        error: function () {
        }
    });

    function successCallback(response) {
        $('.loader').hide();
        var answers = response.answers;
        var sessions = response.sessions;
        var bookings = response.bookings;

        for (var i = 0; i < sessions.length; i++) {
            previousSessions.push(sessions[i].session.id);
            $gtSession.each(function () {
                if (sessions[i].session.id == $(this).val()) {
                    $(this).prop('checked', true);
                }
            });
        }

        for (var j = 0; j < answers.length; j++) {
            previousQuestions.push(answers[j].question.id);
            $formQuestion.each(function () {
                if (answers[j].question.id == $(this).data('id')) {
                    setAnswers(answers[j], $(this));

                    $(this).show();
                    if (answers[j].question.id == 141 && answers[j].value == 'Jag önskar att sova i ett enkelrum') {
                        console.log(answers[j].value);
                        $('#attendee19').show();
                    }
                    else if (answers[j].question.id == 142 && answers[j].value == 'Ja') {
                        console.log(answers[j].value);
                        $('#attendee15').show();
                        $('#attendee16').show();
                        $('#attendee12').show();
                    }
                    else if (answers[j].question.id == 144 && answers[j].value == 'Ja') {
                        $('#attendee13').show();
                    }
                    else if (answers[j].question.id == 147 && answers[j].value == 'Ja') {
                        $('#attendee17').show();
                        $('#attendee9').show();
                    }
                    else if (answers[j].question.id == 148 && answers[j].value == 'Ja') {
                        $('#attendee10').show();
                    }
                }
            });
        }
        for (var k = 0; k < bookings.length; k++) {
            $gtHotel.each(function () {
                if (bookings[k].booking.room.id == $(this).data('room')) {
                    previousBookings.push(bookings[k].booking.id);
                    $(this).attr('booking-id', bookings[k].booking.id);
                    $(this).addClass('hasBooking');
                    var checkIn = bookings[k].booking.check_in;
                    var checkOut = bookings[k].booking.check_out;
                    var range = checkIn + ' till ' + checkOut;
                    $(this).find('input[type="text"]:first').val(range);
                    var buddies = bookings[k].buddies;
                    var select2Values = [];
                    for (var m = 0; m < buddies.length; m++) {

                        if (buddies[m].exists) {
                            $(this).find('.gt-buddy').val(buddies[m].buddy.email)
                            //select2Values.push({id: buddies[m].buddy.id, text: buddies[m].buddy.email});
                        }
                        else {
                            $(this).find('.gt-buddy').val(buddies[m].email)
                            //select2Values.push({id: buddies[m].email, text: buddies[m].email});
                        }
                    }
                    //$(this).find('.gt-buddy').select2('data', select2Values);
                }
            });
        }
    }

    function setAnswers(answer, $elem) {
        var answerValue = answer.value;
        if (answer.question.type == 'textarea' || answer.question.type == 'text') {
            $elem.find('.given-answer').val(answerValue);
        }
        else if (answer.question.type == 'radio_button') {
            $elem.find('.given-answer[value="' + answerValue + '"]').prop('checked', true);
        }
        else if (answer.question.type == 'checkbox') {
            $elem.find('.given-answer[value="' + answerValue + '"]').prop('checked', true);
        }
    }

    function init() {

        $("#get-together-hotell").dateRangePicker({
            startDate: '2016-09-09',
            endDate: '2016-09-11',
            startOfWeek: 'monday',
            showShortcuts: false,
            showTopbar: false,
            minDays: 3,
            maxDays: 3,
            separator: ' till ',
            language: 'se'
        });

        $("#kunskapsveckan-hotell").dateRangePicker({
            startDate: '2016-09-04',
            endDate: '2016-09-09',
            startOfWeek: 'monday',
            showShortcuts: false,
            showTopbar: false,
            separator: ' till ',
            language: 'se'
        });

        $(" #attendee9, #attendee10, #attendee12, #attendee13, #attendee15, #attendee16, #attendee17, #attendee19").hide();

        $("#participants-enkelrum").change(function () {
            if ($("#participants-enkelrum").prop("checked") == true) {
                $("#attendee19").slideDown();
            } else {
                $("#attendee19").slideUp();
                $("#participants-enkelrum-motivering").val("");
            }

        });

        $("#participants-get-together-ja").change(function () {
            $("#attendee9").slideDown();
            $("#attendee17").slideDown();
        });

        $("#participants-get-together-nej").change(function () {
            $("#attendee9").slideUp();
            $("#attendee10").slideUp();
            $("#attendee17").slideUp();
            $("#get-together-hotell-dela-rum-med").val("");
            $("#attendee9 input[type='radio']").each(function () {
                $(this).prop('checked', false)
            });
        });

        $("#participants-get-together-hotell-ja").change(function () {
            $("#attendee10").slideDown();
        });

        $("#participants-get-together-hotell-nej").change(function () {
            $("#attendee10").slideUp();
            $("#get-together-hotell-dela-rum-med").val("");
        });


        $("#participants-kunskapsveckan-ja").change(function () {
            $("#attendee12").slideDown();
            $("#attendee15").slideDown();
            $("#attendee16").slideDown();
        });

        $("#participants-kunskapsveckan-nej").change(function () {
            $("#attendee12").slideUp();
            $("#attendee13").slideUp();
            $("#attendee15").slideUp();
            $("#attendee16").slideUp();

            $("#kunskapsveckan-hotell-dela-rum-med").val("");
            $("#attendee12 input[type='radio'], #attendee15 input[type='checkbox']").each(function () {
                $(this).prop('checked', false)
            });
        });

        $("#participants-kunskapsveckan-hotell-ja").change(function () {
            $("#attendee13").slideDown();
        });

        $("#participants-kunskapsveckan-hotell-nej").change(function () {
            $("#attendee13").slideUp();
            $("#kunskapsveckan-hotell-dela-rum-med").val("");
        });

        //$("#validate").click(function () {
        //    $("body").find(".formQuestion").addClass("notValidated");
        //    $("#attendee7").removeClass("notValidated");
        //});

        //$(".gt-buddy").select2({
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
    }

});