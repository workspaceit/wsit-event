var base_url = window.location.origin + '/' + event_url;
var $body = $('body');
var site_url = window.location.origin;
var lang_hotel_validation_msg = "";
var reservation_Data = [];
var js_data = '';
var economy_data = {
    'sessions': [], 'hotels': [], 'travels': [], 'rebates': [], 'rebate_type': '',
    'multiple': {'is_multiple': false, 'order_number': null}
};

var multiple_attendee_id = "";
var multiple_attendee_id_array = [];

var multiple_registration_attendee = {};


var multiple_registration_order_owner = [];

var cookie_expire = $('#cookie_expire').val();
var cookie_counter = cookie_expire;
if ($('#hidden_secret').length > 0) {
    var cookie_expire_msg = $('#cookie_expire_msg').val();
    var cookie_timer = setInterval(function () {
        cookie_counter -= 1;
        if (cookie_counter <= -10) {
            //alert(cookie_expire_msg);
            $("<div></div>").html(cookie_expire_msg).dialog({
                modal: true,
                resizable: false,
                width: 'auto',
                close: function (event, ui) {
                    location = base_url + '/logout';
                },
                buttons: {
                    "OK": function () {
                        location = base_url + '/logout';
                    }
                }
            });
            clearInterval(cookie_timer);
        }
    }, 1000);
}


function onLoadJs() {
    $('body').find('#content').removeClass('loading-page');
    $body.find('.element').each(function () {
        if ($.trim($(this).html()) == '' && $.trim($(this).closest('.col').text()) == '') {
            if ($(this).is(".event-plugin-next-up,.event-plugin-evaluations,.event-plugin-messages")) {
                // $(this).closest('.col').hide();
            } else {
                $(this).closest('.col').remove();
            }

        }
    });
    var $elem = $body.find('.given-answer');
    //var filter_container = $('#filter-container').val();
    var page_classes = $('#page-class-list').val();
    // page_classes = page_classes.replace(/'/g, '"');
    if (page_classes != "" && page_classes != "None") {
        var class_list = JSON.parse(page_classes);
        for (var c = 0; c < class_list.length; c++) {
            var div_id = "page-" + class_list[c].page_id + "-box-" + class_list[c].box_id;
            $("[id=" + div_id + "],[id^=" + div_id + "-]").addClass(class_list[c].class_name);
        }
    }
    addMarginForHeader();
    $body.find('.event-plugin-multiple-registration').each(function () {
        var $registration_plugin = $(this);
        if ($registration_plugin.find('.loop-registration-form').length > 0) {
            $registration_plugin.closest('.section').find('.event-plugin-submit-button').each(function () {
                // $registration_plugin.nextAll('.event-plugin-submit-button').each(function () {
                if ($(this).closest('.event-plugin-multiple-registration').length < 1) {
                    var box_id = $(this).attr('id').split('-')[3];
                    var button_id = $(this).attr('data-submit-id');
                    $registration_plugin.attr('data-submit-button-id', button_id);
                    $registration_plugin.attr('data-submit-button-box-id', box_id);
                    $(this).remove();
                }
            });
        } else {
            $registration_plugin.find('.event-plugin-submit-button').each(function () {
                $(this).remove();
            });
        }

    });

    // hotel reservation start
    if ($('.event-plugin-hotel-reservation').length > 0) {
        hotel_reservation_init();
    }

    $('body').find('.defaultCountdown').each(
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
                else {
                    var parentElem = self.closest('.event-plugin-messages');
                    self.closest('.event-plugin-item').remove();
                    if (parentElem.children('.event-plugin-list').children('.event-plugin-item').length == 0) {
                        //$('.event-plugin-messages').parent().remove();
                        //parentElem.find('.messages-read-archived-messages').remove();
                        parentElem.find('.messages-mark-all-button').remove();
                    }
                }
            }, 1000);
        }
    );

    // attendee-list-plugin

    $('body').find('.event-plugin-attendee-list').each(
        function () {

            var $this_plugin = $(this);
            var show_counting_column = $this_plugin.closest('.event-plugin-attendee-list').find('.attendee-plugin-counting-column').val();
            var attendee_export_id = $this_plugin.closest('.event-plugin-attendee-list').find('.attendee-plugin-attendee-export-id').val();
            var show_counting_column_header = $this_plugin.closest('.event-plugin-attendee-list').find('.attendee-plugin-counting-column-header').val();
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            var show_entries = Math.abs($this_plugin.closest('.event-plugin-attendee-list').find('.attendee-plugin-attendee-per-page').val());
            var display_table = $this_plugin.closest('.event-plugin-attendee-list').find('.attendee-plugin-display-attendee-table').val();
            var data = {
                attendee_export_id: attendee_export_id,
                csrfmiddlewaretoken: csrf_token,
                show_counting_column: show_counting_column
            };
            if (display_table == 'True') {
                $.ajax({
                    url: base_url + '/get-attendee-plugin-data-2/',
                    type: "POST",
                    async: false,
                    data: {
                        // filter_id: filter_id,
                        // column_ids: column_ids,
                        attendee_export_id: attendee_export_id,
                        show_counting_column: show_counting_column,
                        show_counting_column_header: show_counting_column_header,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        /*if (result.status) {
                         $this_plugin.find('.attendee-table-content').html(result.html);

                         // default first column sorted, except counting serial colmun
                         //var sorting_col = 0;
                         //var sorted_col_th = $this_plugin.find('.attendee-table-content').find('thead th:nth-child(1)');
                         //if(sorted_col_th.attr('data-th-checker') == 'not-question'){
                         //    sorted_col_th = $this_plugin.find('.attendee-table-content').find('thead th:nth-child(2)');
                         //    sorting_col = 1;
                         //}
                         //sorted_col_th.addClass('asc');
                         f_sl_att_plugin *= -1;
                         //sortAttendeeList(f_sl_att_plugin, sorting_col, $this_plugin.find('.attendee-table-content').find('tbody'));
                         }*/
                        if (result.status) {
                            $this_plugin.find('.attendee-table-content').html(result.html);
                            $this_plugin.find('.attendee-table-content').find('.attendee-plugin-dt-table').DataTable({
                                "scrollX": true,
                                "bAutoWidth": true,
                                "language": dt_language,
                                "sDom": '<"dt_top" <"dt_left"f><"clear">>rt<"dt_bottom" <"dt_left"i><"dt_right"p><"clear">>',
                                "iDisplayLength": show_entries,
                                // "language": dt_language,
                                "columnDefs": [
                                    {
                                        "searchable": true,
                                        "orderable": true,
                                        "className": "",
                                        "targets": '_all'
                                    },
                                    {"visible": true, "targets": ['_all']}
                                ],
                                "searching": true,
                                "processing": false,
                                "serverSide": true,
                                "destroy": true,
                                "ajax": {
                                    'type': 'POST',
                                    'url': base_url + '/get-attendee-plugin-dt/',
                                    'data': data
                                },
                                "initComplete": function () {
                                    $('.dataTables_filter input').unbind('.DT');
                                    $('.dataTables_filter').hide();
                                    var attendee_table = $this_plugin.find('.attendee-table-content').find('.attendee-plugin-dt-table').DataTable();
                                    $this_plugin.find('.total-attendees-wrapper').find('.total-attendees-number').html(attendee_table.page.info().recordsTotal);
                                    $this_plugin.find('.total-attendees-wrapper');
                                    $this_plugin.find('.not-sortable').unbind('click');
                                    $this_plugin.find('.attendee-table-content').find('.dataTables_scroll').addClass('scroll-x');
                                }
                            });
                        }
                    }
                });
            }
            else {
                $this_plugin.find('.total-attendees-wrapper').hide();
                $this_plugin.find('.attendee-plugin-search').hide();
            }
        }
    );

    var search_timer = null;
    $("body").find(".attendee-plugin-search").on('keyup', function (e) {
        var search_data = $(this).val();
        var attendee_table = $(this).closest('.event-plugin-attendee-list').find('.attendee-plugin-dt-table').DataTable();
        clearTimeout(search_timer);
        search_timer = setTimeout(function () {
            attendee_table.search(search_data).draw();
        }, 350);
    });

    // Amsul date time picker functionalities for questions

    $('.question-date').each(function () {
        var id = $(this).attr('id');
        var min = $(this).attr('data-from-date');
        var max = $(this).attr('data-to-date');
        var mindate = min.split("-");
        mindate[1] = mindate[1] - 1;
        var maxdate = max.split("-");
        maxdate[1] = maxdate[1] - 1;
        $(this).pickadate({
            min: mindate,
            max: maxdate
        });
    });

    $('.question-time').each(function () {
        var id = $(this).attr('id');
        var min = $(this).attr('data-from-time');
        var max = $(this).attr('data-to-time');
        var mintime = min.split(":");
        var maxtime = max.split(":");
        var time_intervel=Number.isInteger(parseInt($(this).attr('time-intervel')))?parseInt($(this).attr('time-intervel')):30;

        mintime.pop();
        maxtime.pop();
        $(this).pickatime({
            min: mintime,
            max: maxtime,
            interval: time_intervel
        });
    });

    $('.question-date-range').each(function () {
        var $this = $(this);
        var id = $(this).attr('id');
        var range_type = $(this).attr('data-range-type');
        var min = $(this).attr('data-from-date');
        var max = $(this).attr('data-to-date');
        var mindate = min.split("-");
        mindate[1] = mindate[1] - 1;
        var maxdate = max.split("-");
        maxdate[1] = maxdate[1] - 1;
        var $input = $(this).pickadate({
            min: mindate,
            max: maxdate
        });
        var picker = $input.pickadate('picker');
        picker.on({
            set: function (thingSet) {
                if (range_type == "from") {
                    var $input = $this.parent().find('.question-date-range-to');
                    var picker_to = $input.pickadate('picker');
                    picker_to.set('min', this.get(), {muted: true});
                } else if (range_type == "to") {
                    var $input = $this.parent().find('.question-date-range-from');
                    var picker_from = $input.pickadate('picker');
                    picker_from.set('max', this.get(), {muted: true});
                }
            }
        });
    });
    $('.question-time-range').each(function () {
        var $this = $(this);
        var id = $(this).attr('id');
        var min = $(this).attr('data-from-time');
        var max = $(this).attr('data-to-time');
        var range_type = $(this).attr('data-range-type');
        var mintime = min.split(":");
        var maxtime = max.split(":");
        var time_intervel=Number.isInteger(parseInt($(this).attr('time-intervel')))?parseInt($(this).attr('time-intervel')):30;

        mintime.pop();
        maxtime.pop();
        var $input = $(this).pickatime({
            min: mintime,
            max: maxtime,
            interval: time_intervel
        });
        var picker = $input.pickatime('picker');
        picker.on({
            set: function (thingSet) {
                if (range_type == "from") {
                    var $input = $this.parent().find('.question-time-range-to');
                    var picker_to = $input.pickatime('picker');
                    picker_to.set('min', this.get(), {muted: true});
                } else if (range_type == "to") {
                    var $input = $this.parent().find('.question-time-range-from');
                    var picker_from = $input.pickatime('picker');
                    picker_from.set('max', this.get(), {muted: true});
                }
            }
        });
    });
    // Attendee logout plugin
    $('body').find('.event-plugin-log-out').each(function () {
        if ($(this).find('.event-plugin-log-out-button').length == 0) {
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/get-logout-plugin/',
                type: "POST",
                async: false,
                data: {
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.status) {

                    }
                }
            });
        }
    });
    $(".event-question-country").each(function () {
        for (var i = 0; i < country_list.length; i++) {
            $(this).append($('<option>', {
                value: country_list[i].id,
                text: country_list[i].text
            }));
        }
        $(this).val($(this).attr('data-default'));
    });
}

