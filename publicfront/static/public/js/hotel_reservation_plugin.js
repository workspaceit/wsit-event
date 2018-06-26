var existing_booking_i = 0;
var att_bookings = [];
var lang_select_room_buddy = $(".lang_select_room_buddy").val();

$(function () {
    $body.on("click", ".hotel-reservation-add-button", function () {
        var default_date_format = $(".default_date_format").val();
        var $element_this = $(this);
        var max_partial_allows = parseInt($(this).closest('.form-plugin-hotel-reservation').find('.partial-data-counter').val());
        // need to increase partial_allows by 1. because it's partial_allows starts with 0
        var partial_allows = parseInt($(this).closest('.form-plugin-hotel-reservation').find('.stay-add-remove-class-for-parial-value').last().val());
        if (partial_allows + 1 >= max_partial_allows) {
            $.growl.warning({message: $('.lang_max_stay_reach').val()});
            return;
        }
        $('.loader').show();
        var h_r_page_id = $(this).closest('.form-plugin-hotel-reservation').find('.form-plugin-intro').find(".h_r_element_page_id").val();
        var h_r_box_id = $(this).closest('.form-plugin-hotel-reservation').find('.form-plugin-intro').find(".h_r_element_box_id").val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var force_default_dates = $(this).closest('.form-plugin-hotel-reservation').find(".force_default_dates_checker").val() == "True" ? true : false;
        var force_hotel_room_selection = $(this).closest('.form-plugin-hotel-reservation').find(".force_hotel_room_selection_checker").val() == "True" ? true : false;
        var hotel_Date_List = JSON.parse($(this).closest('.form-plugin-hotel-reservation').find('.hrp-available-dates').val());
        var $main_element = $(this).closest('.form-plugin-hotel-reservation').find('.class-for-partial-append');
        partial_allows++;
        var user_id = $main_element.find('.uid-text-calss').val().replace('-u', '');
        $.ajax({
            url: base_url + '/hotel-reservation-partial-alow-element/',
            type: "POST",
            data: {
                'page_id': h_r_page_id,
                'box_id': h_r_box_id,
                'csrfmiddlewaretoken': csrf_token,
                'partial_counter': partial_allows,
                'user_id': user_id
            },
            success: function (result) {
                if (result) {
                    $main_element.append(result);
                    var check_in_date_for_select = $main_element.find(".hotel-check-in" + partial_allows).val();
                    var check_out_date_for_select = $main_element.find(".hotel-check-out" + partial_allows).val();

                    var max_buddy_select_no = 1;
                    if (force_hotel_room_selection) {
                        if (check_in_date_for_select.length < 1) {
                            check_in_date_for_select = "2017-01-01";
                        }
                        if (check_out_date_for_select.length < 1) {
                            check_out_date_for_select = "2017-01-01";
                        }
                        var dt_check_in, picker_check_in, dt_check_out, picker_check_out;
                        var list_of_dateList = strdate_list_to_dateList(hotel_Date_List);
                        if (check_in_date_for_select.length > 1 && check_out_date_for_select.length > 1) {
                            var testDate = new Date(check_in_date_for_select);
                            check_in_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                            if ($.inArray(check_in_date_for_select, hotel_Date_List) == -1) {
                                check_in_date_for_select = get_closest_date(testDate, hotel_Date_List);
                                if (testDate > new Date(check_in_date_for_select)){
                                    check_in_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_in_date_for_select) - 1];
                                }
                            }
                            dt_check_in = $main_element.find(".hotel-check-in" + partial_allows).pickadate();
                            picker_check_in = dt_check_in.pickadate('picker');
                            picker_check_in.set('disable', list_of_dateList);
                            picker_check_in.set('disable', 'flip');
                            picker_check_in.set('select', new Date(check_in_date_for_select));

                            testDate = new Date(check_out_date_for_select);
                            check_out_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                            if ($.inArray(check_out_date_for_select, hotel_Date_List) == -1) {
                                check_out_date_for_select = get_closest_date(testDate, hotel_Date_List);
                                if (check_out_date_for_select == check_in_date_for_select) {
                                    var tempdate = check_out_date_for_select;
                                    check_out_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_in_date_for_select) + 1];
                                    if (check_out_date_for_select == undefined) {
                                        check_out_date_for_select = tempdate;
                                    }
                                }
                            }
                            dt_check_out = $main_element.find(".hotel-check-out" + partial_allows).pickadate();
                            picker_check_out = dt_check_out.pickadate('picker');
                            picker_check_out.set('disable', list_of_dateList);
                            picker_check_out.set('disable', 'flip');
                            picker_check_out.set('select', new Date(check_out_date_for_select));

                        } else {
                            console.log('no date found');
                        }

                        var buddy_list_hide_show = $main_element.find('.room-beds').val();
                        $main_element.find('.room-buddy-hide-show').show();
                        if (buddy_list_hide_show == '1') {
                            $main_element.find('.room-buddy-hide-show').hide();
                        }
                        try{
                            max_buddy_select_no = parseInt(buddy_list_hide_show) - 1;
                            if (max_buddy_select_no == undefined || max_buddy_select_no == NaN || max_buddy_select_no == null || max_buddy_select_no < 0){
                                throw Error('max_buddy_select_no value is undefined');
                            }
                        }catch (ex){
                            console.log(ex);
                            max_buddy_select_no = 1;
                        }

                    }

                    var lang_no_data_found = $(".lang_no_data_found").val();
                    init_select2($main_element.find(".hotel-r-buddy" + partial_allows), max_buddy_select_no);
                    $element_this.closest('.form-plugin-hotel-reservation').find('.stay-add-remove-class-for-parial-value').val(partial_allows);

                } else {
                    console.log('Error to get partial allow');
                }
                $('.loader').hide();
            }
        });

    });

    $body.on("click", ".hotel-reservation-remove-button", function () {
        var partial_allows = parseInt($(this).closest('.form-plugin-hotel-reservation').find('.stay-add-remove-class-for-parial-value').last().val());
        if (partial_allows > 0) {
            var $main_element = $(this).closest('.form-plugin-hotel-reservation').find('.class-for-partial-append');
            $main_element.find('.form-plugin-list').last().remove();
            partial_allows--;
            $(this).closest('.form-plugin-hotel-reservation').find('.stay-add-remove-class-for-parial-value').val(partial_allows);
        }
    });

    $body.on('click', '.class-for-date-show', function () {
        $(this).closest('.form-plugin-item').find('.h-r-p-check-in-check-out').show();
        var buddy_list_hide_show = $(this).closest('tr').find('.room-beds').val();
        if (buddy_list_hide_show == 0){
            $(this).closest('.form-plugin-item').find('.room-buddy-hide-show').hide();
            $(this).closest('.form-plugin-item').find('.h-r-p-check-in-check-out').hide();
            return;
        }
        $(this).closest('.form-plugin-item').find('.room-buddy-hide-show').show();
        if (buddy_list_hide_show == '1') {
            $(this).closest('.form-plugin-item').find('.room-buddy-hide-show').hide();
        }
        var hotel_Date_List = JSON.parse($(this).closest('tr').find('.hrp-available-dates').val());
        var default_date_format = $(".default_date_format").val();
        var force_default_dates = $(this).closest('.form-plugin-hotel-reservation').find(".force_default_dates_checker").val() == "True" ? true : false;
        var partial_stay_value = $(this).closest('tbody').find('.date-class-for-parial-value').val();
        var check_in_date_for_select = $(".default_checkin_date_value").val();
        var check_out_date_for_select = $(".default_checkout_date_value").val();
        if (check_in_date_for_select.length < 1) {
            check_in_date_for_select = "2017-01-01";
        }
        if (check_out_date_for_select.length < 1) {
            check_out_date_for_select = "2017-01-01";
        }
        var dt_check_in, picker_check_in, dt_check_out, picker_check_out;
        var list_of_dateList = strdate_list_to_dateList(hotel_Date_List);
        if (!force_default_dates) {
            if (check_in_date_for_select.length > 1 && check_out_date_for_select.length > 1) {
                var testDate = new Date(check_in_date_for_select);
                check_in_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                if ($.inArray(check_in_date_for_select, hotel_Date_List) == -1) {
                    check_in_date_for_select = get_closest_date(testDate, hotel_Date_List);
                    if (testDate > new Date(check_in_date_for_select)){
                        check_in_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_in_date_for_select) - 1];
                    }
                }

                testDate = new Date(check_out_date_for_select);
                check_out_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                if ($.inArray(check_out_date_for_select, hotel_Date_List) == -1) {
                    check_out_date_for_select = get_closest_date(testDate, hotel_Date_List);
                    if (check_out_date_for_select == check_in_date_for_select) {
                        var tempdate = check_out_date_for_select;
                        check_out_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_in_date_for_select) + 1];
                        if (check_out_date_for_select == undefined) {
                            check_out_date_for_select = tempdate;
                        }
                    }
                }

            } else {
                console.log('no date found');
            }
        } else {
            testDate = new Date(check_in_date_for_select);
            check_in_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
            testDate = new Date(check_out_date_for_select);
            check_out_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
        }

        dt_check_in = $(this).closest('.form-plugin-item').find(".hotel-check-in" + partial_stay_value).pickadate();
        picker_check_in = dt_check_in.pickadate('picker');
        picker_check_in.set('enable', true);
        picker_check_in.set('disable', list_of_dateList);
        picker_check_in.set('disable', 'flip');
        picker_check_in.set('select', new Date(check_in_date_for_select));

        dt_check_out = $(this).closest('.form-plugin-item').find(".hotel-check-out" + partial_stay_value).pickadate();
        picker_check_out = dt_check_out.pickadate('picker');
        picker_check_out.set('enable', true);
        picker_check_out.set('disable', list_of_dateList);
        picker_check_out.set('disable', 'flip');
        picker_check_out.set('select', new Date(check_out_date_for_select));

        if (force_default_dates) {
            picker_check_in.stop();
            $(this).closest('.form-plugin-item').find(".hotel-check-in" + partial_stay_value).attr('readonly', true);
            picker_check_out.stop();
            $(this).closest('.form-plugin-item').find(".hotel-check-out" + partial_stay_value).attr('readonly', true);
        }
        var max_buddy_select_no = 1;
        try{
            max_buddy_select_no = parseInt(buddy_list_hide_show) - 1;
            if (max_buddy_select_no == undefined || max_buddy_select_no == NaN || max_buddy_select_no == null || max_buddy_select_no < 0){
                throw Error('max_buddy_select_no value is undefined');
            }
        }catch (ex){
            console.log(ex);
            max_buddy_select_no = 1;
        }

        $(this).closest('.form-plugin-item').find(".hotel-r-buddy" + partial_stay_value).val(null);
        $(this).closest('.form-plugin-item').find(".hotel-r-buddy" + partial_stay_value).trigger('change');
        init_select2($(this).closest('.form-plugin-item').find(".hotel-r-buddy" + partial_stay_value), max_buddy_select_no);
    });

});

