/**
 * Created by mahedi on 7/23/15.
 */
var base_url = window.location.origin;
var headerlist = [];
var timeZone;
var attendee_group = [];
var questionType;
var sessionTabActivate = true;
var travelTabActivate = true;
var hotelTabActivate = true;
var historyTabActivate = true;
var groupRegistrationTabActivate = true;
var datepicker_date_format;
var moment_date_format;

var cookie_expire = $('#cookie_expire').val();
var cookie_counter = cookie_expire;
$(document).ajaxSuccess(function () {
    // cookie_counter = cookie_expire;
    console.log("Triggered ajaxSuccess handler.");
});
// var cookie_expire_msg = 'You have been idle for too long and have been logged out. Click Okay to reload the page.';
// var cookie_timer = setInterval(function () {
//     cookie_counter -= 1;
//     if (cookie_counter <= -10) {
//         bootbox.alert(cookie_expire_msg, function () {
//             location.reload();
//         });
//         clearInterval(cookie_timer);
//     }
// }, 1000);

init.push(function () {
    $('#add-attendee-question-attendee-tags').editable({
        select2: {
            tags: ['Received Invitation', 'Registered Late', 'Early Birds'],
            tokenSeparators: [","]
        }
    });
    $('#add-attendee-question-password').editable({
        type: 'text',
        name: 'password',
        title: 'Password',
//        async:false,
        validate: function (value) {

            if (value.length < 6) {
                return 'Atleast 6 charecter';
            }
        }

    });
    $('#add-attendee-question-first-name').editable({
        type: 'text',
        name: 'first-name',
        title: 'First Name'
    });
    $('#add-attendee-question-last-name').editable({
        type: 'text',
        name: 'last-name',
        title: 'Last Name'
    });
    $('#add-attendee-question-firstname').editable({
        validate: function (value) {
            if ($.trim(value) == '') return 'This field is required';
        }
    });
    $('#add-attendee-question-company').editable({
        validate: function (value) {
            if ($.trim(value) == '') return 'This field is required';
        }
    });
    $('#add-attendee-question-email').editable({
        validate: function (value) {
            if ($.trim(value) == '') return 'This field is required';
        }
    });
    $('#add-attendee-question-phone-number').editable({
        validate: function (value) {
            if ($.trim(value) == '') return 'This field is required';
        }
    });
    $('#add-attendee-question-information1').editable({
        source: [
            {value: 1, text: 'Yes'},
            {value: 2, text: 'No'},
            {value: 3, text: 'Unsure'}
        ]
    });
    $('#add-attendee-question-information2').editable({
        validate: function (value) {
            if ($.trim(value) == '') return 'This field is required';
        }
    });
    $('#add-attendee-question-information3').editable({
        showbuttons: 'bottom'
    });
    $('#add-attendee-question-food1').editable({
        source: [
            {value: 1, text: 'No'},
            {value: 2, text: 'Vegetarian'},
            {value: 3, text: 'Vegan'}
        ]
    });
    $('#add-attendee-question-food2').editable({
        showbuttons: 'bottom'
    });
    var options = {
        todayBtn: "linked",
        orientation: $('body').hasClass('right-to-left') ? "auto right" : 'auto auto'
    }
    $('.hotel-details-add-room-datepicker-range').datepicker(options);
    $('.btn').tooltip();
    $('.filter-datepicker').datepicker(options);
    $('.filter-datepicker-range').datepicker(options);
    $('.edit-attendee-hotels-datepicker-range').datepicker(options);
    $('#filter-switch').switcher();
    $('.btn').tooltip();
    $('.datepicker-range').datepicker(options);
    $(".filter-question-selector").select2({
        placeholder: "Select a question"
    });
    $(".select-filter").select2({
        placeholder: "Select a filter"
    });
//    $(".filter-session-selector").select2({
//        placeholder: "Select a session"
//    });
//    $('#filter-rules-switcher').switcher();
    $('#edit-question-country').select2({
        placeholder: "Select A Country",
        data: country_list
    });
    $('#add-question-country').select2({
        placeholder: "Select A Country",
        data: country_list
    });
});
$.fn.editable.defaults.mode = 'inline';
$(function () {
    //$.ajax({
    //    url: base_url + '/get-timezone/',
    //    type: "get",
    //    dataType: "json",
    //    success: function (data) {
    //        //moment.tz.setDefault(data.timezone);
    //        timeZone = data.timezone;
    //    }
    //});

    $('#add-from-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1,
    });
    $('#add-to-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1,
    });
    $('#add-from-time').timepicker({showMeridian: false});
    $('#add-to-time').timepicker({showMeridian: false});

    $('#edit-from-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1,
    });
    $('#edit-to-date').datepicker({
        format: 'yyyy-mm-dd',
        weekStart: 1,
    });
    $('#edit-from-time').timepicker({showMeridian: false});
    $('#edit-to-time').timepicker({showMeridian: false});

    $(".filter-rule-list").sortable({
        connectWith: ".filter-rule-list"
    });
    $(".filter-rule-list").disableSelection();
    $(".sortable tbody").sortable({
        helper: keepWidth
    }).disableSelection();
    $('#edit-attendee-push-notification-status').editable({
        source: [
            {value: 1, text: 'True'},
            {value: 0, text: 'False'}
        ]
    });

    $('body').on('click', '.editable-submit', function () {
        if ($(this).closest('td').find('a').hasClass('select-question-information-184')) {
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            var travel_data = $(this).parent().siblings('.editable-input').find('.input-sm').val();
            var travel_id = travel_data.split('_')[1];
            $.ajax({
                url: base_url + '/admin/travels/get-homebound/',
                type: "POST",
                data: {
                    travel_id: travel_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (data) {
                    var homebound_flights = data.homebound_flights;
                    var options = [];
                    var value = "";
                    for (var flight = 0; flight < homebound_flights.length; flight++) {
                        var departure_date = moment(homebound_flights[flight].departure).format('YYYY-MM-DD'),
                            arrival_date = moment(homebound_flights[flight].arrival).format('YYYY-MM-DD');
                        var departure_time = moment(homebound_flights[flight].departure).format('HH:mm');
                        var arrival_time = moment(homebound_flights[flight].arrival).format('HH:mm');
                        var text = departure_date + ' ' + homebound_flights[flight].name + ' ' + departure_time + '-' + arrival_time;
                        var option = {value: 'flight_' + homebound_flights[flight].id, text: text}
                        options.push(option);
                    }
                    $('.select-question-information-185').parent().html('<a href="#" class="select-question-information-185" name="questions[]" data-type="select" data-pk="185" data-value="' + value + '" data-title="Homebound flight request" data-req="false"></a>');
                    $('body').find('.select-question-information-185').editable({
                        type: "select",
                        source: options
                    });

                }
            });
        }
    });


    var current_attendee = location.hash.split('#id');
    if (current_attendee.length > 1) {
        console.log(current_attendee);
        var current_attendee_id = current_attendee[1];
        console.log(current_attendee_id);
        setTimeout(function () {
            showUserInfo(current_attendee_id);
        }, 100);
    }

});
// Return a helper with preserved width of cells
var keepWidth = function (e, ui) {
    ui.children().each(function () {
        $(this).width($(this).width());
    });
    return ui;
};
//$(".add-classes").select2({
//    tags: true,
//    tokenSeparators: [',', ' '],
//    formatNoMatches: function () {
//        return '';
//    },
//    dropdownCssClass: 'select2-hidden'
//});
$('.datepicker-start, .datepicker-end, .datepicker-registration-available').datepicker();
var options2 = {
    //defaultTime: null,
    minuteStep: 15,
    showMeridian: false,
    showInputs: false,
    orientation: $('body').hasClass('right-to-left') ? {x: 'right', y: 'auto'} : {x: 'auto', y: 'auto'}
}
$('.timepicker-start, .timepicker-end').timepicker(options2);
window.PixelAdmin.start(init);
var multiple_attendee = [];
var multiple_attendee_ids = "";
$('body').on('click', '.attendee-group-id .editable-submit', function (event) {
    attendee_group = [];
    $('#edit-attendee-question-attendee-groups').parent().find('input[type="checkbox"]').each(function () {
        if ($(this).prop('checked')) {
            if ($(this).attr('value') != "Empty" && $.inArray($(this).attr('value'), attendee_group) == -1) {
                attendee_group.push($(this).attr('value'));
            }
        }
    });
});
$('body').on('click', '.add-attendee-group-id .editable-submit', function (event) {
    attendee_group = [];
    $('#add-attendee-question-attendee-groups').parent().find('input[type="checkbox"]').each(function () {
        if ($(this).prop('checked')) {
            if ($(this).attr('value') != "Empty" && $.inArray($(this).attr('value'), attendee_group) == -1) {
                attendee_group.push($(this).attr('value'));
            }
        }
    });
});
//$('body').on('change', '.question_prerequisite', function (event) {
//    var $this = $(this);
//    var question_id = $(this).val();
//    var option_selected = $(this).attr('data-id');
//    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
//    $.ajax({
//        url: base_url + '/admin/questions/option/',
//        type: "POST",
//        dataType: "json",
//        data: {
//            question_id: question_id,
//            csrfmiddlewaretoken: csrf_token
//        },
//        success: function (data) {
//
//            options = data.options;
//            var $el = $this.next(".question_prerequisite_option");
//            $el.empty(); // remove old options
//            $el.append($("<option></option>")
//                .attr("value", '').text('Please Select'));
//            $.each(options, function (value, key) {
//                console.log(value)
//                $el.append($("<option></option>")
//                    .attr("value", key.id).text(key.option));
//            });
//            if (option_selected != '' && option_selected != undefined) {
//                $this.next(".question_prerequisite_option").val(option_selected);
//            }
//        }
//    });
//});
//$('body').on('click', '.btn-add-pre-rule', function (e) {
//    e.preventDefault();
//    $(this).closest('.filr-list').append($('#hidden_filter_item').html());
//    //$('.question_prerequisite').select2();
//
//
//});
//$('body').on('click', '.btn-delete-pre-rule', function (e) {
//    e.preventDefault();
//    $(this).closest('.filr').remove();
//});
$('body').on('click', '.showAddAttendee', function (event) {
    $('body .loader').show();

    headerlist = [];
    $('#filter-search-table thead tr th').each(function () {
        var id = $(this).data('id');
        if (typeof id !== 'undefined') {
            headerlist.push({q_id: id});
        }
    });
    $.ajax({
        url: base_url + '/admin/questions/all/',
        type: "GET",
        data: {},
        success: function (result) {
            var randmPass = randomPassword(6);

            $("#add-attendee-question-password").html(randmPass);
            $("#add-attendee-question-password").editable('setValue', randmPass);
//            $("#add-attendee-question-password").text(randmPass);
//            $("#user_secret").text(result.secret_key);
            questions_groups = result.questionGroup;
//            questions_food = result.questions_food;
            attendee_groups = result.attendee_groups;
            clog(result);
            var outbound_flights = result.outbound_flights;
            var homebound_flights = result.homebound_flights;
            //questions = $.parseJSON(result);
            var appendDiv = "search-add-attende";
            datepicker_date_format = result.datepicker_date_format;
            moment_date_format = result.moment_date_format;
            timeZone = result.timezone;
            for (var i = 0; i < questions_groups.length; i++) {
                var appendClass = "attendee-group-" + questions_groups[i].group.id + "-allQuestions";
                showAttendeeQuestions(questions_groups[i].questions[0], appendDiv, appendClass, outbound_flights, homebound_flights, null);
            }

//            appendClass = "attendee-food-allQuestions";
////            $('.attendee-info-allQuestions').html(info_questions);
//            showAttendeeQuestions(questions_food, appendDiv, appendClass);
            attendee_groupList = [];
            for (var j = 0; j < attendee_groups.length; j++) {
                var group = {value: attendee_groups[j].id, text: replaceValueWithSpecialCharacter(attendee_groups[j].name)}
                attendee_groupList.push(group);
            }

            $('#add-attendee-question-attendee-groups').editable({
                limit: 1,
                source: attendee_groupList,
                defaultValue: null
            });
            clog(attendee_groupList);
            $('#add-attendee-question-password').editable({
                type: 'text',
                name: 'password',
                title: 'Password'
//        async:false,
//                validate: function (value) {
//
//                    if (value.length < 6) {
//                        return 'Atleast 6 charecter';
//                    }
//                }

            });
            var date_format = datepicker_date_format;
            if (date_format == null) {
                date_format = 'yyyy-mm-dd';
            }
            $('.date-question-attendee-info').each(function () {
                var from_date = $(this).attr('data-range-from-date');
                var to_date = $(this).attr('data-range-to-date');
                $(this).editable({
                    mode: 'popup',
                    format: 'yyyy-mm-dd',
                    viewformat: date_format,
                    datepicker: {
                        weekStart: 1,
                        startDate: from_date,
                        endDate: to_date
                    }
                });
            });

            $('.date-range-question-attendee-info').each(function () {
                var from_date = $(this).attr('data-range-from-date');
                var to_date = $(this).attr('data-range-to-date');
                from_date = moment(from_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                to_date = moment(to_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                $(this).editable({
                    mode: 'popup',
                    format: 'yyyy-mm-dd',
                    viewformat: date_format,
                    datepicker: {
                        weekStart: 1,
                        startDate: from_date,
                        endDate: to_date
                    }
                });
            });

            $('.time-question-attendee-info').editable({
                mode: 'popup',
                format: 'hh:ii',
                viewformat: 'hh:ii'

            });
            $('.time-range-question-attendee-info').editable({
                mode: 'popup',
                format: 'hh:ii',
                viewformat: 'hh:ii'
            });

            $('.attendee-panel-title strong').html("New Attendee");
//            $("#add-attendee-question-password").html("hffdf");

//            $('.text-question-information').editable({
//                validate: function (value) {
//                    if ($.trim(value) == '') return 'This field is required';
//                }
//            });
//            $('.radio-question-information').editable({
//                source: [
//                    {value: 1, text: 'Yes'},
//                    {value: 2, text: 'No'}
//                ]
//            });
        }
    });
    $('body .loader').hide();
    $('#search-add-attende').modal();
    clearAttendeeData('search-add-attende');
});

$('#search-add-attende').on('hidden.bs.modal', function () {
    clearAttendeeData('search-add-attende');
    $('#add-attendee-question-attendee-groups').editable('setValue', null);
});

$('body').on('click', '#attendee-history', function (event) {
    if (historyTabActivate) {
        $('.loader').show();
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $.ajax({
            url: base_url + '/admin/attendee/activity/' + attendee_id + '/',
            type: "GET",
            success: function (result) {
                $('#edit-attendee-history').html(result);
                historyTabActivate = false;
                $('.loader').hide();
            }
        });
    }

});

$('body').on('click', '#edit-attendee-order', function (event) {
    $('.loader').show();
    var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
    $.ajax({
        url: base_url + '/admin/attendee/' + attendee_id + '/attendee-orders/',
        type: "GET",
        success: function (result) {
            $('#edit-orders-attendee').html(result.html);
            $('#edit-orders-attendee').find('.order-status-edit-dropdown').select2();
            $('.loader').hide();

        }
    });
});
$('body').on('click', '#edit-group-order', function (event) {
    $('.loader').show();
    var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
    $.ajax({
        url: base_url + '/admin/attendee/' + attendee_id + '/group-orders/',
        type: "GET",
        success: function (result) {
            console.log(result)
            $('#edit-orders-group').html(result.html);
            $('#edit-orders-group').find('.order-status-edit-dropdown').select2();
            $('.loader').hide();

        }
    });
    // }
});

$('body').on('click', '#attendee-registration-group', function (event) {
    if (groupRegistrationTabActivate) {
        $('.loader').show();
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $.ajax({
            url: base_url + '/admin/attendee/group-activity/' + attendee_id + '/',
            type: "GET",
            success: function (result) {
                $('#edit-attendee-registration-group').html(result);
                groupRegistrationTabActivate = false;
                $('.loader').hide();
            }
        });
    }

});

$('body').on("change", '.order-status-edit-dropdown', function (e) {
    var $this = $(this);
    var previous_value = e.removed.id;
    var id = $(this).attr('data-id');
    var status = $(this).val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var user_id = $('.attendee-panel-title').attr('data-attendee-id');
    bootbox.confirm("Do you want to change the order status?", function (confirm) {
        if (confirm) {
            $('.loader').show();
            $.ajax({
                url: base_url + '/admin/attendee/change-order-status/',
                type: "POST",
                data: {
                    order_number: id,
                    status: status,
                    csrfmiddlewaretoken: csrf_token,
                    user_id: user_id
                },
                success: function (result) {
                    $('.loader').hide();
                    if (result.status) {
                        $.growl.notice({message: result.message});
                        if (result.current_order_status == 'pending') {
                            window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=order-invoice&order_number=" + id;
                        } else if (result.current_order_status == 'paid') {
                            window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=receipt&order_number=" + id;
                        }
                    } else {
                        $.growl.warning({message: result.message});
                    }
                    $('#edit-orders li.active a').click();
                }
            });
        } else {
            $this.select2('val', previous_value);
        }
    });
});

$('body').on('click', '.add-rebate-to-order', function (event) {
    var order_number = $(this).attr('data-order-number');
    var order_id = $(this).attr('data-order-id');
    var user_id = $(this).attr('data-attendee-id');
    $('#btn-add-rebate-order').attr('data-order-number', order_number);
    $('#btn-add-rebate-order').attr('data-order-id', order_id);
    $('#btn-add-rebate-order').attr('data-attendee-id', user_id);
    $.ajax({
        url: base_url + '/admin/economy/rebates/',
        type: "GET",
        success: function (result) {
            var rebates = result.rebates;
            var html = '';
            for (i = 0; i < rebates.length; i++) {
                html += "<option value=" + rebates[i].id + ">" + rebates[i].name + "</option>"
            }
            $('#add-rebate-modal').find('#rebates').html(html);
            $('#add-rebate-modal').modal();
        }
    });


});

$('body').on('click', '#btn-add-rebate-order', function (event) {
    var $this = $(this);
    var order_id = $(this).attr('data-order-id');
    var order_number = $(this).attr('data-order-number');
    var rebate_id = $('#rebates').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var user_id = $(this).attr('data-attendee-id');
    console.log('user_id');
    console.log(user_id);
    $('.loader').show();
    $this.attr('disabled', true);
    $.ajax({
        url: base_url + '/admin/attendee/add-rebate-to-order/',
        type: "POST",
        data: {
            order_id: order_id,
            rebate_id: rebate_id,
            user_id: user_id,
            order_number: order_number,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.status) {
                // $('.pnl-' + order_id).find('.pnl-content').html(result.html);
                $('#edit-orders li.active a').click();
                $('.loader').hide();
                $.growl.notice({message: "Rebate added successfully"});
                $('#add-rebate-modal').modal('hide');
                if (result.download_flag) {
                    window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=credit-invoice&order_number=" + order_number;
                }
            }
            $this.attr('disabled', false);

        }
    });

});

$('body').on('click', '#edit-order-tab', function () {
    var is_part_of_group = $('#attendee-economy').attr('data-attendee-type');
    if(is_part_of_group == "false")
        $('#edit-attendee-order').click();
    else $('#edit-group-order').click();
});
$('body').on('click', '#attendee-economy', function () {
    $('#edit-order-tab').click();
});

$('body').on('click', '#edit-balance-tab', function () {
    $('.loader').show();
    var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
    $.ajax({
        url: base_url + '/admin/attendee/' + attendee_id + '/balance/',
        type: "GET",
        success: function (result) {
            $('#edit-balance').html(result.html);
            $('.loader').hide();
        }
    });
});

$('body').on('click', '#economy-activity-tab', function () {
    $('.loader').show();
    var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
    $.ajax({
        url: base_url + '/admin/attendee/activity/' + attendee_id + '/?type=economy-activity',
        type: "GET",
        success: function (result) {
            $('#edit-logs').html(result);
            $('.loader').hide();
        }
    });
});

$('body').on('click', '.remove-rebate-from-order', function () {
    var $this = $(this);
    bootbox.confirm("Do you want to remove the rebate?", function (confirm) {
        if (confirm) {
            var rebate_id = $this.attr('data-rebate-id');
            var order_id = $this.attr('data-order-id');
            var rebate_for_item_id = $this.attr('data-rebate-for-item-id');
            var rebate_for_item_type = $this.attr('data-rebate-for-item-type');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            var user_id = $this.attr('data-attendee-id');
            $('.loader').show();
            // $this.attr('disabled',true);
            $.ajax({
                url: base_url + '/admin/attendee/remove-rebate-from-order/',
                type: "POST",
                data: {
                    order_id: order_id,
                    rebate_id: rebate_id,
                    user_id: user_id,
                    rebate_for_item_id: rebate_for_item_id,
                    rebate_for_item_type: rebate_for_item_type,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    $('.loader').hide();
                    if (result.status) {
                        // $('.pnl-' + order_id).find('.pnl-content').html(result.html);
                        $.growl.notice({message: result.message});
                        $('#add-rebate-modal').modal('hide');
                    } else {
                        $.growl.error({message: result.message});
                    }
                    $('#edit-orders li.active a').click();
                }
            });
        }
    });
});

$('body').on('click', '.admin-request-download-pdf', function (event) {
    var data_pdf = $(this).attr('data-pdf');
    var order_number = $(this).attr('data-order_number');
    var user_id = $('.attendee-panel-title').attr('data-attendee-id');
    if (data_pdf == 'order-invoice') {
        window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=order-invoice&order_number=" + order_number;
    }
    else if (data_pdf == 'receipt') {
        window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=receipt&order_number=" + order_number;
    }
    else if (data_pdf == 'credit-invoice') {
        window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=credit-invoice&order_number=" + order_number;
    }
});

$('body').on('click', '.cost-exl-td .editable-submit', function (e) {
    console.log('clicked');
    var order_item = $(this).closest('td').find('.change-item-cost-show-id').attr('data-order-item');
    var item_cost = $(this).closest('td').find('.change-item-cost-show-id').attr('data-cost');
    var new_cost = $(this).closest('td').find('.input-mini').val();
    if(new_cost != '' && item_cost != new_cost && new_cost > 0){
        console.log('Cost changed');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/attendee/change-order-item-cost/',
            type: "POST",
            data: {
                order_item_id: order_item,
                new_cost: new_cost,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if(result.success){
                    if(result.canceled_order){
                        $.growl.warning({message: result.message});
                    }else{
                        $.growl.notice({message: result.message});
                        $('#edit-orders li.active a').click();
                    }

                }else{
                    $.growl.error({message: result.message});
                }
            }
        });
    }
});

