$(document).ready(function () {
    $('#filter-rules-switcher').switcher();
    var $visibleColumns = $('#visible_columns');
    var show_entries = $('#show_entries').val();
    var sorted_column = $('#sorted_column_attendee').val();
    var sorting_order = $('#sorting_order_attendee').val();
    var $lastActiveFilter = $('#last_active_filter');
    var search_key = $('#search_key').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var data = {
        csrfmiddlewaretoken: csrf_token
    };
    var question_length = $('#question_length').find('option').length;
    if (question_length < 3){
        var visibleColumns = [0, 1];
    }else{
        var visibleColumns = [0, 1, 4, 11, 12, 13, 14];
        if($visibleColumns.val() != ''){
            visibleColumns = JSON.parse($visibleColumns.val());
        }
    }
    var $ruleCheckbox = $('#filter-rules-switcher');
    var $rule = $('#rule');
    if($lastActiveFilter.val()!='') {
        $rule.val($lastActiveFilter.val());
        $('#filter-rules-switcher').switcher('on');
    }
    var $dataTableContainer = $('#filter-search-table');
    $dataTableContainer.show();
    clog(visibleColumns);
    var attendee_table = $dataTableContainer.DataTable({
        "scrollX": true,
        "bAutoWidth": true,
        "language": dt_language,
        "order": [
            [ sorted_column, sorting_order ]
        ],

        "lengthMenu": [
            [10, 25, 50, 100],
            [10, 25, 50, 100]
        ],
        "iDisplayLength": show_entries,
        "sDom": '<"dt_top" <"dt_left"f><"dt_right"l><"clear">>rt<"dt_bottom" <"dt_left"i><"dt_right"p><"clear">>',
        "createdRow": function (row, data, index) {
            $(row).addClass('userInfo');
            $(row).attr('data-id', data[0]);
        },
        "columnDefs": [
            {
                "orderable": false,
                "searchable": false,
                "className": "",
                "targets": 0,
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                }
            },
            {
                "orderable": true,
                "searchable": true,
                "className": "",
                "targets": '_all'
            },
            { "visible": true, "targets": visibleColumns },
            { "visible": false, "targets": [ '_all' ] }
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
            clog("data-table initialized");
            $('body .loader').hide()
        }
    });
    $('#filter-search-table_wrapper').css('min-height','350px');
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
       for(var i =0; i<visibleColumns.length; i++){
           if($(this).val() == visibleColumns[i]){
               $(this).attr('selected', 'selected');
           }
       }


        //
        // var element_index = $(this).prop('index');
        // // clog($(this).prop('text'));
        // if(element_index>1){
        //     if($.inArray(element_index-2, visibleColumns) != -1) {
        //         $(this).attr('selected', 'selected');
        //         clog($(this).prop('index'));
        //         clog($(this).prop('text'));
        //     }
        // }

    });

    // Handles showing and hiding the datatable columns for attendee page
    $('.datatable-column-control').on('change', function () {
        var predefinedColumns = [0, 1];
        var selectedColumns = $(this).val();
        var columns = predefinedColumns.concat(selectedColumns);

//        var table = $('#filter-search-table').DataTable();
        clog(columns);
        columns = columns.filter(function (v, i, a) {
            return a.indexOf(v) == i
        });
        var index = columns.indexOf("999");
        if (index >= 0) {
            columns.splice(index, 1);
        }
        clog(columns);
        attendee_table.columns().visible(false, false);
        attendee_table.columns(columns).visible(true, true);
        visibleColumns = columns;
        clog(visibleColumns);
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

});