function hotel_reservation_init() {
    var hotel_Date_List = [];
    var partial_allows = 1;
    var max_partial_allows = parseInt($(".partial-data-counter").val());
    var force_default_dates = $(".force_default_dates_checker").val() == "True" ? true : false;
    var require_room_selection = $(".require_room_selection_checker").val() == "True" ? true : false;
    var require_room_buddy = $(".require_room_buddy_checker").val() == "True" ? true : false;
    var force_hotel_room_selection = $(".force_hotel_room_selection_checker").val() == "True" ? true : false;
    var week_start_day = parseInt($(".week_start_day").val());
    var kendo_language_select = $(".kendo_language_select").val();
    var default_date_format = $(".default_date_format").val();
    var lang_no_data_found = $(".lang_no_data_found").val();

    $(".form-plugin-hotel-reservation").each(function () {
        force_hotel_room_selection = $(this).find(".force_hotel_room_selection_checker").val() == "True" ? true : false;
        var max_buddy_select_no = 1;
        if (force_hotel_room_selection) {
            force_default_dates = $(this).find(".force_default_dates_checker").val() == "True" ? true : false;
            hotel_Date_List = JSON.parse($(this).find('.hrp-available-dates').val());

            var check_in_date_for_select = $(this).find(".hotel-check-in0").val();
            var check_out_date_for_select = $(this).find(".hotel-check-out0").val();

            if (check_in_date_for_select.length < 1) {
                check_in_date_for_select = "2017-01-01";
            }
            if (check_out_date_for_select.length < 1) {
                check_out_date_for_select = "2017-01-01";
            }
            var dt_check_in, picker_check_in, dt_check_out, picker_check_out;
            if (force_default_dates) {
                dt_check_in = $(this).find(".hotel-check-in0").pickadate();
                picker_check_in = dt_check_in.pickadate('picker');
                picker_check_in.set('select', new Date(check_in_date_for_select));
                picker_check_in.stop();
                $(this).find(".hotel-check-in0").attr('readonly', true);
                dt_check_out = $(this).find(".hotel-check-out0").pickadate();

                picker_check_out = dt_check_out.pickadate('picker');
                picker_check_out.set('select', new Date(check_out_date_for_select));
                picker_check_out.stop();
                $(this).find(".hotel-check-out0").attr('readonly', true);
            } else {
                var list_of_dateList = strdate_list_to_dateList(hotel_Date_List);
                var testDate = new Date(check_in_date_for_select);
                check_in_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                if ($.inArray(check_in_date_for_select, hotel_Date_List) == -1) {
                    check_in_date_for_select = get_closest_date(testDate, hotel_Date_List);
                    if (testDate > new Date(check_in_date_for_select)){
                        check_in_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_in_date_for_select) - 1];
                    }
                }
                console.log(check_in_date_for_select)
                dt_check_in = $(this).find(".hotel-check-in0").pickadate();
                picker_check_in = dt_check_in.pickadate('picker');
                picker_check_in.set('disable', list_of_dateList);
                picker_check_in.set('disable', 'flip');
                picker_check_in.set('select', new Date(check_in_date_for_select));

                testDate = new Date(check_out_date_for_select);
                check_out_date_for_select = testDate.getFullYear() + "-" + ("0" + (testDate.getMonth() + 1)).slice(-2) + "-" + ("0" + testDate.getDate()).slice(-2);
                if ($.inArray(check_out_date_for_select, hotel_Date_List) == -1) {
                    check_out_date_for_select = get_closest_date(testDate, hotel_Date_List);
                    if (check_out_date_for_select == check_in_date_for_select) {
                        var tempdate = check_out_date_for_select;
                        check_out_date_for_select = hotel_Date_List[hotel_Date_List.indexOf(check_out_date_for_select) + 1];
                        if (check_out_date_for_select == undefined) {
                            check_out_date_for_select = tempdate;
                        }
                    }
                }
                console.log(check_out_date_for_select)
                dt_check_out = $(this).find(".hotel-check-out0").pickadate();
                picker_check_out = dt_check_out.pickadate('picker');
                picker_check_out.set('disable', list_of_dateList);
                picker_check_out.set('disable', 'flip');
                picker_check_out.set('select', new Date(check_out_date_for_select));
            }
            var buddy_list_hide_show = $(this).find('tbody').find('.room-beds').val();
            $(this).find('.form-plugin-item').find('.room-buddy-hide-show').show();
            if (buddy_list_hide_show == '1') {
                $(this).find('.form-plugin-item').find('.room-buddy-hide-show').hide();
            }
            try{
                max_buddy_select_no = parseInt(buddy_list_hide_show) - 1;
                if (max_buddy_select_no == undefined || max_buddy_select_no == NaN || max_buddy_select_no == null || max_buddy_select_no < 0){
                    throw Error('max_buddy_select_no value is undefined');
                }
            }catch (ex){
                console.log(ex);
                max_buddy_select_no = 1;
            }
        }

        try {
            init_select2($(this).find(".hotel-room-buddy"), max_buddy_select_no);
            if ($(this).find('.hrp_existing_bookings').val() != undefined) {
                existing_booking($(this).find('.hrp_existing_bookings').val(), $(this));
            }
        } catch (exception) {
            console.log(exception);
        }
    });

}