$('body').on('click', '#attendee-sessions', function (event) {
    if (sessionTabActivate) {
        $('.loader').show();
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $.ajax({
            url: base_url + '/admin/attendee/sessions/' + attendee_id + '/',
            type: "GET",
            success: function (result) {

                var session_row = '';
                var attendee_sessions = result.attendee_sessions;
                var date_format = moment_date_format + ' HH:mm:ss';
                if (result.assign_session_write_access) {
                    clog(result);
                    for (var i = 0; i < attendee_sessions.length; i++) {
                        var created = "N/A";
                        if (attendee_sessions[i].created != 'None') {
                            created = moment.utc(attendee_sessions[i].created);
                            created = created.tz(timeZone).format(date_format);
                        }

                        session_row += '<tr>' +
                            '<td><button type="button" class="btn btn-sm btn-attendee-session-delete" data-id=' + attendee_sessions[i].id + ' data-session=' + attendee_sessions[i].session.id + '><i class="fa fa-minus"></i></button></td>' +
                            '<td>' + attendee_sessions[i].session.name + '</td>' +
                            '<td>' + moment(attendee_sessions[i].session.start, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + moment(attendee_sessions[i].session.end, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + attendee_sessions[i].status + '</td>' +
                            //'<td>' + moment.tz(created ,timeZone).format('MM/DD/YYYY HH:mm A')+ '</td>' +
                            '<td>' + created + '</td>' +

//                    '<td>€120</td>' +
//                    '<td>€20 (Student)</td>' +
//                    '<td>€100</td>' +
//                    '<td>25%</td>' +
//                    '<td>€125</td>' +
                            '</tr>';

                    }
                } else {
                    for (var i = 0; i < attendee_sessions.length; i++) {
                        var created = "N/A";
                        if (attendee_sessions[i].created != 'None') {
                            created = moment.utc(attendee_sessions[i].created);
                            created = created.tz(timeZone).format(date_format);
                        }

                        session_row += '<tr>' +
                            '<td></td>' +
                            '<td>' + attendee_sessions[i].session.name + '</td>' +
                            '<td>' + moment(attendee_sessions[i].session.start, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + moment(attendee_sessions[i].session.end, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + attendee_sessions[i].status + '</td>' +
                            '<td>' + created + '</td>' +
                            '</tr>';

                    }
                }
                $('#edit-attendee-sessions').find('.attendee-sessions').html(session_row);
                sessionTabActivate = false;
                $('.loader').hide();
            }
        });
    }

});

$('body').on('click', '#attendee-hotels', function (event) {
    if (hotelTabActivate) {
        $('.loader').show();
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $.ajax({
            url: base_url + '/admin/attendee/hotels/' + attendee_id + '/',
            type: "GET",
            success: function (result) {
                //var bookingsBuddies = result.bookings_buddies;
                var addTable = $('#attendee-edit-hotels');
                addTable.find('.total').html('');
                addTable.find('tbody').html('');
                var div_id = $('#attendee-edit-hotels').closest('.fade').attr('id');
                clog(div_id);
                var bookingsBuddies = result.bookings_buddies;
                for (var i = 0; i < bookingsBuddies.length; i++) {
                    var booking = bookingsBuddies[i]['booking'];
                    clog('booking');
                    clog(booking);
                    var buddies = bookingsBuddies[i].buddies;
                    var actual_buddies = bookingsBuddies[i].actual_buddies;

                    var room_id = booking.room.id;
                    var room_description = booking.room.description + '-' + booking.room.hotel.name;
//                var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('MM/DD/YYYY');
//                var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('MM/DD/YYYY');
                    var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('YYYY-MM-DD');
                    var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('YYYY-MM-DD');
                    var cost = Number(booking.room.cost);
                    //var vat = Number(booking.room.vat.name);
                    var total = cost;
                    var allHotels = $('#hotel-selector').html();
                    if (result.assign_hotel_write_access) {
                        var row = '' +
                            '<tr data-booking-id="' + booking.id + '">' +
                            '   <td>' +
                            '       <button type="button" class="btn btn-sm btn-remove-attendee-hotel" data-id=' + booking.id + '><i class="fa fa-minus"></i></button>' +
                            '   </td>' +
                            '   <td>' + allHotels +
                            '   </td>' +
                            '   <td>' +
                            '       <div class="form-group">' +
                            '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
                            '               <input type="text" class="input-sm form-control start_date" name="start" placeholder="Start date" value="' + check_in + '">' +
                            '               <span class="input-group-addon">to</span>' +
                            '               <input type="text" class="input-sm form-control end_date" name="end" placeholder="End date" value="' + check_out + '">' +
                            '           </div>' +
                            '       </div>' +
                            '   </td>' +
                            '   <td>' +
                            '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies"></a>' +
                            '   </td>' +
                            '<td>' +
                            '       <a href="#" class="add-attendee-hotel-select-actual-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies" style="pointer-events:none;"></a>' +
                            '   </td>' +
//                    '   <td class="cost">' + cost + '</td>' +
//                    '   <td class="">€20 (Student)</td>' +
//                    '   <td>' + cost + '</td>' +
//                    '   <td>' + vat + '</td>' +
//                    '   <td>' + total + '</td>' +
                            '</tr>';
                    } else {
                        var row = '' +
                            '<tr data-booking-id="' + booking.id + '">' +
                            '   <td></td>' +
                            '   <td>' + allHotels +
                            '   </td>' +
                            '   <td>' +
                            '       <div class="form-group">' +
                            '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
                            '               <input type="text" class="input-sm form-control start_date" name="start" placeholder="Start date" value="' + check_in + '" disabled>' +
                            '               <span class="input-group-addon">to</span>' +
                            '               <input type="text" class="input-sm form-control end_date" name="end" placeholder="End date" value="' + check_out + '" disabled>' +
                            '           </div>' +
                            '       </div>' +
                            '   </td>' +
                            '   <td>' +
                            '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies" style="pointer-events:none;"></a>' +
                            '   </td>' +
                            '<td>' +
                            '<a href="#" class="add-attendee-hotel-select-actual-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies" style="pointer-events:none;"></a>' +
                            '</td>' +
                            '</tr>';
                    }

                    var lastRow = '';
//                    '<td colspan="4">TOTAL</td>' +
//                    '<td>$310</td>' +
//                    '<td>$50</td>' +
//                    '<td>$260</td>' +
//                    '<td>25%</td>' +
//                    '<td>€325</td>';
                    addTable.find('.total').html(lastRow);
                    addTable.find('tbody').append(row);


                    //$('.add-attendee-hotels-datepicker-range').datepicker({
                    //    format: 'yyyy-mm-dd',
                    //    startDate: '2016-09-04',
                    //    endDate: '2016-09-11'
                    //});
                    addTable.find('tbody').children('tr:last').find('select').val(room_id);
                    activateAutoSuggestForBuddies(div_id);

                    var lastInsertedRow = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-select-room-buddies');

                    var alraedyThere = [];
                    for (var j = 0; j < buddies.length; j++) {
                        clog('buddies[j]');
                        clog(buddies[j]);
                        if (buddies[j].exists == 1) {
                            alraedyThere.push({
                                id: buddies[j].buddy.id,
                                text: buddies[j].buddy.firstname + ' ' + buddies[j].buddy.lastname
                            });
                        }
                        else {
                            alraedyThere.push({id: buddies[j].email, text: buddies[j].email});
                        }
                    }
                    lastInsertedRow.select2('data', alraedyThere);


                    var actualBuddyInsertedRow = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-select-actual-room-buddies');
                    actualBuddyInsertedRow.select2({
                        tags: true,
                        tokenSeparators: [","]
                    })
                    // addTable.find('tbody').children('tr:last').find('select').val(room_id);
                    var actualBuddyalraedyThere = [];
                    for (var j = 0; j < actual_buddies.length; j++) {
                        clog('actual_buddies[j]');
                        clog(actual_buddies[j]);

                        actualBuddyalraedyThere.push({
                            id: actual_buddies[j].booking.attendee.id,
                            text: actual_buddies[j].booking.attendee.firstname + ' ' + actual_buddies[j].booking.attendee.lastname
                        });
                    }
                    actualBuddyInsertedRow.select2('data', actualBuddyalraedyThere);
                }

                $('#attendee-edit-hotels').find('tbody').find('tr').each(function () {
                    var allotment = $(this).find('.add-attendee-hotel-selector option:selected').attr('data-allotments');
                    var availableDates = $.parseJSON(allotment);
                    var d = new Date();
                    if (availableDates.length > 0) {
                        var dateStr = availableDates[0];
                    } else {
                        var currDate = d.getDate();
                        var currMonth = d.getMonth();
                        var currYear = d.getFullYear();

                        var dateStr = currYear + "-" + currMonth + "-" + currDate;
                    }
                    var booked_start_date = $(this).find('.add-attendee-hotels-datepicker-range').find('.start_date').val();
                    var booked_end_date = $(this).find('.add-attendee-hotels-datepicker-range').find('.end_date').val();
                    var currentDate = new Date(booked_start_date);
                    var endDate = new Date(booked_end_date);
                    var between = [];

                    while (currentDate <= endDate) {
                        var booked_date = new Date(currentDate);
                        between.push(booked_date.getFullYear() + "-" + ("0" + (booked_date.getMonth() + 1)).slice(-2) + "-" + ("0" + booked_date.getDate()).slice(-2));
                        currentDate.setDate(currentDate.getDate() + 1);
                    }
                    $(this).find('.add-attendee-hotels-datepicker-range').datepicker({
                        format: 'yyyy-mm-dd',
                        beforeShowDay: function (date) {
                            //clog(date)
                            var dmy = date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2) + "-" + ("0" + date.getDate()).slice(-2);
                            if ($.inArray(dmy, availableDates) != -1 || $.inArray(dmy, between) != -1) {
                                return true;
                            } else {
                                return false;
                            }
                        },
                        startDate: dateStr
                    });
                });
                hotelTabActivate = false;
                $('.loader').hide();
            }
        });
    }
});

$('body').on('click', '#attendee-travels', function (event) {
    if (travelTabActivate) {
        $('.loader').show();
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $.ajax({
            url: base_url + '/admin/attendee/travels/' + attendee_id + '/',
            type: "GET",
            success: function (result) {
                var travel_row = '';
                var attendee_travels = result.attendee_travels;
                var date_format = moment_date_format + ' HH:mm:ss';
                if (result.assign_travel_write_access) {
                    for (var i = 0; i < attendee_travels.length; i++) {
                        var created = "N/A";
                        if (attendee_travels[i].created != 'None') {
                            // created = moment.tz(attendee_travels[i].created, timeZone).format('YYYY-MM-DD HH:mm:ss');
                            created = moment.utc(attendee_travels[i].created);
                            created = created.tz(timeZone).format(date_format);

                        }
                        clog(created)
                        clog(timeZone)
                        clog(moment.tz(created, timeZone).format('MM/DD/YYYY HH:mm A'))
                        travel_row += '<tr>' +
                            '<td><button type="button" class="btn btn-sm btn-attendee-travel-delete" data-id=' + attendee_travels[i].id + ' data-travel=' + attendee_travels[i].travel.id + '><i class="fa fa-minus"></i></button></td>' +
                            '<td>' + attendee_travels[i].travel.name + '</td>' +
                            '<td>' + moment(attendee_travels[i].travel.departure, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + moment(attendee_travels[i].travel.arrival, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + attendee_travels[i].status + '</td>' +
                            //'<td>' +moment.tz(created ,timeZone).format('MM/DD/YYYY HH:mm A')+ '</td>' +
                            '<td>' + created + '</td>' +
//                    '<td>€120</td>' +
//                    '<td>€20 (Student)</td>' +
//                    '<td>€100</td>' +
//                    '<td>25%</td>' +
//                    '<td>€125</td>' +
                            '</tr>';
                    }
                } else {
                    for (var i = 0; i < attendee_travels.length; i++) {
                        var created = "N/A";
                        if (attendee_travels[i].created != 'None') {
                            // created = moment.tz(attendee_travels[i].created, timeZone).format('YYYY-MM-DD HH:mm:ss');
                            created = moment.utc(attendee_travels[i].created);
                            created = created.tz(timeZone).format(date_format);

                        }
                        travel_row += '<tr>' +
                            '<td></td>' +
                            '<td>' + attendee_travels[i].travel.name + '</td>' +
                            '<td>' + moment(attendee_travels[i].travel.departure, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + moment(attendee_travels[i].travel.arrival, 'YYYY-MM-DD HH:mm:ss').format(date_format) + '</td>' +
                            '<td>' + attendee_travels[i].status + '</td>' +
                            '<td>' + created + '</td>' +
                            '</tr>';
                    }
                }

                $('#edit-attendee-travels').find('.attendee-travels').html(travel_row);
                travelTabActivate = false;
                $('.loader').hide();
            }
        });
    }

});

$('body').on('click', '.userInfo', function (event) {
    var id = $(this).attr('data-id');
    headerlist = [];
    $('#filter-search-table thead tr th').each(function () {
        var id = $(this).data('id');
        if (typeof id !== 'undefined') {
            headerlist.push({q_id: id});
        }
    });
    showUserInfo(id);
});

function showUserInfo(id) {
    $('body .loader').show();
    $.ajax({
        url: base_url + '/admin/attendee/' + id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            if (result.success) {
                //$(".filter-session-selector").select2({
                //    placeholder: "Select a session"
                //});
                //var activity_history = result.activity_history;
                sessionTabActivate = true;
                hotelTabActivate = true;
                travelTabActivate = true;
                historyTabActivate = true;
                groupRegistrationTabActivate = true;
                $('#edit-attendee-history').html("");
                $('#edit-attendee-sessions').find('.attendee-sessions').html("");
                $('#edit-attendee-travels').find('.attendee-travels').html("");
                $('#attendee-edit-hotels').find('tbody').html("");
                $('.nav-tabs a[href="#edit-attendee-questions"]').tab('show');
                var attendee_groups = result.attendee_groups;
                clog(attendee_groups)
                var outbound_flights = result.outbound_flights;
                var homebound_flights = result.homebound_flights;
                var user = result.user;
                questions_groups = result.question_groups;
                answers = result.answers;
                //attendee_group = user.group.id;
                attendee_group = result.attendee_selected_groups;
                //var bookingsBuddies = result.bookings_buddies;
                var attendeeTags = result.attendee_tags;
                $('.attendee-panel-title strong').html(user.firstname + ' ' + user.lastname);
                $('.attendee-panel-title').attr('data-attendee-id', id);
                $('#attendee-economy').attr('data-attendee-type', result.is_part_of_group);
                //$('#edit-registration-date').html(moment.tz(user.created, timeZone).format('MM/DD/YYYY HH:mm A'));
                //$('#edit-update-date').html(moment.tz(user.updated, timeZone).format('MM/DD/YYYY HH:mm A'));

                // $('#edit-registration-date').html(moment(user.created, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm'));
                // $('#edit-update-date').html(moment(user.updated, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm'));

                $('#edit-registration-date').html(user.created);
                $('#edit-update-date').html(user.updated);
                $('#edit-user-id').html(user.id);
                $('#edit-user-bid').html(user.bid);
                $('#edit-external-user-id').html(user.secret_key);
                $('#login-uid').attr('href', $('#login-uid').attr('data-href') + "?uid=" + user.secret_key);
                $("#edit-attendee-question-password").editable('setValue', '');
                $('#edit-attendee-question-password').html('Changed Password');
//            $('#edit-attendee-question-attendee-groups').attr('data-value', user.group.id);
//            $('#edit-attendee-question-attendee-groups').editable('setValue',user.group.id);
                $('#edit-attendee-question-first-name').html(user.firstname);
                $('#edit-attendee-question-last-name').html(user.lastname);
                $('#edit-attendee-question-company').html(user.company);
                $('#edit-attendee-question-email').html(user.email);
                $('#edit-attendee-question-phone-number').html(user.phonenumber);
                datepicker_date_format = result.datepicker_date_format;
                moment_date_format = result.moment_date_format;
                timeZone = result.timezone;
                var appendDiv = "search-edit-attende";
                for (var i = 0; i < questions_groups.length; i++) {
                    var appendClass = "attendee-group-" + questions_groups[i].group.id + "-allQuestions";
                    showAttendeeQuestions(questions_groups[i].questions[0], appendDiv, appendClass, outbound_flights, homebound_flights, answers);
                }

                var attendee_groupList = [];
                for (var j = 0; j < attendee_groups.length; j++) {
                    var group = {value: attendee_groups[j].id, text: replaceValueWithSpecialCharacter(attendee_groups[j].name)}
                    attendee_groupList.push(group);
                }
                var tagList = [];
                for (var k = 0; k < attendeeTags.length; k++) {
                    tagList.push({id: attendeeTags[k].tag.id, text: attendeeTags[k].tag.name});
                }
                clog(tagList);
                $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('data', tagList);
                var push_status = 0;
                if (user.push_notification_status == true) {
                    push_status = 1;
                }
                $('#edit-attendee-push-notification-status').editable('setValue', push_status);

                $('#edit-attendee-question-attendee-groups').editable({
                    //limit: 1,
                    source: attendee_groupList,
                });
                $('#edit-attendee-question-attendee-groups').editable('setValue', attendee_group);
                $('#edit-attendee-question-attendee-tags').editable({
                    select2: {
                        tags: ['Received Invitation', 'Registered Late', 'Early Birds'],
                        tokenSeparators: [","]
                    }
                });
                $('#edit-attendee-question-password').editable({
                    type: 'text',
                    name: 'password',
                    title: 'Password'
                });
                $('#edit-attendee-question-first-name').editable({
                    type: 'text',
                    name: 'first-name',
                    title: 'First Name'
                });
                $('#edit-attendee-question-last-name').editable({
                    type: 'text',
                    name: 'last-name',
                    title: 'Last Name'
                });
                $('#edit-attendee-question-firstname').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });
                $('#edit-attendee-question-company').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });
                $('#edit-attendee-question-email').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });
                $('#edit-attendee-question-phone-number').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });
                $('#edit-attendee-question-information1').editable({
                    source: [
                        {value: 1, text: 'Yes'},
                        {value: 2, text: 'No'},
                        {value: 3, text: 'Unsure'}
                    ]
                });
                $('#edit-attendee-question-information2').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });
                $('#edit-attendee-question-information3').editable({
                    showbuttons: 'bottom'
                });
                $('#edit-attendee-question-food1').editable({
                    source: [
                        {value: 1, text: 'No'},
                        {value: 2, text: 'Vegetarian'},
                        {value: 3, text: 'Vegan'}
                    ]
                });
                $('#edit-attendee-question-food2').editable({
                    showbuttons: 'bottom'
                });
                $('#bs-x-editable-vacation').editable({
                    type: 'datepicker',
                    datepicker: {
                        todayBtn: 'linked'
                    }
                });

                var date_format = datepicker_date_format;
                if (date_format == null) {
                    date_format = 'yyyy-mm-dd';
                }
                $('.date-question-attendee-info').each(function () {
                    var from_date = $(this).attr('data-range-from-date');
                    var to_date = $(this).attr('data-range-to-date');
                    from_date = moment(from_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                    to_date = moment(to_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                    $(this).editable({
                        mode: 'popup',
                        format: 'yyyy-mm-dd',
                        viewformat: date_format,
                        datepicker: {
                            weekStart: 1,
                            startDate: from_date,
                            endDate: to_date
                        }
                    });
                });

                $('.date-range-question-attendee-info').each(function () {
                    var from_date = $(this).attr('data-range-from-date');
                    var to_date = $(this).attr('data-range-to-date');
                    from_date = moment(from_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                    to_date = moment(to_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
                    $(this).editable({
                        mode: 'popup',
                        format: 'yyyy-mm-dd',
                        viewformat: date_format,
                        datepicker: {
                            weekStart: 1,
                            startDate: from_date,
                            endDate: to_date
                        }
                    });
                });

                $('.time-question-attendee-info').editable({
                    mode: 'popup',
                    format: 'hh:ii',
                    viewformat: 'hh:ii'

                });
                $('.time-range-question-attendee-info').editable({
                    mode: 'popup',
                    format: 'hh:ii',
                    viewformat: 'hh:ii'
                });

                $('body .loader').hide();
                $("#search-edit-attende").modal();
            } else {
                $('body .loader').hide();
                $.growl.error({message: "Something went wrong"});
            }
        }
    });
}

