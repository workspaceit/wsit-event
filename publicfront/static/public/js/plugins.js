$(function () {

    // Evaluation Start
    $body.on('click', '.evaluation-send-button', function (e) {
        var sessions_rating = [];
        var $this = $(this);
        $this.closest('.event-plugin-evaluations').find('.star-evaluation-group').each(function () {
            var rate = $(this).find('input:checked').val();
            if (rate != '0' && rate != 0 && rate != NaN && rate != undefined) {
                var rating = {session_id: $(this).attr('data-id'), rating: parseInt(rate)}
                sessions_rating.push(rating);
            }
        });
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $this.closest('.event-plugin-evaluations').removeClass('not-validated');
        if (sessions_rating.length != 0) {
            $.ajax({
                url: base_url + '/set-ratings/',
                type: "POST",
                data: {
                    sessions_rating: JSON.stringify(sessions_rating),
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $this.closest('.event-plugin-evaluations').find('.error-validating').html(result.error);
                    } else {
                        var parentElem = $this.closest('.event-plugin-evaluations');
                        $.growl.notice({message: result.message});
                        for (var i = 0; i < sessions_rating.length; i++) {
                            $this.parent().find('#rated_session_' + sessions_rating[i].session_id).closest('.event-plugin-item').remove();
                        }
                        if (parentElem.children('.event-plugin-list').children('.event-plugin-item').length == 0) {
                            //$this.closest('.event-plugin-evaluations').parent().remove();
                            parentElem.find('.evaluation-send-button').remove();
                            addEmptyDiv(parentElem, result.empty_txt_language);
                        }
                    }
                }
            });
        } else {
            $this.closest('.event-plugin-evaluations').addClass('not-validated');
        }
    });
    // Evaluation End

    // Message Start

    $body.on('click', '.messages-hide', function (e) {
        archivedNotification($(this));
    });

    $body.on('click', '.messages-mark-all-button', function (e) {
        var $this = $(this);
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $this.closest('.event-plugin-messages').removeClass('not-validated');
        $.ajax(
            {
                type: "Post",
                url: base_url + '/archive-all-messages/',
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (response) {
                    if (response.error) {
                        $this.closest('.event-plugin-messages').addClass('not-validated');
                        $this.closest('.event-plugin-messages').find('.error-validating').html(response.message);
                    } else {
                        $.growl.notice({message: response.message});
                        var parentElem = $this.closest('.event-plugin-messages');
                        $this.closest('.event-plugin-messages').find('.event-plugin-item').remove();
                        //parentElem.find('.messages-read-archived-messages').remove();
                        parentElem.find('.messages-mark-all-button').remove();
                        if (!parentElem.find('.messages-read-archived-messages').is(":visible")) {
                            parentElem.find('.messages-read-archived-messages').css('display', 'block');
                        }
                        addEmptyDiv(parentElem, response.empty_txt_language);
                    }
                }
            }
        );
    });

    // Message End

    // Location Start

    // Location End

    $body.on('keyup', '.page-search-location', function (e) {
        var $this = $(this);
        var page = window.location.pathname.split('/')[2];
        var element_id = $this.closest('.box').attr('data-id');
        var box_id = $this.closest('.box').attr('id').split('-')[3];
        if (page != undefined && box_id != undefined && page != '' && box_id != '') {
            $this.closest('.event-plugin-location-list').find('.event-plugin-item').hide();
            var search_key = $.trim($(this).val());
            $('.event-plugin-item').each(function () {
                if ($(this).find('.event-plugin-title').text().toUpperCase().indexOf(search_key.toUpperCase()) != -1) {
                    $(this).show();
                }
            });
        }

    });

    $body.on('click', '.verification-login-send-button', function (e) {
        var $form = $(this).closest('.event-plugin-login-form');
        var email = $.trim($form.find('.email-password-verification-email').val());
        var password = $.trim($form.find('.email-password-verification-password').val());
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (email == '' || !checkEmail(email) || password == '') {
            $form.addClass('not-validated');
        }
        else {
            $.ajax({
                url: base_url + '/login/',
                type: "POST",
                data: {
                    user_email: email,
                    user_password: password,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        redirectToPage(result.redirect_url);
                    } else {
                        $form.addClass('not-validated');
                    }
                }
            });
        }

    });

    $body.on('click', '.request-login-send-button', function (e) {
        var $form = $(this).closest('.event-plugin-request-login');
        var email = $form.find('.request-login-email').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var send_email_id = $(this).attr("data-email-id");
        if (email == '' || !checkEmail(email)) {
            $form.addClass('not-validated');
        } else {
            $form.removeClass('not-validated');
            var data = {
                user_email: email,
                csrfmiddlewaretoken: csrf_token
            };
            if (send_email_id != '' && send_email_id != 'null' && send_email_id != undefined) {
                data['send_email_id'] = send_email_id;
            }
            $.ajax({
                url: base_url + '/retrieve-uid/',
                type: "POST",
                data: data,
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                    } else {
                        $.growl.error({message: result.message});
                        $form.addClass('not-validated');
                    }
                }
            });
        }
    });

    $body.on('click', '.reset-password-button', function (e) {
        var $form = $(this).closest('.event-plugin-reset-password');
        var email = $form.find('.event-plugin-reset-password-email').val();
        var email_id = $(this).attr('data-email-id');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (email == '' || !checkEmail(email)) {
            $form.addClass('not-validated');
        } else {
            $form.removeClass('not-validated');
            var data = {
                user_email: email,
                csrfmiddlewaretoken: csrf_token
            };
            if (email_id != "" && email_id != undefined && email_id != null) {
                data['email_id'] = email_id;
            }

            locaion_href = window.location.href

            if (locaion_href.indexOf("retrieve-password") > 0) {
                $.ajax({
                    url: site_url + '/retrieve-password/',
                    type: "POST",
                    data: data,
                    success: function (result) {
                        if (result.success) {
                            $.growl.notice({message: result.message});
                        } else {
                            $form.addClass('not-validated');
                        }
                    }
                });
            } else {
                $.ajax({
                    url: base_url + '/resetpass/',
                    type: "POST",
                    data: data,
                    success: function (result) {
                        if (result.success) {
                            $.growl.notice({message: result.message});
                        } else {
                            $form.addClass('not-validated');
                        }
                    }
                });
            }
        }
    });

    $body.on('click', '.new-password-button', function (e) {
        var $form = $(this).closest('.event-plugin-new-password');
        var password = $form.find('.event-plugin-new-password-email').val();
        var repeat_password = $form.find('.event-plugin-repeat-new-password-email').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (password == '' || repeat_password == '' || password != repeat_password || password.length < 6) {
            $form.addClass('not-validated');
        } else {
            $form.removeClass('not-validated');
            var data = {
                new_password: password,
                csrfmiddlewaretoken: csrf_token
            };

            $.ajax({
                url: base_url + '/savepass/',
                type: "POST",
                data: data,
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        window.location.replace(result.location);
                    } else {
                        $form.addClass('not-validated');
                    }
                }
            });
        }
    });

    $body.on('click', '.upload-image', function (e) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var $button = $(this);
        try {
            $button.closest(".event-plugin-photo-upload").removeClass('not-validated');
            var image = $('input[name=pic]')[0].files[0];
            if (image != undefined) {
                var formdata = new FormData();
                var comment = $button.closest('.event-plugin-photo-upload').find('textarea[name=comment]').val();
                $('.submit-loader').show();
                $button.prop("disabled", true);
                formdata.append('pic', image);
                if(comment != undefined){
                    formdata.append('comment', comment);
                }
                var page_id = $button.closest('.event-plugin-photo-upload').attr('id').split('-')[1];
                var box_id = $button.closest('.event-plugin-photo-upload').attr('id').split('-')[3];
                var photo_group_id = $button.closest('.event-plugin-photo-upload').attr('data-photo-group-id');
                formdata.append('page_id', page_id);
                formdata.append('box_id', box_id);
                formdata.append('photo_group_id', photo_group_id);
                formdata.append('csrfmiddlewaretoken', csrf_token);

                $.ajax({
                    url: base_url + '/upload-files/',
                    type: 'POST',
                    data: formdata,
                    //async: false,
                    //cache: false,
                    contentType: false,
                    processData: false,
                    success: function (result) {
                        $('.submit-loader').hide();
                        $button.prop("disabled", false);
                        if (result.success) {
                            $.growl.notice({message: result.message});
                            $button.closest(".event-plugin-photo-upload").find('input[name=pic]').val("");
                            $button.closest(".event-plugin-photo-upload").find('.selected-file').css("display", "none");
                            $button.closest(".event-plugin-photo-upload").find('textarea[name=comment]').val("");
                        } else {
                            $button.closest(".event-plugin-photo-upload").find('.error-validating').html(result.message);
                            $button.closest(".event-plugin-photo-upload").addClass('not-validated');
                        }
                    }
                });
            } else {
                $button.closest(".event-plugin-photo-upload").addClass('not-validated');
            }
        }
        catch (err) {
            $('.submit-loader').hide();
            $button.prop("disabled", false);
            $button.closest(".event-plugin-photo-upload").addClass('not-validated');
        }
    });

    // session Attend or Cancel from message

    $('body').on('click', '.click-notification', function (e) {
        var $this = $(this);
        var id = $(this).attr('data-id');
        var action = $(this).attr('data-value');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            id: id,
            action: action,
            csrfmiddlewaretoken: csrf_token
        };
        $.ajax({
            url: base_url + '/notification-session/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.success) {
                    $this.closest('li').remove();
                }
                if (result.download_flag) {
                    window.location = base_url + "/economy-pdf-request?data=credit-invoice&order_number=" + result.order_number;
                }
                $.growl.notice({message: result.message});
            }
        });
    });

    $body.on('change', 'input[name="pic"]', function () {
        var filepath = $(this).val();
        var filename = filepath.split('\\').pop();
        $(this).closest('.event-plugin-photo-upload').find('.file-fake-path').html(filename);
        $(this).closest('.event-plugin-photo-upload').find('.selected-file').css('display', 'block');
    });

    $('body').on('click', '.form-pdf-button', function (event) {
        var page_id = $(this).closest('.event-plugin-pdf-button').attr('id').split('-')[1];
        var box_id = $(this).closest('.event-plugin-pdf-button').attr('id').split('-')[3];
        window.location = base_url + "/convert-html-to-pdf/?page_id=" + page_id+"&box_id="+box_id;
    });
});