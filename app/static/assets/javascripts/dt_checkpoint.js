$(document).ready(function () {
    $('#filter-rules-switcher').switcher();
    var $visibleColumns = $('#visible_columns');
    var show_entries = $('#show_entries_checkpoint').val();
    var sorted_column = $('#sorted_column_checkpoint').val();
    var sorting_order = $('#sorting_order_checkpoint').val();
    var $lastActiveFilter = $('#last_active_filter');
    var search_key = $('#search_key').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        csrfmiddlewaretoken: csrf_token,
        checkpoint_id: $("#checkpoint_id").val()
    };
    var question_length = $('#question_length').find('option').length;
    if (question_length < 3) {
        var visibleColumns = [0, 1];
    } else {
        var visibleColumns = [0, 1, 7, 8, 9];
        if ($visibleColumns.val() != '') {
            visibleColumns = JSON.parse($visibleColumns.val());
        }
    }
    var $ruleCheckbox = $('#filter-rules-switcher');
    var $rule = $('#rule');
    if ($lastActiveFilter.val() != '') {
        $rule.val($lastActiveFilter.val());
        $('#filter-rules-switcher').switcher('on');
    }
    var $dataTableContainer = $('#filter-search-table');
    $dataTableContainer.show();
    var attendee_table = $dataTableContainer.DataTable({
        "scrollX": true,
        "bAutoWidth": true,
        "language": dt_language,
        "order": [
            [sorted_column, sorting_order]
        ],

        "lengthMenu": [
            [10, 25, 50, 100],
            [10, 25, 50, 100]
        ],
        "iDisplayLength": show_entries,
        "sDom": '<"dt_top" <"dt_left"f><"dt_right"l><"clear">>rt<"dt_bottom" <"dt_left"i><"dt_right"p><"clear">>',
        "createdRow": function (row, data, index) {
            $(row).addClass('checkpoint_row');
            $(row).attr('data-id', data[1]);
        },
        "columnDefs": [
            {
                "orderable": true,
                "searchable": false,
                "className": "",
                "targets": 0,
                'render': function (data, type, full, meta) {
                    var star_icon = "";
                    if (data.scan_status == 0)
                        star_icon = '<i class="fa fa-star-o" style="color: #ffbb33;"></i><span></span>';
                    else {
                        star_icon = '<i class="fa fa-star" style="color: #ffbb33;"></i> <span>' + data.scan_time + '</span>';
                    }
                    return star_icon;
                }
            },
            {
                "orderable" : false,
                "searchable" : false,
                "targets" : -1,
                "render" : function (data, type, full, meta) {
                    var changeStatus = '<button class="btn btn-xs btn-change-status-checkpoint"\n' +
                        'data-toggle="tooltip" data-id="'+data+'" data-original-title="Change Status"><i\n' +
                        'class="dropdown-icon fa fa-refresh"></i></button>';
                    return changeStatus;
                } 
            },
            {
                "orderable": true,
                "searchable": true,
                "className": "",
                "targets": '_all'
            },
            {"visible": true, "targets": ['_all']}
        ],
        "fnDrawCallback": function (settings) {
            //managing the "Select all" checkbox
            // everytime the table is drawn, it checks if all the
            //checkboxes are checked and if they are, then the select all
            // checkbox in the table header is selected
            var allChecked = true;
            $('.datatable thead tr').each(function () {
                $(this).find(':checkbox[name=flowcheckall]').each(function () {
                    if (!$(this).is(':checked')) {
                        allChecked = false;
                    }
                });
            });
            var table = $('#filter-search-table').DataTable();
            $(':checkbox', table.rows().nodes()).prop('checked', allChecked);
        },
        "searching": true,
        "processing": true,
        "serverSide": true,
        "destroy": true,
        "oSearch": {"sSearch": search_key},
        "ajax": {
            'type': 'POST',
            'url': ATTENDEE_LIST_JSON_URL,
            'data': data
        },
        "fnServerParams": function (aoData) {
            aoData['visible'] = visibleColumns.join(",");
            aoData['activate_rule'] = $ruleCheckbox.prop('checked');
            aoData['rule_id'] = $rule.val();
        },
        "initComplete": function () {
            $('body .loader').hide();
            $('.dataTables_filter input').unbind('.DT');
        }
    });

    $(".flowcheckall").click(function () {
        var table = $('#filter-search-table').DataTable();
        $(':checkbox', table.rows().nodes()).prop('checked', this.checked);
        //$('#filter-search-table tbody input[type="checkbox"]').prop('checked', this.checked);
    });

    var counter = 2;
    $('.selected_column').each(function () {

        $(this).val(counter++);
        if ($(this).attr("value") != 2) {
            // if ($(this).val() == 7|| $(this).val() == 8 || $(this).val() == 9) {
            //     $(this).attr('selected', 'selected');
            // }
        }
        for (var i = 0; i < visibleColumns.length; i++) {
            if ($(this).val() == visibleColumns[i]) {
                $(this).attr('selected', 'selected');
            }
        }


        //
        // var element_index = $(this).prop('index');
        // // console.log($(this).prop('text'));
        // if(element_index>1){
        //     if($.inArray(element_index-2, visibleColumns) != -1) {
        //         $(this).attr('selected', 'selected');
        //         console.log($(this).prop('index'));
        //         console.log($(this).prop('text'));
        //     }
        // }

    });

    // Handles showing and hiding the datatable columns for attendee page
    $('.datatable-column-control').on('change', function () {
        var predefinedColumns = [0, 1];
        var selectedColumns = $(this).val();
        var columns = predefinedColumns.concat(selectedColumns);

//        var table = $('#filter-search-table').DataTable();
        columns = columns.filter(function (v, i, a) {
            return a.indexOf(v) == i
        });
        var index = columns.indexOf("999");
        if (index >= 0) {
            columns.splice(index, 1);
        }
        attendee_table.columns().visible(false, false);
        attendee_table.columns(columns).visible(true, true);
        visibleColumns = columns;
        attendee_table.draw();
    });

    $rule.change(function () {
        if ($ruleCheckbox.prop('checked')) {
            attendee_table.draw();
        }
    });

    $ruleCheckbox.change(function () {
        attendee_table.draw();
    });


    $("body").on('click', ".checkpoint_row", function () {
        changeAttendeeStatus($(this).attr('data-id'), $("#checkpoint_id").val(), $(this));
    });

    function changeAttendeeStatus(attendee_id, checkpoint_id, $row_element) {
        $.ajax({
            url: base_url + '/admin/change-checkpoint-status/',
            type: "POST",
            data: {
                attendee_id: attendee_id,
                checkpoint_id: checkpoint_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {

                result = JSON.parse(result);

                if (result.error) {
                    $("#last_check_error").find('p').html(result.msg);
                    $("#last_check_error").show();
                    $("#last_check").hide();
                } else {
                    $("#last_check_error").hide();
                    $("#last_check").show();
                    $("#last_check_firstname").html(result.scan.attendee.firstname);
                    $("#last_check_lastname").html(result.scan.attendee.lastname);
                    if (result.scan.status == 1) {
                        $row_element.find('i').removeClass('fa-star-o');
                        $row_element.find('i').addClass('fa-star');
                        var scan_date_time = ' ' + result.scan.scan_time;
                        $row_element.find('td:first').find('span').html(scan_date_time);
                        if (!$('#last_check').find('i').hasClass('fa-thumbs-up')) {
                            $('#last_check').find('i').removeClass();
                            $('#last_check').find('i').css('color', '#00C851');
                            $('#last_check').find('i').addClass('fa fa-thumbs-up');
                        }
                    } else {
                        $row_element.find('i').removeClass('fa-star');
                        $row_element.find('i').addClass('fa-star-o');
                        $row_element.find('td:first').find('span').html('');
                        $('#last_check').find('i').removeClass();
                        $('#last_check').find('i').addClass('fa fa-star-o');
                        $('#last_check').find('i').css('color', '#ffbb33');
                    }
                    update_checkpoint_stats(result.checkpoint);
                }
            }
        });
    }

    if (window.location.search.indexOf('page') > -1) {
        $('#myTab a[href="#attendee-rules"]').tab('show');
    }
    var timer = setTimeout(function() {}, 350);
    $("body").find("#filter-search-table_filter input").on('keyup', function (e) {
        //$('.dataTables_filter input').unbind('.DT');
        var attendee_secret = $(this).val();
        var checkpoint_id = $("#checkpoint_id").val();
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (e.which == 13) {
            clearTimeout(timer);
            if(!attendee_secret.length) return;
            $.ajax({
                url: base_url + '/admin/auto-perform-check/',
                type: "POST",
                data: {
                    attendee_secret: attendee_secret,
                    checkpoint_id: checkpoint_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    result = JSON.parse(result);
                    if (result.error) {
                        $("#last_check_error").find('p').html(result.msg);
                        $("#last_check_error").show();
                        $("#last_check").hide();
                    } else {
                        $("#last_check_error").hide();
                        $("#last_check").show();
                        $("#last_check_firstname").html(result.scan.attendee.firstname);
                        $("#last_check_lastname").html(result.scan.attendee.lastname);

                        var att_id = result.scan.attendee.id;
                        var $row_element = $(".checkpoint_row[data-id=" + att_id + "]");

                        if (result.scan.status == 1) {
                            $row_element.find('i').removeClass('fa-star-o');
                            $row_element.find('i').addClass('fa-star');
                            var scan_date_time = ' ' + result.scan.scan_time;
                            $row_element.find('td:first').find('span').html(scan_date_time);

                            $('#last_check').find('i').removeClass();
                            $('#last_check').find('i').addClass('fa fa-thumbs-up');
                            $('#last_check').find('i').css('color', '#00C851');
                        } else {
                            // wR4C6OnOchJnnfENCWhrm5DsKrTKSUbaR63MQeyF
                            $row_element.find('i').removeClass('fa-star');
                            $row_element.find('i').addClass('fa-star-o');
                            $row_element.find('td:first').find('span').html('');
                            $('#last_check').find('i').removeClass();
                            $('#last_check').find('i').addClass('fa fa-star-o');
                            $('#last_check').find('i').css('color', '#ffbb33');
                        }
                        update_checkpoint_stats(result.checkpoint);
                    }
                    $("body").find("#filter-search-table_filter input").val('');
                }
            });
        }
        else {
            //$('.dataTables_filter input').unbind('.DT').bind('.DT', function(e) {
                var value = this.value;
                clearTimeout(timer);
                timer = setTimeout(function() {
                    console.log("Timer");
                    attendee_table.search(value).draw();
                    //$('.dataTables_filter input').unbind('keypress');
                }, 350);
            //});
        }
    });

    function update_checkpoint_stats(stats) {
        $('.chkpnt-checked-text').html(stats.checked);
        $('.chkpnt-percentage-text').html('(' + stats.percentage + '%)');
        $('.chkpnt-remaining-text').html(stats.remaining);
        $('.chkpnt-max-text').html(stats.max);
    }

    $("body").on('click', ".checkpoint-update-stat", function () {
        var checkpoint_id = $("#checkpoint_id").val();
        $.ajax({
            url: base_url + '/admin/checkpoint-update-manually/',
            type: "POST",
            data: {
                checkpoint_id: checkpoint_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.success) {
                    update_checkpoint_stats(result.checkpoint)
                }
            }
        });
        var $dataTableContainer = $('#filter-search-table').DataTable();
        $dataTableContainer.ajax.reload();

    });

    $("body").on('click', ".btn-change-status-checkpoint", function (e) {
        e.stopPropagation();
        var checkpoint_id = $("#checkpoint_id").val();
        var attendee_id = $(this).attr('data-id');
        $.ajax({
            url: base_url + '/admin/toggle-checkpoint-status/',
            type: "POST",
            data: {
                attendee_id: attendee_id,
                checkpoint_id: checkpoint_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                result = JSON.parse(result);
                if (result.error) {
                    $("#last_check_error").find('p').html(result.msg);
                    $("#last_check_error").show();
                    $("#last_check").hide();
                } else {
                    $("#last_check_error").hide();
                    $("#last_check").show();
                    $("#last_check_firstname").html(result.scan.attendee.firstname);
                    $("#last_check_lastname").html(result.scan.attendee.lastname);

                    var att_id = result.scan.attendee.id;
                    var $row_element = $(".checkpoint_row[data-id=" + att_id + "]");

                    if (result.scan.status == 1) {
                        $row_element.find('i').removeClass('fa-star-o');
                        $row_element.find('i').addClass('fa-star');
                        var scan_date_time = ' ' + result.scan.scan_time;
                        $row_element.find('td:first').find('span').html(scan_date_time);

                        $('#last_check').find('i').removeClass();
                        $('#last_check').find('i').addClass('fa fa-thumbs-up');
                        $('#last_check').find('i').css('color', '#00C851');
                    } else {
                        // wR4C6OnOchJnnfENCWhrm5DsKrTKSUbaR63MQeyF
                        $row_element.find('i').removeClass('fa-star');
                        $row_element.find('i').addClass('fa-star-o');
                        $row_element.find('td:first').find('span').html('');
                        $('#last_check').find('i').removeClass();
                        $('#last_check').find('i').addClass('fa fa-star-o');
                        $('#last_check').find('i').css('color', '#ffbb33');
                    }
                    update_checkpoint_stats(result.checkpoint);
                }
                $("body").find("#filter-search-table_filter input").val('');
            }
        });
    });

});