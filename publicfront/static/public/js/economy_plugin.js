function economy_add_to_order($element, item_type, item_id) {
    var item_detail = JSON.parse($element.closest('td').find('.session-cost-detail').val());
    // var rebates = $element.closest('.section-box').find('.order-rebate-to-apply').val();
    var rebates = $('.order-rebate-to-apply').val();
    if (rebates != undefined && rebates != '') {
        rebates = JSON.parse(rebates);
        if (item_type == 'session') {
            economy_data.sessions.push(item_id);
            if(rebates.prerequisite){
                clog(rebates.prerequisite);
            } else {
                var rebate_index = $.inArray(item_id, rebates.session_ids);
                if (rebate_index != -1) {
                    var new_rebate_flag = true;
                    for (var i_n_r_f = 0; i_n_r_f < economy_data.rebates.length; i_n_r_f++) {
                        if (economy_data.rebates[i_n_r_f].rebate_id == rebates.rebates.sessions[rebate_index].rebate_id && economy_data.rebates[i_n_r_f].item_type == item_type && economy_data.rebates[i_n_r_f].rebate_for == item_id) {
                            new_rebate_flag = false;
                            break;
                        }
                    }
                    if (new_rebate_flag) {
                        economy_data.rebates.push({
                            'rebate_id': rebates.rebates.sessions[rebate_index].rebate_id,
                            'item_type': item_type,
                            'rebate_for': item_id
                        });
                    }
                    var item_actual_cost = item_detail.cost;
                    item_detail = apply_rebate_amount(item_detail, rebates.rebates.sessions[rebate_index]);
                    if ($('.event-plugin-economy').length == 0) {
                        return;
                    }
                    // add_order_table_row($element, item_type, item_detail, 0);
                    var info_for_rebate = {
                        'item_cost': item_detail.cost,
                        'item_type': item_type,
                        'item_id': item_id,
                        'actual_cost': item_actual_cost
                    };
                    // add_order_table_row($element, 'rebate', rebates.rebates.sessions[rebate_index], info_for_rebate);
                } else {
                    // add_order_table_row($element, item_type, item_detail, 0);
                }
            }
        }
    } else {
        if (item_type == 'session') {
            economy_data.sessions.push(item_id);
            if($('.event-plugin-economy').length == 0){
                return;
            }
            // add_order_table_row($element, item_type, item_detail, 0);
        }
    }

}

function apply_rebate_amount(item_detail, rebate) {
    if (rebate.rebate_type == 'percentage') {
        item_detail.cost = item_detail.cost - (rebate.value / 100) * item_detail.cost;
    } else {
        item_detail.cost -= rebate.value;
    }
    item_detail.vat_amount = (item_detail.vat_rate / 100) * item_detail.cost;
    item_detail.total_cost = (item_detail.vat_rate / 100) * item_detail.cost + item_detail.cost;
    return item_detail;
}

