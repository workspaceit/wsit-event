var base_url = window.location.origin + '/gt';
$(function () {
    var login_user = $('#hidden_secret').val();
    if (login_user) {
        setTimeout(getNotification, 60000);
    }
    $('body').on('click', '.star', function (e) {
        var rate = $(this).data('rating');
        $(this).parent('ul').find('.star ').removeClass('selected');
        $(this).parent('ul').find('.star:lt("' + rate + '")').toggleClass('selected');
    });
    $('body').on('click', '.session-evaluate', function (e) {
        var sessions_rating = []
        $('.stars').each(function () {
            var rate = $(this).find('li.selected').length
            if (rate != 0) {
                var rating = {session_id: $(this).attr('data-id'), rating: rate}
                sessions_rating.push(rating);
            }
        });
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (sessions_rating.length != 0) {
            $.ajax({
                url: base_url + '/gt-set-ratings/',
                type: "POST",
                data: {
                    sessions_rating: JSON.stringify(sessions_rating),
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        for (var i = 0; i < sessions_rating.length; i++) {
                            $('#rated_session_' + sessions_rating[i].session_id).parent().remove();
                        }
                        if ($('.evaluate').children('li').length == 0) {
                            //$('.evaluate').parent().remove();
                            $('.evaluate').parent().css("display", "none");
                        }
                    }
                }
            });
        } else {
            $.growl.warning({message: "Du behöver utvärdera något"});
        }

    });
    $('body').on('click', '.delete_notification', function (e) {
        deleteNotification($(this));
    });

    $('body').on('click', '.click-notification', function (e) {
        var $this = $(this);
        var id = $(this).attr('data-id')
        var action_swe = $(this).html();
        if ($.trim(action_swe) == 'Ja') {
            var action = 'Yes';
        } else {
            var action = 'No';
        }
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        data = {
            id: id,
            action: action,
            csrfmiddlewaretoken: csrf_token
        }
        $.ajax({
            url: window.location.origin + '/kingfomarket/notification-session/',
            type: "POST",
            data: data,
            success: function (result) {
                $this.closest('li').remove();
                $.growl.notice({message: result.message});
            }
        });
    });

    $('body').find('.defaultCountdown').each(
        function () {

            var self = $(this);
            var date_string = self.attr('data-id');
            console.log(date_string);
            var timestamp = date_string.split("-");
            var year = timestamp[0];
            var month = timestamp[1];
            var day = timestamp[2];
            var hour = timestamp[3];
            var minute = timestamp[4];
            var second = timestamp[5];
            var austDay = new Date(year, month - 1, day, hour, minute, second);
            self.countdown({
                until: austDay,
                onExpiry: reload,
                layout: '{hn} {hl} ,{mn} {ml}'
            });
        }
    );
});

function getNotification() {
    var noty = $('#new_notification_count').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var sort_type = $('#notification_type :selected').val();
    var key = $('#searchKey').val();
    $.ajax(
        {
            type: "Post",
            url: base_url + '/gt-get-notifications/',
            data: {
                sort_type: sort_type,
                key: key,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                $('.defaultCountdown').each(
                    function () {
                        var self = $(this);
                        self.countdown('destroy');
                    }
                );
                if (response.success) {
                    if (response.notifications != "") {
                        $("#noti_hidden").css("display", "block");
                    } else {
                        $("#noti_hidden").css("display", "none");
                    }
                    if (response.evaluations != "") {
                        $(".elementEvaluate").css("display", "block");
                    } else {
                        $(".elementEvaluate").css("display", "none");
                    }
                    if (response.next_up != "") {
                        $(".elementNextUp").css("display", "block");
                    } else {
                        $(".elementNextUp").css("display", "none");
                    }

                    $('.notifications').html(response.notifications);
                    $('.evaluate').html(response.evaluations);
                    $('.nextUp').html(response.next_up);
                    var new_noty = response.new_noty;
                    //if ($('#new_next_up').val() == '' || $('#new_next_up').val() == undefined) {
                    //    var old_next_up = [];
                    //} else {
                    //    var old_next_up = JSON.parse($('#new_next_up').val());
                    //}
                    var new_next_up = response.new_sessions_next_up;
                    //var noty_next = 0;
                    //for (var i = 0; i < new_next_up.length; i++) {
                    //    if ($.inArray(new_next_up[i], old_next_up) == -1) {
                    //        noty_next = 1;
                    //        break
                    //    }
                    //}
                    //if ($('#new_evaluations').val() == '' || $('#new_evaluations').val() == undefined) {
                    //    var old_evaluations = [];
                    //} else {
                    //    var old_evaluations = JSON.parse($('#new_evaluations').val());
                    //}
                    var new_evaluations = response.new_sessions_finished;
                    //var noty_evaluate = 0;
                    //for (var j = 0; j < new_evaluations.length; j++) {
                    //    if ($.inArray(new_evaluations[j], old_evaluations) == -1) {
                    //        noty_evaluate = 1;
                    //        break
                    //    }
                    //}
                    if (new_noty > noty) {
                        $.growl.notify({
                            message: 'Du har ett nytt meddelande',
                            url: base_url + '/summering/',
                            duration: 10000
                        });
                    //} else if (noty_next == 1 && response.next_up_message != '') {
                    } else if (response.show_next_up && response.next_up_message != '') {
                        $.growl.notify({
                            message: response.next_up_message,
                            url: base_url + '/summering/',
                            duration: 10000
                        });
                    //} else if (noty_evaluate == 1 && response.show_evaluation_message == 1 && response.evaluation_message != '') {
                    } else if (response.show_evaluation && response.show_evaluation_message == 1 && response.evaluation_message != '') {
                        $.growl.notify({
                            message: response.evaluation_message,
                            url: base_url + '/summering/',
                            duration: 10000
                        });
                    }
                    $('.growl').css('cursor', 'pointer');
                    $('#new_notification_count').val(new_noty);
                    $('#new_next_up').val(JSON.stringify(new_next_up));
                    $('#new_evaluations').val(JSON.stringify(new_evaluations));
                    $('.defaultCountdown').each(
                        function () {

                            var self = $(this);
                            var date_string = self.attr('data-id');
                            var timestamp = date_string.split("-");
                            var year = timestamp[0];
                            var month = timestamp[1];
                            var day = timestamp[2];
                            var hour = timestamp[3];
                            var minute = timestamp[4];
                            var second = timestamp[5];
                            var austDay = new Date(year, month - 1, day, hour, minute, second);
                            self.countdown({
                                until: austDay,
                                onExpiry: reload,
                                layout: '{hn} {hl} ,{mn} {ml}'
                            });
                        }
                    );
                }
            }
        }
    );
    setTimeout(getNotification, 60000);
}

function deleteNotification(elm) {
    var id = $(elm).attr('data-id');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax(
        {
            type: "Post",
            url: base_url + '/gt-delete-notification/',
            data: {
                id: id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.status == "success") {
                    $.growl.notice({message: 'Meddelandet togs bort'});
                    console.log(elm.parent());
                    elm.parent().remove();
                    if ($('.notifications').children('li').length == 0) {
                        //$('.notifications').parent().remove();
                        $('.notifications').prev('#noti_hidden').css("display", "none");
                    }
                }
            }
        }
    );
}
function reload() {
    location.reload();
}