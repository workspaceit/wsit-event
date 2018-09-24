$(function () {
    var $body = $('body');
    $body.find('div[inline-data-owner-idz4Vv3ZLs3R]:visible').each(function () {
        multiple_attendee_id_array.push($(this).attr("inline-data-owner-idz4Vv3ZLs3R"));
    });
    $body.find('div[inline-data-attendee-idz4Vv3ZLs3R]:visible').each(function () {
        multiple_attendee_id_array.push($(this).attr("inline-data-attendee-idz4Vv3ZLs3R"));
    });
    $body.on('click', '.event-plugin-multiple-registration-add-attendee-button-inline', function () {
        var $this = $(this);
        // var current_attendee_sum = multiple_attendee_id_array.length + 1;
        var current_attendee_sum = multiple_attendee_id_array.length;
        checkMaxMinAttendeeInline($this, current_attendee_sum, 'append', NaN);
    });
    $body.on('click', '.event-plugin-multiple-registration-delete-attendee-button-from-inline', function () {
        var $this = $(this);
        var current_attendee_sum = multiple_attendee_id_array.length - 2;
        checkMaxMinAttendeeInline($this, current_attendee_sum, 'delete', $this.attr("inline-data-attendee-del-idz4Vv3ZLs3R"));
    });
});

function checkMaxMinAttendeeInline(elem, current_attendee_sum, click_event, attendee_id) {
    var page_id = elem.closest('.box').attr('id').split('-')[1];
    var box_id = elem.closest('.box').attr('id').split('-')[3];
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var include_owner = $("[inline-data-owner-idz4Vv3ZLs3R]").attr('data-include-ownerz4Vv3ZLs3R');
    $.ajax({
        url: base_url + '/check-min-max-registration-attendee/',
        type: "POST",
        data: {
            page_id: page_id,
            box_id: box_id,
            click_event: click_event,
            current_attendee: current_attendee_sum,
            attendee_id: attendee_id,
            include_owner: include_owner,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.success) {
                console.log();
                var current_attendee_sum_show = parseInt(elem.closest('.box').find('.event-plugin-multiple-registration-current-count-number-inline').html());
                console.log(current_attendee_sum);
                if (click_event == 'append') {
                    appendAttendeeInline(elem, result.html, result.js, result.attendee_id);
                    elem.closest('.box').find('.event-plugin-multiple-registration-current-count-number-inline').html(current_attendee_sum_show + 1);
                    if(current_attendee_sum + 1 > result.max_attendees){
                        elem.hide();
                    }
                } else {
                    elem.closest('.box').find('.event-plugin-multiple-registration-current-count-number-inline').html(current_attendee_sum_show - 1);
                    deleteAttendeeInline(elem, result.attendee_id);
                    $('.event-plugin-multiple-registration-add-attendee-button-inline').show();
                }

            }
        }
    });
}

function appendAttendeeInline(elem, html, js, attendee_id) {
    pageDisable96();
    $(".event-plugin-multiple-registration-form-information-number").each(function () {
        var other_serial_number = $(this).html();
        if (other_serial_number != "") {
            var other_count_number = parseInt(other_serial_number.split('/')[0]);
            var other_total_number = parseInt(other_serial_number.split('/')[1]) + 1;
            $(this).html(other_count_number + " / " + other_total_number);
        }
    });
    $(".event-plugin-multiple-registration-attendee-forms-inline").append(html);
    eval(js);
    multiple_attendee_id_array.push(attendee_id.toString());
    pageEnable69();
    setOrUnsetSession();
}

function deleteAttendeeInline(elem, attendee_id) {
    var deleteAttendeeInline = $("[inline-data-attendee-idz4vv3zls3r='" + attendee_id + "']");
    var serial_number = deleteAttendeeInline.find(".event-plugin-multiple-registration-form-information-number").html();
    var count_number = parseInt(serial_number.split('/')[0]);
    var total_number = parseInt(serial_number.split('/')[1]) - 1;
    $(".event-plugin-multiple-registration-form-information-number").each(function () {
        var other_serial_number = $(this).html();
        if (other_serial_number != "") {
            var other_count_number = parseInt(other_serial_number.split('/')[0]);
            if (other_count_number > count_number) {
                other_count_number -= 1;
            }
            var other_total_number = parseInt(other_serial_number.split('/')[1]) - 1;
            $(this).html(other_count_number + " / " + other_total_number);
        }
    });
    deleteAttendeeInline.remove();
    multiple_attendee_id_array.pop(attendee_id.toString())
}