//Sortable attendee list
var f_sl_att_plugin = 1;
function sortAttendeeList(f, n, elem_tbody) {
    var rows = elem_tbody.find('tr:visible').get();

    rows.sort(function (a, b) {

        var A = getVal(a);
        var B = getVal(b);

        if (A > B) {
            return -1 * f;
        }
        if (A < B) {
            return 1 * f;
        }
        return 0;
    });

    function getVal(elm) {
        var v = $(elm).children('td').eq(n).text().toUpperCase();
        //if ($.isNumeric(v)) {
        //    v = parseInt(v, 10);
        //}
        return v;
    }

    $.each(rows, function (index, row) {
        $(this).find('td.attendee-list-counting-col').html(index + 1);
        elem_tbody.append(row);
    });
}


$(function () {
    var disallow_page = $('#disallow_page').val();
    var access = true;
    $('body').find('#content').each(function () {
        var page_url = $.trim($('body').attr('id'));
        $.ajax({
            url: base_url + '/api/' + page_url + '/',
            type: "GET",
            async: false,
            success: function (result) {
                $('#content').html(result.html);
                js_data = result.js;
                eval(result.js);
            }
        });
    });
    // Submit Button Start

    $body.on('click', '.form-submit-button', function (e) {
        e.preventDefault();
        var $this_section = $(this).closest('.section-box');
        setEmptyValueToQuestions($body);
        var box_id = $this_section.attr('id');
        var required_actual = true;
        var required_field = [];
        var validated = true;
        var answers = [];
        var firstName = '';
        var lastName = '';
        var email = '';
        var phone = '';
        var $button = $(this);
        var page_id = $(this).attr('data-page-id');
        var btn_id = $(this).closest('.event-plugin-submit-button').attr('data-submit-id');
        var btn_box_id = $(this).closest('.event-plugin-submit-button').attr('id').split('-')[3];
        var is_loop_multiple = false;
        var is_inline_multiple = false;
        if ($this_section.closest('.event-plugin-multiple-registration').find(".loop-registration-form").length > 0) {
            is_loop_multiple = true;
        }
        if ($this_section.find('.event-plugin-multiple-registration').find(".inline-registration-form").length > 0) {
            is_inline_multiple = true;
        }
        $this_section.find('.event-question').removeClass('validation-failed');
        $this_section.find('.event-plugin').removeClass('validation-failed');

        var $this_sec_form_questions;
        if (is_loop_multiple) {
            $this_sec_form_questions = $this_section.closest('.event-plugin-multiple-registration').closest('.section-box').find('.event-question');
        }
        if ($this_sec_form_questions == undefined) {
            $this_sec_form_questions = $this_section.find('.event-question');
        }

        // $this_section.find('.event-question').each(function () {
        $this_sec_form_questions.each(function () {
            var $form_question = $(this);
            //if ($form_question.closest('.section-box').css('display') != 'none' && $form_question.closest('.row').css('display') != 'none' && $form_question.closest('.col').css('display') != 'none' && $form_question.css('display') != 'none') {
            var answer = '';
            var valid = true;
            var include = true;
            if ($form_question.attr('data-def') == 'firstname' || $form_question.attr('data-def') == 'lastname' || $form_question.attr('data-def') == 'email') {
                if ($.inArray($form_question.attr('data-def'), required_field) == -1) {
                    required_field.push($form_question.attr('data-def'));
                }
            }
            var element = $form_question.find('.given-answer');
            if (element.length > 0) {
                var type = element.prop('type');
                if (type == 'text' || type == 'select-one' || type == 'textarea' || type == 'date') {
                    answer = element.val();
                    if ($form_question.is(":visible")) {
                        if (answer == '' || answer == 'not selected') {
                            if ($form_question.attr('data-def') == 'firstname' || $form_question.attr('data-def') == 'lastname' || $form_question.attr('data-def') == 'email') {
                                required_actual = false;
                            }
                            if ($form_question.attr('data-req') == 1) {
                                valid = false;
                            }
                            if ($form_question.attr('type') == 'date_range' || $form_question.attr('type') == 'time_range') {
                                answerList = ['', ''];
                                answer = JSON.stringify(answerList);
                            }
                        }
                        else if ($form_question.attr('data-def') == 'firstname') {
                            firstName = element.val();
                        } else if ($form_question.attr('data-def') == 'lastname') {
                            lastName = element.val();
                        } else if ($form_question.attr('data-def') == 'email') {
                            if (!validateEmail(element.val())) {
                                valid = false;
                            } else {
                                email = element.val();
                            }
                        } else if ($form_question.attr('data-def') == 'phone') {
                            phone = element.val();
                            var re = /^[0-9+-\\(\\) ]*$/;
                            if (!re.test(phone)) {
                                valid = false;
                            }
                        } else if ($form_question.attr('type') == 'date') {
                            var input_field_name = element.attr('name');
                            answer = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                        } else if ($form_question.attr('type') == 'time') {
                            var input_field_name = element.attr('name');
                            answer = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                        }
                        else if ($form_question.attr('type') == 'date_range') {
                            var answerList = []
                            $form_question.find('.question-date-range').each(function () {
                                if ($(this).attr('data-range-type') == 'to') {
                                    // var ans = $(this).val();
                                    var input_field_name = $(this).attr('name');
                                    var ans = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                                    if (ans == '') {
                                        answerList[1] = '';
                                    }
                                    else {
                                        answerList[1] = ans;
                                    }

                                } else if ($(this).attr('data-range-type') == 'from') {
                                    // var ans = $(this).val();
                                    var input_field_name = $(this).attr('name');
                                    var ans = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                                    if (ans == '') {
                                        answerList[0] = '';
                                    }
                                    else {
                                        answerList[0] = ans;
                                    }
                                }
                            });
                            if (answerList[0] != '' && answerList[1] != '') {
                                answer = JSON.stringify(answerList);
                            } else {
                                valid = false;
                            }


                        }
                        else if ($form_question.attr('type') == 'time_range') {
                            var answerList = []
                            $form_question.find('.question-time-range').each(function () {
                                if ($(this).attr('data-range-type') == 'to') {
                                    var input_field_name = $(this).attr('name');
                                    var ans = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                                    if (ans == '') {
                                        answerList[1] = '';
                                    }
                                    else {
                                        answerList[1] = ans;
                                    }

                                } else if ($(this).attr('data-range-type') == 'from') {
                                    var input_field_name = $(this).attr('name');
                                    var ans = $(this).closest('.event-question').find('input[name=' + input_field_name + '_submit]').val();
                                    if (ans == '') {
                                        answerList[0] = '';
                                    }
                                    else {
                                        answerList[0] = ans;
                                    }
                                }
                            });

                            if (answerList[0] != '' && answerList[1] != '') {
                                answer = JSON.stringify(answerList);
                            } else {
                                valid = false;
                            }
                        }

                    } else {
                        include = false;
                    }
                    //else if (element.attr('data-def') == 'phonenumber') {
                    //    if (!phoneValidate(element.val())) {
                    //        valid = false;
                    //    }
                    //}
                }
                else if (type == 'radio') {
                    if ($form_question.is(":visible")) {
                        if (!element.is(':checked')) {
                            if ($form_question.attr('data-req') == 1) {
                                valid = false;
                            }
                        }
                        else {
                            var elemName = element.attr('name');
                            answer = $('input[name="' + elemName + '"]:checked').val();
                        }
                    } else {
                        answer = "";
                        include = false;
                    }
                }
                else if (type == 'checkbox') {
                    if ($form_question.is(":visible")) {
                        var checkbox_answer_lists = [];
                        element.each(function () {
                            if ($(this).is(':checked')) {
                                checkbox_answer_lists.push($(this).val());
                            }
                        });
                        if (checkbox_answer_lists.length == 0) {
                            if ($form_question.attr('data-req') == 1) {
                                valid = false;
                            }
                        }
                        else {
                            var checkbox_answers = "";
                            for (var cBox = 0; cBox < checkbox_answer_lists.length; cBox++) {
                                if (cBox != 0) {
                                    checkbox_answers += "<br>";
                                }
                                checkbox_answers += checkbox_answer_lists[cBox];
                            }
                            answer = checkbox_answers;
                        }
                    } else {
                        answer = "";
                        include = false;
                    }
                }
                if (!valid) {
                    validated = false;
                    $form_question.addClass('validation-failed');
                } else {
                    if (include) {
                        var id = $.trim($form_question.attr('data-id'));
                        var type = $.trim($form_question.attr('type'));
                        if (id != '' && id != null && id != undefined) {
                            var duid = $.trim($form_question.attr('data-uid'));
                            if (duid != undefined && duid != '' && duid != null) {
                                var ans_data = {
                                    id: id,
                                    answer: answer,
                                    duid: duid,
                                    type: type
                                };
                                if ($form_question.attr('data-def') != undefined && $form_question.attr('data-def') != 'null') {
                                    ans_data['actual_defination'] = $form_question.attr('data-def');
                                }

                            } else if (is_loop_multiple) {
                                duid = $form_question.closest('.section').find('.event-plugin-multiple-registration-attendee-table tr:nth-child(2)').attr('data-multiple-attendee-id');
                                var ans_data = {
                                    id: id,
                                    answer: answer,
                                    duid: duid,
                                    type: type
                                };
                                if ($form_question.attr('data-def') != undefined && $form_question.attr('data-def') != 'null') {
                                    ans_data['actual_defination'] = $form_question.attr('data-def');
                                }
                            } else if (is_inline_multiple) {
                                duid = $form_question.closest('.section').find('.inline-registration-form .event-plugin-multiple-registration-order-owner-form').attr('inline-data-owner-idz4Vv3ZLs3R');
                                var ans_data = {
                                    id: id,
                                    answer: answer,
                                    duid: duid,
                                    type: type
                                }
                                if ($form_question.attr('data-def') != undefined && $form_question.attr('data-def') != 'null') {
                                    ans_data['actual_defination'] = $form_question.attr('data-def');
                                }
                                answers.push(ans_data);
                                $form_question.closest('.section').find('.inline-registration-form .event-plugin-multiple-registration-attendee-form-inline').each(function () {
                                    duid = $(this).attr('inline-data-attendee-idz4vv3zls3r');
                                    var ans_data = {
                                        id: id,
                                        answer: answer,
                                        duid: duid,
                                        type: type
                                    }
                                    if ($form_question.attr('data-def') != undefined && $form_question.attr('data-def') != 'null') {
                                        ans_data['actual_defination'] = $form_question.attr('data-def');
                                    }
                                    answers.push(ans_data);
                                });
                                return true;
                            } else {
                                var ans_data = {
                                    id: id,
                                    answer: answer,
                                    type: type
                                }
                            }
                            answers.push(ans_data);
                        }
                    }
                }
            }
            //}
        });

        var language_id = 0;

        var find_language = findGetParameter('languageid');
        if (find_language != undefined && find_language != null && find_language != '') {
            language_id = find_language;
        }

        var h_r_validation = true;
        reservation_Data = [];
        $this_section.find('.event-plugin-hotel-reservation:visible').each(function () {
            h_r_validation = get_hotel_resrevation_data($(this));
            if (!h_r_validation) {
                return false;
            }
        });
        var session_validation = validateSession($this_section);
        if (!session_validation) {
            validated = false;
        }
        // validated = false;
        if (is_loop_multiple) {
            if (validated && h_r_validation) {

                $('.submit-loader').show();
                $button.prop("disabled", true);
                var multiple_form = $this_section.closest('.event-plugin-multiple-registration');
                var count_attendee = multiple_form.find('.event-plugin-multiple-registration-attendee-table tbody tr:not(.default-empty-attendee)').length;
                var form_box_id = multiple_form.attr('id').split('-')[3];
                var page_id = $(this).attr('data-page-id');
                var btn_id = $(this).closest('.event-plugin-submit-button').attr('data-submit-id');
                var btn_box_id = $(this).closest('.event-plugin-submit-button').attr('id').split('-')[3];
                var main_submit_btn_id = multiple_form.attr('data-submit-button-id');
                var main_submit_btn_box_id = multiple_form.attr('data-submit-button-box-id');
                var main_page_id = multiple_form.attr('data-page-id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                if (count_attendee >= multiple_attendee_id_array.indexOf(multiple_attendee_id) + 1) {
                    multiple_registration_attendee[multiple_attendee_id] = {}
                    multiple_registration_attendee[multiple_attendee_id]["attendee_id"] = multiple_attendee_id;
                    if (firstName != '') {
                        multiple_registration_attendee[multiple_attendee_id]['firstname'] = firstName;
                    }
                    if (lastName != '') {
                        multiple_registration_attendee[multiple_attendee_id]['lastname'] = lastName;
                    }
                    if (email != '') {
                        multiple_registration_attendee[multiple_attendee_id]['email'] = email;
                    }
                    if (phone != '') {
                        multiple_registration_attendee[multiple_attendee_id]['phonenumber'] = phone;
                    }
                    if (reservation_Data.length > 0) {
                        multiple_registration_attendee[multiple_attendee_id]['hotel_reservation'] = JSON.stringify(reservation_Data);
                    }

                    multiple_registration_attendee[multiple_attendee_id]['answers'] = answers;
                    $.each(answers, function (index, value) {
                        if (value.type == 'date_range' || value.type == 'time_range') {
                            var answer_values = JSON.parse(value.answer);
                            var answer_value = answer_values[0] + ' to ' + answer_values[1];
                            $(".event-plugin-multiple-registration-attendee-table").find("tr[class='active']").find("td[data-column-id='" + value.id + "']").html(answer_value);
                        } else {
                            $(".event-plugin-multiple-registration-attendee-table").find("tr[class='active']").find("td[data-column-id='" + value.id + "']").html(value.answer);
                        }
                    });
                    var group_order_number = null;
                    if (economy_data.multiple.order_number) {
                        group_order_number = economy_data.multiple.order_number
                    }
                    add_ineffective_rebates();
                    $.ajax({
                        url: base_url + '/get-attendee-next-page/',
                        type: "POST",
                        data: {
                            page_id: page_id,
                            attendee_id: multiple_attendee_id,
                            attendee_data: JSON.stringify(multiple_registration_attendee[multiple_attendee_id]),
                            button_id: btn_id,
                            box_id: btn_box_id,
                            order_number: group_order_number,
                            economy_data: JSON.stringify(economy_data),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('.submit-loader').hide();
                            $button.prop('disabled', false);
                            if (result.success) {
                                if (result.next_page) {
                                    multiple_form.find('.event-plugin-multiple-registration-form').html(result.attendee_page);
                                    eval(result.attendee_js);
                                } else {
                                    if (!economy_data.multiple.order_number && result.order_number) {
                                        economy_data.multiple.order_number = result.order_number
                                    }
                                    if (count_attendee > multiple_attendee_id_array.indexOf(multiple_attendee_id) + 1) {
                                        multiple_attendee_id = multiple_attendee_id_array[multiple_attendee_id_array.indexOf(multiple_attendee_id) + 1];
                                        getMultipleAttendeeForm(multiple_form, multiple_attendee_id);
                                        var attendee_text = $('#attendee_text').val();
                                        multiple_form.find('.event-plugin-multiple-registration-form-header').html(attendee_text + ' ' + $("[data-attendee-idz4Vv3ZLs3R='" + multiple_attendee_id + "']").closest('tr').find('td:first').html());
                                    } else {
                                        multiple_form.find('.event-plugin-multiple-registration-form').html("");
                                        multiple_form.find('.event-plugin-multiple-registration-form-header').html("");
                                        saveOrUpdateMultipleAttendee($button, main_submit_btn_id, main_submit_btn_box_id, main_page_id, form_box_id, language_id);
                                    }
                                    $('html, body').animate({
                                        scrollTop: $('.event-plugin-multiple-registration').offset().top
                                    }, 500);
                                }
                            } else {
                                $button.closest('.event-plugin-submit-button').addClass('validation-failed');
                                $button.closest('.event-plugin-submit-button').find('.error-on-validate').text(result.message);
                            }
                        }
                    });
                } else {
                    $('.submit-loader').hide();
                    $button.prop('disabled', false);
                    saveOrUpdateMultipleAttendee($button, main_submit_btn_id, main_submit_btn_box_id, main_page_id, form_box_id, language_id);
                }
            } else {
                if ($('.validation-failed:visible:first').length > 0) {
                    $('html, body').animate({
                        scrollTop: $('.validation-failed:visible:first').offset().top
                    }, 300);
                }
            }
        } else if (is_inline_multiple) {
            var min_attendee = $this_section.find('.event-plugin-multiple-registration').attr('data-min-attendees');
            var total_attendees = multiple_attendee_id_array.length;
            if ($this_section.find('.event-plugin-multiple-registration-order-owner-form').attr('data-include-ownerz4Vv3ZLs3R') == '0') {
                total_attendees = multiple_attendee_id_array.length - 1;
            }
            if (total_attendees < min_attendee) {
                validated = false;
            }
            if (validated && h_r_validation) {
                var multiple_form = $this_section.find('.event-plugin-multiple-registration');
                var form_box_id = multiple_form.attr('id').split('-')[3];
                var btn_box_id = $(this).closest('.event-plugin-submit-button').attr('id').split('-')[3];
                var main_submit_btn_id = $(this).closest('.event-plugin-submit-button').attr('data-submit-id');
                var main_submit_btn_box_id = $(this).closest('.event-plugin-submit-button').attr('id').split('-')[3];
                var main_page_id = multiple_form.attr('data-page-id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                saveOrUpdateMultipleAttendeeInline($button, main_submit_btn_id, main_submit_btn_box_id, main_page_id, form_box_id, answers, language_id)
            } else {
                if ($('.validation-failed:visible:first').length > 0) {
                    $('html, body').animate({
                        scrollTop: $('.validation-failed:visible:first').offset().top
                    }, 300);
                }
            }
        } else {
            if (validated) {
                if ($.trim($('#hidden_secret').val()) == undefined || $.trim($('#hidden_secret').val()) == "") {
                    if (required_field.length < 3 || !required_actual) {
                        validated = false;
                        $.growl.error({message: "You need to fill up Firstname, Lastname and Email for Registration"});
                    }
                }
            }
            //temporary att added 8-July-2017
            var temporary_attendee_id = 'not_exists';
            if ($this_section.find('.temporary-user-id-for-reg').val() != undefined) {
                if (isNaN($this_section.find('.temporary-user-id-for-reg').val()) == false) {
                    temporary_attendee_id = $this_section.find('.temporary-user-id-for-reg').val().trim();
                }
            }
            add_ineffective_rebates();
            if (validated && h_r_validation) {
                var user_login = false;
                if ($.trim($('#hidden_secret').val()) != undefined && $.trim($('#hidden_secret').val()) != "") {
                    user_login = true;
                }
                if (answers.length > 0 || reservation_Data.length > 0 || user_login) {
                    $('.submit-loader').show();
                    $button.prop("disabled", true);
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    //var deleted_sessions = [];
                    //$.each(previousSessions[box_id], function (i, e) {
                    //    if ($.inArray(e, sessions) == -1) deleted_sessions.push(e);
                    //});
                    var data = {
                        answers: JSON.stringify(answers),
                        language_id: language_id,
                        // sessions: JSON.stringify(sessions),
                        // deleted_sessions: JSON.stringify(deleted_sessions),
                        hotel_reservation: JSON.stringify(reservation_Data),
                        economy_data: JSON.stringify(economy_data),
                        button_id: btn_id,
                        page_id: page_id,
                        box_id: btn_box_id,
                        temporary_attendee_id: temporary_attendee_id,
                        csrfmiddlewaretoken: csrf_token
                    };
                    if (firstName != '') {
                        data['firstname'] = firstName;
                    }
                    if (lastName != '') {
                        data['lastname'] = lastName;
                    }
                    if (email != '') {
                        data['email'] = email;
                    }
                    if (phone != '') {
                        data['phonenumber'] = phone;
                    }

                    $.ajax({
                        url: base_url + '/attendee-registration/',
                        type: "POST",
                        data: data,
                        success: function (result) {
                            $('.submit-loader').hide();
                            $button.prop('disabled', false);
                            if (!result.success) {
                                // $.growl.error({message: result.message});
                                $button.closest('.event-plugin-submit-button').addClass('validation-failed');
                                $button.closest('.event-plugin-submit-button').find('.error-on-validate').text(result.message);
                            } else {
                                $.growl.notice({message: result.message});
                                setEmptyValueToQuestions($body);
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
                                diplay_new_order_info($this_section, result);
                            }
                        }
                    });
                }

            }
            else {
                if ($('.validation-failed:visible:first').length > 0) {
                    $('html, body').animate({
                        scrollTop: $('.validation-failed:visible:first').offset().top
                    }, 300);
                }
            }
        }

    });

    // Submit Button End

    // Attendee list download excelsheet

    $("body").on("click", ".attendee-list-download-spreadsheet-button", function () {
        $('body').find('.loader').show();
        var attendee_export_id = $(this).closest('.event-plugin-attendee-list').find('.attendee-plugin-attendee-export-id').val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: base_url + '/export-plugin-attendee/',
            type: "POST",
            data: {
                attendee_export_id: attendee_export_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.result) {
                    $.growl.notice({message: result.message});
                    var public_checker = result.public_checker;
                    attendee_export_state_check(public_checker, csrf_token);
                }

            }
        });
    });

    function attendee_export_state_check(public_checker, csrf_token) {
        $.ajax({
            url: base_url + '/attendee-plugin-export-state/',
            type: "POST",
            data: {
                public_checker: public_checker,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.next_ajax_req) {
                    setTimeout(function () {
                        attendee_export_state_check(public_checker, csrf_token);
                    }, 2000);
                } else {
                    $('body').find('.loader').hide();
                    window.location = base_url + "/export-plugin-attendee/";
                }

            }
        });
    }