$('body').on('focus', '.attendee-add-hotels .add-attendee-hotel-selector', function () {
    previous = $(this).val();
    clog(previous);
}).on('change', '.attendee-add-hotels .add-attendee-hotel-selector', function () {
    //var checkIsBreakUp = true;
    clog(previous);
    var $html = $(this);
    var attendee_name = $('.attendee-panel-title strong').html();
    var booking_id = $(this).closest('tr').attr('data-booking-id');
    var room_id = $(this).val();
    var checkIn = $(this).closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=start]').val();
    var checkOut = $(this).closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=end]').val();
    if (booking_id != '' && booking_id != undefined) {
        //var checkIsBreakUp = checkIsBookingBreakUp(booking_id,room_id,checkIn,checkOut);
        //clog(checkIsBreakUp);
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/admin/hotels/check-match/',
            type: "POST",
            data: {
                booking_id: booking_id,
                room_id: room_id,
                check_in: checkIn,
                check_out: checkOut,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                //clog(result);
                if (result.error) {
                    $.growl.error({message: result.error});
                    $html.val(previous);
                } else {
                    clog(result);
                    var status = 3;
                    if (result.status == 1) {
                        bootbox.confirm(result.message, function (confirm) {
                            if (confirm) {
                                status = 1;
                                changeBooking($html);
                                $html.closest('tr').attr('data-status', '1');
                            } else {
                                status = 0;
                                $html.val(previous);
                            }
                        });
                    } else if (result.status == 2) {
                        bootbox.dialog({
                            message: result.message,
                            title: "",
                            buttons: {
                                success: {
                                    label: "Yes",
                                    className: "btn-success",
                                    callback: function () {
                                        status = 2;
                                        changeBooking($html);
                                        $html.closest('tr').attr('data-status', '2');
                                    }
                                },
                                danger: {
                                    label: "No, only move " + attendee_name + "",
                                    className: "btn-primary",
                                    callback: function () {
                                        status = 1;
                                        changeBooking($html);
                                        $html.closest('tr').attr('data-status', '1');
                                    }
                                },
                                main: {
                                    label: "Cancel",
                                    className: "btn-danger",
                                    callback: function () {
                                        status = 0;
                                        $html.val(previous);
                                        //return false;
                                    }
                                }
                            }

                        });
                    } else if (result.status == 0) {
                        changeBooking($html);
                    }
                    //clog(status);
                    //if (status != 0) {
                    //
                    //}else{
                    //    return false;
                    //}
                }
            }
        });

        //activateAutoSuggestForBuddies(div_id);
    } else {
        changeBooking($html);
    }

});
$('body').on('focus', '#search-edit-attende .attendee-add-hotels .add-attendee-hotels-datepicker-range .start_date', function (event) {
    previous_start_date = $(this).val();
    pre_val = '';
    clog("Focus on start date");
}).on('change', '#search-edit-attende .attendee-add-hotels .add-attendee-hotels-datepicker-range .start_date', function (e) {
    clog("Change on start date");
    var checkIn = $(this).val();
    var checkOut = $(this).closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=end]').val();
    var new_val = $(this).val();
    var checkConflicts = false;
    var from = new Date(checkIn);
    var to = new Date(checkOut);
    var $html = $(this);
    var tr_object = this;
    clog("FROM : " + from);
    clog("TO : " + to);


    clog($(tr_object).closest('tr').siblings());

    $(tr_object).closest('tr').siblings().each(
        function () {
            var checkindate = new Date($(this).find('td:nth(2)').find('div').find('div').find('input[name=start]').val());
            var checkoutdate = new Date($(this).find('td:nth(2)').find('div').find('div').find('input[name=end]').val());
            if (from == checkindate) {
                clog("Check in date clashed");
                checkConflicts = true;
            } else if (from > checkindate && from < checkoutdate) {
                clog("Selected start date into some other date");
                checkConflicts = true;
            } else if (from > to) {
                clog("Check in date is greater than check out date");
                checkConflicts = true;
            } else if (to < checkindate && from > checkoutdate) {
                clog("Date taking in another date");
                checkConflicts = true;
            }
            clog("TR FROM : " + checkindate);
            clog("TR TO : " + checkoutdate);
        });

    clog(checkConflicts);

    if (new_val != pre_val && checkConflicts == false) {
        var prev_date = previous_start_date;
        pre_val = new_val;

        var attendee_name = $('.attendee-panel-title strong').html();
        var booking_id = $(this).closest('tr').attr('data-booking-id');
        var room_id = $(this).closest('tr').find('.add-attendee-hotel-selector').val();

        if (booking_id != '' && booking_id != undefined) {
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/hotels/check-match/',
                type: "POST",
                data: {
                    booking_id: booking_id,
                    room_id: room_id,
                    check_in: checkIn,
                    check_out: checkOut,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {

                    if (result.error) {
                        $.growl.error({message: result.error});
                        // } else if (checkConflicts) {
                        //     $.growl.error({message: "Input start date conficts Inner"});
                        //     $html.val("");
                        //     checkConflicts = false;
                    } else {
                        clog(result);
                        var status = 3;
                        if (result.status == 1 || result.status == 2) {
                            bootbox.confirm(result.date_message, function (confirm) {
                                if (confirm) {
                                    status = 1;
                                    $html.closest('tr').attr('data-status', '1');
                                } else {
                                    status = 0;
                                    $html.val(prev_date);
                                }
                            });
                        }
                    }
                    pre_val = new_val;
                }
            });
        }
    }
    // else if (checkConflicts) {
    //     $.growl.error({message: "Input start date conficts Outer"});
    //     $html.val("");
    //     checkConflicts = false;
    // }

});
$('body').on('focus', '#search-edit-attende .attendee-add-hotels .add-attendee-hotels-datepicker-range .end_date', function (event) {
    previous_start_date = $(this).val();
    pre_val = '';
    clog("Focus on end date");
}).on('change', '#search-edit-attende .attendee-add-hotels .add-attendee-hotels-datepicker-range .end_date', function (e) {
    clog("Change on end date");
    var tr_object = this;
    var checkIn = $(this).closest('tr').find('.add-attendee-hotels-datepicker-range').find('input[name=start]').val();
    var checkOut = $(this).val();
    var checkConflicts = false;
    var from = new Date(checkIn);
    var to = new Date(checkOut);
    var $html = $(this);
    clog("FROM : " + from);
    clog("TO : " + to);

    // clog($(tr_object).closest('tr').siblings());

    $(tr_object).closest('tr').siblings().each(
        function () {
            var checkindate = new Date($(this).find('td:nth(2)').find('div').find('div').find('input[name=start]').val());
            var checkoutdate = new Date($(this).find('td:nth(2)').find('div').find('div').find('input[name=end]').val());
            if (to == checkoutdate) {
                // clog("End date clashed");
                checkConflicts = true;
            } else if (to > checkindate && to < checkoutdate) {
                // clog("Selected end date into some other date");
                checkConflicts = true;
            } else if (from > to) {
                // clog("Check in date is greater than check out date");
                checkConflicts = true;
            } else if (to < checkindate && from > checkoutdate) {
                // clog("Date taking in another date");
                checkConflicts = true;
            }
            // clog("TR FROM : " + checkindate);
            // clog("TR TO : " + checkoutdate);
        });

    clog(checkConflicts);
    var new_val = $(this).val();
    if (new_val != pre_val && checkConflicts == false) {
        var prev_date = previous_start_date;
        pre_val = new_val;
        var attendee_name = $('.attendee-panel-title strong').html();
        var booking_id = $(this).closest('tr').attr('data-booking-id');
        var room_id = $(this).closest('tr').find('.add-attendee-hotel-selector').val();
        if (booking_id != '' && booking_id != undefined) {
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/hotels/check-match/',
                type: "POST",
                data: {
                    booking_id: booking_id,
                    room_id: room_id,
                    check_in: checkIn,
                    check_out: checkOut,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {

                    if (result.error) {
                        $.growl.error({message: result.error});
                        // } else if (checkConflicts) {
                        //     $.growl.error({message: "Input end date conficts Inner"});
                        //     $html.val("");
                        //     checkConflicts = false;
                    } else {
                        clog(result);
                        var status = 3;
                        if (result.status == 1 || result.status == 2) {
                            bootbox.confirm(result.date_message, function (confirm) {
                                if (confirm) {
                                    status = 1;
                                    $html.closest('tr').attr('data-status', '1');
                                } else {
                                    status = 0;
                                    $html.val(prev_date);
                                }
                            });
                        }
                    }
                    pre_val = new_val;
                }
            });
        }
    }
    // else if (checkConflicts) {
    //     $.growl.error({message: "Input start date conficts Outer"});
    //     $html.val("");
    //     checkConflicts = false;
    // }

});
$('body').on('click', '.userInfo td:first-child', function (e) {
    e.stopPropagation();
});
$('body').on('click', '.createAttendee', function (event) {
    $('body .loader').show();
    var groups = attendee_group;
    var fname = '';
    var lname = '';
    var email = '';
    var phonenumber = '';
    var password = $("#add-attendee-question-password").editable('getValue').password;
    var checkMail = false;
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var answers = [];
    var attendee_session = $('#attendee_session_list').val();
    var attendee_travel = $('#attendee_travel_list').val();
    var attendee_tags = $('#add-attendee-questions').find('.attendee-question-attendee-tags').select2('val');
    var error = false;
    var msg = "";

    $('#search-add-attende a[name="questions\\[\\]"]').each(function () {
        if ($.trim($(this).html()) != "" && $.trim($(this).html()) != "Empty") {
            var value = decodeHTMLEntities($(this).html());

            if ($(this).attr('data-type') == 'date') {
                var id = $(this).attr('data-pk')
                var value_obj = $(this).editable('getValue');
                value = value_obj[id + "_date"]
            }
            if ($(this).attr('data-type') == 'time') {
                var id = $(this).attr('data-pk')
                var value_obj = $(this).editable('getValue');
                value = value_obj[id + "_time"]
            }
            if ($(this).hasClass("date_range")) {
                var id = $(this).attr('data-pk');
                var value_obj = $(this).editable('getValue');
                var value_from = value_obj[id + "_from"];
                if (value_from == null) {
                    value_from = '';
                }
                var elm_to_obj = $(this).parent().find('.date-range-question-attendee-info:nth-child(2)').editable('getValue');
                var value_to = elm_to_obj[id + "_to"];
                if (value_to == null) {
                    value_to = '';
                }
                var values = []
                values[0] = value_from;
                values[1] = value_to;
                value = JSON.stringify(values);

            }
            if ($(this).hasClass("time_range")) {
                var id = $(this).attr('data-pk');
                var value_obj = $(this).editable('getValue');
                var value_from = value_obj[id + "_from"];
                if (value_from == null) {
                    value_from = '';
                }
                var elm_to_obj = $(this).parent().find('.time-range-question-attendee-info:nth-child(2)').editable('getValue');
                var value_to = elm_to_obj[id + "_to"];
                if (value_to == null) {
                    value_to = '';
                }
                var values = []
                values[0] = value_from;
                values[1] = value_to;
                value = JSON.stringify(values);


            }
            if($(this).hasClass("country-question-information")) {
                var value_obj = $(this).editable('getValue')['undefined'];
                value = value_obj;
            }

            var answer = {id: $(this).attr('data-pk'), value: value};
            var msgName = $(this).closest('tr').attr('data-actual');
            if (msgName == "firstname") {
                fname = $(this).html();
            }
            if (msgName == "lastname") {
                lname = $(this).html();
            }
            if (msgName == "email") {
                email = $(this).html();
                if (!validateEmail(email)) {
                    error = true;
                    msg += "Please enter a valid email" + "\n";
                }
            }
            if (msgName == "phone") {
                phonenumber = $(this).html();
                clog(phonenumber);
                if (phonenumber != '' && phonenumber != "Empty" && !phoneValidate(phonenumber)) {
                    error = true;
                    msg += "Please enter a valid phonenumber" + "\n";
                }
            }
            answers.push(answer);
        }
        console.log(answers);

        //else {
        //
        //    if ($(this).attr('data-req') == 'true') {
        //        error = true;
        //        var msgName = $(this).closest('tr').find('td:first').html();
        //        msg += "Please fill up " + msgName + " field" + "\n";
        //
        //    }
        //}

    });
    answers = JSON.stringify(answers);
    clog(answers);
    clog(msg);
    // hotels and rooms
    var bookings = [];

    var rows = $('#attendee-add-hotels').children('tbody').children('tr');
    var check_in_out_flag = true;
    rows.each(function () {
        var roomId = $(this).find('.selected-room').val();
        var checkIn = $(this).find('input[name="start"]').val();
        var checkOut = $(this).find('input[name="end"]').val();
        var roomBuddies = $(this).find('.add-attendee-hotel-select-room-buddies').select2('val');
        if (checkIn.length < 4 || checkOut.length < 4) {
            $.growl.warning({message: 'Set check-in and check-out date'});
            check_in_out_flag = false;
        }
        var booking = {
            room_id: roomId,
            check_in: moment(checkIn, 'YYYY-MM-DD').format('YYYY-MM-DD'),
            check_out: moment(checkOut, 'YYYY-MM-DD').format('YYYY-MM-DD'),
            room_buddies: roomBuddies
        };
        bookings.push(booking);
    });
    clog(bookings);
    if (!check_in_out_flag) {
        $('body .loader').hide();
        return;
    }
    var send_mail = false;
    var send_custom = false;
    var send_custom_type = '';
    var send_custom_value = '';
    if ($(this).attr('data-name')) {
        if ($(this).attr('data-name') == "send_mail") {
            send_mail = true;
        }
        else if ($(this).attr('data-name') == "send_custom_message") {
            send_custom = true;
            send_custom_value = $('.create-attendee-custom-message-selector').select2('val');
            send_custom_type = $('.create-attendee-custom-message-selector').select2('data').element[0].attributes['data-type'].value;
        }
    }
    //end hotels and rooms
    //if (attendee_group.length < 1) {
    //    error = true;
    //    msg += "Please fill up group field" + "\n";
    //}
//    else if (checkMail == false) {
//        error = true;
//        msg += "Please insert a Valid Email" + "\n";
//    }
//    else if ($.trim(fname) == "" || $.trim(fname) == "Empty") {
//        error = true;
//        msg = "Please fill up First Name";
//    } else if ($.trim(lname) == "" || $.trim(lname) == "Empty") {
//        error = true;
//        msg = "Please fill up Last Name";
//    } else if ($.trim(company) == "" || $.trim(company) == "Empty") {
//        error = true;
//        msg = "Please fill up Company Name";
//    } else if ($.trim(email) == "" || $.trim(email) == "Empty") {
//        error = true;
//        msg = "Please fill up email";
//    }
    if ($.trim(password) == "" || $.trim(password) == "Empty") {
        error = true;
        msg += "Please fill up Password";
    }
//        else if ($.trim(phone) == "" || $.trim(phone) == "Empty") {
//        error = true;
//        msg = "Please fill up Phone Number";
//    } else if (checkMail == false) {
//        error = true;
//        msg = "Please insert a Valid Email";
//    }
    var data = {
        attendee_groups: JSON.stringify(groups),
        fname: fname,
        lname: lname,
        send_mail: send_mail,
        send_custom: send_custom,
        send_custom_value: send_custom_value,
        send_custom_type: send_custom_type,
        email: email,
        password: password,
        phonenumber: phonenumber,
        answers: answers,
        attendee_session: attendee_session,
        attendee_travel: attendee_travel,
        attendee_bookings: JSON.stringify(bookings),
        attendee_tags: JSON.stringify(attendee_tags),
        csrfmiddlewaretoken: csrf_token
    }
    if (password != '' && password != null && password != undefined) {
        data['password'] = password;
    }
    if (error) {
        $.growl.warning({message: msg});
        $('body .loader').hide();
        //alert(msg);
    } else {
        $.ajax({
            url: base_url + '/admin/attendee/',
            type: "POST",
            data: data,
            success: function (result) {
                $('body .loader').hide();
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    $('#search-add-attende').modal('hide');
                    $('#create-attendee-custom-message-modal').modal('hide');
                    var updated_answers = result.updated_answers;
                    var tag_list = result.tag_list;
                    var group_list = result.group_list;
                    var order_number = result.order_number;
                    if(order_number === undefined)
                        order_number = '';

                    var row = '<td><input type="checkbox"></td>' +
                        '<td>' + updated_answers[0].user.id + '</td>';
                    for (var i = 0; i < headerlist.length; i++) {
                        if (headerlist[i].q_id == 'r_date') {
                            row += '<td>' + updated_answers[0].user.created + '</td>';
                        }
                        if (headerlist[i].q_id == 'u_date') {
                            row += '<td>' + updated_answers[0].user.updated + '</td>';
                        }
                        if (headerlist[i].q_id == 'uid_external') {
                            row += '<td>' + updated_answers[0].user.secret_key + '</td>';
                        }
                        if (headerlist[i].q_id == 'bid_badge') {
                            row += '<td>' + updated_answers[0].user.bid + '</td>';
                        }
                        if (headerlist[i].q_id == 'group') {
                            row += '<td>' + group_list + '</td>';
                        }
                        if (headerlist[i].q_id == 'tag') {
                            row += '<td>' + tag_list + '</td>';
                        }
                        if (headerlist[i].q_id == 'order_number') {
                            row += '<td>' + order_number + '</td>';
                        }
                        if (headerlist[i].q_id == 'invoice_id') {
                            row += '<td></td>';
                        }
                        if (headerlist[i].q_id == 'transaction_id') {
                            row += '<td></td>';
                        }
                        for (var j = 0; j < updated_answers.length; j++) {
                            if (headerlist[i].q_id == updated_answers[j].question.id) {
                                if(updated_answers[j].question.type == 'country' && updated_answers[j].value != "N/A") {
                                    row += '<td>' + textLookup[updated_answers[j].value] + '</td>';
                                }
                                else row += '<td>' + updated_answers[j].value + '</td>'
                            }
                        }
                    }
                    $('#filter-search-table tbody').prepend('<tr class="userInfo" data-id="' + updated_answers[0].user.id + '">' + row + '</tr>');
//                    setTimeout(function () {
//                        window.location.href = '';
//                    }, 3000);
//                    headerlist = [];
                }
            }
        });
    }

});
$('body').on('click', '.editAttendee', function (event) {

    $('body .loader').show();
    if ($(this).attr('data-multiple')) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var multiple_answers = [];
        var first_name = '';
        var last_name = '';
        var king_email = '';
        var mobile_phone = '';
        var role = attendee_group;
        var attendee_tags = $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('val');
        clog(role);
        clog(attendee_tags);
        $('#search-edit-attende a[name="questions\\[\\]"]').each(function () {
//            if ($.trim($(this).html()) != "" && $.trim($(this).html()) != "Empty") {
            var msgName = $(this).closest('tr').find('td:first').html();
//            if (msgName != "First Name" && msgName != "Last Name" && msgName != "King Email" && msgName != "Mobile phone") {
            var answer = {id: $(this).attr('data-pk'), value: decodeHTMLEntities($(this).html())};
            multiple_answers.push(answer);
            if (msgName == "First Name" || msgName == "Förnamn") {
                first_name = $(this).html();
            }
            if (msgName == "Last Name" || msgName == "Efternamn") {
                last_name = $(this).html();
            }
            if (msgName == "Email" || msgName == "E-postadress") {
                king_email = $(this).html();
                if (!validateEmail(king_email)) {
                    error = true;
                    msg += "Please enter a valid email" + "\n";
                }
            }
            if (msgName == "Mobile phone" || msgName == "Mobiltelefon") {
                mobile_phone = $(this).html();
            }
//            }
//            }

        });
        answers = JSON.stringify(multiple_answers);
        var attendees = JSON.stringify(multiple_attendee_ids);


        var attendee_session = $('#attendee_session_list').val();
        var attendee_travel = $('#attendee_travel_list').val();
        clog(attendee_session);
        var bookings = [];
        var rows = $('#attendee-edit-hotels').children('tbody').children('tr');
        var check_in_out_flag = true;
        rows.each(function () {
            var bookingId = $(this).data('booking-id');
            //clog(bookingId);
            var roomId = $(this).find('.selected-room').val();
            var checkIn = $(this).find('input[name="start"]').val();
            var checkOut = $(this).find('input[name="end"]').val();
            var roomBuddies = $(this).find('.add-attendee-hotel-select-room-buddies').select2('val');
            if (checkIn.length < 4 || checkOut.length < 4) {
                $.growl.warning({message: 'Set check-in and check-out date'});
                check_in_out_flag = false;
            }
            var booking = {
                room_id: roomId,
                check_in: moment(checkIn, 'YYYY-MM-DD').format('YYYY-MM-DD'),
                check_out: moment(checkOut, 'YYYY-MM-DD').format('YYYY-MM-DD'),
                room_buddies: roomBuddies
            };
            if (bookingId) {
                booking['exists'] = 1;
                booking['id'] = bookingId;
            }
            else {
                booking['exists'] = 0;
            }
            bookings.push(booking);
        });
        clog("bookings: ");
        if (!check_in_out_flag) {
            $('body .loader').hide();
            return;
        }
        clog(bookings);
        //end edit hotels and rooms

        var data = {
            role: role,
            answers: answers,
            attendees: attendees,
            attendee_bookings: JSON.stringify(bookings),
            attendee_session: attendee_session,
            attendee_travel: attendee_travel,
            csrfmiddlewaretoken: csrf_token,
            first_name: first_name,
            last_name: last_name,
            king_email: king_email,
            mobile_phone: mobile_phone,
            attendee_tags: JSON.stringify(attendee_tags)


        };
        $.ajax({
            url: base_url + '/admin/update_multiple_attendee/',
            type: "POST",
            data: data,
            success: function (result) {
                $('body .loader').hide();
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    if (result.warning)
                        $.growl.warning({message: result.warning});
                    $.growl.notice({message: result.success});
                    multiple_attendee_ids = [];
                    $('#search-edit-attende').modal('hide');
                    var updated_attendee = result.updated_answers;
                    for (var k = 0; k < updated_attendee.length; k++) {
                        var updated_answers = updated_attendee[k].updated_answers;
                        //clog(updated_answers);
                        //clog(headerlist);
                        var row = '<td><input type="checkbox"></td>' +
                            '<td>' + updated_attendee[k].attendee_id + '</td>';
                        for (var i = 0; i < headerlist.length; i++) {
                            for (var j = 0; j < updated_answers.length; j++) {
                                if (headerlist[i].q_id == updated_answers[j].question.id) {
                                    if(updated_answers[j].question.type == 'country' && updated_answers[j].value != "N/A") {
                                        row += '<td>' + textLookup[updated_answers[j].value] + '</td>';
                                    }
                                    else row += '<td>' + updated_answers[j].value + '</td>'
                                }
                            }
                        }
                        $('#filter-search-table tbody tr').each(function () {
                            if ($(this).data('id') == updated_attendee[k].attendee_id) {
                                $(this).html(row);
                            }
                        });
                    }
//                    setTimeout(function () {
//                        window.location.href = '';
//                    }, 3000);
                }
            }
        });

    } else {
        var id = $('#edit-user-id').html();
        //var role = attendee_group;
        var groups = attendee_group;
        //$('.attendee-group-id').find('input[type="checkbox"]').each(function () {
        //    if ($(this).prop('checked')) {
        //        if ($(this).attr('value') != "Empty") {
        //            groups.push($(this).attr('value'));
        //        }
        //    }
        //});
        //clog(groups);
        var first_name = '';
        var last_name = '';
        var king_email = '';
        var phonenumber = '';
        var checkMail = false;
        //var password = decodeHTMLEntities($("#edit-attendee-question-password").html());
        //var password = $("#edit-attendee-question-password").editable('getValue').password;
        var password = $("#edit-attendee-question-password").editable('getValue')['edit-attendee-question-password'];
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var answers = [];
        var attendee_session = $('#attendee_session_list').val();
        var attendee_travel = $('#attendee_travel_list').val();
        var attendee_tags = $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('val');
        var push_notification_status = $('#edit-attendee-push-notification-status').html();
        var error = false;
        var msg = "";
        $('#search-edit-attende a[name="questions\\[\\]"]').each(function () {
//            if ($.trim($(this).html()) != "" && $.trim($(this).html()) != "Empty") {
//            clog($(this).editable('getValue'));
            var value = decodeHTMLEntities($(this).html());
            if ($(this).attr('data-pk') == 104) {
                value = $(this).editable('getValue', true);
            }
            if ($(this).attr('data-type') == 'date') {
                var id = $(this).attr('data-pk');
                var value_obj = $(this).editable('getValue');
                value = value_obj[id + "_date"]
                if (value == null) {
                    value = '';
                }

            }
            if ($(this).attr('data-type') == 'time') {
                var id = $(this).attr('data-pk')
                var value_obj = $(this).editable('getValue');
                value = value_obj[id + "_time"]
                if (value == null) {
                    value = '';
                }
            }
            if ($(this).hasClass("date_range")) {
                var id = $(this).attr('data-pk');
                var value_obj = $(this).editable('getValue');
                var value_from = value_obj[id + "_from"];
                if (value_from == null) {
                    value_from = '';
                }
                var elm_to_obj = $(this).parent().find('.date-range-question-attendee-info:nth-child(2)').editable('getValue');
                var value_to = elm_to_obj[id + "_to"];
                if (value_to == null) {
                    value_to = '';
                }
                var values = []
                values[0] = value_from;
                values[1] = value_to;
                if (values[0] == '' && values[1] == '') {
                    value = ''
                } else {
                    value = JSON.stringify(values);
                }


            }
            if ($(this).hasClass("time_range")) {
                var id = $(this).attr('data-pk');
                var value_obj = $(this).editable('getValue');
                var value_from = value_obj[id + "_from"];
                if (value_from == null) {
                    value_from = '';
                }
                var elm_to_obj = $(this).parent().find('.time-range-question-attendee-info:nth-child(2)').editable('getValue');
                var value_to = elm_to_obj[id + "_to"];
                if (value_to == null) {
                    value_to = '';
                }
                var values = []
                values[0] = value_from;
                values[1] = value_to;
                if (values[0] == '' && values[1] == '') {
                    value = ''
                } else {
                    value = JSON.stringify(values);
                }


            }
            if($(this).hasClass('country-question-information')) {
                var value_obj = $(this).editable('getValue')['undefined'];
                value = value_obj;
            }
            var answer = {id: $(this).attr('data-pk'), value: value};
            var msgName = $(this).closest('tr').attr('data-actual');
            if (msgName == "firstname") {
                first_name = $(this).html();
            }
            if (msgName == "lastname") {
                last_name = $(this).html();
            }
            if (msgName == "email") {
                king_email = $(this).html();
                if (!validateEmail(king_email)) {
                    error = true;
                    msg += "Please enter a valid email" + "\n";
                }
            }
            if (msgName == "phone") {
                phonenumber = $(this).html();
                clog(phonenumber);
                if (phonenumber != '' && phonenumber != "Empty" && !phoneValidate(phonenumber)) {
                    error = true;
                    msg += "Please enter a valid phonenumber" + "\n";
                }
            }

            answers.push(answer);
//            }
//            if ($.trim($(this).html()) == "" || $.trim($(this).html()) == "Empty") {
//                if ($(this).attr('data-req') == 'true') {
//                    error = true;
//                    var msgName = $(this).closest('tr').find('td:first').html();
//                    msg += "Please fill up " + msgName + " field" + "\n";
//
//                }
//            }

        });
        answers = JSON.stringify(answers);


        // hotels and rooms edit
        var bookings = [];
        var rows = $('#attendee-edit-hotels').children('tbody').children('tr');
        var check_in_out_flag = true;
        rows.each(function () {
            var bookingId = $(this).data('booking-id');
            clog(bookingId);
            var status = $(this).attr('data-status');
            var roomId = $(this).find('.selected-room').val();
            var checkIn = $(this).find('input[name="start"]').val();
            var checkOut = $(this).find('input[name="end"]').val();
            var roomBuddies = $(this).find('.add-attendee-hotel-select-room-buddies').select2('val');
            var roomBuddiesName = $(this).find('.add-attendee-hotel-select-room-buddies').select2('data');
            if (checkIn.length < 4 || checkOut.length < 4) {
                $.growl.warning({message: 'Set check-in and check-out date'});
                check_in_out_flag = false;
            }
            var booking = {
                room_id: roomId,
                check_in: moment(checkIn, 'YYYY-MM-DD').format('YYYY-MM-DD'),
                check_out: moment(checkOut, 'YYYY-MM-DD').format('YYYY-MM-DD'),
                room_buddies: roomBuddies,
                roomBuddiesName: roomBuddiesName
            };
            if (status != '0' && status != undefined) {
                booking['status'] = status;
            }
            if (bookingId) {
                booking['exists'] = 1;
                booking['id'] = bookingId;
            }
            else {
                booking['exists'] = 0;
            }
            bookings.push(booking);
        });
        clog(answers);

        if (!check_in_out_flag) {
            $('body .loader').hide();
            return;
        }

        //end edit hotels and rooms
        var send_mail = false;
        var send_custom = false;
        var send_custom_type = '';
        var send_custom_value = '';
        if ($(this).attr('data-name')) {
            if ($(this).attr('data-name') == "send_mail") {
                send_mail = true;
            }
            else if ($(this).attr('data-name') == "send_custom_message") {
                send_custom = true;
                send_custom_value = $('.edit-attendee-custom-message-selector').select2('val');
                send_custom_type = $('.edit-attendee-custom-message-selector').select2('data').element[0].attributes['data-type'].value;
            }
        }
        var data = {
            id: id,
            //role: role,
            attendee_groups: JSON.stringify(groups),
            fname: first_name,
            lname: last_name,
            email: king_email,
            phonenumber: phonenumber,
            send_mail: send_mail,
            send_custom: send_custom,
            send_custom_type: send_custom_type,
            send_custom_value: send_custom_value,
            answers: answers,
            attendee_bookings: JSON.stringify(bookings),
            attendee_tags: JSON.stringify(attendee_tags),
            attendee_session: attendee_session,
            attendee_travel: attendee_travel,
            push_notification_status: push_notification_status,
            csrfmiddlewaretoken: csrf_token
        };
        if (password != '' && password != null && password != undefined) {
            data['password'] = password;
        }
        clog(data);


        //if ($.trim(role) == "" || $.trim(role) == "Empty") {
        clog('groups.length');
        clog(groups.length);
        //if (groups.length < 1) {
        //    error = true;
        //    msg += "Please fill up group field" + "\n";
        //}
//        else if (checkMail == false) {
//            error = true;
//            msg += "Please insert a Valid Email" + "\n";
//        }
        if (error) {
            $.growl.warning({message: msg});
            $('body .loader').hide();
        } else {
            $.ajax({
                url: base_url + '/admin/attendee/',
                type: "POST",
                data: data,
                success: function (result) {
                    $('body .loader').hide();
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        if (result.warning)
                            $.growl.warning({message: result.warning});
                        $.growl.notice({message: result.success});
                        $('#edit-attendee-custom-message-modal').modal('hide');
                        $('#search-edit-attende').modal('hide');
                        var updated_answers = result.updated_answers;
                        var tag_list = result.tag_list;
                        var group_list = result.group_list;
                        var order_numbers = result.order_numbers;
                        var invoice_ids = result.invoice_ids;
                        var transaction_ids = result.transaction_ids;
                        var row = '<td><input type="checkbox"></td>' +
                            '<td>' + id + '</td>';

                        for (var i = 0; i < headerlist.length; i++) {
                            if (headerlist[i].q_id == 'r_date') {
                                row += '<td>' + updated_answers[0].user.created + '</td>';
                            }
                            if (headerlist[i].q_id == 'u_date') {
                                row += '<td>' + updated_answers[0].user.updated + '</td>';
                            }
                            if (headerlist[i].q_id == 'uid_external') {
                                row += '<td>' + updated_answers[0].user.secret_key + '</td>';
                            }
                            if (headerlist[i].q_id == 'bid_badge') {
                                row += '<td>' + updated_answers[0].user.bid + '</td>';
                            }
                            if (headerlist[i].q_id == 'tag') {
                                row += '<td>' + tag_list + '</td>';
                            }
                            if (headerlist[i].q_id == 'group') {
                                row += '<td>' + group_list + '</td>';
                            }
                            if (headerlist[i].q_id == 'order_number') {
                                row += '<td>' + order_numbers + '</td>';
                            }
                            if (headerlist[i].q_id == 'invoice_id') {
                                row += '<td>' + invoice_ids + '</td>';
                            }
                            if (headerlist[i].q_id == 'transaction_id') {
                                row += '<td>' + transaction_ids + '</td>';
                            }
                            for (var j = 0; j < updated_answers.length; j++) {
                                if (headerlist[i].q_id == updated_answers[j].question.id) {
                                    if ((updated_answers[j].question.type == 'date_range' || updated_answers[j].question.type == 'time_range') && updated_answers[j].value != "N/A") {
                                        values = JSON.parse(updated_answers[j].value);
                                        if (values[0].length == 0 && values[1].length == 0)
                                            row += '<td>' + 'N/A' + '</td>'
                                        else row += '<td>' + values[0] + ' to ' + values[1] + '</td>'
                                    }
                                    else if(updated_answers[j].question.type == 'country' && updated_answers[j].value != "N/A") {
                                        row += '<td>' + textLookup[updated_answers[j].value] + '</td>';
                                    }
                                    else row += '<td>' + updated_answers[j].value + '</td>'
                                }
                            }
                        }
                        $('#filter-search-table tbody tr').each(function () {
                            if ($(this).data('id') == id) {
                                $(this).html(row);
                            }
                        });


                        //update Hotel match at hotels/match
                        var room_id = $('#match_room_id').val();
                        if (room_id != "" && room_id != null && room_id != undefined) {
                            $.ajax({
                                url: base_url + '/admin/hotels/match-partial/?room_id=' + room_id,
                                type: "GET",
                                data: data,
                                success: function (result) {
                                    $('#hotels').html(result);
                                }
                            });
                        }


                        //var oldBuddies = []
                        //$('.match-table-unmatched').find('.userInfo').each(function () {
                        //    var elm = $(this);
                        //    var BookingID = elm.find('.match_checkbox').data('id');
                        //    for (var i = 0; i < bookings.length; i++) {
                        //        var booking_id = bookings[i].id;
                        //        if (BookingID == booking_id) {
                        //
                        //            var buddy = elm.find('.buddyInfo');
                        //
                        //            var buddy_id = buddy.attr('data-buddy');
                        //            oldBuddies.push(buddy_id);
                        //            if ($.inArray(buddy_id, bookings[i].room_buddies) < 0) {
                        //                elm.remove();
                        //            }
                        //        }
                        //    }
                        //
                        //
                        //});
                        //$('.match-table-unmatched').find('.userInfo').each(function () {
                        //    var elm = $(this);
                        //    var BookingID = elm.find('.match_checkbox').data('id');
                        //
                        //    for (var i = 0; i < bookings.length; i++) {
                        //        var booking_id = bookings[i].id;
                        //        if (BookingID == booking_id) {
                        //            var buddies = bookings[i].room_buddies;
                        //            clog("Buddies")
                        //            clog(buddies);
                        //            clog("old buddies");
                        //            clog(oldBuddies);
                        //
                        //            for (var obj = 0; obj < buddies.length; obj++) {
                        //                if ($.inArray(buddies[obj], oldBuddies) < 0) {
                        //
                        //                    var myvar = '<tr class="userInfo" data-id="' + id + '">' +
                        //                        '                                            <td><input type="checkbox" class="match_checkbox" data-id="' + booking_id + '"></td>' +
                        //                        '                                            <td>' + data.fname + " " + data.lname + '</td>' +
                        //                        '                                            <td data-buddy="' + buddies[obj] + '" class="buddyInfo">' +
                        //                        '                                                ' + bookings[i].roomBuddiesName[obj].text +
                        //                        '                                                ' +
                        //                        '                                            </td>' +
                        //                        '                                            <td>' + moment(bookings[i].check_in, 'YYYY-MM-DD').format('MMM d, YYYY') + '</td>' +
                        //                        '                                            <td>' + moment(bookings[i].check_out, 'YYYY-MM-DD').format('MMM d, YYYY') + '</td>' +
                        //                        '                                        </tr>';
                        //
                        //                    elm.parent().append(myvar);
                        //                }
                        //            }
                        //        }
                        //    }
                        //
                        //
                        //});
                        //clog("old Buddies");
                        //clog(oldBuddies);
                        //clog("bookings: ");
                        //clog(bookings)

                    }
                }
            });
        }
    }
});