function strdate_list_to_dateList(str_date_list) {
    var dateList = [];
    for(var i=0; i<str_date_list.length; i++){
        dateList.push(new Date(str_date_list[i]));
    }
    return dateList;
}

function existing_booking(att_bookings_string, $hotel_element) {
    try {
        if(att_bookings_string != '') {
            console.log(att_bookings_string);
            att_bookings = JSON.parse(att_bookings_string);
            console.log(att_bookings);

            if (att_bookings.length > 0) {
                existing_booking_i = 0;
                var partial_counter = 0;
                $hotel_element.find(".class-for-existing-booking").each(function () {
                    var $this = $(this);
                    var box_id = $this.find('.plugin-box-id').val();
                    var user_text = $this.find('.uid-text-calss').val();
                    var hotel_Date_List_arr = [];
                    var default_date_format = $(".default_date_format").val();
                    if (att_bookings[existing_booking_i] != undefined) {
                        $this.find("input[type='radio'][value='" + att_bookings[existing_booking_i].hotelroomid + "']").each(function () {

                            $(this).attr('checked', 'checked');
                            $this.find('.h-r-p-check-in-check-out').show();
                            var box_and_stay = $(this).closest('tr').find('.class-for-setting-existing-booking').val();
                            if (!$(this).hasClass('class-for-date-show')) {
                                $(this).show();
                                $(this).attr('name', 'data-hotel-b' + box_id + '-p-' + partial_counter + user_text);
                                partial_counter++;
                                $(this).addClass('class-for-date-show');
                            }
                            hotel_Date_List_arr[box_and_stay] = JSON.parse($(this).closest('tr').find('.hrp-available-dates').val());
                            if ($.inArray(att_bookings[existing_booking_i].checkin, hotel_Date_List_arr[box_and_stay]) == -1) {
                                hotel_Date_List_arr[box_and_stay].push(att_bookings[existing_booking_i].checkin);
                            }
                            if ($.inArray(att_bookings[existing_booking_i].checkout, hotel_Date_List_arr[box_and_stay]) == -1) {
                                hotel_Date_List_arr[box_and_stay].push(att_bookings[existing_booking_i].checkout);
                            }
                            $(this).closest('tr').find('.hrp-available-dates').val(JSON.stringify(hotel_Date_List_arr[box_and_stay]));
                            var list_of_dateList = strdate_list_to_dateList(hotel_Date_List_arr[box_and_stay]);
                            var dt_check_in, picker_check_in, dt_check_out, picker_check_out;
                            dt_check_in = $this.find('.hotel-reservation-calendar:input').first().pickadate();
                            picker_check_in = dt_check_in.pickadate('picker');
                            picker_check_in.set('disable', list_of_dateList);
                            picker_check_in.set('disable', 'flip');
                            picker_check_in.set('select', new Date(att_bookings[existing_booking_i].checkin));

                            dt_check_out = $this.find('.hotel-reservation-calendar:input').last().pickadate();
                            picker_check_out = dt_check_out.pickadate('picker');
                            picker_check_out.set('disable', list_of_dateList);
                            picker_check_out.set('disable', 'flip');
                            picker_check_out.set('select', new Date(att_bookings[existing_booking_i].checkout));

                            var force_default_dates = $this.closest('.form-plugin-hotel-reservation').find('.force_default_dates_checker').val() == "True" ? true : false;
                            if (force_default_dates) {
                                picker_check_in.stop();
                                $this.find('.hotel-reservation-calendar:input').first().attr('readonly', true);
                                picker_check_out.stop();
                                $this.find('.hotel-reservation-calendar:input').last().attr('readonly', true);
                            }
                            var room_beds = $(this).closest('tr').find('.room-beds').val();
                            var max_select_no = 1;
                            if (room_beds != '1') {
                                var b_ids = [];
                                for (var i = 0; i < att_bookings[existing_booking_i].buddyids.length; i++) {
                                    var option = new Option(att_bookings[existing_booking_i].buddyids[i].text, att_bookings[existing_booking_i].buddyids[i].id);
                                    $(this).closest('.form-plugin-list').find('.hotel-room-buddy').append(option).trigger('change');
                                    b_ids.push(att_bookings[existing_booking_i].buddyids[i].id);
                                    max_select_no = parseInt(room_beds) - 1;
                                }
                                init_select2($(this).closest('.form-plugin-list').find('.hotel-room-buddy'), max_select_no);
                                $(this).closest('.form-plugin-list').find('.hotel-room-buddy').val(b_ids);
                                $(this).closest('.form-plugin-list').find('.hotel-room-buddy').trigger('change');
                                $(this).closest('.form-plugin-list').find('.room-buddy-hide-show').show();
                            }
                            return false;

                        });
                        existing_booking_i++;
                    } else {
                        console.log("att_bookings undefined");
                    }

                });

            }
        }
    } catch (e) {
        console.log("Error: " + e + ".");
    }
}