function saveOrUpdateMultipleAttendeeInline(button, main_submit_btn_id, main_submit_btn_box_id, main_page_id, form_box_id, answers, language_id) {
    var answer_data_by_id = {};
    var mult_reg_attendee_inline = {};
    $.each(answers, function (index, value) {
        console.log(value.id);
        console.log(value.answer);
        if (mult_reg_attendee_inline[value.duid] != undefined) {
            mult_reg_attendee_inline[value.duid]['attendee_id'] = value.duid;
            if (value.actual_defination != undefined) {
                mult_reg_attendee_inline[value.duid][value.actual_defination] = value.answer
            }
            if (mult_reg_attendee_inline[value.duid]['answers'] != undefined) {
                mult_reg_attendee_inline[value.duid]['answers'].push(value)
            } else {
                mult_reg_attendee_inline[value.duid]['answers'] = [];
                mult_reg_attendee_inline[value.duid]['answers'].push(value)
            }
        } else {
            mult_reg_attendee_inline[value.duid] = {}
            mult_reg_attendee_inline[value.duid]['attendee_id'] = value.duid;
            if (value.actual_defination != undefined) {
                mult_reg_attendee_inline[value.duid][value.actual_defination] = value.answer
            }
            if (mult_reg_attendee_inline[value.duid]['answers'] != undefined) {
                mult_reg_attendee_inline[value.duid]['answers'].push(value)
            } else {
                mult_reg_attendee_inline[value.duid]['answers'] = [];
                mult_reg_attendee_inline[value.duid]['answers'].push(value)
            }
        }

    });

    $.each(reservation_Data, function (index, value) {
        if (mult_reg_attendee_inline[value.user_id] != undefined) {
            if (mult_reg_attendee_inline[value.user_id]["hotel_reservation"] != undefined) {
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.parse(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"].push(value);
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.stringify(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
            } else {
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = [];
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"].push(value);
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.stringify(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
            }
        } else {
            mult_reg_attendee_inline[value.user_id] = {}
            if (mult_reg_attendee_inline[value.user_id]["hotel_reservation"] != undefined) {
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.parse(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"].push(value);
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.stringify(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
            } else {
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = [];
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"].push(value);
                mult_reg_attendee_inline[value.user_id]["hotel_reservation"] = JSON.stringify(mult_reg_attendee_inline[value.user_id]["hotel_reservation"])
            }
        }
    })

    console.log(mult_reg_attendee_inline);
    $('[inline-data-owner-idz4Vv3ZLs3R]').each(function () {
        console.log($(this).attr('inline-data-owner-idz4Vv3ZLs3R'));
    })
    $('[inline-data-attendee-idz4Vv3ZLs3R]').each(function () {
        console.log($(this).attr('inline-data-attendee-idz4Vv3ZLs3R'));
    });

    var attendees_data = [];
    $("[inline-data-attendee-idz4Vv3ZLs3R]").each(function () {
        attendees_data.push($(this).attr("inline-data-attendee-idz4Vv3ZLs3R"));
    })
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    add_ineffective_rebates();
    var data = {
        attendee_owner_id: $("[inline-data-owner-idz4Vv3ZLs3R]").attr("inline-data-owner-idz4Vv3ZLs3R"),
        attendee_ids: JSON.stringify(attendees_data),
        button_id: main_submit_btn_id,
        page_id: main_page_id,
        box_id: main_submit_btn_box_id,
        form_box_id: form_box_id,
        attendee_datas: JSON.stringify(mult_reg_attendee_inline),
        economy_data: JSON.stringify(economy_data),
        language_id: language_id,
        csrfmiddlewaretoken: csrf_token
    };
    console.log(data);
    $.ajax({
        url: base_url + '/multiple-attendee-save-inline/',
        type: "POST",
        data: data,
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.message});
                setEmptyValueToQuestions($body);
                console.log(result);
                if (result.download_flag) {
                    window.location = base_url + "/economy-pdf-request?data=order-invoice&order_number=" + result.order_number;
                    $('.submit-loader').show();
                    setTimeout(function () {
                        $('.submit-loader').hide();
                        redirectToPage(result.redirect_url);
                    }, 3000);
                } else {
                    redirectToPage(result.redirect_url);
                }
            } else {
                button.closest('.event-plugin-submit-button').addClass('not-validated');
                button.closest('.event-plugin-submit-button').find('.error-validating').text(result.message);
            }
        }
    });
}