$('body').on('click', '.create-attendee-send-custom-message', function () {
    $('#create-attendee-custom-message-modal').modal();
})

$('body').on('click', '.edit-attendee-send-custom-message', function () {
    $('#edit-attendee-custom-message-modal').modal();
})

$('body').on('click', '.deleteAttendee', function (event) {
    if ($(this).attr('data-multiple')) {
        alert("ok");

    } else {
        bootbox.confirm("Are you sure you want to delete this attendee?", function (result) {
            if (result) {
                var id = $('#edit-user-id').html();
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/attendee/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else if(result.warn){
                            $.growl.warning({message: result.warn});
                        } else {
                            $.growl.notice({message: result.success});
                            $('#search-edit-attende').modal('hide');
                            $('tr.userInfo').each(function () {
                                if ($(this).data('id') == id) {
                                    $(this).remove()
                                }
                            });
                        }
                    }
                });
            }
            // Example.show("Confirm result: " + result);
        });
    }
});
$('body').on('click', '.resetAttendee', function (event) {
    if ($(this).attr('data-multiple')) {
        alert("ok");

    } else {
        bootbox.confirm("Are you sure you want to reset this attendee?", function (result) {
            if (result) {
                var id = $('#edit-user-id').html();
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/attendee/reset/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else {
                            $('#search-edit-attende').modal('hide');
                            $('#filter-search-table').DataTable().ajax.reload();
                            $.growl.notice({message: result.success});
                            // setTimeout(function () {
                            //     window.location.href = '';
                            // }, 3000);
                        }
                    }
                });
            }
            // Example.show("Confirm result: " + result);
        });
    }
});
$('body').on('click', '.addQuestionType', function (event) {
    if ($('input[name=questionType]:checked').length > 0) {
        questionType = $("input[type='radio'][name='questionType']:checked").val();
        if (questionType == '') {
            questionType = $("input[type='radio'][name='questionType']:checked").attr('id').split('add_')[1];
        }
        questionHead(questionType, 'add');
        $("#add-question-group").select2('val', '');
        $('#questions-add-type').modal('hide');
        $('#questions-add').modal();
        $('#add-from-date').val('');
        $('#add-to-date').val('');
        $('#add-to-time').val('');
        $('#add-from-time').val('');
        $('.required-yes').val('1');
        $('.required-no').val('0');
        if (!questionType == 'time' || !questionType == 'time_range') {
            $('#add-time-interval').val('');
        }
    }
});
$('body').on('click', '.addQuestion', function (event) {
    var title = $('.addTitle').val();
    var event = 1;
    var group = $("#add-question-group").select2('val');
    var description = $("#add-description").val();
    //var min_character = $("#add-min-character").val();
    //var max_character = $("#add-max-character").val();
    //var regular_expression = $("#add-regex").val();
    //var question_class = $("#add-class").val();
    var required = $("input[type='radio'][name='questionAddRequired']:checked").val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var error = false;
    var msg = "";
    var optionsList = getOptionList('questions-add');
    clog(optionsList);
    var from_date = $('#add-from-date').val();
    var to_date = $('#add-to-date').val();
    var to_time = $('#add-to-time').val();
    var from_time = $('#add-from-time').val();
    var country = $('#add-question-country').val();
    var time_interval = $('#add-time-interval').val();

    if (questionType == 'date' || questionType == 'date_range') {
        if (from_date == '') {
            error = true;
            msg += "From Date can not be blank" + "<br>";
        }
        if (to_date == '') {
            error = true;
            msg += "To Date can not be blank" + "<br>";
        }
        if (from_date != "" && to_date != "") {
            var from_date_obj = new Date(from_date);
            var to_date_obj = new Date(to_date);
            if (to_date_obj < from_date_obj) {
                error = true;
                msg += "To date must be greater or equal to from date" + "<br>";
            }
        }

    }
    if (questionType == 'time' || questionType == 'time_range') {
        if(time_interval==''){
            error = true;
            msg += "From Specify Interval can not be blank" + "<br>";
        }
        if (from_time == '') {
            error = true;
            msg += "From Time can not be blank" + "<br>";
        }
        if (to_time == '') {
            error = true;
            msg += "To Time can not be blank" + "<br>";
        }
        if (from_time != "" && to_time != "") {
            var from_time_obj = Date.parse('1 Jan 2000 ' + from_time);
            var to_time_obj = Date.parse('1 Jan 2000 ' + to_time);

            if (to_time_obj < from_time_obj) {
                error = true;
                msg += "To time must be greater or equal to from time" + "<br>";
            }
        }
    }


    //var pre_requisite_list = [];
    //$('#questions-add').find('.filr-list').find('.filr').each(
    //    function () {
    //        var action = $(this).find('.question_status').val();
    //        var question_id = $(this).find('.question_prerequisite').val();
    //        var question_answer = $(this).find('.question_prerequisite_option').val();
    //        if (action != "" && question_id != "" && question_answer != "") {
    //            var pre_req = {
    //                'action': action,
    //                'pre_question_id': question_id,
    //                'pre_question_answer_id': question_answer
    //            }
    //            pre_requisite_list.push(pre_req);
    //        }
    //
    //
    //    }
    //);
    var show_description = $('#id_checkbox_add_description').prop('checked');
    var title_lang = valueWithSpecialCharacter(title);
    var description_lang = valueWithSpecialCharacter(description);
    var data = {
        title: title,
        event: event,
        required: required,
        type: questionType,
        group: group,
        description: description,
        //question_class: question_class,
        options_list: JSON.stringify(optionsList),
        //pre_requisite_list: JSON.stringify(pre_requisite_list),
        csrfmiddlewaretoken: csrf_token,
        show_description: show_description,
        title_lang: title_lang,
        description_lang: description_lang,
        to_date: to_date,
        from_date: from_date,
        to_time: to_time,
        from_time: from_time,
        default_country: country,
        time_interval:time_interval
    }
    //if ($('#id_checkbox_add_description').prop('checked')) {
    //    if (description.length === 0) {
    //        error = true;
    //        msg += "*Description can not be blank" + "<br>";
    //    } else {
    //        data['description'] = description;
    //    }
    //}
    if ($('#id_checkbox_add_min_character').prop('checked')) {
        if (min_character.length === 0) {
            error = true;
            msg += "*Min Character can not be blank" + "<br>";
        } else {
            data['min_character'] = min_character;
        }
    }
    if ($('#id_checkbox_add_max_character').prop('checked')) {
        if (max_character.length === 0) {
            error = true;
            msg += "*Max Character can not be blank" + "<br>";
        } else {
            data['max_character'] = max_character;
        }
    }
    //if ($('#id_checkbox_add_regex').prop('checked')) {
    //    if (regular_expression.length === 0) {
    //        error = true;
    //        msg += "*Regular Expression can not be blank" + "<br>";
    //    } else {
    //        data['regular_expression'] = regular_expression;
    //    }
    //}


    if ($.trim(title) == "" || $.trim(title) == "Empty") {
        error = true;
        msg += "Please fill up Title field" + "<br>";
    }
    if ($('input[name=questionAddRequired]:checked').length < 1) {
        error = true;
        msg += "Please Choose the question is Required or Not" + "<br>";
    }
    if ($.trim(group) == "" || $.trim(group) == "Empty") {
        error = true;
        msg += "Please fill up Group field" + "<br>";
    }
    if (error) {
        $.growl.warning({message: msg});
    } else {
        $.ajax({
            url: base_url + '/admin/questions/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    $('#questions-add').find('#options_table tbody').remove();
                    var updated_question = result.question;
                    if (updated_question.required == 1) {
                        var required = 'Yes';
                    } else {
                        var required = 'No';
                    }
                    var row = '' +
                        '      <td>' + updated_question.title + '</td>' +
                        '      <td>' + updated_question.type + '</td>' +
                        '      <td>' + required + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs questionInfo" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '          <button class="btn btn-xs btn-duplicate-question" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '          <button class="btn btn-xs btn-danger deleteQuestion" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
//                    var counter = $('body #questions_group_' + updated_question.group.id).next('.showQuestions').find('tbody tr:last td:first-child').html();
//                    clog(counter)
//                    counter = parseInt(counter) + 1;
                    $('body #questions_group_' + updated_question.group.id).next('.showQuestions').find('tbody').append('<tr><td data-id="' + updated_question.id + '">' + updated_question.id + '</td>' + row + '</tr>');
                    $('#questions-add').modal('hide');
                }
            }
        });
    }

});