//    Search Attendee list

    /*$body.on('keyup', '.attendee-plugin-search', function (e) {
     var $this = $(this);
     var page = window.location.pathname.split('/')[2];
     var element_id = $this.closest('.box').attr('data-id');
     var box_id = $this.closest('.box').attr('id').split('-')[3];
     if (page != undefined && box_id != undefined && page != '' && box_id != '') {
     var listElem = $this.closest('.event-plugin-attendee-list');
     listElem.find('.event-plugin-table tbody tr').hide();
     var search_key = $.trim($this.val());
     listElem.find('.event-plugin-table tbody tr').each(function () {
     var found_attendee = false;
     var $this_tr = $(this);
     var fullname = $this_tr.find('td.firstname').text().toUpperCase() + ' ' + $this_tr.find('td.lastname').text().toUpperCase();
     $this_tr.find('td').each(function () {
     if (!$(this).hasClass('attendee-list-counting-col')) {
     if ($(this).text().toUpperCase().indexOf(search_key.toUpperCase()) != -1) {
     found_attendee = true;
     } else if (fullname.indexOf(search_key.toUpperCase()) != -1) {
     found_attendee = true;
     }
     }
     });
     if (found_attendee) {
     $this_tr.show();
     }
     });
     listElem.find('.event-plugin-table tbody tr:visible').each(function (index) {
     $(this).find('td.attendee-list-counting-col').html(index + 1);
     });
     }

     });*/

    $body.on('click', '.event-plugin-attendee-list .event-plugin-table thead th', function () {
        if (!$(this).hasClass('attendee-list-counting-header')) {
            f_sl_att_plugin *= -1;
            var n = $(this).prevAll().length;
            var elem_tbody = $(this).closest('.event-plugin-attendee-list').find('.event-plugin-table tbody');
            var className = $.trim($(this).attr("class"));
            $(this).closest('.event-plugin-attendee-list').find('.event-plugin-table thead th').removeClass('asc desc');
            if (className == '' || className == undefined) {
                $(this).addClass('desc');
            } else if (className == 'asc') {
                $(this).addClass('desc');
            } else if (className == 'desc') {
                $(this).addClass('asc');
            } else {
                $(this).addClass('desc');
            }
            sortAttendeeList(f_sl_att_plugin, n, elem_tbody);
        }
    });

    $body.on('click', '.event-plugin-clear-search', function () {
        var search_elem = $(this).prev('.event-plugin-search');
        search_elem.val('');
        search_elem.keyup();
    });

    $body.on('click', '#language-select a', function () {
        if (!$(this).hasClass('current')) {
            var edited_answers = [];

            // Get Changed data

            $('body').find('.event-question').each(function () {
                var $form_question = $(this);
                var element = $form_question.find('.given-answer');
                if (element.length > 0) {
                    var type = element.prop('type');
                    if (type == 'radio') {
                        if (element.is(':checked')) {
                            var question_answers = {};
                            var name = element.attr('name');
                            var id = $('input[name=' + name + ']:checked').attr('id');
                            question_answers['answer'] = true;
                            question_answers['id'] = id;
                            question_answers['type'] = type;
                            question_answers['box_id'] = $form_question.attr('id');
                            edited_answers.push(question_answers);
                        }
                    }
                    else if (type == 'checkbox') {
                        element.each(function () {
                            var question_answers = {};
                            question_answers['answer'] = $(this).is(':checked');
                            question_answers['id'] = $(this).attr('id');
                            question_answers['type'] = type;
                            question_answers['box_id'] = $form_question.attr('id');
                            edited_answers.push(question_answers);
                        });
                    } else {
                        var answer = element.val();
                        var question_answers = {};
                        question_answers['answer'] = answer;
                        question_answers['id'] = element.attr('id');
                        question_answers['type'] = type;
                        question_answers['box_id'] = $form_question.attr('id');
                        edited_answers.push(question_answers);
                    }
                }

            });

            var id = $(this).attr('data-id');
            var page_url = window.location.pathname.split('/')[2];
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $('.loader').show();
            $.ajax({
                url: base_url + '/change-language/',
                type: "POST",
                data: {
                    language_id: id,
                    page_url: page_url,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.success) {
                        var main_div = $('body').find('#content');
                        $('body').find('ul.menu').html(result.menus);
                        $('body').find('#growl_success').val(result.growl_success);
                        $('body').find('#growl_warning').val(result.growl_warning);
                        $('body').find('#growl_error').val(result.growl_error);
                        $('body').find('#growl_notify').val(result.growl_notify);
                        $('body').find('#language-select').replaceWith(result.languages);
                        main_div.html(result.page);
                        eval(result.js);

                        // Set Changed data

                        for (var i = 0; i < edited_answers.length; i++) {
                            var answer = edited_answers[i];
                            if (answer['type'] == 'radio' || answer['type'] == 'checkbox') {
                                $('#' + answer['box_id']).find('#' + answer['id']).prop("checked", answer['answer']);
                            } else {
                                $('#' + answer['box_id']).find('#' + answer['id']).val(answer['answer']);
                            }
                        }

                        $('.loader').hide();
                    }
                }
            });
        }
    });
});

