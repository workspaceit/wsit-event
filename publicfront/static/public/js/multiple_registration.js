$(function () {
    var $body = $('body');
    $body.find('button[data-owner-idz4Vv3ZLs3R]:visible').each(function () {
        multiple_attendee_id_array.push($(this).attr("data-owner-idz4Vv3ZLs3R"))
        multiple_attendee_id = $(this).attr("data-owner-idz4Vv3ZLs3R");
    });
    $body.find('button[data-attendee-idz4Vv3ZLs3R]:visible').each(function () {
        multiple_attendee_id_array.push($(this).attr("data-attendee-idz4Vv3ZLs3R"))
    });
    // Multiple Resistration Loop Add Atendee
    $body.on('click', '.form-plugin-multiple-registration-add-attendee-button', function () {
        var $this = $(this);
        var current_attendee_sum = $this.closest('.box').find('.form-plugin-multiple-registration-attendee-table tbody tr:not(.default-empty-attendee)').length;

        checkMaxMinAttendee($this, current_attendee_sum, 'append', NaN);
    });
    // Multiple Resistration Loop Delete Atendee
    $body.on('click', '.form-plugin-multiple-registration-delete-attendee-button', function () {
        var $this = $(this);
        var current_attendee_sum = $this.closest('.box').find('.form-plugin-multiple-registration-attendee-table tbody tr:not(.default-empty-attendee)').length - 2;
        checkMaxMinAttendee($this, current_attendee_sum, 'delete', $this.attr("data-attendee-del-idz4Vv3ZLs3R"));
    });
    // Multiple Resistration Loop Edit Atendee
    $body.on('click', '.form-plugin-multiple-registration-edit-attendee-button', function (e) {
        var is_order_owner = false;
        if ($(this).attr("data-attendee-idz4Vv3ZLs3R") != undefined) {
            multiple_attendee_id = $(this).attr("data-attendee-idz4Vv3ZLs3R");
        } else if ($(this).attr("data-owner-idz4Vv3ZLs3R") != undefined) {
            multiple_attendee_id = $(this).attr("data-owner-idz4Vv3ZLs3R");
            is_order_owner = true;
        }


        var multiple_form = $(this).closest('.form-plugin-multiple-registration');
        getMultipleAttendeeForm(multiple_form, multiple_attendee_id);

        var attendee_serial = $(this).closest('tr').find('td:first').html();
        if(is_order_owner) {
            var order_owner_text = $('#order_owner_text').val();
            multiple_form.find('.form-plugin-multiple-registration-form-header').html(order_owner_text);
        }
        else {
            var attendee_text = $('#attendee_text').val();
            multiple_form.find('.form-plugin-multiple-registration-form-header').html(attendee_text + ' ' + attendee_serial);
        }
    });
});

function checkMaxMinAttendee(elem, current_attendee_sum, click_event, attendee_id) {
    var page_id = elem.closest('.box').attr('id').split('-')[1];
    var box_id = elem.closest('.box').attr('id').split('-')[3];
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: base_url + '/check-min-max-registration-attendee/',
        type: "POST",
        data: {
            page_id: page_id,
            box_id: box_id,
            click_event: click_event,
            current_attendee: current_attendee_sum,
            attendee_id: attendee_id,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.success) {
                var current_attendee_sum_show = parseInt(elem.closest('.box').find('.form-plugin-multiple-registration-current-count-number').html());
                // console.log('current_attendee_sum after:');
                // console.log(current_attendee_sum);
                if (click_event == 'append') {
                    appendAttendee(elem, result.attendee_id);
                    elem.closest('.box').find('.form-plugin-multiple-registration-current-count-number').html(current_attendee_sum_show + 1);
                    if(current_attendee_sum + 1 > result.max_attendees){
                        elem.hide();
                    }
                } else {
                    elem.closest('.box').find('.form-plugin-multiple-registration-current-count-number').html(current_attendee_sum_show - 1);
                    deleteAttendee(elem, result.attendee_id);
                    $('.form-plugin-multiple-registration-add-attendee-button').show();
                }
            }
        }
    });
}

function appendAttendee(elem, attendee_id) {
    var tbody = elem.closest('.box').find('.form-plugin-multiple-registration-attendee-table tbody');
    var empty_tr = tbody.find('tr.default-empty-attendee').clone();
    var new_id = tbody.find('tr:last td:first').html();
    empty_tr.find('td:first').html(parseInt(new_id) + 1);
    empty_tr.find('td:last').find(".form-plugin-multiple-registration-edit-attendee-button").attr('data-attendee-idz4Vv3ZLs3R', attendee_id).attr('data-id', attendee_id);
    empty_tr.find('td:last').find(".form-plugin-multiple-registration-delete-attendee-button").attr('data-attendee-del-idz4Vv3ZLs3R', attendee_id);
    empty_tr.attr('data-multiple-attendee-id', attendee_id);
    empty_tr.removeClass('default-empty-attendee');
    empty_tr.show();
    tbody.append(empty_tr);
    multiple_attendee_id_array.push(attendee_id.toString());
    setOrUnsetSession();
}

function deleteAttendee(elem, attendee_id) {
    var selected_tr_no = parseInt(elem.closest('tr').find('td:first').html());
    elem.closest('tr').nextAll().each(function () {
        $(this).find('td:first').html(selected_tr_no++);
    });
    elem.closest('tr').remove();
    multiple_attendee_id_array.pop(attendee_id.toString())
}