function add_order_table_row($element, item_type, item_detail, info_for_rebate) {
    var $table, order_attendee_checker = $element.closest('.section-box').find('.economy-order-table').find('.data-economy-attendee-id').val();
    $element.closest('.section-box').find('.event-plugin-economy-order-table').each(function () {
        //// need to check which order table is for the logged in attedee's (neede when group order)
        if ($(this).attr('data-order-status') == 'open' && $(this).attr('data-order-attendee') == order_attendee_checker) {
            $table = $(this);
        }
    });
    if ($table == undefined) {
        var empty_order_table = $element.closest('.section-box').find('.empty-order-table').val();
        $element.closest('.section-box').find('.economy-order-table').append(empty_order_table);
        $table = $element.closest('.section-box').find('.economy-order-table').find('.event-plugin-economy-order-table:last');
        if (order_attendee_checker != undefined) {
            $table.attr('data-order-attendee', order_attendee_checker);
            $table.closest('.order-table-event-question').find('.data-economy-attendee-id').val(order_attendee_checker);
        }
    }
    var row, rebate_value, rebate_amount, economy_currency = $table.closest('.economy-order-table').find('.economy-text-lang-currency').val();
    var ot_visible_columns = JSON.parse($table.closest('.economy-order-table').find('.order-table-visible-columns').val());
    if (item_type == 'rebate') {
        if (item_detail.rebate_type == 'percentage') {
            rebate_value = '-' + item_detail.value + "%";
            rebate_amount = (parseFloat(item_detail.value) / 100) * info_for_rebate.actual_cost * (-1);
        } else {
            rebate_value = '-' + item_detail.value;
            rebate_amount = parseFloat(item_detail.value) * (-1);
        }
        row = "<tr data-item-type='" + item_type + "' data-rebate-amount='" + rebate_value + "' data-rebate-for-item-type='"
            + info_for_rebate.item_type + "' data-rebate-for-item-id='" + info_for_rebate.item_id + "'>";
            row += eval(ot_visible_columns.show_item_name) ? "<td>" + item_detail.name + "</td>" : "";
            row += eval(ot_visible_columns.show_cost_excl_vat) ? "<td></td>" : "";
            row += eval(ot_visible_columns.show_rebate_amount) ? "<td>" + rebate_value + " " + economy_currency + "</td>" : "";
            row += eval(ot_visible_columns.show_vat_amount) ? "<td></td>" : "";
            row += eval(ot_visible_columns.show_vat_rate) ? "<td></td>" : "";
            row += eval(ot_visible_columns.show_cost_incl_vat) ? "<td></td>" : "";
            row += "</tr>";

        // if ($table.find('.total_rebate_amount').text() != '') {
        //     $table.find('.total_rebate_amount').text(parseFloat($table.find('.total_rebate_amount').text()) + rebate_amount + " " + economy_currency);
        // } else {
        //     $table.find('.total_rebate_amount').text(rebate_amount + " " + economy_currency);
        // }
        var data_total_rebate_amount = parseFloat($table.find('.total_rebate_amount').attr('data-amount')) + rebate_amount;
        $table.find('.total_rebate_amount').text(data_total_rebate_amount + " " + economy_currency);
        $table.find('.total_rebate_amount').attr('data-amount', data_total_rebate_amount);
    } else {
        row = "<tr data-item-type='" + item_type + "' data-item-id='" + item_detail.id +
            "' data-item-cost='" + item_detail.cost + "' data-item-vat-amount='" + item_detail.vat_amount +
            "' data-item-cost-incl-vat='" + item_detail.total_cost + "' data-item-vat-rate='" + item_detail.vat_rate + "'>";
            row += eval(ot_visible_columns.show_item_name) ? "<td>" + item_detail.name + "</td>" : "";
            row += eval(ot_visible_columns.show_cost_excl_vat) ? "<td>" + item_detail.cost + " " + economy_currency + "</td>" : "";
            row += eval(ot_visible_columns.show_rebate_amount) ? "<td></td>" : "";
            row += eval(ot_visible_columns.show_vat_amount) ? "<td>" + item_detail.vat_amount + " " + economy_currency + "</td>" : "";
            row += eval(ot_visible_columns.show_vat_rate) ? "<td>" + item_detail.vat_rate + "%</td>" : "";
            row += eval(ot_visible_columns.show_cost_incl_vat) ? "<td>" + item_detail.total_cost + " " + economy_currency + "</td>" : "";
            row += "</tr>";

        // if ($table.find('.total_cost_exl_vat').text() != '') {
        //     $table.find('.total_cost_exl_vat').text(parseFloat($table.find('.total_cost_exl_vat').text()) + item_detail.cost + " " + economy_currency);
        // } else {
        //     $table.find('.total_cost_exl_vat').text(item_detail.cost + " " + economy_currency);
        // }

        // if ($table.find('.total_vat_amount').text() != '') {
        //     $table.find('.total_vat_amount').text(parseFloat($table.find('.total_vat_amount').text()) + item_detail.vat_amount + " " + economy_currency);
        // } else {
        //     $table.find('.total_vat_amount').text(item_detail.vat_amount + " " + economy_currency);
        // }

        // if ($table.find('.total_cost_incl_vat').text() != '') {
        //     $table.find('.total_cost_incl_vat').text(parseFloat($table.find('.total_cost_incl_vat').text()) + item_detail.total_cost + " " + economy_currency);
        // } else {
        //     $table.find('.total_cost_incl_vat').text(item_detail.total_cost + " " + economy_currency);
        // }

        var data_total_cost_exl_vat = parseFloat($table.find('.total_cost_exl_vat').attr('data-amount')) + item_detail.cost;
        $table.find('.total_cost_exl_vat').text(data_total_cost_exl_vat + " " + economy_currency);
        $table.find('.total_cost_exl_vat').attr('data-amount', data_total_cost_exl_vat);
        var data_total_vat_amount = parseFloat($table.find('.total_vat_amount').attr('data-amount')) + item_detail.vat_amount;
        $table.find('.total_vat_amount').text(data_total_vat_amount + " " + economy_currency);
        $table.find('.total_vat_amount').attr('data-amount', data_total_vat_amount);
        var data_total_cost_incl_vat = parseFloat($table.find('.total_cost_incl_vat').attr('data-amount')) + item_detail.total_cost;
        $table.find('.total_cost_incl_vat').text(data_total_cost_incl_vat + " " + economy_currency);
        $table.find('.total_cost_incl_vat').attr('data-amount', data_total_cost_incl_vat);


        var vat_adding_flag = true;
        var $vat_table = $table.closest('.order-table-event-question').find('.event-plugin-economy-vat-table');
        $vat_table.find('tbody tr').each(function () {
            var vat_rate = $(this).find('td:first').attr('data-vat-rate');
            if (vat_rate == item_detail.vat_rate) {
                var data_vat_amount = parseFloat($(this).find('td:last').attr('data-amount')) + item_detail.vat_amount;
                $(this).find('td:last').text(data_vat_amount + " " + economy_currency);
                $(this).find('td:last').attr('data-amount', data_vat_amount);
                // $(this).find('td:last').text(parseFloat($(this).find('td:last').text()) + item_detail.vat_amount + " " + economy_currency);
                vat_adding_flag = false;
            }
        });
        if (vat_adding_flag) {
            $vat_table.find('tbody').append('<tr><td data-vat-rate="'+item_detail.vat_rate+'">' + item_detail.vat_rate + '%</td> <td data-amount="'+item_detail.vat_amount+'">' + item_detail.vat_amount + " " + economy_currency + '</td></tr>');
        }
    }
    $table.find('tbody tr:last').before(row);

    //// for group order (group grand table update)
    var order_number = $table.attr('data-order-number');
    if (order_number != undefined) {
        var $group_grand_total_table = $('.group-order-' + order_number);
        if ($group_grand_total_table.length > 0) {
            if (item_type == 'rebate') {
                var data_group_total_rebate_amount = parseFloat($group_grand_total_table.find('.total_rebate_amount').attr('data-amount')) + rebate_amount;
                $group_grand_total_table.find('.total_rebate_amount').text(data_group_total_rebate_amount + " " + economy_currency);
                $group_grand_total_table.find('.total_rebate_amount').attr('data-amount', data_group_total_rebate_amount);
                // $group_grand_total_table.find('.total_rebate_amount').text(parseFloat($group_grand_total_table.find('.total_rebate_amount').text()) + rebate_amount + " " + economy_currency);
            } else {
                $group_grand_total_table.find('.total_cost_exl_vat').text(parseFloat($group_grand_total_table.find('.total_cost_exl_vat').text()) + item_detail.cost + " " + economy_currency);
                // $group_grand_total_table.find('.total_vat_amount').text(parseFloat($group_grand_total_table.find('.total_vat_amount').text()) + item_detail.vat_amount + " " + economy_currency);
                // $group_grand_total_table.find('.total_cost_incl_vat').text(parseFloat($group_grand_total_table.find('.total_cost_incl_vat').text()) + item_detail.total_cost + " " + economy_currency);

                var data_group_total_cost_exl_vat = parseFloat($group_grand_total_table.find('.total_cost_exl_vat').attr('data-amount')) + item_detail.cost;
                $group_grand_total_table.find('.total_cost_exl_vat').text(data_group_total_cost_exl_vat + " " + economy_currency);
                $group_grand_total_table.find('.total_cost_exl_vat').attr('data-amount', data_group_total_cost_exl_vat);
                var data_group_total_vat_amount = parseFloat($group_grand_total_table.find('.total_vat_amount').attr('data-amount')) + item_detail.vat_amount;
                $group_grand_total_table.find('.total_vat_amount').text(data_group_total_vat_amount + " " + economy_currency);
                $group_grand_total_table.find('.total_vat_amount').attr('data-amount', data_group_total_vat_amount);
                var data_group_total_cost_incl_vat = parseFloat($group_grand_total_table.find('.total_cost_incl_vat').attr('data-amount')) + item_detail.total_cost;
                $group_grand_total_table.find('.total_cost_incl_vat').text(data_group_total_cost_incl_vat + " " + economy_currency);
                $group_grand_total_table.find('.total_cost_incl_vat').attr('data-amount' ,data_group_total_cost_incl_vat);
            }
        }
    }
}