// setEmptyValueToQuestions($body);


// Multiple Resistration plugin submit

function saveOrUpdateMultipleAttendee(button, main_submit_btn_id, main_submit_btn_box_id, main_page_id, form_box_id, language_id) {

    var attendees_data = [];
    $("[data-attendee-idz4Vv3ZLs3R]").each(function () {
        attendees_data.push($(this).attr("data-attendee-idz4Vv3ZLs3R"));
    })
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        attendee_owner_id: $("[data-owner-idz4Vv3ZLs3R]").attr("data-owner-idz4Vv3ZLs3R"),
        attendee_ids: JSON.stringify(attendees_data),
        button_id: main_submit_btn_id,
        page_id: main_page_id,
        box_id: main_submit_btn_box_id,
        form_box_id: form_box_id,
        language_id: language_id,
        economy_data: JSON.stringify(economy_data),
        csrfmiddlewaretoken: csrf_token
    };
    $.ajax({
        url: base_url + '/multiple-attendee-save/',
        type: "POST",
        data: data,
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.message});
                setEmptyValueToQuestions($body);
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
                $("[data-owner-idz4Vv3ZLs3R]").closest('tr').find('td:eq(1)').html(result.group_name);
                $("[data-attendee-idz4Vv3ZLs3R]").each(function () {
                    $("[data-attendee-idz4Vv3ZLs3R='" + $(this).attr("data-attendee-idz4Vv3ZLs3R") + "']").closest('tr').find('td:eq(1)').html(result.group_name)
                })

            } else {
                button.closest('.event-plugin-submit-button').addClass('validation-failed');
                button.closest('.event-plugin-submit-button').find('.error-on-validate').text(result.message);
            }
        }
    });
}

