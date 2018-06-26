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

    $('body').on('click', '#btn-sen-register-attendee', function (e) {
        e.preventDefault();
        var validated = true;
        var answers = [];
        var firstName = '';
        var lastName = '';
        var email = '';
        var phone = '';
        var data = {};


        var sessions = [];
        var rooms = [];


        var questionsAnswered = [];
        var bookingSelected = [];

        $('.formQuestion').removeClass('notValidated');

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
                    else if (element.attr('id') == 'attendee-anstallningsnummer') {
                        if(!validateEmployeeNumber(answer)){
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
            $('#registration-loader').show();
            $('#btn-sen-register-attendee').prop("disabled", true);
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            firstName = $('#attendee-fornamn').val();
            lastName = $('#attendee-efternamn').val();
            email = $('#attendee-email').val();
            phone = $('#attendee-mobiltelefon').val();
            data = {
                answers: JSON.stringify(answers),
                csrfmiddlewaretoken: csrf_token,
                fname: firstName,
                lname: lastName,
                email: email,
                phone: phone,
                event_id: 10,
                rooms: JSON.stringify(rooms),
                sessions: JSON.stringify(sessions)
            };
            $.ajax({
                url: base_url + '/sen-anmalan/',
                type: "POST",
                data: data,
                success: function (result) {
                    $('#registration-loader').hide();
                    $('#btn-sen-register-attendee').prop('disabled', false);
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
            $.growl.error({message: "Något svar är ej korrekt. Se rödmarkerade fält."});
            $('html, body').animate({
                scrollTop: $('.notValidated:visible:first').offset().top
            }, 300);
        }


    });

    function phoneValidate(phone) {
        var re = /^[0-9+-\\(\\) ]*$/;
        return re.test(phone);
    }

    function validateEmployeeNumber(number) {
        var valid = true;
        if(number.length != 4){
            valid = false;
        }
        else if(isNaN(number)){
            valid = false;
        }
        return valid;
    }



    // min-medvarkan



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
            language: 'en',
            minDays: 2
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
    }

});
