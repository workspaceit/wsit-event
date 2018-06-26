$(function () {

    var $body = $('body');
    $body.on('change', '.session-agenda-group-toggle-list-item input[type="checkbox"]', function (e) {
        var $this_plugin = $(this).closest('.form-plugin-session-agenda');
        sessionAgendaFilter($this_plugin);
    });
    $body.on('change', '.session-agenda-my-session-toggle', function (e) {
        var $this_plugin = $(this).closest('.form-plugin-session-agenda');
        sessionAgendaFilter($this_plugin);
    });
    $body.on('keyup', '.page-search-session-agenda', function (e) {
        var $this_plugin = $(this).closest('.form-plugin-session-agenda');
        sessionAgendaFilter($this_plugin);
    });
    $body.on('click', '.session-agenda-today', function (e) {
        var date = new Date();
        var val = moment(date).format("MM/DD/YYYY");
        var text = moment(date).format("YYYY-MM-DD");
        var $this_span = $(this).closest('.session-agenda-date').find('.session-agenda-date-picker')
        getDateWithLanguage(text, $this_span);
    });
    $body.on('click', '.session-agenda-prev', function (e) {
        var $this_plugin = $(this).closest('.form-plugin-session-agenda');
        var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
        // date_range = date_range.split('-');
        var start_date = date_range.split("/");
        var date = new Date(start_date[2], start_date[0] - 1, start_date[1] - 1);
        var val = moment(date).format("MM/DD/YYYY");
        var text = moment(date).format("YYYY-MM-DD");
        var $this_span = $(this).closest('.session-agenda-date').find('.session-agenda-date-picker')
        getDateWithLanguage(text, $this_span);
    });
    $body.on('click', '.session-agenda-next', function (e) {
        var $this_plugin = $(this).closest('.form-plugin-session-agenda');
        var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
        var start_date = date_range.split("/");
        var date = new Date(start_date[2], start_date[0] - 1, parseInt(start_date[1]) + 1);
        var val = moment(date).format("MM/DD/YYYY");
        var text = moment(date).format("YYYY-MM-DD");
        var $this_span = $(this).closest('.session-agenda-date').find('.session-agenda-date-picker')
        getDateWithLanguage(text, $this_span);
    });
    


    // onLoadDateJs();

    var BoxId = '';
    // Show SESSION DETAIL POPUP

    $('body').on('click', '.session', function (e) {

        var id = $(this).data('id');
        //var box_id = $this.closest('.form-plugin-session-scheduler').find('.box_id').val();
        var box_id = $.trim($(this).attr('data-box-id'));
        BoxId = $(this).closest('.form-plugin').attr('id');
        //var page_id = $this.closest('.form-plugin-session-scheduler').find('.page_id').val();
        var page_id = $.trim($(this).attr('data-page-id'));
        var plugin_name = $(this).closest('.form-plugin').attr('data-name');
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/get-scheduler-session-details/',
            type: "POST",
            data: {
                box_id: box_id,
                page_id: page_id,
                session_id: id,
                plugin_name: plugin_name,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (result) {
                if (result.success) {
                    $('#dialoge').html(result.session_html);
                    $('#dialoge').removeClass("_visible").addClass("visible");
                }
            }
        });
    });


    //ATTEND OR NOT ATTEND
    $('body').on('change', '#attende-or-cancel-session input[type=checkbox]', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('.loader').show();
        var slider = $(this);
        var elm = $(this);
        var sessionId = $(this).attr('data-session-id');
        var currentStatus = $(this).attr('data-status');
        var type = 'unchecked'
        if (currentStatus == "not-attending") {
            type = "checked"
        } else if (currentStatus == "attending") {
            type = 'unchecked'
        } else if (currentStatus == "in-queue") {
            type = 'unchecked';
        } else if (currentStatus == "deciding") {
            type = 'unchecked';
        }
        var plugin_name = $("#" + BoxId).closest('.form-plugin').attr('data-name');
        var user_id = $("#" + BoxId).closest('.form-plugin').attr('data-uid');
        if (plugin_name == 'session-agenda') {
            var json = $("#" + BoxId).find('.agenda_settings_options').val();
            var options = JSON.parse(json);
            var session_option = options.session_agenda_session_available;
        } else {
            var json = $("#" + BoxId).find('.scheduler_settings_options').val();
            var options = JSON.parse(json);
            var session_option = options.session_scheduler_session_available;
        }
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            //session_id: sessionId,
            //session_option: session_option,
            //type: type,
            operation: type,
            session_id: sessionId,
            seats_option: session_option,
            temp_user_id: user_id,
            rebates: JSON.stringify([]),
            csrfmiddlewaretoken: csrfToken
        };
        slider.prop("disabled", true);
        $.ajax({
            //url: base_url + '/attend-or-cancel-session/',
            url: base_url + '/check-session-availability/',
            type: "POST",
            data: data,
            success: function (response) {
                console.log(response)
                $('.loader').hide();
                slider.prop("disabled", false);
                if (response.success) {
                    $('#attende-or-cancel-session').closest('.switch-wrapper').find('.session-slider-label').html(response.status_msg);
                    if (response.status == "full-queue-open") {
                        elm.attr('data-status', "not-attending");
                        $('#attende-or-cancel-session').closest('.session-details').find('.status').find('em').html(response.status_queue_open_msg);
                    } else {
                        elm.attr('data-status', response.status);
                        $('#attende-or-cancel-session').closest('.session-details').find('.status').find('em').html(response.status_msg);
                    }

                    if (response.seats_availability != undefined) {
                        $('#attende-or-cancel-session').closest('.session-details').find('.form-plugin-table').find('.seats-available').find('.available-seats').html(response.seats_availability);
                    }
                    $.growl.notice({message: response.message});
                    if (plugin_name == 'session-scheduler') {
                        var sc = scheduler.data("kendoScheduler");
                        sc.dataSource.read();
                        sc.view(sc.view().name);
                    } else if (plugin_name == 'session-agenda') {
                        var $this_plugin = $("#" + BoxId).closest('.form-plugin-session-agenda');
                        getSessionAgendaReload($this_plugin);
                    }
                }
            }
        });
    });
});