function getArrayFromDict(attendee_list) {
    var input = attendee_list;
    var output = [], item;
    for (var serial in input) {
        if (input.hasOwnProperty(serial)) {
            item = {};
            item.serial = serial;
            item.data = input[serial];
            output.push(item);
        }
    }
    return output;
}


function getMultipleAttendeeForm(multiple_form, attendee_id) {
    $("tr[data-multiple-attendee-id='" + attendee_id + "']").parent().find('tr[class="active"]').removeClass("active");
    $("tr[data-multiple-attendee-id='" + attendee_id + "']").addClass("active");
    var attendee_page_id = multiple_form.attr('data-attendee-page');
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        attendee_id: attendee_id,
        attendee_page_id: attendee_page_id,
        csrfmiddlewaretoken: csrf_token
    };

    $.ajax({
        url: base_url + '/get-multiple-registration-attendee-form/',
        type: "POST",
        data: data,
        success: function (result) {
            if (result.success) {
                multiple_form.find('.event-plugin-multiple-registration-form').html(result.attendee_page);
                eval(result.attendee_js);
            }
        }
    });
}

// Add empty div in evalution, next up and message

function addEmptyDiv($plugin, empty_message) {
    var empty_div = '<div class="placeholder empty">' + empty_message + '</div>';
    $plugin.find(".event-plugin-list").html(empty_div);
}


