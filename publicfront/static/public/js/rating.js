var base_url = window.location.origin + '/' + event_url;
$(function () {
    var login_user = $('#hidden_secret').val();
    console.log(login_user)
    //if(login_user){
        //setTimeout(getNotification, 20000);
    //}
    $.stayInWebApp();
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
        console.log(sessions_rating.length);
        console.log(sessions_rating);
        //var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        //if (sessions_rating.length != 0) {
        //    $.ajax({
        //        url: base_url + '/set-ratings/',
        //        type: "POST",
        //        data: {
        //            sessions_rating: JSON.stringify(sessions_rating),
        //            csrfmiddlewaretoken: csrf_token
        //        },
        //        success: function (result) {
        //            if (result.error) {
        //                $.growl.error({ message: result.error });
        //            } else {
        //                $.growl.notice({ message: result.success });
        //                for (var i = 0; i < sessions_rating.length; i++) {
        //                    $('#rated_session_' + sessions_rating[i].session_id).parent().remove();
        //                }
        //                if ($('.evaluate').children('li').length == 0) {
        //                    $('.evaluate').parent().remove();
        //                }
        //            }
        //        }
        //    });
        //} else {
        //    $.growl.warning({ message: "You Need to rate your sessions" });
        //}

    });


    $('body').on('keyup', '.search-location', function (e) {
        search_key = $(this).val();
        var sort = $('.sort-locations').val();
//        var tab = "all-session";
//        if ($('.my-session').hasClass('selected')) {
//            tab = "my-session"
//        }
        if ($.trim(search_key) != '') {
            data = {
                search_key: search_key,
                sort: sort
            }
            $.ajax({
                url: base_url + '/locations-search/',
                type: "GET",
                data: data,
                success: function (result) {
                    $('.location-show').html(result);
                }
            });
        }
    });
    $('body').on('click', '.delete_notification', function (e) {
        deleteNotification($(this));
    });
});

function getNotification() {
    var noty = $('#new_notification_count').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var sort_type = $('#notification_type :selected').val();
    var key = $('#searchKey').val();
    $.ajax(
        {
            type: "Post",
            url: base_url + '/get-notifications/',
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
                if(response.notifications != ""){
                    $("#noti_hidden").css("display","block");
                }

                $('.notifications').html(response.notifications);
                var new_noty = response.new_noty;
                if(new_noty > noty){
                    $.growl.notify({ message: 'You have a new Notification', url: base_url+'/notifications/', duration: 10000 });
                }
                $('#new_notification_count').val(new_noty);
                $('.defaultCountdown').each(
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
            }
        }
    );
    //setTimeout(getNotification, 20000);
}

function deleteNotification(elm) {
    var id = $(elm).attr('data-id');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax(
        {
            type: "Post",
            url: base_url + '/delete-notification/',
            data: {
                id: id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.status == "success") {
                    $.growl.notice({ message: 'Notification Successfully deleted' });
                    console.log(elm.parent());
                    elm.parent().remove();
                }
            }
        }
    );
}
function reload() {
    location.reload();
}