$('body').on('click', '.btn-duplicate-question', function () {
    var question_id = $(this).data('id');
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        question_id: question_id,
        csrfmiddlewaretoken: csrfToken
    }
    $.ajax({
        url: base_url + '/admin/questions/duplicate/',
        type: "POST",
        data: data,
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.success});
                var updated_question = result.question;
                if (updated_question.required == 1) {
                    var required = 'Yes';
                } else {
                    var required = 'No';
                }
                var row = '' +
                    '      <td>' + updated_question.title + '</td>' +
                    '      <td>' + updated_question.type + '</td>' +
                    '      <td>' + required + '</td>' +
                    '      <td>' +
                    '          <button class="btn btn-xs questionInfo" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                    '          <button class="btn btn-xs btn-duplicate-question " data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                    '          <button class="btn btn-xs btn-danger deleteQuestion" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                    '      </td>';
                $('body #questions_group_' + updated_question.group.id).next('.showQuestions').find('tbody').append('<tr><td data-id="' + updated_question.id + '">' + updated_question.id + '</td>' + row + '</tr>');

            } else {
                $.growl.warning({message: result.error});
            }
        }
    });
});

$('body').on('click', '.questionInfo', function (event) {
    var id = $(this).attr('data-id');
    $.ajax({
        url: base_url + '/admin/questions/' + id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            var current_language_id = result.current_language_id;
            default_language_id = current_language_id;
            $('.question-language-presets-selector').select2('val',current_language_id);
            var question = result.question;
            question_language = question;
            var option_list = result.option_list;
            option_language = result.option_list;
            var question_pre_req = result.pre_req_list;
            questionHead(question.type, 'edit');
            $('#questions-edit-id').html("#" + question.id);
            $('.editTitle').val(getcontentByLanguage(question.title, question.title_lang, current_language_id));
            $("#edit-question-group").select2('val', question.group.id);
            $("#edit-question-group").attr('data-id', question.group.id);
            if(question.type == 'country' && question.default_answer)
                $('#edit-question-country').select2('val', question.default_answer);
            else if(question.type == 'country')
                $('#edit-question-country').select2('val', '');
            $("#questionEditRequired_1").val('1');
            $("#questionEditRequired_2").val('0');
            if (question.required == 1) {
                $("#questionEditRequired_1").prop("checked", true);
            } else {
                $("#questionEditRequired_2").prop("checked", true)
            }
            if (question.show_description == 1) {
                $('#id_checkbox_edit_description').prop('checked', true);
            }
            // if (question.description != '' && question.description != null) {
            $('#edit-description').val(getcontentByLanguage(question.description, question.description_lang, current_language_id));
            // }
            //if (question.min_character != '' && question.min_character != null) {
            //    $('#edit-min-character').val(question.min_character);
            //    $('#id_checkbox_edit_min_character').prop('checked', true);
            //}
            //if (question.max_character != '' && question.max_character != null) {
            //    $('#edit-max-character').val(question.max_character);
            //    $('#id_checkbox_edit_max_character').prop('checked', true);
            //}
            $('#edit-class').val(question.question_class);

            $('#edit-from-date').val("");
            $('#edit-to-date').val("");
            $('#edit-from-time').val("");
            $('#edit-to-time').val("");
//            $("input[name=questionEditRequired][value='" + question.required + "']").prop("checked", true);
            questionType = question.type;

            if (questionType == 'date' || questionType == 'date_range') {
                $('#edit-from-date').data('datepicker').setDate(question.from_date);
                $('#edit-to-date').data('datepicker').setDate(question.to_date);
            } else if (questionType == 'time' || questionType == 'time_range') {
                $('#edit-from-time').timepicker('setTime', question.from_time);
                $('#edit-to-time').timepicker('setTime', question.to_time);
                $('#edit-time-interval').val(question.time_interval);
            }
            if (questionType == 'select' || questionType == 'radio_button' || questionType == 'checkbox') {
                var rows = '';
                for (var i = 0; i < option_list.length; i++) {
                    var row = '<tr data-id="' + option_list[i].id + '">' +
                        '      <td>' + (i + 1) + '</td>' +
                        '      <td><a href="#" class="edit-button-label" data-type="text" data-pk="1" data-title="title">' + getcontentByLanguage(option_list[i].option, option_list[i].option_lang, current_language_id) + '</a></td>';

                    if (questionType == 'select' || questionType == 'radio_button') {
                        if (option_list[i].default_value) {
                            row += '<td><input type="checkbox" class="option_default" name="option_val" checked></td>'
                        } else {
                            row += '<td><input type="checkbox" class="option_default" name="option_val"></td>'
                        }

                    } else if (questionType == 'checkbox') {
                        if (option_list[i].default_value) {
                            row += '<td><input type="checkbox" class="option_default" name="option_val" checked></td>'
                        } else {
                            row += '<td><input type="checkbox" class="option_default" name="option_val"></td>'
                        }
                    }
                    row += '      <td></td>';
                    row += '      <td>' +
                        '          <button class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '          <button class="btn btn-xs btn-danger delete_option" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete" data-id="' + option_list[i].id + '"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>' +
                        '</tr>';
                    rows += row;
                }
                $('#questions-edit').find('#q_options').show();
                $('#questions-edit').find('#options_table').html('<tbody></tbody>');
                $('#questions-edit').find('#options_table').find('tbody').append(rows);
            } else {
//                $('#questions-edit').find('#q_options').remove();
                $('#questions-edit').find('#options_table').find('tbody').remove();
                $('#questions-edit').find('#q_options').hide();
            }
            var option_tableElement = $('#questions-edit').find('#options_table');
            var removeClasses = ["question_options_text", "question_options_select", "question_options_radio_button", "question_options_date", "question_options_checkbox", "question_options_textarea", "question_options_rate", "question_options_image_upload", "question_options_password"];
            removeMultipleClass(removeClasses, option_tableElement);
            option_tableElement.addClass('question_options_' + questionType);
            //$('#questions-edit').find('.filr-list').html('');
            //if (question_pre_req.length > 0) {
            //    for (var i = 0; i < question_pre_req.length; i++) {
            //        var action = 0;
            //        if (question_pre_req[i].action == true) {
            //            action = 1;
            //        }
            //
            //        $('#questions-edit').find('.filr-list').append($('#hidden_filter_item').html());
            //        $('#questions-edit').find('.filr-list').find('.filr').last().attr('data-id', question_pre_req[i].id);
            //        $('#questions-edit').find('.filr-list').find('.filr').last().find('.question_status').val(action);
            //        $('#questions-edit').find('.filr-list').find('.filr').last().find('.question_prerequisite').val(question_pre_req[i].pre_req_question.id);
            //        $('#questions-edit').find('.filr-list').find('.filr').last().find('.question_prerequisite').attr('data-id', question_pre_req[i].pre_req_answer.id)
            //        $('#questions-edit').find('.filr-list').find('.filr').last().find('.question_prerequisite').trigger("change");
            //
            //    }
            //} else {
            //    $('#questions-edit').find('.filr-list').append($('#hidden_filter_item').html());
            //}


            $('.edit-button-label').editable({
                type: 'text',
                name: '',
                title: 'Label'
            });
            $('#questions-edit').modal();

            $('#options_table tbody').sortable({
                revert: true,
                connectWith: ".sortable",
                stop: function (event, ui) { /* do whatever here */
                    var optionRowOrder = [];
                    var count = 0;
                    $('#options_table tbody tr').each(function () {
                        var option_id = $(this).attr('data-id');
                        count++;
                        rowOrder = {'order': count, 'option_id': option_id};
                        optionRowOrder.push(rowOrder);

                    });
                    clog(optionRowOrder);
                    if (optionRowOrder.length > 0) {
                        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                        $.ajax({
                            url: base_url + '/admin/questions/option-order/',
                            type: "POST",
                            data: {
                                option_order: JSON.stringify(optionRowOrder),
                                csrfmiddlewaretoken: csrf_token
                            },
                            success: function (result) {
                                if (result.error) {
                                    $.growl.error({message: result.error});
                                    setTimeout(function () {
                                        window.location.href = '';
                                    }, 1000);
                                } else {
                                    $.growl.notice({message: result.success});

                                }
                            }
                        });
                    }
                }
            });
        }
    });
});