function checkEmail(email) {
    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    return re.test(email);
}

function redirectToPage(page_url) {
    if (page_url == '/') {
        setTimeout(function () {
            window.location = base_url + "/"
        }, 500);
    }
    else if (page_url != '') {
        setTimeout(function () {
            window.location = base_url + "/" + page_url
        }, 500);
    }
}

function validateEmail(email) {
    var emails = [];
    $.ajax({
        url: base_url + '/get-allowed-emails/',
        type: "get",
        async: false,
        success: function (result) {
            result.forEach(function (entry) {
                emails.push(entry.name);
            });
        }
    });
    var validEmail = [];
    var validDomain = [];
    emails.forEach(function (entry) {

        if (entry.indexOf("*") >= 0) {
            var domain = entry.substring(entry.lastIndexOf("@") + 1);
            validDomain.push(domain)
        } else {
            validEmail.push(entry);
        }
    });

    var regularExp = ""
    validDomain.forEach(function (entry) {
        if (entry == '*') {
            regularExp = '';
            return false;
        }
        regularExp += "\\b";
        regularExp += entry;
        regularExp += "|";
    });
    var regex = regularExp.slice(0, -1);
    if (emails.length > 0) {
        if (jQuery.inArray(email, validEmail) !== -1) {
            return true;
        } else {
            if (regex.length > 0) {
                var re = new RegExp("^([\\w-]+(?:\\.[\\w-]+)*)@(" + regex + ")$");
            } else {
                var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            }
            return re.test(email);
        }
    } else {
        return true;
    }

}

$(window).on('resize', addMarginForHeader);

function addMarginForHeader() {
    var totalHeight = $(".section.fixed-header").outerHeight(true);
    $("#content").css("padding-top", totalHeight);
};

function footerAlign() {
    var footerHeight = $('.section.fixed-footer').outerHeight();
    $('body').css('padding-bottom', footerHeight);
}

$(window).bind("load", function () {
    equalHeight($(".equal-height"))
    equalHeight($(".equal-height2"))
    footerAlign();
});

$(window).resize(function () {
    equalHeight($(".equal-height"))
    equalHeight($(".equal-height2"))
    footerAlign();
});

function equalHeight(group) {
    tallest = 0;
    group.css("height", "");
    group.each(function () {
        thisHeight = $(this).height();
        if (thisHeight > tallest) {
            tallest = thisHeight;
        }
    });
    group.height(tallest);
}

function setEmptyValueToQuestions($elem) {
    var a = 0;
    $elem.find('.event-question:not(:visible)').each(function () {
        var element = $(this).find('.given-answer');
        if (element.length > 0) {
            a++;
            var type = element.prop('type');
            if (type == 'text' || type == 'select-one' || type == 'textarea' || type == 'date') {
                element.val("");
            } else if (type == 'radio') {
                element.prop('checked', false);
            } else if (type == 'checkbox') {
                element.prop('checked', false);
            }
        }
    });
}


function archivedNotification(elm) {
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
                    $.growl.notice({message: response.message});
                    var parentElem = elm.closest('.event-plugin-messages');
                    elm.parent().remove();
                    if (parentElem.children('.event-plugin-list').children('.event-plugin-item').length == 0) {
                        //$('.event-plugin-messages').parent().remove();
                        //parentElem.find('.messages-read-archived-messages').remove();
                        parentElem.find('.messages-mark-all-button').remove();
                        addEmptyDiv(parentElem, response.empty_txt_language);
                    }
                    if (!parentElem.find('.messages-read-archived-messages').is(":visible")) {
                        parentElem.find('.messages-read-archived-messages').show();
                    }

                }
            }
        }
    );
}


if (window.location.hostname == '192.168.1.67') {
    console.log = function () {
    }
}


function pageDisable96() {
    $('.submit-loader').show();
    $("body").prepend("<div class=\"o1pi09kjjsd\"></div>");
    $(".o1pi09kjjsd").css({
        "position": "absolute",
        "width": $(document).width(),
        "height": $(document).height(),
        "z-index": 99999,
    }).fadeTo(0, 0.8);
}
function pageEnable69() {
    $('.submit-loader').hide();
    $(".o1pi09kjjsd").remove();
}


$(document).ajaxStart(function () {
    pageDisable96();
    $('body').find('.loader').show();
});

$(document).ajaxStop(function () {
    pageEnable69();
    $('body').find('.loader').hide();
});

$(document).ajaxSend(function () {

    clog("Triggered ajaxSend handler.");
});

$(document).ajaxError(function () {
    clog("Triggered ajaxError handler.");
});

$(document).ajaxComplete(function () {
    clog("Triggered ajaxComplete handler.");
});
$(document).ajaxSuccess(function () {
    cookie_counter = cookie_expire;
    clog("Triggered ajaxSuccess handler.");
});

Array.prototype.unique_answer = function () {
    var a = this.concat();
    for (var i = 0; i < a.length; ++i) {
        for (var j = i + 1; j < a.length; ++j) {
            if (a[i].id === a[j].id) {
                a[i].answer = a[j].answer;
                a.splice(j--, 1);
            }
        }
    }
    return a;
};