function economy_remove_item_from_economy($element, item_type, item_to_remove) {
    if (item_type == 'session') {
        var item_index = $.inArray(item_to_remove, economy_data.sessions);
        if (item_index != -1) {
            economy_data.sessions.splice(item_index, 1);
        }
        // DISPLAY OFF
        return;

        var $table, order_attendee_checker = $element.closest('.section-box').find('.economy-order-table').find('.data-economy-attendee-id').val();
        $element.closest('.section-box').find('.event-plugin-economy-order-table').each(function () {
            //// need to check which order table is for the logged in attedee's (neede when group order)
            if ($(this).attr('data-order-status') == 'open' && $(this).attr('data-order-attendee') == order_attendee_checker) {
                $table = $(this);
            }
        });
        //// no open order exists
        if ($table == undefined) {
            return;
        }
        var rebate_amount, total_cost_exl_vat, total_vat_amount, total_cost_incl_vat, rebate_exists = false;
        // for vat table
        var vat_rate_to_remove = 0, vat_amount_to_remove = 0, economy_currency = $table.closest('.economy-order-table').find('.economy-text-lang-currency').val();

        $table.find('tbody tr').each(function () {
            var tr_item_type = $(this).attr('data-item-type');
            if (tr_item_type != 'rebate') {
                if (tr_item_type == item_type && $(this).attr('data-item-id') == item_to_remove) {
                    total_cost_exl_vat = $(this).attr('data-item-cost');
                    total_vat_amount = $(this).attr('data-item-vat-amount');
                    total_cost_incl_vat = $(this).attr('data-item-cost-incl-vat');

                    // $(this).closest('tbody').find('.total_cost_exl_vat').text(parseFloat($(this).closest('tbody').find('.total_cost_exl_vat').text()) - total_cost_exl_vat + " " + economy_currency);
                    // $(this).closest('tbody').find('.total_vat_amount').text(parseFloat($(this).closest('tbody').find('.total_vat_amount').text()) - total_vat_amount + " " + economy_currency);
                    // $(this).closest('tbody').find('.total_cost_incl_vat').text(parseFloat($(this).closest('tbody').find('.total_cost_incl_vat').text()) - total_cost_incl_vat + " " + economy_currency);
                    var total_cost_exl_vat_element = $(this).closest('tbody').find('.total_cost_exl_vat');
                    var data_total_cost_exl_vat = parseFloat(total_cost_exl_vat_element.attr('data-amount')) - total_cost_exl_vat;
                    total_cost_exl_vat_element.text(data_total_cost_exl_vat + " " + economy_currency);
                    total_cost_exl_vat_element.attr('data-amount', data_total_cost_exl_vat);

                    var total_vat_amount_element = $(this).closest('tbody').find('.total_vat_amount');
                    var data_vat_amount = parseFloat(total_vat_amount_element.attr('data-amount')) - total_vat_amount;
                    total_vat_amount_element.text(data_vat_amount + " " + economy_currency);
                    total_vat_amount_element.attr('data-amount', data_vat_amount);

                    // $(this).closest('tbody').find('.total_cost_incl_vat').text(parseFloat($(this).closest('tbody').find('.total_cost_incl_vat').text()) - total_cost_incl_vat + " " + economy_currency);
                    var total_cost_incl_vat_element = $(this).closest('tbody').find('.total_cost_incl_vat');
                    var data_cost_incl_vat = parseFloat(total_cost_incl_vat_element.attr('data-amount')) - total_cost_incl_vat;
                    total_cost_incl_vat_element.text(data_cost_incl_vat + " " + economy_currency);
                    total_cost_incl_vat_element.attr('data-amount', data_cost_incl_vat);

                    vat_rate_to_remove = $(this).attr('data-item-vat-rate');
                    vat_amount_to_remove = total_vat_amount;

                    $(this).remove();
                }
            } else {
                if ($(this).attr('data-rebate-for-item-type') == item_type && $(this).attr('data-rebate-for-item-id') == item_to_remove) {
                    rebate_exists = true;
                    rebate_amount = Math.abs(parseFloat($(this).attr('data-rebate-amount')));
                    var rebate_item_element = $(this).closest('tbody').find('.total_rebate_amount');
                    var data_rebate_amount = parseFloat(rebate_item_element.attr('data-amount')) + rebate_amount;
                    rebate_item_element.text(data_rebate_amount + " " + economy_currency);
                    rebate_item_element.attr('data-amount', data_rebate_amount);
                    $(this).remove();
                }
            }
        });

        if (vat_rate_to_remove != 0 && vat_rate_to_remove != '') {
            $table.closest('.order-table-event-question').find('.event-plugin-economy-vat-table tbody tr').each(function () {
                if ($(this).find('td:first').attr('data-vat-rate') == vat_rate_to_remove) {
                    var remaining_vat_amount = parseFloat($(this).find('td:last').attr('data-amount')) - vat_amount_to_remove;
                    if (remaining_vat_amount == 0) {
                        $(this).remove();
                    } else {
                        $(this).find('td:last').text(remaining_vat_amount + " " + economy_currency);
                        $(this).find('td:last').attr('data-amount', remaining_vat_amount);
                    }
                }
            });
        }

        //// for group order (group grand table update)
        var order_number = $table.attr('data-order-number');
        if (order_number != undefined) {
            var $group_grand_total_table = $('.group-order-' + order_number);
            if ($group_grand_total_table.length > 0) {
                if (rebate_exists) {
                    // $group_grand_total_table.find('.total_rebate_amount').text(parseFloat($group_grand_total_table.find('.total_rebate_amount').text()) + rebate_amount + " " + economy_currency);
                    var data_group_total_rebate_amount = parseFloat($group_grand_total_table.find('.total_rebate_amount').attr('data-amount')) + rebate_amount;
                    $group_grand_total_table.find('.total_rebate_amount').text(data_group_total_rebate_amount + " " + economy_currency);
                    $group_grand_total_table.find('.total_rebate_amount').attr('data-amount', data_group_total_rebate_amount);
                }
                // $group_grand_total_table.find('.total_cost_exl_vat').text(parseFloat($group_grand_total_table.find('.total_cost_exl_vat').text()) - total_cost_exl_vat + " " + economy_currency);
                // $group_grand_total_table.find('.total_vat_amount').text(parseFloat($group_grand_total_table.find('.total_vat_amount').text()) - total_vat_amount + " " + economy_currency);
                // $group_grand_total_table.find('.total_cost_incl_vat').text(parseFloat($group_grand_total_table.find('.total_cost_incl_vat').text()) - total_cost_incl_vat + " " + economy_currency);

                var data_group_total_cost_exl_vat = parseFloat($group_grand_total_table.find('.total_cost_exl_vat').attr('data-amount')) - total_cost_exl_vat;
                $group_grand_total_table.find('.total_cost_exl_vat').text(data_group_total_cost_exl_vat + " " + economy_currency);
                $group_grand_total_table.find('.total_cost_exl_vat').attr('data-amount', data_group_total_cost_exl_vat);

                var data_group_total_vat_amount = parseFloat($group_grand_total_table.find('.total_vat_amount').attr('data-amount')) - total_vat_amount;
                $group_grand_total_table.find('.total_vat_amount').text(data_group_total_vat_amount + " " + economy_currency);
                $group_grand_total_table.find('.total_vat_amount').attr('data-amount', data_group_total_vat_amount);

                var data_group_total_cost_incl_vat = parseFloat($group_grand_total_table.find('.total_cost_incl_vat').attr('data-amount')) - total_cost_incl_vat;
                $group_grand_total_table.find('.total_cost_incl_vat').text(data_group_total_cost_incl_vat + " " + economy_currency);
                $group_grand_total_table.find('.total_cost_incl_vat').attr('data-amount', data_group_total_cost_incl_vat);
            }
        }
    }
}