$('body').on('click', '.btn-view-questionInfo', function (event) {
    var id = $(this).attr('data-id');
    $.ajax({
        url: base_url + '/admin/questions/' + id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            var question = result.question;
            var option_list = result.option_list;
            questionHead(question.type, 'view');
            $('#questions-view-id').html("#" + question.id);
            $('.viewTitle').val(question.title);
            $("#view-question-group").select2('val', question.group.id);
            $("#view-question-group").attr('data-id', question.group.id);
            $("#questionViewRequired_1").val('1');
            $("#questionViewRequired_2").val('0');
            if (question.required == 1) {
                $("#questionViewRequired_1").prop("checked", true);
            } else {
                $("#questionViewRequired_2").prop("checked", true)
            }
            if (question.description != '' && question.description != null) {
                $('#view-description').val(question.description);
                $('#id_checkbox_view_description').prop('checked', true);
            }
            if (question.min_character != '' && question.min_character != null) {
                $('#view-min-character').val(question.min_character);
                $('#id_checkbox_view_min_character').prop('checked', true);
            }
            if (question.max_character != '' && question.max_character != null) {
                $('#view-max-character').val(question.max_character);
                $('#id_checkbox_view_max_character').prop('checked', true);
            }
            $('#edit-class').val(question.question_class);
            questionType = question.type;
            if (questionType == 'date' || questionType == 'date_range') {
                $('#view-from-date').val(question.from_date);
                $('#view-to-date').val(question.to_date);
            } else if (questionType == 'time' || questionType == 'time_range') {
                $('#view-from-time').val(question.from_time);
                $('#view-to-time').val(question.to_time);
            }
            else if (questionType == 'select' || questionType == 'radio_button' || questionType == 'checkbox') {
                var rows = '';
                for (var i = 0; i < option_list.length; i++) {
                    var row = '<tr data-id="' + option_list[i].id + '">' +
                        '      <td>' + (i + 1) + '</td>' +
                        '      <td><a href="#" class="view-button-label" data-type="text" data-pk="1" data-title="title" disabled>' + option_list[i].option + '</a></td>' +
                        '      <td></td>' +
                        '      <td></td>' +
                        '      <td></td>' +
                        '</tr>';
                    rows += row;
                }
                $('#questions-view').find('#q_options').show();
                $('#questions-view').find('#options_table').html('<tbody></tbody>');
                $('#questions-view').find('#options_table').find('tbody').append(rows);
            } else {
                $('#questions-view').find('#options_table').find('tbody').remove();
                $('#questions-view').find('#q_options').hide();
            }
            $('.view-button-label').editable({
                type: 'text',
                name: '',
                title: 'Label',
                disabled: true
            });
            $('#questions-view').modal();

        }
    });
});

