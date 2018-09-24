var previousSessions = [];
var previousSessionsActRadio = [];
var previousSessionsInQueueActRadio = [];
var temp_user_id = 'user_exists';
var temporary_attendee_expire_time, csrf_token;

function onLoadPluginSession() {
    csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    temporary_attendee_expire_time = $('.temporary_attendee_expire_time').val();

    if ($(".event-plugin-multiple-registration").length > 0) {
        economy_data.multiple.is_multiple = true;
    }

    $('body').find('.event-plugin-session-radio-button').each(function () {
        var $section = $(this);
        var box_id = $section.attr('id');
        previousSessions[box_id] = [];
        $section.find('.event-plugin-item').find('td:first').find('input').each(function () {
            if ($(this).prop('checked')) {
                var session_id = $(this).attr('data-session-id').split("_")[0];
                if ($.inArray(session_id, previousSessions[box_id]) == -1) {
                    previousSessions[box_id].push(session_id);
                }
            }
        });
    });

    $('body').find('.event-plugin-session-checkbox').each(function () {
        var $section = $(this);
        var act_like_radio = $section.attr('data-act-like-radio');
        if (act_like_radio == '1') {
            var box_id = $section.attr('id');
            var count_attending = $(this).find('.event-plugin-list').attr('data-count-attending');
            previousSessionsActRadio[box_id] = [];
            previousSessionsInQueueActRadio[box_id] = [];
            $section.find('.event-plugin-item').find('td:first').find('input').each(function () {
                if ($(this).prop('checked')) {
                    if (count_attending == 1 && $(this).parent().parent().hasClass('in-queue')) {
                        if ($(this).attr('data-session-id')) {
                            var session_id = $(this).attr('data-session-id').split("_")[0];
                            if ($.inArray(session_id, previousSessionsActRadio[box_id]) == -1) {
                                previousSessionsInQueueActRadio[box_id].push(session_id);
                            }
                        }
                    } else {
                        if ($(this).attr('data-session-id')) {
                            var session_id = $(this).attr('data-session-id').split("_")[0];
                            if ($.inArray(session_id, previousSessionsActRadio[box_id]) == -1) {
                                previousSessionsActRadio[box_id].push(session_id);
                            }
                        }
                    }
                }
            });
        }
    });
}

unchecked_box_elms = [];

//Session Agenda js