function getSessionAgenda($this_plugin) {
    var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
    var all_dates = $this_plugin.find('.session-agenda-table').data('all-date');
    if (jQuery.inArray(date_range, all_dates) !== -1) {
        sessionAgendaFilter($this_plugin);
    } else {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var settings = $this_plugin.find('.agenda_settings_options').val();
        var page_id = $this_plugin.find('.page_id').val();
        var box_id = $this_plugin.find('.box_id').val();
        var element_id = $this_plugin.attr('data-id');
        var data = {
            "page_id": page_id,
            "box_id": box_id,
            "element_id": element_id,
            "date_range": date_range,
            "settings": settings,
            "csrfmiddlewaretoken": csrf_token
        }
        $('.loader').show();
        $.ajax({
            url: base_url + '/get-session-agenda-filtered-data/',
            type: 'POST',
            data: data,
            success: function (res) {
                if (res.success) {
                    all_dates.push(date_range);
                    $this_plugin.find('.session-agenda-table').attr('data-all-date', all_dates);
                    $this_plugin.find('.session-agenda-table').find('tbody').append(res.session_agenda_list);
                    sessionAgendaFilter($this_plugin);
                    $('.loader').hide();
                }
            }
        });
    }
}

function getSessionAgendaReload($this_plugin) {
    var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
    var all_dates = $this_plugin.find('.session-agenda-table').data('all-date');
    all_dates = jQuery.grep(all_dates, function (value) {
        return value != date_range;
    });
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var settings = $this_plugin.find('.agenda_settings_options').val();
    var page_id = $this_plugin.find('.page_id').val();
    var box_id = $this_plugin.find('.box_id').val();
    var element_id = $this_plugin.attr('data-id');
    var data = {
        "page_id": page_id,
        "box_id": box_id,
        "element_id": element_id,
        "date_range": date_range,
        "settings": settings,
        "csrfmiddlewaretoken": csrf_token
    }
    $('.loader').show();
    $.ajax({
        url: base_url + '/get-session-agenda-filtered-data/',
        type: 'POST',
        data: data,
        success: function (res) {
            if (res.success) {
                all_dates.push(date_range);
                var removed_item = '[data-start="' + date_range + '"]';
                $this_plugin.find('.session-agenda-table').find('tbody tr').filter(removed_item).remove();
                $this_plugin.find('.session-agenda-table').attr('data-all-date', all_dates);
                $this_plugin.find('.session-agenda-table').find('tbody').append(res.session_agenda_list);
                sessionAgendaFilter($this_plugin);
                $('.loader').hide();
            }
        }
    });
}

