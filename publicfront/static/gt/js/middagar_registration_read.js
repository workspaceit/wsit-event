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
                        }
                        else {
                            $(this).find('.gt-buddy').val(buddies[m].email)
                        }
                    }
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

    }

});