$(function () {

    var $body = $('body');
    $body.on('change', '.session-agenda-group-toggle-list-item input[type="checkbox"]', function (e) {
        var $this_plugin = $(this).closest('.event-plugin-session-agenda');
        sessionAgendaFilter($this_plugin);
    });
    $body.on('change', '.session-agenda-my-session-toggle', function (e) {
        var $this_plugin = $(this).closest('.event-plugin-session-agenda');
        sessionAgendaFilter($this_plugin);
    });
    $body.on('keyup', '.page-search-session-agenda', function (e) {
        var $this_plugin = $(this).closest('.event-plugin-session-agenda');
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
        if (!$(this).hasClass('disabled')) {
            var $this_plugin = $(this).closest('.event-plugin-session-agenda');
            var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
            // date_range = date_range.split('-');
            var start_date = date_range.split("/");
            var date = new Date(start_date[2], start_date[0] - 1, start_date[1] - 1);
            var val = moment(date).format("MM/DD/YYYY");
            var text = moment(date).format("YYYY-MM-DD");
            var $this_span = $(this).closest('.session-agenda-date').find('.session-agenda-date-picker');
            getDateWithLanguage(text, $this_span);
        }
    });
    $body.on('click', '.session-agenda-next', function (e) {
        if (!$(this).hasClass('disabled')) {
            var $this_plugin = $(this).closest('.event-plugin-session-agenda');
            var date_range = $this_plugin.find('.session-agenda-date-range').attr('data-date-range');
            var start_date = date_range.split("/");
            var date = new Date(start_date[2], start_date[0] - 1, parseInt(start_date[1]) + 1);
            var val = moment(date).format("MM/DD/YYYY");
            var text = moment(date).format("YYYY-MM-DD");
            var $this_span = $(this).closest('.session-agenda-date').find('.session-agenda-date-picker')
            getDateWithLanguage(text, $this_span);
        }
    });


    // onLoadDateJs();

    var BoxId = '';
    // Show SESSION DETAIL POPUP

    $('body').on('click', '.session', function (e) {
        var id = $(this).data('id');
        //var box_id = $this.closest('.event-plugin-session-scheduler').find('.box_id').val();
        var box_id = $.trim($(this).attr('data-box-id'));
        BoxId = $(this).closest('.event-plugin').attr('id');
        //var page_id = $this.closest('.event-plugin-session-scheduler').find('.page_id').val();
        var page_id = $.trim($(this).attr('data-page-id'));
        var plugin_name = $(this).closest('.event-plugin').attr('data-name');
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

    $('body').on('click', '.message-session-details', function (e) {
        var id = $(this).data('id');
        var data_status = $(this).data('status');
        var msg_elm = $(this).closest('.event-plugin-messages-message-wrapper').clone();
        var form_plugin_elm = $(this).closest('.event-plugin');
        var box_id = $.trim(form_plugin_elm.attr('data-box-id'));
        // BoxId = form_plugin_elm.attr('id');
        var page_id = $.trim(form_plugin_elm.attr('data-page-id'));
        var plugin_name = form_plugin_elm.attr('data-name');
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
                    if (data_status == 'deciding') {
                        $('#dialoge .switch-wrapper').append(msg_elm);
                        $('#dialoge .switch-wrapper .message-session-details').removeClass('message-session-details');
                        $('#dialoge .defaultCountdown').each(
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
                                var austDay = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
                                var endTime = moment(austDay);
                                setInterval(function () {
                                    var curTime = moment();
                                    if (curTime.isBefore(endTime)) {
                                        var diffTime = moment.duration(endTime.diff(curTime));
                                        var dHour = diffTime.hours();
                                        var dMinute = diffTime.minutes();
                                        var dSeconds = diffTime.seconds();
                                        self.html(dHour + " Hours, " + dMinute + " Minutes, " + dSeconds + " Seconds");
                                    }
                                }, 1000);
                            }
                        );
                    }
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
        var plugin_name = $("#" + BoxId).closest('.event-plugin').attr('data-name');
        var user_id = $("#" + BoxId).closest('.event-plugin').attr('data-uid');
        if (plugin_name == 'session-agenda') {
            var json = $("#" + BoxId).find('.agenda_settings_options').val();
            var options = JSON.parse(json);
            var session_option = options.session_agenda_session_available;
        } else if(plugin_name == 'session-scheduler'){
            var json = $("#" + BoxId).find('.scheduler_settings_options').val();
            var options = JSON.parse(json);
            var session_option = options.session_scheduler_session_available;
        }else{
            var session_option = 'x';
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
        var all_sessions = getAllSessionsId();
        data['all_sessions'] = JSON.stringify(all_sessions);
        $.ajax({
            //url: base_url + '/attend-or-cancel-session/',
            url: base_url + '/check-session-availability/',
            type: "POST",
            data: data,
            success: function (response) {
                $('.loader').hide();
                slider.prop("disabled", false);
                if (response.success) {
                    $('#attende-or-cancel-session').closest('.switch-wrapper').find('.session-slider-label').removeClass('not-attending attending');
                    $('#attende-or-cancel-session').closest('.switch-wrapper').find('.session-slider-label').addClass(response.status);
                    $('#attende-or-cancel-session').closest('.switch-wrapper').find('.session-slider-label').html(response.status_msg);
                    $('#attende-or-cancel-session').closest('.session-details-wrapper').find('.status').attr('class', 'status');
                    $('#attende-or-cancel-session').closest('.session-details-wrapper').find('.status').addClass(response.status);
                    $('#attende-or-cancel-session').attr('class', 'switch');
                    $('#attende-or-cancel-session').addClass(response.status);
                    if (response.status == "full-queue-open") {
                        elm.attr('data-status', "not-attending");
                        $('#attende-or-cancel-session').closest('.session-details-wrapper').find('.status').html(response.status_queue_open_msg);
                    } else {
                        elm.attr('data-status', response.status);
                        $('#attende-or-cancel-session').closest('.session-details-wrapper').find('.status').html(response.status_msg);
                    }

                    if (response.seats_availability != undefined) {
                        $('#attende-or-cancel-session').closest('.session-details-wrapper').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(response.seats_availability);
                    }
                    if (response.status == "attending" || response.status == "in-queue") {
                        $('#attende-or-cancel-session').addClass('active');
                    }
                    $.growl.notice({message: response.message});
                    if (plugin_name == 'session-scheduler') {
                        var sc = scheduler.data("kendoScheduler");
                        sc.dataSource.read();
                        sc.view(sc.view().name);
                    } else if (plugin_name == 'session-agenda') {
                        var $this_plugin = $("#" + BoxId).closest('.event-plugin-session-agenda');
                        getSessionAgendaReload($this_plugin);
                    }
                    if (response.sessions_info) {
                        updateSessionsInfo(response.sessions_info, temp_user_id);
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
    $body.find('.event-plugin-session-agenda').each(function () {
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
                var formated_val = moment(new Date(val)).format("MM/DD/YYYY");
                var $this_plugin = this.$node.closest('.event-plugin-session-agenda');
                $this_plugin.find('.session-agenda-date-range').attr('data-date-range', formated_val);
                var min_range = moment(date_range_start_at).format("MM/DD/YYYY");
                var max_range = moment(date_range_end_at).format("MM/DD/YYYY");
                $this_plugin.find('.session-agenda-prev').removeClass('disabled');
                $this_plugin.find('.session-agenda-next').removeClass('disabled');
                if (min_range == formated_val) {
                    $this_plugin.find('.session-agenda-prev').addClass('disabled');
                }
                if (max_range == formated_val) {
                    $this_plugin.find('.session-agenda-next').addClass('disabled');
                }
                var today_date = new Date();
                var nextDay = new Date(today_date);
                var prevDay = new Date(today_date);
                nextDay.setDate(today_date.getDate() + 1);
                prevDay.setDate(today_date.getDate() - 1);
                var today = moment(today_date).format('MM/DD/YYYY');
                var tomorrow = moment(nextDay).format('MM/DD/YYYY');
                var yesterday = moment(prevDay).format('MM/DD/YYYY');
                if (today == formated_val) {
                    this.$node.val(this.component.settings.today);
                } else if (tomorrow == formated_val) {
                    this.$node.val(this.component.settings.tomorrow);
                } else if (yesterday == formated_val) {
                    this.$node.val(this.component.settings.yesterday);
                }
                getSessionAgenda($this_plugin);

            }
        });
        var min_range = $(this).find('.session-agenda-date-picker').pickadate('picker').get('min', 'mm/dd/yyyy');
        var max_range = $(this).find('.session-agenda-date-picker').pickadate('picker').get('max', 'mm/dd/yyyy');
        var $date_button_div = $(this).find('.session-agenda-date-picker').closest('.session-agenda-date-range');
        var current_date = $date_button_div.attr('data-date-range');
        $date_button_div.find('.session-agenda-prev').removeClass('disabled');
        $date_button_div.find('.session-agenda-next').removeClass('disabled');
        if (min_range == current_date) {
            $date_button_div.find('.session-agenda-prev').addClass('disabled');
        }
        if (max_range == current_date) {
            $date_button_div.find('.session-agenda-next').addClass('disabled');
        }
        setAgendaTodayTomorrowYesterdayString($(this).find('.session-agenda-date-picker'), current_date);
    });
    // }

}

function setAgendaTodayTomorrowYesterdayString($this_span, current_date) {
    var picker = $this_span.pickadate('picker');
    // var $date_button_div = $this_span.closest('.session-agenda-date-range');
    // var current_date = $date_button_div.attr('data-date-range');
    var today_date = new Date();
    var nextDay = new Date(today_date);
    var prevDay = new Date(today_date);
    nextDay.setDate(today_date.getDate() + 1);
    prevDay.setDate(today_date.getDate() - 1);
    var today = moment(today_date).format('MM/DD/YYYY');
    var tomorrow = moment(nextDay).format('MM/DD/YYYY');
    var yesterday = moment(prevDay).format('MM/DD/YYYY');
    if (today == current_date) {
        var today_lang = $this_span.pickadate('picker').component.settings.today;
        $this_span.val(today_lang);
    } else if (tomorrow == current_date) {
        var tomorrow_lang = $this_span.pickadate('picker').component.settings.tomorrow;
        $this_span.val(tomorrow_lang);
    } else if (yesterday == current_date) {
        var yesterday_lang = $this_span.pickadate('picker').component.settings.yesterday;
        $this_span.val(yesterday_lang);
    }
}

function getDateWithLanguage(text_date, $this_span) {
    var converted_date = global_getDateWithLanguage(text_date);
    // var $input2 = $('.session-agenda-date-picker');
    var picker = $this_span.pickadate('picker');
    picker.set('select', $.trim(converted_date));
    // var today_lang = $this_span.pickadate('picker').component.settings.today;
    var min_range = $this_span.pickadate('picker').get('min', 'mm/dd/yyyy');
    var max_range = $this_span.pickadate('picker').get('max', 'mm/dd/yyyy');
    var $date_button_div = $this_span.closest('.session-agenda-date-range');
    var current_date = $date_button_div.attr('data-date-range');
    $date_button_div.find('.session-agenda-prev').removeClass('disabled');
    $date_button_div.find('.session-agenda-next').removeClass('disabled');
    if (min_range == current_date) {
        $date_button_div.find('.session-agenda-prev').addClass('disabled');
    }
    if (max_range == current_date) {
        $date_button_div.find('.session-agenda-next').addClass('disabled');
    }
    setAgendaTodayTomorrowYesterdayString($this_span, current_date);
}

function sessionAgendaFilter($this_plugin) {
    $this_plugin.find('.event-plugin-table tbody tr').hide();
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
    $this_plugin.find('.session-agenda-my-session-toggle').closest('.switch').removeClass('active');
    if ($this_plugin.find('.session-agenda-my-session-toggle').is(':checked')) {
        my_session = true;
        $this_plugin.find('.session-agenda-my-session-toggle').closest('.switch').addClass('active');
    }
    var all_tr = $this_plugin.find('.event-plugin-table tbody tr');
    if (my_session) {
        all_tr = $this_plugin.find('.event-plugin-table tbody tr.attending');
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
    if ($this_plugin.find('.event-plugin-table tbody tr:visible').length == 0) {
        $this_plugin.find('.empty-session-agenda-table').show();
    } else {
        $this_plugin.find('.empty-session-agenda-table').hide();
    }

}

// Details js

$(document).ready(function () {
    $('body').on('click', '#dialoge .dialoge-menu a', function () {
        var section = $(this).parent("li").attr("data-id");
        $("#dialoge .dialoge-menu li").removeClass("active");
        $(this).parent("li").addClass("active");
        $("#dialoge .section").hide();
        $("#dialoge .section[data-id='" + section + "']").show();
    });

    $('body').on('click', '.dialoge-menu-close-button', function (e) {
        e.stopPropagation();
        var closeSection = $(this).closest("li").attr("data-id");
        $(this).closest('.dialogue-content').find(".section[data-id='" + closeSection + "']").remove();
        $(this).closest("li").remove();
        if (!$("#dialoge .dialoge-menu").has("li").length) {
            $("#dialoge *").empty();
            $("#dialoge").removeClass("visible");
        } else {
            if (!$("#dialoge .dialoge-menu li").hasClass("active")) {
                $("#dialoge .dialoge-menu").find("li").first().addClass("active");
                var newSection = $("#dialoge .dialoge-menu .active").attr("data-id");
                $("#dialoge .section").hide();
                $("#dialoge .section[data-id='" + newSection + "']").show();
            } else {
                var newSection = $("#dialoge .dialoge-menu .active").attr("data-id");
                $("#dialoge .section").hide();
                $("#dialoge .section[data-id='" + newSection + "']").show();
            }

        }
    });

    $('#dialoge .dialoge-button-row').on('click', '.close-button', function () {
        var closeSection = $("#dialoge .dialoge-menu .active").attr("data-section");
        $("." + closeSection).remove();
        $("#dialoge .dialoge-menu .active").remove();
        $("#dialoge .dialoge-menu").find("li").first().addClass("active");
        var newSection = $("#dialoge .dialoge-menu .active").attr("data-section");
        $("#dialoge .section." + newSection).show();
        if (!$("#dialoge .dialoge-menu").has("li").length) {
            $("#dialoge *").empty();
            $("#dialoge").removeClass("visible");
        }
    });

    $('body').on('click', '.close-dialouge', function () {
        $("#dialoge *").empty();
        $("#dialoge").removeClass("visible");
    });

    function appendTab(title, name, resp, class_name) {
        $("#dialoge .dialoge-menu").append("<li data-section='" + class_name + "' data-id='" + name + "'><a>" + title + "<span class='dialoge-menu-close-button'></span></a></li>");
        $("#dialoge .dialogue-content").append("<div class='section " + class_name + "-wrapper " + class_name + "' data-id='" + name + "'>" + resp + "</div>");
        $("#dialoge .dialogue-content .section").not("[data-id='" + name + "']").hide();
        $("#dialoge .dialoge-menu li").removeClass("active");
        $("#dialoge .dialoge-menu li[data-id='" + name + "']").addClass("active");
        $("#dialoge .dialoge-menu").animate({scrollLeft: $("#dialoge .dialoge-menu").width()}, 250);
    }

    $('body').on('click', function (e) {
        if (!$(e.target).hasClass('o1pi09kjjsd')) {
            $('#dialoge').removeClass("visible").addClass("_visible");
        }
    });
    $('body').on('click', '#dialoge .dialoge-menu, #dialoge .section, #dialoge .dg-body-content', function (e) {
        e.stopPropagation();
        $('#dialoge').removeClass("_visible").addClass("visible");
    });

    var tempDivCounter = 0;

    $('body').on('click', '.location .location-details', function (event) {
        var $anchore = $(this);
        $('.submit-loader').show();
        var href = $anchore.attr('href');
        // $anchore.attr('href', 'javascript:void(0)');
        $anchore.prop("disabled", true);
        try {
            event.preventDefault();
            event.stopPropagation();
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var box_id = $.trim($(this).attr('data-box-id'));
            var page_id = $.trim($(this).attr('data-page-id'));
            var location_id = $.trim($(this).attr('data-location-id'));

            $.ajax({
                url: base_url + '/get-location-details/' + parseInt(location_id) + '/',
                type: "POST",
                data: {
                    box_id: box_id,
                    page_id: page_id,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function (resp) {

                    if ($('#dialoge').hasClass('visible')) {

                        // appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details, "location-details");
                        appendTab(resp.lang_details, "location-details" + tempDivCounter, resp.details, "location-details");
                        tempDivCounter = tempDivCounter + 1;
                    } else {

                        var html = "<div class='dialogue-content'><div class='dialogue-menu-wrapper'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div></div></div>";
                        $('#dialoge').html(html);
                        $('#dialoge').removeClass("_visible").addClass("visible");
                        appendTab(resp.lang_details, "location-details" + tempDivCounter, resp.details, "location-details");
                        tempDivCounter = tempDivCounter + 1;
                    }
                    $('.submit-loader').hide();
                    $anchore.prop("disabled", false);
                    // $anchore.attr('href', href);
                }
            });
        }
        catch (err) {
            console.log(err);
            $('.submit-loader').hide();
            $anchore.prop("disabled", false);
            // $anchore.attr('href', href);
        }
    });

    $('body').on('click', '.speaker .attendee-details', function (event) {
        var $anchore = $(this);
        $('.submit-loader').show();
        var href = $anchore.attr('href');
        // $anchore.attr('href', 'javascript:void(0)');
        $anchore.prop("disabled", true);
        try {
            event.preventDefault();
            event.stopPropagation();
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var box_id = $.trim($(this).attr('data-box-id'));
            var page_id = $.trim($(this).attr('data-page-id'));
            var attendee_id = $.trim($(this).attr('data-attendee-id'));

            $.ajax({
                url: base_url + '/get-attendee-details/' + parseInt(attendee_id) + '/',
                type: "POST",
                data: {
                    box_id: box_id,
                    page_id: page_id,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function (resp) {

                    if ($('#dialoge').hasClass('visible')) {

                        // appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details, "attendee-details");
                        appendTab(resp.lang_details, "attendee-details" + tempDivCounter, resp.details, "attendee-details");
                        tempDivCounter = tempDivCounter + 1;
                    } else {

                        var html = "<div class='dialogue-content'><div class='dialogue-menu-wrapper'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div></div></div>"
                        $('#dialoge').html(html);
                        $('#dialoge').removeClass("_visible").addClass("visible");
                        appendTab(resp.lang_details, "attendee-details" + tempDivCounter, resp.details, "attendee-details");
                        tempDivCounter = tempDivCounter + 1;
                    }
                    $('.submit-loader').hide();
                    $anchore.prop("disabled", false);
                    // $anchore.attr('href', href);
                }
            });
        }
        catch (err) {
            console.log(err);
            $('.submit-loader').hide();
            $anchore.prop("disabled", false);
            // $anchore.attr('href', href);
        }
    });
});

function uncheck_others($this, pre_id, previous_check_value, post_id, result, box_id, session_id, previous_sessions_content_seats_availability) {
    for (var i = 0; i <= previous_check_value.length; i++) {
        if ($('#' + pre_id + previous_check_value[i] + post_id)) {
            var previous_elm = $('#' + pre_id + previous_check_value[i] + post_id);
            // if ($this.attr('data-session-id').split("_")[0] != previous_check_value[i]) {
            //     previous_elm.attr('data-checked', false);
            //     previous_elm.attr('checked', false);
            // }
            // previous_elm.closest('tr').removeClass('not-attending not-answerd attending in-queue');
            // previous_elm.closest('tr').find('.status').removeClass('not-attending not-answerd attending in-queue');
            // previous_elm.closest('tr').addClass('not-attending');
            // previous_elm.closest('tr').find('.status').addClass('not-attending');
            // previous_elm.closest('tr').find('.status').html('');
            economy_remove_item_from_economy($this, 'session', previous_check_value[i]);
            if (previous_sessions_content_seats_availability != undefined && previous_sessions_content_seats_availability[previous_check_value[i]] != undefined) {
                previous_elm.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(previous_sessions_content_seats_availability[previous_check_value[i]]);
                if (parseInt(previous_sessions_content_seats_availability[previous_check_value[i]]) > 0) {
                    if ($('#temporary-checkbox-' + box_id.split('-')[1] + '-id-' + previous_check_value[i]).prop('disabled')) {
                        $('#temporary-checkbox-' + box_id.split('-')[1] + '-id-' + previous_check_value[i]).prop('disabled', false);
                    }

                }
            }
        }


        economy_add_to_order($this, 'session', session_id);
        if (economy_data.multiple.is_multiple && result.order_number != null && result.order_number != 'None') {
            economy_data.multiple.order_number = result.order_number;
        }
        previousSessionsActRadio[box_id] = [];
        previousSessionsActRadio[box_id][0] = session_id;
    }
}

// Plugin Session js
$(function () {
    // onLoadPluginSession();
    // session availability check (when user select session)
    $('body').on('click', '.session-check-availability', function (e) {
        var data;
        var $this = $(this);
        if (!$this.hasClass('disabled')) {
            console.log("e.currentTarget.checked");
            var data_checked = $(this).attr('data-checked');
            var target_checked = true;
            console.log(data_checked);
            if (data_checked == 'true') {
                target_checked = false;
            }
            //var $this_section = $this.closest('.event-plugin-list').closest('.section-box');
            if (validateMaxSessionCheckbox($this, target_checked)) {
                $this.closest('.event-plugin-session-checkbox').removeClass('not-validated');
                var seats_option = $this.closest('.event-plugin-list').attr('data-seats-option');
                var $status_elm = $this.closest('tr').find('.status');
                // if ($('#hidden_secret').val() == undefined) {
                temp_user_id = get_temp_user_id($this, 'checkbox');
                // }
                var session_id = $this.attr('data-session-id').split("_")[0];
                var operation_unchecked = false;
                if (target_checked) {
                    unchecked_box_elms.remove($this.attr('id'));
                    var rebate_details = rebate_for_session($(this), session_id);
                    data = {
                        operation: 'checked',
                        session_id: session_id,
                        seats_option: seats_option,
                        temp_user_id: temp_user_id,
                        rebate_type: rebate_details.rebate_type,
                        rebates: JSON.stringify(rebate_details.rebates),
                        order_number: economy_data.multiple.order_number,
                        csrfmiddlewaretoken: csrf_token
                    };
                } else {
                    unchecked_box_elms.push($this.attr('id'));
                    operation_unchecked = true;
                    data = {
                        operation: 'unchecked',
                        session_id: session_id,
                        seats_option: seats_option,
                        temp_user_id: temp_user_id,
                        csrfmiddlewaretoken: csrf_token
                    };
                }
                var all_sessions = getAllSessionsId();
                data['all_sessions'] = JSON.stringify(all_sessions);
                $.ajax({
                    url: base_url + '/check-session-availability/',
                    type: "POST",
                    data: data,
                    async: false,
                    success: function (result) {
                        if (result.success) {
                            $this.closest('tr').removeClass('not-attending not-answered attending in-queue time-conflict');
                            $status_elm.removeClass('not-attending not-answered attending in-queue time-conflict');
                            $this.closest('tr').addClass(result.status);
                            $status_elm.addClass(result.status);
                            $status_elm.html(result.status_msg);
                            if (result.result) {
                                if (e.originalEvent != undefined) {
                                    $.growl.notice({message: result.message});
                                }
                                $this.attr('data-checked', true);
                                if (result.status == 'attending') {
                                    economy_add_to_order($this, 'session', session_id);
                                    if (economy_data.multiple.is_multiple && result.order_number != null && result.order_number != 'None') {
                                        economy_data.multiple.order_number = result.order_number;
                                    }
                                }
                            } else {
                                if (e.originalEvent != undefined) {
                                    $.growl.warning({message: result.message});
                                }
                                $this.prop('checked', false);
                                $this.attr('data-checked', false);
                                if (result.status == 'not-attending') {
                                    $this.closest('tr').addClass(result.status);
                                    $status_elm.addClass(result.status);
                                    $status_elm.html(result.status_msg);
                                }
                                if (operation_unchecked) {
                                    economy_remove_item_from_economy($this, 'session', session_id);
                                    if (result.download_flag) {
                                        window.location = base_url + "/economy-pdf-request?uid=" + result.user_id + "&data=credit-invoice&order_number=" + result.order_number;
                                    }
                                }
                            }
                            if (temp_user_id == 'new') {
                                $this.closest('.section').find('.temporary-user-id-for-reg').val(result.temp_user_id);
                                temp_user_id = result.temp_user_id;
                                attendee_timeout_worker(result.temp_user_id, $this.closest('.section'));
                            }
                            if (result.seats_availability != undefined) {
                                $this.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(result.seats_availability);
                            }
                            // if (!$status_elm.is(':visible')) {
                            if (result.status != 'not-attending' && result.status != 'not-answered') {
                                $status_elm.show();
                            } else {
                                $status_elm.hide();
                            }
                            if (result.sessions_info) {
                                updateSessionsInfo(result.sessions_info, temp_user_id);
                            }
                            // }
                        }
                    }
                });
            } else {
                if ($('.not-validated:visible:first').length > 0) {
                    $('html, body').animate({
                        scrollTop: $('.not-validated:visible:first').offset().top
                    }, 300);
                }
                return false;
            }
        } else {
            return false;
        }
    });


    $('body').on('click', '.session-check-availability-act-radio', function (e) {
        var data;
        var $this = $(this);
        console.log("=================================================");

        var box_id = $this.closest('.event-plugin-session-checkbox').attr('id');
        var previous_check_value = [];


        if (previousSessionsActRadio[box_id].length > 0) {
            previous_check_value = previousSessionsActRadio[box_id];

        }

        var count_attending = $this.closest('.event-plugin-list').attr('data-count-attending');
        if (!$this.hasClass('disabled')) {

            var data_checked = $(this).attr('data-checked');
            var target_checked = true;

            if (data_checked == 'true') {
                target_checked = false;
            }
            var id_of_this = $this.attr('id');

            var id_split = id_of_this.split("-")
            var pre_id = id_split[0] + '-' + id_split[1] + '-' + id_split[2] + '-' + id_split[3] + '-'
            var post_id = '-' + id_split[5];


            var session_id = $this.attr('data-session-id').split("_")[0];
            //var $this_section = $this.closest('.event-plugin-list').closest('.section-box');
            if (must_choose_one_session($this) && !(previous_check_value.indexOf(session_id.toString()) == -1) && (previous_check_value.length == 1)) {
                return false;
            } else {
                $this.closest('.event-plugin-session-checkbox').removeClass('not-validated');
                var seats_option = $this.closest('.event-plugin-list').attr('data-seats-option');
                var $status_elm = $this.closest('tr').find('.status');
                var conflict_session_setting = $this.closest('.event-plugin-session-checkbox').attr('data-conflict-session');
                // if ($('#hidden_secret').val() == undefined) {
                temp_user_id = get_temp_user_id($this, 'checkbox');
                // }
                var operation_unchecked = false;
                if (target_checked) {
                    unchecked_box_elms.remove($this.attr('id'));
                    var rebate_details = rebate_for_session($(this), session_id);
                    data = {
                        operation: 'radio',
                        session_id: session_id,
                        previous_id: previous_check_value,
                        seats_option: seats_option,
                        count_attending: count_attending,
                        temp_user_id: temp_user_id,
                        rebate_type: rebate_details.rebate_type,
                        rebates: JSON.stringify(rebate_details.rebates),
                        order_number: economy_data.multiple.order_number,
                        conflict_session_setting: conflict_session_setting,
                        csrfmiddlewaretoken: csrf_token
                    };
                } else {
                    unchecked_box_elms.push($this.attr('id'));
                    operation_unchecked = true;
                    data = {
                        operation: 'unchecked',
                        session_id: session_id,
                        seats_option: seats_option,
                        temp_user_id: temp_user_id,
                        csrfmiddlewaretoken: csrf_token
                    };
                }
                var all_sessions = getAllSessionsId();
                data['all_sessions'] = JSON.stringify(all_sessions);

                $.ajax({
                        url: base_url + '/check-session-availability-act-radio/',
                        type: "POST",
                        data: data,
                        async: false,
                        success: function (result) {
                            if (result.success) {
                                var previous_sessions_content_seats_availability = result.previous_sessions_content_seats_availability;
                                var previous_sessions_content_status_msg = result.previous_sessions_content_status_msg;

                                // $this.closest('tr').removeClass('not-attending not-answered attending in-queue');
                                // $status_elm.removeClass('not-attending not-answered attending in-queue');
                                // if (result.result) {
                                //     for (var i = 0; i <= previous_check_value.length; i++) {
                                //         console.log(i);
                                //         console.log(previous_check_value[i]);
                                //
                                //
                                //     }
                                // }
                                // $this.closest('tr').addClass(result.status);
                                // $status_elm.addClass(result.status);
                                // $status_elm.html(result.status_msg);
                                // $this.attr('data-checked', true);

                                if (result.status == 'attending') {
                                    uncheck_others($this, pre_id, previous_check_value, post_id, result, box_id, session_id, previous_sessions_content_seats_availability);
                                    if (e.originalEvent != undefined) {
                                        $.growl.notice({message: result.message});
                                    }
                                } else {

                                    // $this.prop('checked', false);
                                    // $this.attr('data-checked', false);
                                    if (result.status == 'not-attending') {
                                        previousSessionsActRadio[box_id].remove(session_id);
                                        // $this.closest('tr').addClass(result.status);
                                        // $status_elm.addClass(result.status);
                                        // $status_elm.html(result.status_msg);
                                        if (e.originalEvent != undefined) {
                                            $.growl.warning({message: result.message});
                                        }
                                    }
                                    if (result.status == 'in-queue') {

                                        // $this.prop('checked', true);
                                        // $this.attr('data-checked', true);
                                        if (count_attending == "0") {
                                            uncheck_others($this, pre_id, previous_check_value, post_id, result, box_id, session_id, previous_sessions_content_seats_availability);
                                        }
                                        // $this.closest('tr').addClass(result.status);
                                        // $status_elm.addClass(result.status);
                                        // $status_elm.html(result.status_msg);

                                        if (e.originalEvent != undefined) {
                                            $.growl.notice({message: result.message});
                                        }
                                    }
                                    if (result.status == "full-queue-open") {
                                        // $status_elm.addClass(result.status);
                                        // $status_elm.html(result.status_queue_open_msg);
                                        if (e.originalEvent != undefined) {
                                            $.growl.warning({message: result.message});
                                        }
                                    }
                                    if (operation_unchecked) {
                                        economy_remove_item_from_economy($this, 'session', session_id);
                                        if (result.download_flag) {
                                            window.location = base_url + "/economy-pdf-request?uid=" + result.user_id + "&data=credit-invoice&order_number=" + result.order_number;
                                        }
                                        // if (e.originalEvent != undefined) {
                                        //     $.growl.warning({message: result.message});
                                        // }
                                    }

                                }
                                if (temp_user_id == 'new') {
                                    $this.closest('.section').find('.temporary-user-id-for-reg').val(result.temp_user_id);
                                    temp_user_id = result.temp_user_id;
                                    attendee_timeout_worker(result.temp_user_id, $this.closest('.section'));
                                }
                                if (result.seats_availability != undefined) {
                                    $this.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(result.seats_availability);
                                }
                                // if (result.previous_session_seats_availability != undefined) {
                                //     $('#temporary-checkbox-' + box_id.split('-')[1] + '-id-' + previous_check_value).closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(result.previous_session_seats_availability);
                                //     if (result.previous_session_seats_availability > 0) {
                                //         if ($('#temporary-checkbox-' + box_id.split('-')[1] + '-id-' + previous_check_value).prop('disabled')) {
                                //             $('#temporary-checkbox-' + box_id.split('-')[1] + '-id-' + previous_check_value).prop('disabled', false);
                                //         }
                                //
                                //     }
                                // }

                                // if (!$status_elm.is(':visible')) {
                                if (result.status != 'not-attending' && result.status != 'not-answered') {
                                    $status_elm.show();

                                } else {
                                    $status_elm.hide();
                                }
                                if (result.sessions_info) {
                                    updateSessionsInfo(result.sessions_info, temp_user_id);
                                }

                                // }
                            }
                        }
                    }
                );

            }
        }
        else {
            console.log("=================================================false");
            return false;
        }
    });

    $('body').on('change', '.session-radio-availability', function (e) {
        var $this = $(this);
        var box_id = $this.closest('.event-plugin-session-radio-button').attr('id');
        var previous_radio_value = 0;
        if (previousSessions[box_id].length > 0) {
            previous_radio_value = previousSessions[box_id][0];
        }
        var seats_option = $this.closest('.event-plugin-list').attr('data-seats-option');
        var $status_elm = $this.closest('tr').find('.status');
        temp_user_id = get_temp_user_id($this, 'radio');
        var session_id = $this.attr('data-session-id').split("_")[0];
        session_id = session_id.trim();
        var rebate_details = rebate_for_session($(this), session_id);
        var data = {
            operation: 'radio',
            session_id: session_id,
            previous_id: previous_radio_value,
            seats_option: seats_option,
            temp_user_id: temp_user_id,
            rebate_type: rebate_details.rebate_type,
            rebates: JSON.stringify(rebate_details.rebates),
            order_number: economy_data.multiple.order_number,
            csrfmiddlewaretoken: csrf_token
        }
        var all_sessions = getAllSessionsId();
        data['all_sessions'] = JSON.stringify(all_sessions);
        if (previous_radio_value != session_id) {
            $.ajax({
                url: base_url + '/check-session-availability/',
                type: "POST",
                data: data,
                async: false,
                success: function (result) {
                    if (result.success) {
                        $this.closest('tr').removeClass('not-attending not-answerd attending in-queue');
                        $status_elm.removeClass('not-attending not-answerd attending in-queue');
                        if (result.result) {
                            if (e.originalEvent != undefined) {
                                $.growl.notice({message: result.message});
                            }
                            $this.closest('tr').addClass(result.status);
                            $status_elm.addClass(result.status);
                            //$status_elm.html(result.status_msg);
                            if (result.status == 'attending') {
                                if (previous_radio_value != 0) {
                                    var user_id = $this.attr('data-session-id').split("_")[1];
                                    var elm_box_id = box_id.split("-")[3]
                                    var previous_elm = $('#temporary-radio-' + elm_box_id + '-id-' + previous_radio_value + '-' + user_id + '');
                                    previous_elm.closest('tr').removeClass('not-attending not-answerd attending in-queue');
                                    previous_elm.closest('tr').find('.status').removeClass('not-attending not-answerd attending in-queue');
                                    previous_elm.closest('tr').addClass('not-attending');
                                    previous_elm.closest('tr').find('.status').addClass('not-attending');
                                }
                                previousSessions[box_id][0] = session_id;
                            }
                            if (temp_user_id == 'new') {
                                $this.closest('.section').find('.temporary-user-id-for-reg').val(result.temp_user_id);
                                temp_user_id = result.temp_user_id;
                                attendee_timeout_worker(result.temp_user_id, $this.closest('.section'));
                            }
                            if (result.status == 'attending') {
                                economy_add_to_order($this, 'session', session_id);
                                if (previous_radio_value != 0) {
                                    economy_remove_item_from_economy($this, 'session', previous_radio_value);
                                }
                                if (economy_data.multiple.is_multiple && result.order_number != null && result.order_number != 'None') {
                                    economy_data.multiple.order_number = result.order_number;
                                }
                            }
                        } else {
                            if (e.originalEvent != undefined) {
                                $.growl.warning({message: result.message});
                            }
                            $this.prop('checked', false);
                            $this.attr('data-checked', false);
                            if (previous_radio_value != 0) {
                                $('#temporary-radio-' + box_id.split('-')[1] + '-id-' + previous_radio_value).prop('checked', true);
                                $('#temporary-radio-' + box_id.split('-')[1] + '-id-' + previous_radio_value).attr('data-checked', true);
                            }
                        }
                        if (result.seats_availability != undefined) {
                            $this.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(result.seats_availability);
                        }
                        if (result.previous_session_seats_availability != undefined) {
                            $('#temporary-radio-' + box_id.split('-')[1] + '-id-' + previous_radio_value).closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(result.previous_session_seats_availability);
                            if (result.previous_session_seats_availability > 0) {
                                if ($('#temporary-radio-' + box_id.split('-')[1] + '-id-' + previous_radio_value).prop('disabled')) {
                                    $('#temporary-radio-' + box_id.split('-')[1] + '-id-' + previous_radio_value).prop('disabled', false)
                                }

                            }
                        }
                    }
                }
            });
        }
    });

    window.onbeforeunload = function () {

        if (isNaN(temp_user_id) == false) {
            $.ajax({
                url: base_url + '/delete-temporary-attendee/',
                type: "POST",
                data: {
                    id: temp_user_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (response) {
                    if (response.result) {
                        console.log(response.message);
                    } else {
                        console.log(response.message);
                    }
                }
            });
        }
        return;
    };

})
;

function attendee_timeout_worker(temp_att_id, $section) {
    // var static_url = $('.public-static-url').val();
    // var worker = new Worker(static_url + '/public/js/session_worker.js');
    // worker.onmessage = function (event) {
    setTimeout(function () {
        $.ajax({
            url: base_url + '/delete-temporary-attendee/',
            type: "POST",
            data: {
                id: temp_att_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.result) {
                    $section.find('.temporary-user-id-for-reg').val('');

                    $section.find('.event-plugin-session-checkbox').each(function () {
                        $(this).find('input:checkbox').each(function () {
                            console.log($(this).is(':checked'));
                            if ($(this).is(':checked')) {
                                $(this).prop('checked', false);
                                $(this).attr('data-checked', false);
                            }
                        })
                    });

                    $section.find('.event-plugin-session-radio-button').each(function () {
                        $(this).find('input:radio').each(function () {
                            console.log($(this).is(':checked'));
                            if ($(this).is(':checked')) {
                                $(this).prop('checked', false);
                                $(this).attr('data-checked', false);
                            }
                        })
                    });

                    $.growl.warning({message: response.message});
                    cleanEconomyData($section)
                } else {
                    console.log(response.message);
                }
            }
        });
    }, temporary_attendee_expire_time);
    // };
}

function validateMaxSessionCheckbox($this_plugin, $target_checked) {
    var validated = true;
    //$this_section.find('.event-plugin-session-radio-button:visible').each(function () {
    //    var min_attendee = $(this).find('.event-plugin-list').attr('data-session-choose');
    //    var $this = $(this);
    //    var session_attend = [];
    //    // this checking is for: when there is no item to show, then to ignore validation
    //    var session_radio_item_check = false;
    //    if ($this.find('.event-plugin-item').length > 0) {
    //        session_radio_item_check = true;
    //    }
    //    $this.find('.event-plugin-item').find('td:first').find('input').each(function () {
    //        if ($(this).prop('checked')) {
    //            var session_id = $(this).attr('data-session-id');
    //            session_attend.push(session_id);
    //        }
    //    });
    //    if (session_radio_item_check && (session_attend.length < min_attendee)) {
    //        validated = false;
    //        $this.addClass('not-validated');
    //    }
    //});
    if ($target_checked) {
        $this_plugin.closest('.event-plugin-session-checkbox:visible').each(function () {
            var max_attendee = $(this).find('.event-plugin-list').attr('data-session-choose-highest');
            console.log(max_attendee);
            if (max_attendee == "up-to-max-available-sessions") {
                max_attendee = 10;
            }
            var $this = $(this);
            var count_only_attending = true;
            var count_attending = $this.find('.event-plugin-list').attr('data-count-attending');
            console.log(count_attending);
            if (count_attending == '0') {
                count_only_attending = false;
            }
            var session_attend = [];
            console.log(count_only_attending);
            $this.find('.event-plugin-item').find('td:first').find('input[type=checkbox]').each(function () {
                var is_checked = false;
                if (count_only_attending) {
                    is_checked = $(this).prop('checked');
                } else {
                    if ($(this).closest('tr').hasClass('attending') || $(this).closest('tr').hasClass('in-queue')) {
                        is_checked = true;
                        console.log("is_checked");
                        console.log(is_checked);
                        console.log($(this).attr('data-session-id'));
                    }
                }
                if (is_checked) {
                    var session_id = $(this).attr('data-session-id');
                    session_attend.push(session_id);
                }
            });
            console.log(session_attend.length);
            if (max_attendee != 0 && session_attend.length > max_attendee) {
                validated = false;
                $this.addClass('not-validated');
            }
        });
    }
    console.log(validated);
    return validated;
}

function must_choose_one_session($this) {
    if ($this.closest('.event-plugin-list').attr('data-session-choose') == '1') {
        return true;
    }
    return false;
}

function get_temp_user_id($this, $type) {
    var session_class = $type == 'radio' ? '.event-plugin-session-radio-button' : '.event-plugin-session-checkbox';
    var temp_user_id = $this.closest('.section').find('.temporary-user-id-for-reg').val();
    var user_id = $this.closest(session_class).attr('data-uid');

    if (user_id != undefined) {
        temp_user_id = user_id;
    }
    else if (temp_user_id == undefined) {
        $this.closest('.section').append('<input class="temporary-user-id-for-reg" type="hidden" value="">');
        temp_user_id = 'new';
    } else if (temp_user_id == '') {
        temp_user_id = 'new';
    }
    return temp_user_id;
}


function setOrUnsetSession() {
    console.log("it's clicked again");
    csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var unset_sessions = [];
    var set_sessions = [];
    $body.find('.event-plugin-session-radio-button:hidden').each(function () {
        var $element = $(this);
        $element.find('input[type=radio]:checked').each(function () {
            var input_id = $(this).attr('data-session-id').split('_');
            var session_id = input_id[0];
            if (input_id.length > 1) {
                var attendee_id = input_id[1].split('u')[1];
            } else {
                var attendee_id = 'new';
            }
            var box_selector = $(this).attr('id');
            var seats_option = $(this).closest('.event-plugin-list').attr('data-seats-option');
            var rebate_details = rebate_for_session($element, session_id);
            var dict_info = {
                attendee_id: attendee_id,
                session_id: session_id,
                box_selector: box_selector,
                seats_option: seats_option,
                rebate_type: rebate_details.rebate_type,
                rebates: JSON.stringify(rebate_details.rebates),
                order_number: economy_data.multiple.order_number,
                type: 'radio'
            };
            unset_sessions.push(dict_info);
        })
    });
    console.log($body.find('.event-plugin-session-checkbox:hidden').length);
    $body.find('.event-plugin-session-checkbox:hidden').each(function () {
        var $element = $(this);
        console.log("$element.find('input[type=checkbox]:checked').length");
        console.log($element.find('input[type=checkbox]:checked').length);
        $element.find('input[type=checkbox]').each(function () {
            console.log($(this).is(":checked"));
            if ($(this).is(":checked")) {
                var input_id = $(this).attr('data-session-id').split('_');
                var session_id = input_id[0];
                if (input_id.length > 1) {
                    var attendee_id = input_id[1].split('u')[1];
                } else {
                    var attendee_id = 'new';
                }
                var box_selector = $(this).attr('id');
                var seats_option = $(this).closest('.event-plugin-list').attr('data-seats-option');
                var rebate_details = rebate_for_session($element, session_id);
                var dict_info = {
                    attendee_id: attendee_id,
                    session_id: session_id,
                    box_selector: box_selector,
                    seats_option: seats_option,
                    rebate_type: rebate_details.rebate_type,
                    rebates: JSON.stringify(rebate_details.rebates),
                    order_number: economy_data.multiple.order_number,
                    type: 'checkbox'
                };
                unset_sessions.push(dict_info);
            } else {
                unchecked_box_elms.remove($(this).attr('id'));
            }
        })
    });
    $body.find('.event-plugin-session-radio-button:visible').each(function () {
        console.log($(this).attr('id'));
        if ($(this).find('input[type=radio]:checked').length < 1) {
            var preselected_session = $(this).attr('preselected_session');
            console.log(preselected_session);
            if (preselected_session != '') {
                var box_attr = $(this).attr('id').split('-');
                var attendee_id = $(this).attr('data-uid');
                if (attendee_id == undefined) {
                    attendee_id = 'new';
                }
                if (attendee_id != 'new') {
                    var box_selector = 'temporary-radio-' + box_attr[3] + '-id-' + preselected_session + '-u' + attendee_id;
                } else {
                    var box_selector = 'temporary-radio-' + box_attr[3] + '-id-' + preselected_session + '-u';
                }
                var seats_option = $(this).find('.event-plugin-list').attr('data-seats-option');
                var rebate_details = rebate_for_session($(this), preselected_session);
                var dict_info = {
                    attendee_id: attendee_id,
                    session_id: preselected_session,
                    box_selector: box_selector,
                    seats_option: seats_option,
                    rebate_type: rebate_details.rebate_type,
                    rebates: JSON.stringify(rebate_details.rebates),
                    order_number: economy_data.multiple.order_number,
                    type: 'radio'
                };
                set_sessions.push(dict_info);
            }
        }
        temp_user_id = get_temp_user_id($(this).find('input[type=radio]:first'), 'radio');
    });
    console.log($body.find('.event-plugin-session-checkbox:visible').length);
    $body.find('.event-plugin-session-checkbox:visible').each(function () {
        if ($(this).find('input[type=checkbox]:checked').length < 1) {
            var conflict_session_setting = '0';
            var act_like_radio = $(this).attr('data-act-like-radio');
            if (act_like_radio == '1') {
                var preselected_session = $(this).attr('radio-preselected-session');
                conflict_session_setting = $(this).attr('data-conflict-session');
            } else {
                var preselected_session = $(this).attr('preselected_session');
            }
            if (preselected_session != '') {
                preselected_session = JSON.parse(preselected_session);
                var box_attr = $(this).attr('id').split('-');
                var attendee_id = $(this).attr('data-uid');
                if (attendee_id == undefined) {
                    attendee_id = 'new';
                }
                if(uncheckedSessionChecking(preselected_session, box_attr, attendee_id)) {
                    for (var i = 0; i < preselected_session.length; i++) {
                        if (attendee_id != 'new') {
                            var box_selector = "temporary-checkbox-" + box_attr[3] + "-id-" + preselected_session[i] + "-u" + attendee_id;
                        } else {
                            var box_selector = "temporary-checkbox-" + box_attr[3] + "-id-" + preselected_session[i] + "-u";
                        }
                        if (unchecked_box_elms.indexOf(box_selector) == -1) {
                            var seats_option = $(this).find('.event-plugin-list').attr('data-seats-option');
                            var rebate_details = rebate_for_session($(this), preselected_session[i]);
                            var dict_info = {
                                attendee_id: attendee_id,
                                session_id: preselected_session[i],
                                box_selector: box_selector,
                                seats_option: seats_option,
                                rebate_type: rebate_details.rebate_type,
                                rebates: JSON.stringify(rebate_details.rebates),
                                order_number: economy_data.multiple.order_number,
                                conflict_session_setting: conflict_session_setting,
                                type: 'checkbox'
                            };
                            set_sessions.push(dict_info);
                        }
                    }
                }
            }
        }
        temp_user_id = get_temp_user_id($(this).find('input[type=checkbox]:first'), 'checkbox');
    });
    console.log(unchecked_box_elms)
    console.log('unset_sessions')
    console.log(unset_sessions)
    console.log('set_sessions')
    console.log(set_sessions)
    if (unset_sessions.length > 0 || set_sessions.length > 0) {
        var data = {
            unset_sessions: JSON.stringify(unset_sessions),
            set_sessions: JSON.stringify(set_sessions),
            csrfmiddlewaretoken: csrf_token
        };
        $.ajax({
            url: base_url + '/session-set-unset-availability/',
            type: "POST",
            data: data,
            async: false,
            success: function (result) {
                var unset_session_response = result.unset_session_response;
                var set_session_response = result.set_session_response;
                for (var u = 0; u < unset_session_response.length; u++) {
                    var u_session = unset_session_response[u];
                    if (u_session.success) {
                        var $selector_u_session = $('#' + u_session.box_selector);
                        $selector_u_session.closest('tr').removeClass('not-attending not-answerd attending in-queue');
                        $selector_u_session.removeClass('not-attending not-answerd attending in-queue');
                        $selector_u_session.prop('checked', false);
                        $selector_u_session.attr('data-checked', false);
                        var $status_elm_u_session = $selector_u_session.closest('tr').find('.status');
                        // $selector_u_session.trigger('change');
                        // triggerSession();
                        if (u_session.status == 'not-attending') {
                            $selector_u_session.closest('tr').addClass(u_session.status);
                            $status_elm_u_session.addClass(u_session.status);
                            $status_elm_u_session.html(u_session.status_msg);
                        }
                        economy_remove_item_from_economy($selector_u_session, 'session', u_session.session_id);
                        if (temp_user_id == 'new') {
                            $selector_u_session.closest('.section').find('.temporary-user-id-for-reg').val(u_session.temp_user_id);
                            temp_user_id = u_session.temp_user_id;
                            attendee_timeout_worker(u_session.temp_user_id, $selector_u_session.closest('.section'));
                        }
                        if (u_session.seats_availability != undefined) {
                            $selector_u_session.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(u_session.seats_availability);
                        }
                        if (u_session.status != 'not-attending' && u_session.status != 'not-answered') {
                            $status_elm_u_session.show();

                        } else {
                            $status_elm_u_session.hide();
                        }
                    }

                }
                for (var s = 0; s < set_session_response.length; s++) {
                    var s_session = set_session_response[s];
                    if (s_session.success) {
                        var $selector_s_session = $('#' + s_session.box_selector);
                        $selector_s_session.closest('tr').removeClass('not-attending not-answerd attending in-queue');
                        $selector_s_session.removeClass('not-attending not-answerd attending in-queue');
                        var $status_elm_s_session = $selector_s_session.closest('tr').find('.status');
                        if (s_session.result) {
                            $selector_s_session.prop('checked', true);
                            $selector_s_session.attr('data-checked', true);
                            // $selector_s_session.trigger('change');
                            $selector_s_session.closest('tr').addClass(s_session.status);
                            $status_elm_s_session.addClass(s_session.status);
                            $status_elm_s_session.html(s_session.status_msg);
                            if (s_session.status == 'attending') {
                                economy_add_to_order($selector_s_session, 'session', s_session.session_id);
                                if (economy_data.multiple.is_multiple && s_session.order_number != null && s_session.order_number != 'None') {
                                    economy_data.multiple.order_number = s_session.order_number;
                                }
                            }
                            if (s_session.type == 'radio') {
                                previousSessions[$selector_s_session.closest('.event-plugin-session-radio-button').attr('id')][0] = s_session.session_id;
                                $selector_s_session.trigger('click');
                                $selector_s_session.trigger('change');
                            } else {
                                if (s_session.status == 'attending') {
                                    if ($selector_s_session.closest('.event-plugin-session-checkbox').attr('data-act-like-radio') == '1') {
                                        var prev_radio_box_id = $selector_s_session.closest('.event-plugin-session-checkbox').attr('id');
                                        previousSessionsActRadio[prev_radio_box_id][0] = s_session.session_id;
                                    }
                                }
                                $selector_s_session.trigger('change');
                            }
                            // $("#session-selection-function").trigger("sessionSelection");
                            // triggerSession();

                        } else {
                            if (s_session.status == 'not-attending') {
                                $selector_s_session.closest('tr').addClass(s_session.status);
                                $status_elm_s_session.addClass(s_session.status);
                                $status_elm_s_session.html(s_session.status_msg);
                            }

                        }
                        if (temp_user_id == 'new') {
                            $selector_s_session.closest('.section').find('.temporary-user-id-for-reg').val(s_session.temp_user_id);
                            temp_user_id = s_session.temp_user_id;
                            attendee_timeout_worker(s_session.temp_user_id, $selector_s_session.closest('.section'));
                        }
                        if (s_session.seats_availability != undefined) {
                            $selector_s_session.closest('tr').find('.event-plugin-table').find('.seats-available').find('.available-seats').html(s_session.seats_availability);
                        }
                        if (s_session.status != 'not-attending' && s_session.status != 'not-answered') {
                            $status_elm_s_session.show();

                        } else {
                            $status_elm_s_session.hide();
                        }

                    }
                }
            }
        });
    }
}

Array.prototype.remove = function () {
    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

// Plugin js
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
                            parentElem.find('.messages-read-archived-messages').show();
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
                url: base_url + '/attendee-login/',
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
                        // $.growl.error({message: result.message});
                        $form.addClass('not-validated');
                    }
                }
            });
        }
    });

    $body.on('click', '.reset-password-button', function (e) {
        var $form = $(this).closest('.event-plugin-reset-password');
        var email = $.trim($form.find('.event-plugin-reset-password-email').val());
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
                            if (result.multiple_event_list != undefined) {
                                $form.html(result.multiple_event_list)
                            } else {
                                $.growl.notice({message: result.message});
                            }
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
                            if(result.multiple){
                                $form.html(result.message);
                            }else{
                                $.growl.notice({message: result.message});
                            }
                        } else {
                            $form.addClass('not-validated');
                        }
                    }
                });
            }
        }
    });

    $body.on('click', '.event-plugin-new-password-button', function (e) {
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
                if (comment != undefined) {
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
                            if ($('body').find('.event-plugin-photo-gallery:visible').length > 0) {
                                get_photos($('body').find('.event-plugin-photo-gallery:visible:first'), 1);
                            }
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
        $('.loader').show();
        $this.prop("disabled", true);
        $.ajax({
            url: base_url + '/notification-session/',
            type: "POST",
            data: data,
            success: function (result) {
                if (result.success) {
                    getUpdatedSessionInfo();
                    $this.closest('.event-plugin-item[data-id="' + id + '"]').remove();
                    $this.closest('.event-plugin-messages-message-wrapper').remove();
                    $('.event-plugin-messages .event-plugin-item[data-id="' + id + '"]').remove();
                }
                if (result.download_flag) {
                    window.location = base_url + "/economy-pdf-request?data=credit-invoice&order_number=" + result.order_number;
                }
                $('.loader').hide();
                $this.prop("disabled", false);
                $.growl.notice({message: result.message});
            }
        });
    });

    $body.on('change', 'input[name="pic"]', function () {
        var filepath = $(this).val();
        var filename = filepath.split('\\').pop();
        $(this).closest('.event-plugin-photo-upload').find('.file-fake-path').html(filename);
        $(this).closest('.event-plugin-photo-upload').find('.selected-file').show();
    });

    $('body').on('click', '.form-pdf-button', function (event) {
        var page_id = $(this).closest('.event-plugin-pdf-button').attr('id').split('-')[1];
        var box_id = $(this).closest('.event-plugin-pdf-button').attr('id').split('-')[3];
        window.location = base_url + "/convert-html-to-pdf/?page_id=" + page_id + "&box_id=" + box_id;
    });
});