function onLoadDateJs() {
    $body.find('.form-plugin-session-agenda').each(function () {
        var settings = $(this).find('.agenda_settings_options').val();
        var options = JSON.parse(settings);
        var range_start_date = options.session_agenda_date_range_start;
        var range_end_date = options.session_agenda_date_range_end;
        var start_date = range_start_date.split("-");
        var date_range_start_at = new Date(start_date[0], start_date[1] - 1, start_date[2]);
        var end_date = range_end_date.split("-");
        var date_range_end_at = new Date(end_date[0], end_date[1] - 1, end_date[2]);

        $(this).find('.session-agenda-date-picker').pickadate({
            // selectYears: true,
            // selectMonths: true,
            min: date_range_start_at,
            max: date_range_end_at,
            onSet: function (e) {
                var val = this.get();
                var formated_val = moment(val).format("MM/DD/YYYY");
                var $this_plugin = this.$node.closest('.form-plugin-session-agenda');
                $this_plugin.find('.session-agenda-date-range').attr('data-date-range', formated_val);
                getSessionAgenda($this_plugin);

            }
        });
    })
    // }

}

function getDateWithLanguage(text_date, $this_span) {
    var converted_date = global_getDateWithLanguage(text_date);
    // var $input2 = $('.session-agenda-date-picker');
    var picker = $this_span.pickadate('picker');
    picker.set('select', $.trim(converted_date));
    // $this_span.val($.trim(converted_date));
}

function sessionAgendaFilter($this_plugin) {
    $this_plugin.find('.form-plugin-table tbody tr').hide();
    var search_key = '';
    var search_data = $this_plugin.find('.page-search-session-agenda').val();
    if (search_data != undefined) {
        search_key = $.trim(search_data);
    }
    var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
    var groups = $.map($this_plugin.find('.session-agenda-group-toggle-list-item').find('input[type="checkbox"]:checked'), function (checkbox) {
        return parseInt($(checkbox).val());
    });
    var my_session = false;
    if ($this_plugin.find('.session-agenda-my-session-toggle').is(':checked')) {
        my_session = true;
    }
    var all_tr = $this_plugin.find('.form-plugin-table tbody tr');
    if (my_session) {
        all_tr = $this_plugin.find('.form-plugin-table tbody tr.attending');
    }
    if ($this_plugin.find('.session-agenda-group-toggle-list').length > 0) {
        for (var i = 0; i < groups.length; i++) {
            all_tr.each(function () {
                var found_session = false;
                var $this_tr = $(this);
                var group_class = 'session-group-' + groups[i];
                if ($this_tr.attr('data-start') == date_range && $this_tr.hasClass(group_class)) {
                    if (search_key != '') {
                        $this_tr.find('.session-agenda-searchable-property').each(function () {
                            if ($(this).text().toUpperCase().indexOf(search_key.toUpperCase()) != -1) {
                                found_session = true;
                            }
                        });
                    } else {
                        found_session = true;
                    }
                }
                if (found_session) {
                    $this_tr.show();
                }
            });
        }
    } else {
        all_tr.each(function () {
            var found_session = false;
            var $this_tr = $(this);
            if ($this_tr.attr('data-start') == date_range) {
                if (search_key != '') {
                    $this_tr.find('.session-agenda-searchable-property').each(function () {
                        if ($(this).text().toUpperCase().indexOf(search_key.toUpperCase()) != -1) {
                            found_session = true;
                        }
                    });
                } else {
                    found_session = true;
                }
            }
            if (found_session) {
                $this_tr.show();
            }
        });
    }
    if ($this_plugin.find('.form-plugin-table tbody tr:visible').length == 0) {
        $this_plugin.find('.empty-session-agenda-table').show();
    } else {
        $this_plugin.find('.empty-session-agenda-table').hide();
    }

}
