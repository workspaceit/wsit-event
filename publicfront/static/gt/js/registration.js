jQuery(document).ready(function ($) {
    $('body').on('click', '#btn-register-attendee', function (e) {
        e.preventDefault();
        var validated = true;
        var answers = [];
        var firstName = '';
        var lastName = '';
        var email = '';
        var phone = '';
        var data = {};

        $('.formQuestion').removeClass('notValidated');

        $('.formQuestion').each(function () {
            var row = $(this);
            if (row.css('display') != 'none') {
                var answer = '';
                var valid = true;
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
                        answer = element.prop('checked');
                    }
                }
                if (!valid) {
                    validated = false;
                    row.addClass('notValidated');
                }
                else {
                    var id = row.data('id');
                    answers.push({
                        id: id,
                        answer: answer
                    });
                }
            }
        });
        if (validated) {
            $('#registration-loader').show();
            $(this).prop("disabled", true);
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
                event_id: 10
            };
            $.ajax({
                url: base_url + '/registration/',
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

});