function cleanEconomyData($section) {
    economy_data = {
        'sessions': [],
        'hotels': [],
        'travels': [],
        'rebates': [],
        'multiple': {'is_multiple': false, 'order_number': null}
    };
    // DISPLAY OFF
    // var order_table_grand_total_row = $('.order-table-grand-total-row').val();
    // $section.find('.event-plugin-economy-order-table tbody').empty();
    // $section.find('.event-plugin-economy-vat-table tbody').empty();
    // $section.find('.event-plugin-economy-order-table tbody').append(order_table_grand_total_row);
    // DISPLAY OFF
}

function add_ineffective_rebates() {
    var rebates = $('.order-rebate-to-apply').val();
    if (rebates != undefined && rebates != '') {
        rebates = JSON.parse(rebates);
        if(rebates.prerequisite){
            economy_data.rebate_type = 'filter';
            economy_data.rebates = rebates.prerequisite;
        } else {
            var new_rebate_flag;
            for (var r_i = 0; r_i < rebates.rebates.sessions.length; r_i++) {
                new_rebate_flag = true;
                for (var e_r_i = 0; e_r_i < economy_data.rebates.length; e_r_i++) {
                    if (economy_data.rebates[e_r_i].rebate_id == rebates.rebates.sessions[r_i].rebate_id && economy_data.rebates[e_r_i].item_type == 'session' && economy_data.rebates[e_r_i].rebate_for == rebates.rebates.sessions[r_i].session_id) {
                        new_rebate_flag = false;
                        break;
                    }
                }
                if (new_rebate_flag) {
                    economy_data.rebates.push({
                        'rebate_id': rebates.rebates.sessions[r_i].rebate_id,
                        'item_type': 'session',
                        'rebate_for': rebates.rebates.sessions[r_i].session_id
                    });
                }
            }
            for (var r_i = 0; r_i < rebates.rebates.rooms.length; r_i++) {
                economy_data.rebates.push({
                    'rebate_id': rebates.rebates.rooms[r_i].rebate_id,
                    'item_type': 'hotel',
                    'rebate_for': rebates.rebates.rooms[r_i].room_id
                });
            }
        }
    }
}

