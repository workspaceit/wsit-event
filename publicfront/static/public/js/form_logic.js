// FORM LOGIC //
var base_url = window.location.origin + '/' + event_url;
$(function () {

    var FR = new FileReader();
    FR.onload = function (e) {
        $('#b64').val(e.target.result);
    };


    $('#inputImage').change(function () {
        FR.readAsDataURL($('#inputImage').get(0).files[0]);
        $('.img-con').hide();
        $('.img-preview').show();
    });

    $('body').on('click', '.update_bio', function (e) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var first_name = $('#bio_first_name').val();
        var last_name = $('#bio_last_name').val();
        var bio = $('#bio').val();
        var image_src = $('.cropped-attendee-image').attr('src');
        var image = '';
        if (image_src != undefined) {
            image = image_src.replace('data:image/png;base64,', '');
        }


        var data = {
            first_name: $.trim(first_name),
            csrfmiddlewaretoken: csrf_token,
            last_name: $.trim(last_name),
            bio: $.trim(bio)
        };

        var imageContainer = $('#inputImage');
        var base64Image = 'gfd';
        if (imageContainer.get(0).files.length != 0) {
            var rotation = -1 * $('#image').cropper('getData').rotate;
            var imageWithData = {
                image: $('#b64').val().split(',')[1],
                data: $('#image').cropper('getData'),
                rotation: rotation
            }
            data['image_data'] = JSON.stringify(imageWithData);
        }


        //if (bio.length > 2000) {
        //    $('#bio').css('border', '2px solid #EF4545');
        //    $.growl.error({message: "The Bio field cannot contain more than 2000 characters!"});
        //} else {
        $.ajax({
            url: base_url + '/attendee-profile/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    setTimeout(function () {
//                        window.location.href = base_url + '/profile/';
                    }, 500);
                }
            }
        });
        //}

    });


    $('body').on('click', '.my-session', function (e) {
        if ($('.my-session').hasClass('selected')) {

        }
        else {
            $('.all-session').removeClass('selected');
            $('.my-session').addClass('selected');
            get_allSession();
        }
//    $('.all-session').removeClass('selected');
//    $('.my-session').addClass('selected');
//    $.ajax({
//        url: base_url + '/my-sessions/',
//        type: "GET",
//        success: function (result) {
//            $('.session-show').html(result);
//        }
//    });
    });
    $('body').on('click', '.all-session', function (e) {
        if ($('.all-session').hasClass('selected')) {

        }
        else {
            $('.my-session').removeClass('selected');
            $('.all-session').addClass('selected');
            get_allSession();
        }
    });

    function get_allSession() {
        $('.search-session').val('');
        var sort = $('.sort-sessions').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var tab = "all-session";
        if ($('.my-session').hasClass('selected')) {
            tab = "my-session"
        }
        data = {
            sort: sort,
            csrfmiddlewaretoken: csrf_token,
            tab: tab
        }
        $('body #session-loader').show();
        $.ajax({
            url: base_url + '/sessions/',
            type: "POST",
            data: data,
            success: function (result) {
                $('body #session-loader').hide();
                $('.session-show').html(result);
            }
        });
    }

    $('body').on('change', '.sort-sessions', function (e) {
        get_allSession();
    });
    $('body').on('keyup', '.search-session', function (e) {
        $('body #session-loader').show();
        search_key = $(this).val();
        var sort = $('.sort-sessions').val();
        var tab = "all-session";
        if ($('.my-session').hasClass('selected')) {
            tab = "my-session"
        }
//    if ($.trim(search_key) != '') {
        data = {
            search_key: search_key,
            sort: sort,
            tab: tab
        }
        $.ajax({
            url: base_url + '/sessions-search/',
            type: "GET",
            data: data,
            success: function (result) {
                $('body #session-loader').hide();
                data = result;
                $('.session-show').html(result);
            }
        });
//    }
    })
    ;

    $('body').on('click', '.click-notification', function (e) {
        var $this = $(this);
        var id = $(this).attr('data-id')
        var action = $(this).html();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        data = {
            id: id,
            action: action,
            csrfmiddlewaretoken: csrf_token
        }
        $.ajax({
            url: base_url + '/notification-session/',
            type: "POST",
            data: data,
            success: function (result) {
                $this.closest('.event-plugin-item').remove();
                $.growl.notice({message: result.message});
            }
        });
    });

    $('body').on('click', '.sign-email-send', function (e) {
        console.log('ok');
        var email = $('#sign-in-email').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $this = $(this);
        if ($.trim(email) != '' && checkEmail(email)) {
            $this.closest('.formQuestion').removeClass("notValidated");
            data = {
                email: email,
                csrfmiddlewaretoken: csrf_token
            }
            $.ajax({
                url: base_url + '/sign-email-send/',
                type: "POST",
                data: data,
                success: function (result) {
                    if (result.error) {
                        $this.closest('.formQuestion').addClass("notValidated");
                    } else {
                        $.growl.notice({message: result.success});
                    }
                }
            });

        }
        else {
            $this.closest('.formQuestion').addClass("notValidated");
        }

    });

    $('body').on('click', '.sign-in-uid-send', function (e) {
        var secret_key = $('#sign-in-uid').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $this = $(this);
        if ($.trim(secret_key) != '') {
            $this.closest('.formQuestion').removeClass("notValidated");
            data = {
                secret_key: secret_key,
                csrfmiddlewaretoken: csrf_token
            }
            $.ajax({
                url: base_url + '/sign-in-uid-send/',
                type: "POST",
                data: data,
                success: function (result) {
                    if (result.error) {
                        $this.closest('.formQuestion').addClass("notValidated");
                    } else {
                        $.growl.notice({message: result.success});
                        setTimeout(function () {
                            window.location.href = base_url + '/';
                        }, 300);
                    }
                }
            });

        }
        else {
            $this.closest('.formQuestion').addClass("notValidated");
        }

    });

    function checkEmail(email) {
        var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        return re.test(email);
    }


    $('body').on('click', '.session-view', function (e) {
        if (!$(e.target).is('a')) {
            var session_id = $(this).attr('data-id');
            console.log(session_id);
            $('body #session-loader').show();
            $.ajax({
                url: base_url + '/sessions/' + session_id + '/',
                type: "GET",
                success: function (result) {
                    if (result.error) {
                    } else {
                        $.fancybox(result, {
                            maxWidth: 1000,
                            maxHeight: 800,
                            fitToView: false,
                            width: '100%',
                            height: '100%',
                            autoSize: false,
                            closeClick: false,
                            openEffect: 'fade',
                            closeEffect: 'fade',
                            openSpeed: 'slow',
                            autoHeight: true
                        });

                    }
                    $('body #session-loader').hide();

                }
            });
        }


    });

    $('body').on('change', '#btn-attend-session', function (e) {
        e.preventDefault();
        $('#loader').show();
        //$(this).prop("disabled", true);
        var sessionId = $(this).data('session');
        var currentStatus = $(this).attr('data-status').trim();
        console.log(currentStatus);
        var type = 'cancel';
        if (currentStatus == 'Not Attending' || currentStatus == 'Not Answered') {
            type = 'attend';
            //$('#btn-attend-session').attr("class", "button rounded color3");
            // .attr( "class", "newClass" )
        } else if (currentStatus == 'In Queue') {
            type = 'not-attending-queue'
        }
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            session_id: sessionId,
            type: type,
            csrfmiddlewaretoken: csrfToken
        };

        $.ajax({
            url: base_url + '/attend-or-cancel-session/',
            type: "POST",
            data: data,
            success: function (response) {
                $('#btn-attend-session').removeClass('queue');
                $('#btn-attend-session').prop('checked', false);
                $('#loader').hide();
                //$('#btn-attend-session').prop('disabled', false);


                var scheduler = $("#scheduler").data("kendoScheduler");
                scheduler.dataSource.read();
                scheduler.view(scheduler.view().name);

                console.log(response);
                if (response.status == 'Clash') {
                    // $.growl.warning({message: 'You have a clash with previously selected session'});
                    $.growl.warning({message: response.msg});
                }
                else {
                    var st = response.status;
                    if (response.status == 'Capacity Full') {
                        st = 'Not Attending';
                    }
                    //$('#btn-attend-session').html(st);
                    $('#btn-attend-session').attr('data-status', st)

                }
                if (response.status == 'Attending') {
                    $('.click-to-attend').find('em').html('Click to cancel attendance');
                    //$('#btn-attend-session').attr("class", "button rounded color2");
                    $('#btn-attend-session').prop('checked', true);
                    // $.growl.notice({message: 'You are registered for this session'});
                    $.growl.notice({message: response.msg});
                }
                else if (response.status == 'In Queue') {
                    $('.click-to-attend').find('em').html('Click to cancel Queue');
                    // $.growl.notice({message: 'You are in Queue for this session'});
                    $.growl.notice({message: response.msg});
                    //$('#btn-attend-session').attr("class", "button rounded color4");
                    $('#btn-attend-session').addClass("queue");
                    $('#btn-attend-session').prop('checked', true);
                }
                else if (response.status == 'Not Attending') {
                    if (response.session_full) {
                        $('.click-to-attend').find('em').html('Click to enter queue');
                    } else {
                        $('.click-to-attend').find('em').html('Click to attend');
                    }
                    //$('#btn-attend-session').attr("class", "button rounded color3");
                    $('#btn-attend-session').prop('checked', false);
                    // $.growl.notice({message: 'You have unregistered for this session'});
                    $.growl.notice({message: response.msg});
                }
                else if (response.status == 'Capacity Full') {
                    if (response.session_full) {
                        $('.click-to-attend').find('em').html('Click to enter queue');
                    } else {
                        $('.click-to-attend').find('em').html('Click to attend');
                    }
                    //$('#btn-attend-session').attr("class", "button rounded color3");
                    $('#btn-attend-session').prop('checked', false);
                    // $.growl.warning({message: 'This sessions Capacity Full'});
                    $.growl.warning({message: response.msg});
                }
            }
        });
    });

    $('body').on('click', 'input:radio[name=attend]', function () {

        var value = $(this).val()

        var sessionId = $(this).data('session');
        var type = "cancel";
        if (value == "yes") {
            type = "attend";
        } else {
            type = "cancel";
        }
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            session_id: sessionId,
            type: type,
            csrfmiddlewaretoken: csrfToken
        };
        $.ajax({
            url: base_url + '/attend-or-cancel-session/',
            type: "POST",
            data: data,
            success: function (response) {
                console.log(response);
                if (response.status == 'Clash') {
                    // $.growl.warning({message: 'You have a clash with previously selected session'});
                    $.growl.warning({message: response.msg});
                    $('#no').prop('checked', true);
                }
                else if (response.status == 'Capacity Full') {
                    // $.growl.warning({message: 'Session Capacity Full'});
                    $.growl.warning({message: response.msg});
                    $('#no').prop('checked', true);
                }
                else if (response.status == 'Attending') {
                    // $.growl.notice({message: 'You are registered for this session'});
                    $.growl.notice({message: response.msg});
                    $('#yes').prop('checked', true);
                }
                else if (response.status == 'Not Attending') {
                    // $.growl.notice({message: 'You have unregistered for this session'});
                    $.growl.notice({message: response.msg});
                    $('#no').prop('checked', true);
                }
            }
        });
    });
});