function validateSession($this_section) {
    var validated = true;
    $this_section.find('.event-plugin-session-radio-button:visible').each(function () {
        var min_attendee = $(this).find('.event-plugin-list').attr('data-session-choose');
        var $this = $(this);
        var session_attend = [];
        // this checking is for: when there is no item to show, then to ignore validation
        var session_radio_item_check = false;
        if ($this.find('.event-plugin-item').length > 0) {
            session_radio_item_check = true;
        }
        $this.find('.event-plugin-item').find('td:first').find('input').each(function () {
            if ($(this).prop('checked')) {
                var session_id = $(this).attr('data-session-id');
                session_attend.push(session_id);
            }
        });
        if (session_radio_item_check && (session_attend.length < min_attendee)) {
            validated = false;
            $this.addClass('validation-failed');
        }
    });
    $this_section.find('.event-plugin-session-checkbox:visible').each(function () {
        var act_like_radio = $(this).attr('data-act-like-radio');
        if (act_like_radio == '1') {
            var session_must_choose = $(this).find('.event-plugin-list').attr('data-session-choose');
            if (session_must_choose == '1') {
                var $this = $(this);
                var count_attending = $(this).find('.event-plugin-list').attr('data-count-attending');
                var checked_session = false;
                if (count_attending == '1') {
                    if ($this.find('.event-plugin-item').find('tr.attending').find('td:first').find('input:checked').length > 0) {
                        checked_session = true;
                    }
                } else {
                    if ($this.find('.event-plugin-item').find('td:first').find('input:checked').length > 0) {
                        checked_session = true;
                    }
                }
                if(!checked_session){
                    validated = false;
                    $this.addClass('validation-failed');
                }
            }
        } else {
            var min_attendee = $(this).find('.event-plugin-list').attr('data-session-choose-least');
            var max_attendee = $(this).find('.event-plugin-list').attr('data-session-choose-highest');
            if (min_attendee == "up-to-max-available-sessions") {
                min_attendee = 5;
            }
            if (max_attendee == "up-to-max-available-sessions") {
                max_attendee = 5;
            }
            var $this = $(this);
            var session_attend = [];
            // this checking is for: when there is no item to show, then to ignore validation
            var session_checkbox_item_count = 0;
            $this.find('.event-plugin-item').each(function () {
                session_checkbox_item_count++;
            });
            $this.find('.event-plugin-item').find('td:first').find('input').each(function () {
                if ($(this).prop('checked')) {
                    var session_id = $(this).attr('data-session-id');
                    session_attend.push(session_id);
                }
            });
            if (session_checkbox_item_count < min_attendee) {
                min_attendee = session_checkbox_item_count;
            }
            if (min_attendee != 0 && session_attend.length < min_attendee) {
                validated = false;
                $this.addClass('validation-failed');
            } else if (max_attendee != 0 && session_attend.length > max_attendee) {
                validated = false;
                $this.addClass('validation-failed');
            }
        }

    });
    return validated;
}