$('body').on('keyup', '#add-description', function () {
    var val = $(this).val();
    if (val.length >= 1) {
        $(this).parent().find('input[type=checkbox]').prop('checked', true);
    } else {
        $(this).parent().find('input[type=checkbox]').prop('checked', false);
    }
});

$('body').on('keyup', '#edit-description', function () {
    var val = $(this).val();
    if (val.length >= 1) {
        $(this).parent().find('input[type=checkbox]').prop('checked', true);
    } else {
        $(this).parent().find('input[type=checkbox]').prop('checked', false);
    }
});


$('body').on('click', '.editQuestion', function (event) {
    var id = $('#questions-edit-id').html().split('#')[1];
    var title = $('.editTitle').val();
    var event = 1;
    var group = $("#edit-question-group").select2('val');
    var old_group = $("#edit-question-group").attr('data-id');
    var description = $("#edit-description").val();
    var min_character = $("#edit-min-character").val();
    var max_character = $("#edit-max-character").val();
    //var question_class = $("#edit-class").val();
    var required = $("input[type='radio'][name='questionEditRequired']:checked").val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var error = false;
    var msg = "";
    var optionsList = getOptionList('questions-edit');
    var current_language_id = $('.question-language-presets-selector').select2('val');
    //var pre_requisite_list = [];
    //$('#questions-edit').find('.filr-list').find('.filr').each(
    //    function () {
    //        var action = $(this).find('.question_status').val();
    //        var question_id = $(this).find('.question_prerequisite').val();
    //        var question_answer = $(this).find('.question_prerequisite_option').val();
    //        var id = $(this).attr('data-id');
    //        if (action != "" && question_id != "" && question_answer != "") {
    //            var pre_req = {
    //                'action': action,
    //                'pre_question_id': question_id,
    //                'pre_question_answer_id': question_answer
    //            }
    //            if (id != '' && id != undefined) {
    //                pre_req['id'] = id;
    //            }
    //            pre_requisite_list.push(pre_req);
    //        }
    //
    //
    //    }
    //);
    var show_description = $('#id_checkbox_edit_description').prop('checked');
    var title_lang = valueWithSpecialCharacter(title);
    var description_lang = valueWithSpecialCharacter(description);
    var from_date = $('#edit-from-date').val();
    var to_date = $('#edit-to-date').val();
    var to_time = $('#edit-to-time').val();
    var from_time = $('#edit-from-time').val();
    var default_country = $('#edit-question-country').val();
    var time_interval = $('#edit-time-interval').val();

    var data = {
        id: id,
        title: title,
        event: event,
        required: required,
        type: questionType,
        group: group,
        options_list: JSON.stringify(optionsList),
        description: description,
        //pre_requisite_list: JSON.stringify(pre_requisite_list),
        //question_class: question_class,
        csrfmiddlewaretoken: csrf_token,
        show_description: show_description,
        title_lang: title_lang,
        description_lang: description_lang,
        to_date: to_date,
        from_date: from_date,
        to_time: to_time,
        from_time: from_time,
        default_country: default_country,
        current_language_id: current_language_id,
        time_interval:time_interval

    }
    //if ($('#id_checkbox_edit_description').prop('checked')) {
    //    if (description.length === 0) {
    //        error = true;
    //        msg = "*Description can not be blank";
    //    } else {
    //        data['description'] = description;
    //    }
    //}


    if ($('#id_checkbox_edit_min_character').prop('checked')) {
        if (min_character.length === 0) {
            error = true;
            msg = "*Min Character can not be blank";
        } else {
            data['min_character'] = min_character;
        }
    }
    if ($('#id_checkbox_edit_max_character').prop('checked')) {
        if (max_character.length === 0) {
            error = true;
            msg = "*Max Character can not be blank";
        } else {
            data['max_character'] = max_character;
        }
    }
    if ($.trim(title) == "" || $.trim(title) == "Empty") {
        error = true;
        msg = "Please fill up Title field";
    } else if ($('input[name=questionEditRequired]:checked').length < 1) {
        error = true;
        msg = "Please Choose the question is Required or Not";
    } else if ($.trim(group) == "" || $.trim(group) == "Empty") {
        error = true;
        msg = "Please fill up Group field";
    }
    if (questionType == 'date' || questionType == 'date_range') {
        if (from_date == '') {
            error = true;
            msg = "From Date can not be blank" + "<br>";
        }
        if (to_date == '') {
            error = true;
            msg = "To Date can not be blank" + "<br>";
        }
        if (from_date != "" && to_date != "") {
            var from_date_obj = new Date(from_date);
            var to_date_obj = new Date(to_date);
            if (to_date_obj < from_date_obj) {
                error = true;
                msg = "To date must be greater or equal to from date" + "<br>";
            }
        }

    }
    if (questionType == 'time' || questionType == 'time_range') {
        if(time_interval==''){
            error = true;
            msg = "From Specify Interval can not be blank" + "<br>";
        }
        if (from_time == '') {
            error = true;
            msg = "From Time can not be blank" + "<br>";
        }
        if (to_time == '') {
            error = true;
            msg = "To Time can not be blank" + "<br>";
        }
        if (from_time != "" && to_time != "") {
            var from_time_obj = Date.parse('1 Jan 2000 ' + from_time);
            var to_time_obj = Date.parse('1 Jan 2000 ' + to_time);

            if (to_time_obj < from_time_obj) {
                error = true;
                msg = "To time must be greater or equal to from time" + "<br>";
            }
        }
    }
    if (error) {
        $.growl.warning({message: msg});
    } else {
        $.ajax({
            url: base_url + '/admin/questions/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    $('#questions-edit').find('#options_table').find('tbody').remove();
                    var updated_question = result.question;
                    if (updated_question.required == 1) {
                        var required = 'Yes';
                    } else {
                        var required = 'No';
                    }
                    var row = '' +
                        '      <td>' + updated_question.title + '</td>' +
                        '      <td>' + updated_question.type + '</td>' +
                        '      <td>' + required + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs questionInfo" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '          <button class="btn btn-xs btn-duplicate-question" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
                        '          <button class="btn btn-xs btn-danger deleteQuestion" data-id="' + updated_question.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
                    if (old_group == updated_question.group.id) {
                        $('body .showQuestions tbody tr').each(function () {
                            if ($(this).find('td:first-child').data('id') == updated_question.id) {
                                $(this).html('<td data-id="' + updated_question.id + '">' + updated_question.id + '</td>' + row);
                            }
                        });
                    } else {
                        $('body .showQuestions tbody tr').each(function () {
                            if ($(this).find('td:first-child').data('id') == updated_question.id) {
                                $(this).remove();
                            }
                        });
//                        var counter = $('body #questions_group_' + updated_question.group.id).next('.showQuestions').find('tbody tr:last td:first-child').html();
//                        counter = parseInt(counter) + 1;
                        $('body #questions_group_' + updated_question.group.id).next('.showQuestions').find('tbody').append('<tr><td data-id="' + updated_question.id + '">' + updated_question.id + '</td>' + row + '</tr>');
                    }
                    $('#questions-edit').modal('hide');

                }
            }
        });
    }

});
$('body').on('click', '.deleteQuestion', function (event) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Question?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            clog(id);
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/questions/delete/',
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        $this.closest('tr').remove();
                    }
                }
            });
        }
        // Example.show("Confirm result: " + result);
    });
});
$('body').on('click', '.questionLabel', function (event) {
    var text = $(this).attr('data-text');
    questionHead(text);
});
$('body').on('click', '.btn-delete-session', function (event) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Seminar?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var table = $this.closest('.table').DataTable();
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/sessions/delete/',
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        // $this.closest('tr').remove();
                        table.row($this.parents('tr')).remove().draw();
                    }
                }
            });
        }
    });
});
$('body').on('change', '.edit-attendee-sessions', function (e) {
    //var session = $('.edit-attendee-sessions option:selected').text();
    var session = $('.edit-attendee-sessions option:selected').attr('data-name');
    if ($.trim(session) != "None") {
        var session_start = $('.edit-attendee-sessions option:selected').attr('data-start');
        var session_end = $('.edit-attendee-sessions option:selected').attr('data-end');
        var pushArray = true;
        $this = $(this);
        if ($.trim(session) != '' && $.trim(session) != undefined) {
            var id = $this.select2('val');
            $('#edit-attendee-sessions').find('.attendee-sessions tr').each(function () {
                var dataId = $(this).children('td').first().children('button').attr('data-id');
                if (dataId == id) {
                    pushArray = false;
                }

            });
            attendeeSession(session, id, pushArray, $this, session_start, session_end);
        }
    }

});
$('body').on('change', '.edit-attendee-travels', function (e) {
    var travel = $('.edit-attendee-travels option:selected').text();
    if ($.trim(travel) != "None") {
        var travel_departure = $('.edit-attendee-travels option:selected').attr('data-departure');
        var travel_arrival = $('.edit-attendee-travels option:selected').attr('data-arrival');
        var pushArray = true;
        $this = $(this);
        if ($.trim(travel) != '' && $.trim(travel) != undefined) {
            var id = $this.select2('val');
            $('#edit-attendee-travels').find('.attendee-travels tr').each(function () {
                var dataId = $(this).children('td').first().children('button').attr('data-id');
                if (dataId == id) {
                    pushArray = false;
                }

            });
            attendeeTravel(travel, id, pushArray, $this, travel_departure, travel_arrival);
        }
    }

});
$('body').on('change', '.add-attendee-sessions', function (e) {
    //var session = $('.add-attendee-sessions option:selected').text();
    var session = $('.add-attendee-sessions option:selected').attr('data-name');
    if ($.trim(session) != "None") {
        var session_start = $('.add-attendee-sessions option:selected').attr('data-start');
        var session_end = $('.add-attendee-sessions option:selected').attr('data-end');
        clog(session_start);
        var pushArray = true;
        $this = $(this);
//    clog($this.val());
        if ($.trim(session) != '' && $.trim(session) != undefined) {
            var id = $this.select2('val');
            attendeeSession(session, id, pushArray, $this, session_start, session_end);
        }
    }

});
$('body').on('change', '.add-attendee-travels', function (e) {
    var travel = $('.add-attendee-travels option:selected').text();
    if ($.trim(travel) != "None") {
        var travel_departure = $('.add-attendee-travels option:selected').attr('data-departure');
        var travel_arrival = $('.add-attendee-travels option:selected').attr('data-arrival');
        var pushArray = true;
        $this = $(this);
        clog($this.select2('val'));
        if ($.trim(travel) != '' && $.trim(travel) != undefined) {
            var id = $this.select2('val');
            attendeeTravel(travel, id, pushArray, $this, travel_departure, travel_arrival);
        }
    }

});
$('body').on('click', '.btn-attendee-session-delete', function (e) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Seminar?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/attendee_session/delete/',
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        $this.parent().parent().html('');
                        if (result.download_flag) {
                            var user_id = result.attendee_id;
                            var order_number = result.order_number;
                            window.location = base_url + "/admin/economy/pdf-request?uid=" + user_id + "&data=credit-invoice&order_number=" + order_number;
                        }
                    } else {
                        $.growl.error({message: result.message});
//                        setTimeout(function () {
//                            window.location.href = base_url + '/sessions/';
//                        }, 3000);
                    }
                }
            });
        }
    });
});
$('body').on('click', '.btn-attendee-travel-delete', function (e) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Travel?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/attendee_travel/delete/',
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        $this.parent().parent().html('');
                    } else {
                        $.growl.error({message: result.message});
//                        setTimeout(function () {
//                            window.location.href = base_url + '/sessions/';
//                        }, 3000);
                    }
                }
            });
        }
    });
});
$('body').on('click', '.btn-attendee-session-remove', function (e) {
    var id = $(this).attr('data-id');
    var $this = $(this);
    var sessions = JSON.parse($('#attendee_session_list').val());
    var ii = -1;
    for (var i = 0; i < sessions.length; i++) {
        if (sessions[i].id == id) {
            ii = i;
            $this.parent().parent().html('');
            break;
        }
    }
    sessions.splice(ii, 1);
    $("#attendee_session_list").val(JSON.stringify(sessions));
});
$('body').on('click', '.btn-attendee-travel-remove', function (e) {
    var id = $(this).attr('data-id');
    var $this = $(this);
    var travels = JSON.parse($('#attendee_travel_list').val());
    var ii = -1;
    for (var i = 0; i < travels.length; i++) {
        if (travels[i].id == id) {
            ii = i;
            $this.parent().parent().html('');
            break;
        }
    }
    travels.splice(ii, 1);
    $("#attendee_travel_list").val(JSON.stringify(travels));
});
$('.edit-multiple-attendees').click(function () {
    headerlist = [];
    $('#filter-search-table thead tr th').each(function () {
        var id = $(this).data('id');
        if (typeof id !== 'undefined') {
            headerlist.push({q_id: id});
        }
    });
    $('#filter-search-table tbody input[type=checkbox]').each(function () {
        if ($(this).is(':checked')) {
            id = $(this).parent().parent().attr('data-id')
            multiple_id = {'id': id}
            multiple_attendee.push(multiple_id);
        }

    });
    if (multiple_attendee.length > 0) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        attendee_ids = JSON.stringify(multiple_attendee);
        $.ajax({
            url: base_url + '/admin/multiple_attendee/',
            type: "POST",
            data: {
                attendee_ids: attendee_ids,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                var attendees = result.attendees;
                questions_groups = result.question_groups;
//                questions_food = result.questions_food;
//                abc = result;
//                var bookingsBuddies = result.booking_list;
                $('#edit-registration-date').html('[Multiple Values]');
                $('#edit-update-date').html('[Multiple Values]');
                $('#edit-user-id').html('[Multiple Values]');
                $('#edit-external-user-id').html('[Multiple Values]');
                var multi_attendee_group = [];
                for (var j = 0; j < attendees.length; j++) {
                    multi_attendee_group.push(attendees[j].group.id);
                }
                clog(multi_attendee_group);
                var attendee_groups = result.attendee_groups;
                var groups_list = [];
                for (var j = 0; j < attendee_groups.length; j++) {
                    var group = {value: attendee_groups[j].id, text: attendee_groups[j].name}
                    groups_list.push(group);
                }
                groups_list.push({value: '[Multiple Values]', text: '[Multiple Values]'});
                $('#edit-attendee-question-password').val();
//                $('#edit-attendee-question-attendee-groups').attr('data-value', '[Multiple Values]');
                $('#edit-attendee-question-first-name').html('[Multiple Values]');
                $('#edit-attendee-question-last-name').html('[Multiple Values]');
                $('#edit-attendee-question-company').html('[Multiple Values]');
                $('#edit-attendee-question-email').html('[Multiple Values]');
                $('#edit-attendee-question-phone-number').html('[Multiple Values]');
                $('.editAttendee').attr('data-multiple', 'true');
                $('.deleteAttendee').attr('data-multiple', 'true');
//                var appendDiv = "search-edit-attende";
                var appendDiv = "search-edit-attende";
                for (var i = 0; i < questions_groups.length; i++) {
                    var appendClass = "attendee-group-" + questions_groups[i].group.id + "-allQuestions";
                    showMultipleAttendeeQuestions(questions_groups[i].questions[0], appendDiv, appendClass);
                }

//            var appendClass = "attendee-info-allQuestions";
//            showAttendeeQuestions(questions_information, appendDiv, appendClass, answers);
//            appendClass = "attendee-food-allQuestions";
////            $('.attendee-info-allQuestions').html(info_questions);
//            showAttendeeQuestions(questions_food, appendDiv, appendClass, answers);
//            $('.attendee-food-allQuestions').html(food_questions);
//            var sessionHtml = '';
//            for (var i = 0; i < attendee_sessions.length; i++) {
//                sessionHtml += '<tr>' +
//                    '<td><button type="button" class="btn btn-sm btn-attendee-session-delete" data-id=' + attendee_sessions[i].id + '><i class="fa fa-minus"></i></button></td>' +
//                    '<td>' + attendee_sessions[i].session.name + '</td>' +
//                    '<td>' + user.status + '</td>' +
////                    '<td>€120</td>' +
////                    '<td>€20 (Student)</td>' +
////                    '<td>€100</td>' +
////                    '<td>25%</td>' +
////                    '<td>€125</td>' +
//                    '</tr>';
//            }
//            $('#edit-attendee-sessions').find('.attendee-sessions').html(sessionHtml);
//            var attendee_groupList = [];
//            for (var j = 0; j < attendee_groups.length; j++) {
//                var group = {value: attendee_groups[j].id, text: attendee_groups[j].name}
//                attendee_groupList.push(group);
//            }
//            var tagList = [];
//            for (var k = 0; k < attendeeTags.length; k++) {
//                tagList.push({id: attendeeTags[k].tag.id, text: attendeeTags[k].tag.name });
//            }
//            clog(tagList);
//            $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('data', tagList);

//                var addTable = $('#attendee-edit-hotels');
//                addTable.find('.total').html('');
//                addTable.find('tbody').html('');
//
//                for (var i = 0; i < bookingsBuddies.length; i++) {
//                    var booking = bookingsBuddies[i]['booking'];
//                    var buddies = bookingsBuddies[i].buddies;
//
//                    var room_id = booking.room.id;
//                    var room_description = booking.room.description + '-' + booking.room.hotel.name;
////                var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('MM/DD/YYYY');
////                var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('MM/DD/YYYY');
//                    var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('YYYY-MM-DD');
//                    var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('YYYY-MM-DD');
//                    var cost = Number(booking.room.cost);
//                    var vat = Number(booking.room.vat.name);
//                    var total = cost + vat;
//                    var allHotels = $('#hotel-selector').html();
//
//                    var row = '' +
//                        '<tr data-booking-id="' + booking.id + '">' +
//                        '   <td>' +
//                        '       <button type="button" class="btn btn-sm btn-remove-attendee-hotel" data-id=' + booking.id + '><i class="fa fa-minus"></i></button>' +
//                        '   </td>' +
//                        '   <td>' + allHotels +
//                        '   </td>' +
//                        '   <td>' +
//                        '       <div class="form-group">' +
//                        '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
//                        '               <input type="text" class="input-sm form-control" name="start" placeholder="Start date" value="' + check_in + '">' +
//                        '               <span class="input-group-addon">to</span>' +
//                        '               <input type="text" class="input-sm form-control" name="end" placeholder="End date" value="' + check_out + '">' +
//                        '           </div>' +
//                        '       </div>' +
//                        '   </td>' +
//                        '   <td>' +
//                        '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies"></a>' +
//                        '   </td>' +
////                    '   <td class="cost">' + cost + '</td>' +
////                    '   <td class="">€20 (Student)</td>' +
////                    '   <td>' + cost + '</td>' +
////                    '   <td>' + vat + '</td>' +
////                    '   <td>' + total + '</td>' +
//                        '</tr>';
//
//                    var lastRow = '';
////                    '<td colspan="4">TOTAL</td>' +
////                    '<td>$310</td>' +
////                    '<td>$50</td>' +
////                    '<td>$260</td>' +
////                    '<td>25%</td>' +
////                    '<td>€325</td>';
//                    addTable.find('.total').html(lastRow);
//                    addTable.find('tbody').append(row);
//
//                    $('.add-attendee-hotels-datepicker-range').datepicker({ format: 'yyyy-mm-dd' });
//                    activateAutoSuggestForBuddies();
//                    var lastInsertedRow = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-select-room-buddies');
//                    addTable.find('tbody').children('tr:last').find('select').val(room_id);
//                    var alraedyThere = [];
//                    for (var j = 0; j < buddies.length; j++) {
//                        clog(buddies[j]);
//                        if (buddies[j].exists == 1) {
//                            alraedyThere.push({id: buddies[j].buddy.id, text: buddies[j].buddy.firstname + ' ' + buddies[j].buddy.lastname});
//                        }
//                        else {
//                            alraedyThere.push({id: buddies[j].name, text: buddies[j].name});
//                        }
//                    }
//                    lastInsertedRow.select2('data', alraedyThere);
//                }


//                var appendClass = "attendee-info-allQuestions";
//                showMultipleAttendeeQuestions(questions_information, appendDiv, appendClass);
//                appendClass = "attendee-food-allQuestions";
//                showMultipleAttendeeQuestions(questions_food, appendDiv, appendClass);
//                $('.text-question-information').editable({
//                    validate: function (value) {
//                        if ($.trim(value) == '') return 'This field is required';
//                    }
//                });
//                $('.radio-question-information').editable({
//                    source: [
//                        {value: 1, text: 'Yes'},
//                        {value: 2, text: 'No'}
//                    ]
//                });
//                $('#edit-attendee-question-attendee-groups').editable({
//                    limit: 3,
//                    source: [
//                        {value: 1, text: 'Participant'},
//                        {value: 3, text: 'Speaker'},
//                        {value: 4, text: 'Student'},
//                        {value: 5, text: 'VIP'}
//                    ]
//                });
                var taglist = []
                $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('data', taglist);
                $('#edit-attendee-question-attendee-groups').editable({
                    limit: 1,
                    source: groups_list
                });
                $('#edit-attendee-question-attendee-groups').editable('setValue', '[Multiple Values]');
                $('#edit-attendee-question-attendee-tags').editable({
                    select2: {
                        tags: ['Received Invitation', 'Registered Late', 'Early Birds'],
                        tokenSeparators: [","]
                    }
                });

                $('#edit-attendee-question-password').editable({
                    type: 'text',
                    name: 'password',
                    title: 'Password'
                });

                $('#edit-attendee-question-first-name').editable({
                    type: 'text',
                    name: 'first-name',
                    title: 'First Name'
                });

                $('#edit-attendee-question-last-name').editable({
                    type: 'text',
                    name: 'last-name',
                    title: 'Last Name'
                });

                $('#edit-attendee-question-firstname').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });

                $('#edit-attendee-question-company').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });

                $('#edit-attendee-question-email').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });

                $('#edit-attendee-question-phone-number').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });

                $('#edit-attendee-question-information1').editable({
                    source: [
                        {value: 1, text: 'Yes'},
                        {value: 2, text: 'No'},
                        {value: 3, text: 'Unsure'}
                    ]
                });

                $('#edit-attendee-question-information2').editable({
                    validate: function (value) {
                        if ($.trim(value) == '') return 'This field is required';
                    }
                });

                $('#edit-attendee-question-information3').editable({
                    showbuttons: 'bottom'
                });

                $('#edit-attendee-question-food1').editable({
                    source: [
                        {value: 1, text: 'No'},
                        {value: 2, text: 'Vegetarian'},
                        {value: 3, text: 'Vegan'}
                    ]
                });

                $('#edit-attendee-question-food2').editable({
                    showbuttons: 'bottom'
                });
                $('.attendee-sessions').html('');
                $('.attendee-travels').html('');
                $("#search-edit-attende").modal();
                multiple_attendee_ids = multiple_attendee;

                multiple_attendee = [];
            }
        });

    } else {
        alert("Please Select Multiple Attendee");
    }
});
$('body').on('click', '.add_new_option', function (e) {
    var question_type = $('#question_type').val();
    var count = $(this).closest('.table-footer').siblings('#options_table').find('tbody tr').length + 1;
    var row;
    if (question_type == 'checkbox') {
        row = '<tr>' +
            '      <td>' + count + '</td>' +
            '     <td><a href="#" class="edit-button-label" data-type="text" data-pk="1" data-title="title"></a></td>' +
            '      <td><input type="checkbox" class="option_default" name="option_val" /></td>' +
            '      <td></td>' +
            '      <td>' +
            '          <button class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
            '          <button class="btn btn-xs btn-danger" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
            '      </td>' +
            '  </tr>';

    }
    else if (question_type == 'radio_button') {
        row = '<tr>' +
            '      <td>' + count + '</td>' +
            '     <td><a href="#" class="edit-button-label" data-type="text" data-pk="1" data-title="title"></a></td>' +
            '      <td><input type="checkbox"   class="option_default" name="option_val" /></td>' +
            '      <td></td>' +
            '      <td>' +
            '          <button class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
            '          <button class="btn btn-xs btn-danger" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
            '      </td>' +
            '  </tr>';
    }
    else if (question_type == 'select') {
        row = '<tr>' +
            '      <td>' + count + '</td>' +
            '     <td><a href="#" class="edit-button-label" data-type="text" data-pk="1" data-title="title"></a></td>' +
            '      <td><input type="checkbox"  class="option_default" name="option_val" /></td>' +
            '      <td></td>' +
            '      <td>' +
            '          <button class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
            '          <button class="btn btn-xs btn-danger" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
            '      </td>' +
            '  </tr>';
    } else {
        row = '<tr>' +
            '      <td>' + count + '</td>' +
            '     <td><a href="#" class="edit-button-label" data-type="text" data-pk="1" data-title="title"></a></td>' +
            '      <td></td>' +
            '      <td></td>' +
            '      <td>' +
            '          <button class="btn btn-xs" data-toggle="tooltip" data-placement="top" title="" data-original-title="Duplicate"><i class="dropdown-icon fa fa-files-o"></i></button>' +
            '          <button class="btn btn-xs btn-danger" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
            '      </td>' +
            '  </tr>';
    }

    var option_tableElem = $(this).closest('.table-footer').siblings('#options_table');
    var removeClasses = ["question_options_text", "question_options_select", "question_options_radio_button", "question_options_date", "question_options_checkbox", "question_options_textarea", "question_options_rate", "question_options_image_upload", "question_options_password"];
    removeMultipleClass(removeClasses, option_tableElem);
    option_tableElem.addClass('question_options_' + question_type);
    option_tableElem.find('tbody').append(row);
    $('.edit-button-label').editable({
        type: 'text',
        name: '',
        title: 'Label'
    });

});