function rebate_for_session($element, item_id) {
    var rebates = $('.order-rebate-to-apply').val();
    if (rebates != undefined && rebates != '') {
        rebates = JSON.parse(rebates);
        if(rebates.prerequisite){
            return {rebate_type: 'filter', rebates: rebates.prerequisite};
        }else{
            var rebate_index = $.inArray(item_id, rebates.session_ids);
            if (rebate_index != -1) {
                var rebate_array = [{
                    'rebate_id': rebates.rebates.sessions[rebate_index].rebate_id,
                    'item_type': 'session',
                    'rebate_for': item_id
                }];
                return {rebate_type: 'date', rebates: rebate_array};
            }
        }
    }
    return {rebate_type: '', rebates: []};
}

function diplay_new_order_info($section, result) {
    var econ_item_count = economy_data.sessions.length + economy_data.hotels.length + economy_data.travels.length;
    var $order_table;
    $section.find('.event-plugin-economy-order-table').each(function () {
        if ($(this).attr('data-order-status') == 'open' && (econ_item_count > 0 || $(this).attr('data-order-number') == result.order_number)) {
            $order_table = $(this);
            return false;
        }
    });
    var economy_currency = $('.economy-text-lang-currency').val();
    if ($order_table != undefined) {
        // set order values to table
        $order_table.closest('.order-table-event-question').find('.data-economy-attendee-id').val(result.attendee_id);
        $order_table.attr('data-order-attendee', result.attendee_id);

        $order_table.closest('.order-table-event-question').find('.economy-order-number-value').html(result.order_number);
        $order_table.closest('.order-table-event-question').find('.economy-status-value').html(result.status_lang);
        var converted_date = global_getDateWithLanguage(result.due_date);
        $order_table.closest('.order-table-event-question').find('.economy-due-date-value').html(converted_date);

        $order_table.closest('.order-table-event-question').find('.change-order-status').attr('data-order-number', result.order_number);
        $order_table.closest('.order-table-event-question').find('.change-order-status').attr('data-order-id', result.id);
        $order_table.closest('.order-table-event-question').find('form').attr('id', 'form-' + result.order_id);

        $order_table.closest('.order-table-event-question').find('.settle-order-button').attr('data-order-number', result.order_number);
        $order_table.closest('.order-table-event-question').find('.settle-order-button').attr('data-order-id', result.order_id);

        // show fields
        $order_table.closest('.order-table-event-question').find('.economy-order-number').show();
        $order_table.closest('.order-table-event-question').find('.economy-status').show();
        if (result.status == 'open') {
            $order_table.closest('.order-table-event-question').find('.status-cahnge-element').show();
        } else if (result.status == 'pending') {
            $order_table.closest('.order-table-event-question').find('.economy-due-date').show();
            $order_table.closest('.order-table-event-question').find('.economy-amount-due-value').html(result.amount_due + ' ' + economy_currency);
            $order_table.closest('.order-table-event-question').find('.economy-amount-due').show();
            $order_table.closest('.order-table-event-question').find('.settle-order').show();
            $order_table.attr('data-order-status', result.status);
            $order_table.closest('.order-table-event-question').find('.status-cahnge-element').hide();
        }else if(result.status == 'paid') {
            $order_table.closest('.order-table-event-question').find('.economy-amount-due-value').html(result.amount_due + ' ' + economy_currency);
            $order_table.closest('.order-table-event-question').find('.economy-amount-due').show();
            $order_table.attr('data-order-status', result.status);
            $order_table.closest('.order-table-event-question').find('.status-cahnge-element').hide();
        }
    }
}