function global_getDateWithLanguage(text_date) {
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    var result_date = text_date;
    try {
        $.ajax({
            url: base_url + '/get-date-with-language/',
            type: "POST",
            async: false,
            data: {
                request_date: text_date,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (result) {
                if (result.success) {
                    result_date = result.converted_date;
                }
            }
        });
    } catch (error) {
        console.log(error);
    }
    return result_date;
}

function clog(message) {
    if (window.location.hostname != '192.168.1.67' && window.location.hostname != '163.53.151.2') {
        console.log(message);
    }
}

var country_list = [{id: "AF", text: "Afghanistan"}, {id: "AX", text: "Åland Islands"}, {
    id: "AL",
    text: "Albania"
}, {id: "DZ", text: "Algeria"}, {id: "AS", text: "American Samoa"}, {id: "AD", text: "Andorra"}, {
    id: "AO",
    text: "Angola"
}, {id: "AI", text: "Anguilla"}, {id: "AQ", text: "Antarctica"}, {id: "AG", text: "Antigua and Barbuda"}, {
    id: "AR",
    text: "Argentina"
}, {id: "AM", text: "Armenia"}, {id: "AW", text: "Aruba"}, {id: "AU", text: "Australia"}, {
    id: "AT",
    text: "Austria"
}, {id: "AZ", text: "Azerbaijan"}, {id: "BS", text: "Bahamas"}, {id: "BH", text: "Bahrain"}, {
    id: "BD",
    text: "Bangladesh"
}, {id: "BB", text: "Barbados"}, {id: "BY", text: "Belarus"}, {id: "BE", text: "Belgium"}, {
    id: "BZ",
    text: "Belize"
}, {id: "BJ", text: "Benin"}, {id: "BM", text: "Bermuda"}, {id: "BT", text: "Bhutan"}, {
    id: "BO",
    text: "Bolivia, Plurinational State of"
}, {id: "BQ", text: "Bonaire, Sint Eustatius and Saba"}, {id: "BA", text: "Bosnia and Herzegovina"}, {
    id: "BW",
    text: "Botswana"
}, {id: "BV", text: "Bouvet Island"}, {id: "BR", text: "Brazil"}, {
    id: "IO",
    text: "British Indian Ocean Territory"
}, {id: "BN", text: "Brunei Darussalam"}, {id: "BG", text: "Bulgaria"}, {id: "BF", text: "Burkina Faso"}, {
    id: "BI",
    text: "Burundi"
}, {id: "KH", text: "Cambodia"}, {id: "CM", text: "Cameroon"}, {id: "CA", text: "Canada"}, {
    id: "CV",
    text: "Cape Verde"
}, {id: "KY", text: "Cayman Islands"}, {id: "CF", text: "Central African Republic"}, {
    id: "TD",
    text: "Chad"
}, {id: "CL", text: "Chile"}, {id: "CN", text: "China"}, {id: "CX", text: "Christmas Island"}, {
    id: "CC",
    text: "Cocos (Keeling) Islands"
}, {id: "CO", text: "Colombia"}, {id: "KM", text: "Comoros"}, {id: "CG", text: "Congo"}, {
    id: "CD",
    text: "Congo, the Democratic Republic of the"
}, {id: "CK", text: "Cook Islands"}, {id: "CR", text: "Costa Rica"}, {id: "CI", text: "Côte d'Ivoire"}, {
    id: "HR",
    text: "Croatia"
}, {id: "CU", text: "Cuba"}, {id: "CW", text: "Curaçao"}, {id: "CY", text: "Cyprus"}, {
    id: "CZ",
    text: "Czech Republic"
}, {id: "DK", text: "Denmark"}, {id: "DJ", text: "Djibouti"}, {id: "DM", text: "Dominica"}, {
    id: "DO",
    text: "Dominican Republic"
}, {id: "EC", text: "Ecuador"}, {id: "EG", text: "Egypt"}, {id: "SV", text: "El Salvador"}, {
    id: "GQ",
    text: "Equatorial Guinea"
}, {id: "ER", text: "Eritrea"}, {id: "EE", text: "Estonia"}, {id: "ET", text: "Ethiopia"}, {
    id: "FK",
    text: "Falkland Islands (Malvinas)"
}, {id: "FO", text: "Faroe Islands"}, {id: "FJ", text: "Fiji"}, {id: "FI", text: "Finland"}, {
    id: "FR",
    text: "France"
}, {id: "GF", text: "French Guiana"}, {id: "PF", text: "French Polynesia"}, {
    id: "TF",
    text: "French Southern Territories"
}, {id: "GA", text: "Gabon"}, {id: "GM", text: "Gambia"}, {id: "GE", text: "Georgia"}, {
    id: "DE",
    text: "Germany"
}, {id: "GH", text: "Ghana"}, {id: "GI", text: "Gibraltar"}, {id: "GR", text: "Greece"}, {
    id: "GL",
    text: "Greenland"
}, {id: "GD", text: "Grenada"}, {id: "GP", text: "Guadeloupe"}, {id: "GU", text: "Guam"}, {
    id: "GT",
    text: "Guatemala"
}, {id: "GG", text: "Guernsey"}, {id: "GN", text: "Guinea"}, {id: "GW", text: "Guinea-Bissau"}, {
    id: "GY",
    text: "Guyana"
}, {id: "HT", text: "Haiti"}, {id: "HM", text: "Heard Island and McDonald Islands"}, {
    id: "VA",
    text: "Holy See (Vatican City State)"
}, {id: "HN", text: "Honduras"}, {id: "HK", text: "Hong Kong"}, {id: "HU", text: "Hungary"}, {
    id: "IS",
    text: "Iceland"
}, {id: "IN", text: "India"}, {id: "ID", text: "Indonesia"}, {id: "IR", text: "Iran, Islamic Republic of"}, {
    id: "IQ",
    text: "Iraq"
}, {id: "IE", text: "Ireland"}, {id: "IM", text: "Isle of Man"}, {id: "IL", text: "Israel"}, {
    id: "IT",
    text: "Italy"
}, {id: "JM", text: "Jamaica"}, {id: "JP", text: "Japan"}, {id: "JE", text: "Jersey"}, {
    id: "JO",
    text: "Jordan"
}, {id: "KZ", text: "Kazakhstan"}, {id: "KE", text: "Kenya"}, {id: "KI", text: "Kiribati"}, {
    id: "KP",
    text: "Korea, Democratic People's Republic of"
}, {id: "KR", text: "Korea, Republic of"}, {id: "KW", text: "Kuwait"}, {id: "KG", text: "Kyrgyzstan"}, {
    id: "LA",
    text: "Lao People's Democratic Republic"
}, {id: "LV", text: "Latvia"}, {id: "LB", text: "Lebanon"}, {id: "LS", text: "Lesotho"}, {
    id: "LR",
    text: "Liberia"
}, {id: "LY", text: "Libya"}, {id: "LI", text: "Liechtenstein"}, {id: "LT", text: "Lithuania"}, {
    id: "LU",
    text: "Luxembourg"
}, {id: "MO", text: "Macao"}, {id: "MK", text: "Macedonia, the Former Yugoslav Republic of"}, {
    id: "MG",
    text: "Madagascar"
}, {id: "MW", text: "Malawi"}, {id: "MY", text: "Malaysia"}, {id: "MV", text: "Maldives"}, {
    id: "ML",
    text: "Mali"
}, {id: "MT", text: "Malta"}, {id: "MH", text: "Marshall Islands"}, {id: "MQ", text: "Martinique"}, {
    id: "MR",
    text: "Mauritania"
}, {id: "MU", text: "Mauritius"}, {id: "YT", text: "Mayotte"}, {id: "MX", text: "Mexico"}, {
    id: "FM",
    text: "Micronesia, Federated States of"
}, {id: "MD", text: "Moldova, Republic of"}, {id: "MC", text: "Monaco"}, {id: "MN", text: "Mongolia"}, {
    id: "ME",
    text: "Montenegro"
}, {id: "MS", text: "Montserrat"}, {id: "MA", text: "Morocco"}, {id: "MZ", text: "Mozambique"}, {
    id: "MM",
    text: "Myanmar"
}, {id: "NA", text: "Namibia"}, {id: "NR", text: "Nauru"}, {id: "NP", text: "Nepal"}, {
    id: "NL",
    text: "Netherlands"
}, {id: "NC", text: "New Caledonia"}, {id: "NZ", text: "New Zealand"}, {id: "NI", text: "Nicaragua"}, {
    id: "NE",
    text: "Niger"
}, {id: "NG", text: "Nigeria"}, {id: "NU", text: "Niue"}, {id: "NF", text: "Norfolk Island"}, {
    id: "MP",
    text: "Northern Mariana Islands"
}, {id: "NO", text: "Norway"}, {id: "OM", text: "Oman"}, {id: "PK", text: "Pakistan"}, {
    id: "PW",
    text: "Palau"
}, {id: "PS", text: "Palestine, State of"}, {id: "PA", text: "Panama"}, {id: "PG", text: "Papua New Guinea"}, {
    id: "PY",
    text: "Paraguay"
}, {id: "PE", text: "Peru"}, {id: "PH", text: "Philippines"}, {id: "PN", text: "Pitcairn"}, {
    id: "PL",
    text: "Poland"
}, {id: "PT", text: "Portugal"}, {id: "PR", text: "Puerto Rico"}, {id: "QA", text: "Qatar"}, {
    id: "RE",
    text: "Réunion"
}, {id: "RO", text: "Romania"}, {id: "RU", text: "Russian Federation"}, {id: "RW", text: "Rwanda"}, {
    id: "BL",
    text: "Saint Barthélemy"
}, {id: "SH", text: "Saint Helena, Ascension and Tristan da Cunha"}, {
    id: "KN",
    text: "Saint Kitts and Nevis"
}, {id: "LC", text: "Saint Lucia"}, {id: "MF", text: "Saint Martin (French part)"}, {
    id: "PM",
    text: "Saint Pierre and Miquelon"
}, {id: "VC", text: "Saint Vincent and the Grenadines"}, {id: "WS", text: "Samoa"}, {
    id: "SM",
    text: "San Marino"
}, {id: "ST", text: "Sao Tome and Principe"}, {id: "SA", text: "Saudi Arabia"}, {id: "SN", text: "Senegal"}, {
    id: "RS",
    text: "Serbia"
}, {id: "SC", text: "Seychelles"}, {id: "SL", text: "Sierra Leone"}, {id: "SG", text: "Singapore"}, {
    id: "SX",
    text: "Sint Maarten (Dutch part)"
}, {id: "SK", text: "Slovakia"}, {id: "SI", text: "Slovenia"}, {id: "SB", text: "Solomon Islands"}, {
    id: "SO",
    text: "Somalia"
}, {id: "ZA", text: "South Africa"}, {id: "GS", text: "South Georgia and the South Sandwich Islands"}, {
    id: "SS",
    text: "South Sudan"
}, {id: "ES", text: "Spain"}, {id: "LK", text: "Sri Lanka"}, {id: "SD", text: "Sudan"}, {
    id: "SR",
    text: "Suritext"
}, {id: "SJ", text: "Svalbard and Jan Mayen"}, {id: "SZ", text: "Swaziland"}, {id: "SE", text: "Sweden"}, {
    id: "CH",
    text: "Switzerland"
}, {id: "SY", text: "Syrian Arab Republic"}, {id: "TW", text: "Taiwan, Province of China"}, {
    id: "TJ",
    text: "Tajikistan"
}, {id: "TZ", text: "Tanzania, United Republic of"}, {id: "TH", text: "Thailand"}, {
    id: "TL",
    text: "Timor-Leste"
}, {id: "TG", text: "Togo"}, {id: "TK", text: "Tokelau"}, {id: "TO", text: "Tonga"}, {
    id: "TT",
    text: "Trinidad and Tobago"
}, {id: "TN", text: "Tunisia"}, {id: "TR", text: "Turkey"}, {id: "TM", text: "Turkmenistan"}, {
    id: "TC",
    text: "Turks and Caicos Islands"
}, {id: "TV", text: "Tuvalu"}, {id: "UG", text: "Uganda"}, {id: "UA", text: "Ukraine"}, {
    id: "AE",
    text: "United Arab Emirates"
}, {id: "GB", text: "United Kingdom"}, {id: "US", text: "United States"}, {
    id: "UM",
    text: "United States Minor Outlying Islands"
}, {id: "UY", text: "Uruguay"}, {id: "UZ", text: "Uzbekistan"}, {id: "VU", text: "Vanuatu"}, {
    id: "VE",
    text: "Venezuela, Bolivarian Republic of"
}, {id: "VN", text: "Viet Nam"}, {id: "VG", text: "Virgin Islands, British"}, {
    id: "VI",
    text: "Virgin Islands, U.S."
}, {id: "WF", text: "Wallis and Futuna"}, {id: "EH", text: "Western Sahara"}, {id: "YE", text: "Yemen"}, {
    id: "ZM",
    text: "Zambia"
}, {id: "ZW", text: "Zimbabwe"}];

country_list.ids = [];
country_list.texts = [];

// define the texts and ids and lookups

var idLookup = {};
var textLookup = {};

var country;
for (var i = 0, len = country_list.length; i < len; i++) {
    country = country_list[i];
    country_list.ids.push(country.id);
    country_list.texts.push(country.text);
    idLookup[country.text.toLowerCase()] = country.id;
    textLookup[country.id] = country.text;
}

// define the lookups
/*
 country_list.name = function name (code) {
 return nameLookup[code.toUpperCase()]
 }

 country_list.code = function code (name) {
 return codeLookup[name.toLowerCase()]
 }*/

// Get Browser Get parameter using parameterName

function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
            tmp = item.split("=");
            if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}