function get_closest_date(testDate, hotel_Date_List) {
    try {
        var days = [];
        for (var i_date_checker = 0; i_date_checker < hotel_Date_List.length; i_date_checker++) {
            days.push(new Date(hotel_Date_List[i_date_checker]));
        }
        var bestDate = days.length;
        var bestDiff = -(new Date(0, 0, 0)).valueOf();
        var currDiff = 0;
        var i_for_colsest_date;
        for (i_for_colsest_date = 0; i_for_colsest_date < days.length; ++i_for_colsest_date) {
            currDiff = Math.abs(days[i_for_colsest_date] - testDate);
            if (currDiff < bestDiff) {
                bestDate = i_for_colsest_date;
                bestDiff = currDiff;
            }
        }
        testDate = days[bestDate].getFullYear() + "-" + ("0" + (days[bestDate].getMonth() + 1)).slice(-2) + "-" + ("0" + days[bestDate].getDate()).slice(-2);
    } catch (except) {
        console.log('Exception in get_closest_date');
        console.log(except);
    }
    return testDate;
}

function get_hotel_resrevation_data($element) {
    var require_room_selection = $element.find(".require_room_selection_checker").val() == "True" ? true : false;
    var require_room_buddy = $element.find(".require_room_buddy_checker").val() == "True" ? true : false;
    var validation_flag = true;
    var stay_counter = 0;
    var default_date_format = $(".default_date_format").val();
    $element.find('.form-plugin-list').each(function () {
        var this_box_id = $(this).find('.plugin-box-id').val();
        var user_text = $(this).find('.uid-text-calss').val();
        var user_id = $(this).find('.uid-text-calss').val().replace('-u', '');
        var result = {user_id: user_id};
        console.log(user_id);

        // var hotel_room_id = $(this).find("input[name='hotel-selection-" + this_box_id + stay_counter + "']:checked").val();
        var hotel_room_id = $(this).find("input[name='data-hotel-b" + this_box_id + "-p" + stay_counter + user_text + "']:checked").val();
        if (hotel_room_id == 'no-hotel'){
            stay_counter++;
            result['hotelroomid'] = 'no-hotel';
            reservation_Data.push(result);
            return true; // continue
        }
        var user_existing_booking_checker = reservation_Data.map(function (item) {
            return item.user_id;
        }).join(',');
        if(user_id == ''){
            // need to check differently for single and group registration
            user_existing_booking_checker = reservation_Data.length < 1;
        }else{
            user_existing_booking_checker = user_existing_booking_checker.indexOf(user_id) == -1;
        }
        if (require_room_selection && hotel_room_id == undefined && user_existing_booking_checker) {
            lang_hotel_validation_msg = $('.lang_require_room_selection').val();
            // $.growl.error({message: "Select room for allow: " + (stay_counter + 1)});
            validation_flag = false;
            display_error_field($(this).find('.err-val-class'));
            return false;
        }
        result['hotelroomid'] = hotel_room_id != undefined ? hotel_room_id : '0';

        try {
            // var check_in_date = $(".hotel-check-in" + stay_counter).find('input')[0].value;
            console.log('stay_counter ' + stay_counter);
            var check_in_date = $(this).find("input[name=hotel-check-in" + stay_counter + "_submit]").val();
            if (check_in_date == undefined && hotel_room_id != undefined){
                $(this).find(".hotel-check-in" + stay_counter).pickadate().pickadate('picker').start();
                check_in_date = $(this).find("input[name=hotel-check-in" + stay_counter + "_submit]").val();
                $(this).find(".hotel-check-in" + stay_counter).pickadate().pickadate('picker').stop();
                $(this).find(".hotel-check-in" + stay_counter).attr('readonly', true);
            }else if(check_in_date == undefined){
                throw new Error('ignore hotel stay');
            }
        } catch (excepttion) {
            lang_hotel_validation_msg = $('.lang_date_not_set').val();
            console.log(excepttion);
            console.log(reservation_Data);
            // $.growl.error({message: "Date is not set for stay : " + (stay_counter + 1)});
            if (require_room_selection && reservation_Data.length < 1) {
                // if validation_flag = false == true then validation needed
                validation_flag = false;
            }
            return false;
        }
        var check_out_date = $(this).find("input[name=hotel-check-out" + stay_counter + "_submit]").val();
        if (check_out_date == undefined && hotel_room_id != undefined){
            $(this).find(".hotel-check-out" + stay_counter).pickadate().pickadate('picker').start();
            check_out_date = $(this).find("input[name=hotel-check-out" + stay_counter + "_submit]").val();
            $(this).find(".hotel-check-out" + stay_counter).pickadate().pickadate('picker').stop();
            $(this).find(".hotel-check-out" + stay_counter).attr('readonly', true);
        }

        if (!(new Date(check_out_date) > new Date(check_in_date))) {
            lang_hotel_validation_msg = $('.lang_fix_date').val();
            // $.growl.error({message: "Fix date for allow: " + (stay_counter + 1)});
            validation_flag = false;
            display_error_field($(this).find(".hotel-check-out" + stay_counter).closest('.form-plugin-hotel-reservation-check-out'));
            return false;
        }

        for (var i_date = reservation_Data.length; i_date > 0; i_date--) {
            if (user_id != reservation_Data[i_date - 1].user_id) {
                continue;
            }
            var current_check_in = new Date(check_in_date);
            var current_check_out = new Date(check_out_date);
            var prev_check_in = new Date(reservation_Data[i_date - 1].checkin);
            var prev_check_out = new Date(reservation_Data[i_date - 1].checkout);

            if (current_check_in.getTime() == prev_check_in.getTime()) {
                lang_hotel_validation_msg = $('.lang_match_previous_date').val();
                // $.growl.error({message: "Match previous date" + ' for allow: ' + (stay_counter + 1)});
                validation_flag = false;
                display_error_field($(this).find(".hotel-check-in" + stay_counter).closest('.form-plugin-hotel-reservation-check-in'));
                display_error_field($(this).find(".hotel-check-out" + stay_counter).closest('.form-plugin-hotel-reservation-check-out'));
                return false;
            } else if (current_check_in > prev_check_in) {
                if (!(current_check_out > prev_check_out)) {
                    lang_hotel_validation_msg = $('.lang_date_clash').val();
                    console.log('came 111');
                    // $.growl.error({message: "Date clash" + ' for allow: ' + (stay_counter + 1)});
                    validation_flag = false;
                    display_error_field($(this).find(".hotel-check-in" + stay_counter).closest('.form-plugin-hotel-reservation-check-in'));
                    display_error_field($(this).find(".hotel-check-out" + stay_counter).closest('.form-plugin-hotel-reservation-check-out'));
                    return false;
                }
                var day_difference = (prev_check_out - current_check_in) / 86400000;
                if (day_difference > .9) {
                    lang_hotel_validation_msg = $('.lang_date_clash').val();
                    console.log('came 222');
                    // $.growl.error({message: "Date clash" + ' for allow: ' + (stay_counter + 1)});
                    validation_flag = false;
                    display_error_field($(this).find(".hotel-check-in" + stay_counter).closest('.form-plugin-hotel-reservation-check-in'));
                    display_error_field($(this).find(".hotel-check-out" + stay_counter).closest('.form-plugin-hotel-reservation-check-out'));
                    return false;
                }
            } else if (current_check_in < prev_check_in) {
                if ((current_check_out > prev_check_in)) {
                    console.log('came 333');
                    lang_hotel_validation_msg = $('.lang_date_clash').val();
                    // $.growl.error({message: "Date clash" + ' for allow: ' + (stay_counter + 1)});
                    validation_flag = false;
                    display_error_field($(this).find(".hotel-check-in" + stay_counter).closest('.form-plugin-hotel-reservation-check-in'));
                    display_error_field($(this).find(".hotel-check-out" + stay_counter).closest('.form-plugin-hotel-reservation-check-out'));
                    return false;
                }
            }
        }

        result['checkin'] = check_in_date;
        result['checkout'] = check_out_date;

        var selected_room_beds = $(this).find("input[name='data-hotel-b" + this_box_id + "-p" + stay_counter + user_text + "']:checked").closest('tr').find('.room-beds').val();
        var rBuddyList = $(this).find('.hotel-r-buddy' + stay_counter).val();
        if (require_room_buddy && (rBuddyList == null || rBuddyList == undefined) && selected_room_beds != 1) {
            lang_hotel_validation_msg = $('.lang_require_room_buddy').val();            
            // $.growl.error({message: "Require room buddy for allow: " + (stay_counter + 1)});            
            validation_flag = false;
            display_error_field($(this).find('.form-plugin-hotel-reservation-room-buddy'));
            return false;
        }
        if (selected_room_beds == 1 || rBuddyList == null){
            rBuddyList = [];
        }
        result['buddyids'] = rBuddyList;

        reservation_Data.push(result);
        stay_counter++;
    });
    console.log('reservation_Data');
    console.log(reservation_Data);
    return validation_flag;
}

function init_select2($element, max_select_no) {
    var txt_input_too_short = $('.txt_input_too_short').val();
    var txt_max_buddy_selected = $('.txt_max_buddy_selected').val();
    $element.select2({
        delay: 500,
        minimumInputLength: 1,
        placeholder: lang_select_room_buddy,
        tags: true,
        multiple: true,
        maximumSelectionLength: max_select_no,
        ajax: {
            url: base_url + "/hotel-reservation-plugin-buddy-list/",
            dataType: 'json',
            type: "POST",
            data: function (params) {
                return {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    q: params.term
                };
            }
        },
        language: {
            inputTooShort: function (args) {
                return txt_input_too_short;
            },
            maximumSelected: function (args) {
                return txt_max_buddy_selected.replace('{X}', args.maximum);
            }
        }
    });
}

function display_error_field($target) {
    $target.addClass('not-validated');
    $target.find('.error-validating').text(lang_hotel_validation_msg);
}