$(function () {
    $('body').on('click', '.change-order-status', function () {
        var $this = $(this);
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var order_id = $this.attr('data-order-id');
        var order_number = $this.attr('data-order-number');
        var show_pdf_button = $this.attr('data-show-pdf-button');
        var download_when_change_status = $this.attr('data-download') == "True" ? true : false;
        var economy_currency = $this.closest('.economy-order-table').find('.economy-text-lang-currency').val();
        $.ajax({
            url: base_url + '/economy-change-order-status/',
            type: "POST",
            data: {
                order_id: order_id,
                order_number: order_number,
                show_pdf_buttons: show_pdf_button,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.result) {
                    $this.closest('.order-table-event-question').find('.economy-status-value').html(response.order_info.status_lang);
                    if (response.order_info.status == 'pending') {
                        var converted_date = global_getDateWithLanguage(response.order_info.due_date);
                        $this.closest('.order-table-event-question').find('.economy-due-date-value').html(converted_date);
                        $this.closest('.order-table-event-question').find('.economy-due-date').show();
                        $this.closest('.order-table-event-question').find('.settle-order').show();
                        if(download_when_change_status){
                            window.location = base_url + "/economy-pdf-request?data=order-invoice&order_number=" + order_number;
                        }

                        // var settle_order_btn = $this.closest('.economy-order-table').find('.settle-order-button-html').val();
                        // $this.closest('.order-table-event-question').find('.settle-order').html(settle_order_btn);
                        // $this.closest('.order-table-event-question').find('.settle-order').find('.settle-order-button').attr('data-order-number', order_number);
                    } else if (response.order_info.status == 'paid') {
                        if(download_when_change_status) {
                            window.location = base_url + "/economy-pdf-request?data=receipt&order_number=" + order_number;
                        }
                    }
                    $this.closest('.order-table-event-question').find('.economy-amount-due-value').html(response.order_info.amount_due + ' ' + economy_currency);
                    $this.closest('.order-table-event-question').find('.economy-amount-due').show();
                    $(response.order_info.balance_table_html).insertBefore($this.closest('.order-table-event-question').find('.event-plugin-economy-order-table').closest('.scroll-x'));

                    var data_is_group_order = $this.attr('data-is-group-order');
                    if (data_is_group_order == undefined) {
                        $this.closest('.order-table-event-question').find('.event-plugin-economy-order-table').attr('data-order-status', response.order_info.status);
                    } else {
                        $this.closest('.order-table-event-question').find('.event-plugin-economy-order-table').attr('data-order-status', response.order_info.status);
                        $this.closest('.economy-order-table').find('.event-plugin-economy-order-table').each(function () {
                            if ($(this).attr('data-order-number') == order_number) {
                                $(this).attr('data-order-status', response.order_info.status);
                            }
                        })
                    }
                    $this.closest('.order-table-event-question').find('.status-cahnge-element').remove();
                    $.growl.notice({message: response.message});
                } else {
                    $.growl.warning({message: 'Something went wrong.'});
                }

            }
        });
    });

    $('body').on('click', '.economy-request-download-pdf, .generate-receipt-button, .generate-invoice-button', function (event) {
        var data_pdf = $(this).attr('data-pdf');
        var order_number = $(this).attr('data-order_number');
        if (data_pdf == 'order-invoice') {
            window.location = base_url + "/economy-pdf-request?data=order-invoice&order_number=" + order_number;
        }
        else if (data_pdf == 'receipt') {
            window.location = base_url + "/economy-pdf-request?data=receipt&order_number=" + order_number;
        }
        else if (data_pdf == 'credit-invoice') {
            window.location = base_url + "/economy-pdf-request?data=credit-invoice&order_number=" + order_number;
        }
    });

    $('body').on('click', '.settle-order-button', function () {
        var order_id = $(this).attr('data-order-id');
        var order_number = $(this).attr('data-order-number');
        var form = $("#form-" + order_id);

        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/get-order-info-for-payment/',
            type: "POST",
            data: {
                order_id: order_id,
                order_number: order_number,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.result) {

                    form.attr('action', response.action_url);

                    form.find('#accepturl').val(base_url + "/" + response.accept_url);
                    form.find('#acceptReturnUrl').val(base_url + "/" + response.accept_return_url);
                    form.find('#amount').val(response.amount);
                    form.find('#currency').val(response.currency);
                    form.find('#merchant').val(response.merchant);
                    form.find('#orderid').val(order_number);
                    form.find('#paytype').val(response.payment_types);
                    // form.find('#test').val(response.test);
                    form.find('#md5key').val(response.md5key);
                    form.find('#account').val(response.account);
                    form.find('#cancelurl').val(response.cancelurl);
                    // console.log(response)
                    form.submit();
                }
            }
        });

    });

});