function getAllSessionsId() {
    var all_sessions = [];
    $('body').find('.event-plugin-session-checkbox').find('.event-plugin-list .event-plugin-item .session-table tr .session-selection').each(function () {
        var s_id = $(this).attr('data-session-id').split("_")[0];
        if (all_sessions.indexOf(s_id) == -1) {
            all_sessions.push(s_id);
        }
    });
    $('body').find('#dialoge .switch-wrapper #attende-or-cancel-session').find('input[type=checkbox]').each(function () {
        var s_d_id = $(this).attr('data-session-id');
        if (all_sessions.indexOf(s_d_id) == -1) {
            all_sessions.push(s_d_id);
        }
    });
    return all_sessions;
}


function updateSessionsInfo(sessions, attendee_id) {
    for (var i = 0; i < sessions.length; i++) {
        var session_id = sessions[i]['id'];
        console.log(session_id);
        console.log(attendee_id);
        $('body').find('.event-plugin-session-checkbox').find('.event-plugin-list .event-plugin-item .session-table[data-attendee-id='+attendee_id+'] tr[data-session-id=' + session_id + ']').each(function () {
            $(this).removeClass('not-attending not-answered attending in-queue time-conflict');
            $(this).find('.status').removeClass('not-attending not-answered attending in-queue time-conflict');
            $(this).addClass(sessions[i]['all_session_status'].join(" "));
            $(this).find('.status').addClass(sessions[i]['all_session_status'].join(" "));
            $(this).find('.status').html(sessions[i]['status_msg']);
            if (sessions[i]['current_status'] != 'not-attending' || sessions[i]['current_status'] != 'not-answered') {
                $(this).find('.status').show();
            }
            if (sessions[i]['current_status'] == 'attending' || sessions[i]['current_status'] == 'in-queue') {
                $(this).find('.session-selection').prop('checked', true);
                $(this).find('.session-selection').attr('data-checked', true);
            } else {
                $(this).find('.session-selection').prop('checked', false);
                $(this).find('.session-selection').attr('data-checked', false);
            }

        });
        $('body').find('.event-plugin-session-radio-button').find('.event-plugin-list .event-plugin-item .session-table[data-attendee-id='+attendee_id+'] tr[data-session-id=' + session_id + ']').each(function () {
            $(this).removeClass('not-attending not-answered attending in-queue time-conflict');
            $(this).find('.status').removeClass('not-attending not-answered attending in-queue time-conflict');
            $(this).addClass(sessions[i]['all_session_status'].join(" "));
            $(this).find('.status').addClass(sessions[i]['all_session_status'].join(" "));
            $(this).find('.status').html(sessions[i]['status_msg']);
            if (sessions[i]['current_status'] != 'not-attending' || sessions[i]['current_status'] != 'not-answered') {
                $(this).find('.status').show();
            }
            if (sessions[i]['current_status'] == 'attending' || sessions[i]['current_status'] == 'in-queue') {
                $(this).find('.session-selection').prop('checked', true);
                $(this).find('.session-selection').attr('data-checked', true);
            } else {
                $(this).find('.session-selection').prop('checked', false);
                $(this).find('.session-selection').attr('data-checked', false);
            }

        });
        $('body').find('#dialoge .switch-wrapper').find('input[data-session-id=' + session_id + ']').each(function () {
            var $session_section = $(this).closest('.session-section');
            $session_section.find('.status').removeClass('not-attending not-answered attending in-queue time-conflict');
            $session_section.find('#attende-or-cancel-session').removeClass('not-attending not-answered attending in-queue time-conflict');
            $session_section.find('.session-slider-label').removeClass('not-attending not-answered attending in-queue time-conflict');
            $session_section.find('.status').addClass(sessions[i]['all_session_status'].join(" "));
            $session_section.find('#attende-or-cancel-session').addClass(sessions[i]['current_status']);
            $session_section.find('.session-slider-label').addClass(sessions[i]['current_status']);
            $(this).attr('data-status', sessions[i]['current_status']);
            $session_section.find('.status').html(sessions[i]['status_msg']);
            $session_section.find('.session-slider-label').html(sessions[i]['status_msg']);
            if (sessions[i]['current_status'] != 'not-attending' || sessions[i]['current_status'] != 'not-answered') {
                $session_section.find('.status').show();
            }
            if (sessions[i]['current_status'] == 'attending' || sessions[i]['current_status'] == 'in-queue') {
                $(this).prop('checked', true);
            } else {
                $(this).prop('checked', false);
            }

        });

    }
}

function getUpdatedSessionInfo() {
    var all_sessions = getAllSessionsId();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: base_url + '/get-updated-session-info/',
        type: "POST",
        data: {
            all_sessions: JSON.stringify(all_sessions),
            csrfmiddlewaretoken: csrf_token
        },
        async: false,
        success: function (result) {
            if (result.success) {
                updateSessionsInfo(result.sessions_info);
            }
        }
    });
}

function uncheckedSessionChecking(preselected_session, box_attr, attendee_id){
    var uncheckedSession = [];
    for (var i = 0; i < preselected_session.length; i++) {
        if (attendee_id != 'new') {
            var box_selector = "temporary-checkbox-" + box_attr[3] + "-id-" + preselected_session[i] + "-u" + attendee_id;
        } else {
            var box_selector = "temporary-checkbox-" + box_attr[3] + "-id-" + preselected_session[i] + "-u";
        }
        uncheckedSession.push(box_selector);
    }
    if(intersect(unchecked_box_elms, uncheckedSession).length > 0){
        return false;
    }else{
        return true;
    }
}
function intersect(a, b) {
    var t;
    if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
    return a.filter(function (e) {
        return b.indexOf(e) > -1;
    });
}