$('.attendee-question-attendee-tags').select2({
    tags: true,
    tokenSeparators: [","],
    ajax: {
        multiple: true,
        url: base_url + '/admin/attendee/gettags/',
        dataType: "json",
        type: "POST",
        data: function (term, page) {
            return {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                q: term
            };
        },
        results: function (data, page) {
            lastResults = data.results;
            return data;
        }
    },
    //Allow manually entered text in drop down.
    createSearchChoice: function (term, data) {
        if ($(data).filter(function () {
                return this.text.localeCompare(term) === 0;
            }).length === 0) {
            return {id: term, text: term};
        }
    }
});
$('body').on('click', '.btn-remove-attendee-hotel', function (e) {
    $this = $(this);
    id = $this.attr('data-id');
    if (id == "") {
        $this.parent().parent().remove();
    } else {
        bootbox.confirm("Are you sure you want to delete this Booking?", function (result) {
            if (result) {
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/attendee_booking/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else {
                            $.growl.notice({message: result.success});
                            $this.parent().parent().remove();
//                        setTimeout(function () {
//                            window.location.href = base_url + '/sessions/';
//                        }, 3000);
                        }
                    }
                });
            }
        });
    }
});
$('body').on('click', '.delete_option', function (e) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Option?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/options/delete/',
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.error) {
                        $.growl.error({message: result.error});
                    } else {
                        $.growl.notice({message: result.success});
                        $this.closest('tr').remove();
//                        setTimeout(function () {
//                            window.location.href = '';
//                        }, 3000);
                    }
                }
            });
        }
        // Example.show("Confirm result: " + result);
    });
});

$('body').on('change', '.question_options_radio_button input[type=checkbox]', function () {
    var $this = $(this);
    uncheckedRadioAndSelect($this);
});

$('body').on('change', '.question_options_select input[type=checkbox]', function () {
    var $this = $(this);
    uncheckedRadioAndSelect($this);
});

function uncheckedRadioAndSelect($elem) {
    $elem.closest('tbody').find('input[type=checkbox]').each(function () {
        $(this).not($elem).prop('checked', false);
    });
}

function removeMultipleClass(classesAlpha, $div) {
    $.each(classesAlpha, function (i, v) {
        $div.removeClass(v);
    });
}

function clog(message) {
    if (window.location.hostname != 'eventdobby.com') {
        console.log(message);
    }
}

function valueWithSpecialCharacter(value) {
    if(value !='' && value != null && value != undefined) {
        value =  value.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
    }
    return value;
}

function valueWithSpecialQuote(value) {
    if(value !='' && value != null && value != undefined) {
        value = value.replace(/"/g, "&quot;").replace(/'/g, "&apos;");
    }
    return value;
}

function replaceSpecialCharacter(value) {
    if(value !='' && value != null && value != undefined) {
        value = value.replace(/&amp;/g, "&");
    }
    return value;
}

function replaceValueWithSpecialCharacter(value){
    if(value !='' && value != null && value != undefined){
        value = value.replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&");
    }
    return value;
}