$(document).ready(function () {
    $('#filter-rules-switcher').switcher();
    var $visibleColumns = $('#visible_columns');
    var $show_entries = $('#show_entries');
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
        var visibleColumns = [0, 1, 7, 8, 9 ];
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
    var attendee_table = $dataTableContainer.DataTable({
        "scrollX": true,
        "bAutoWidth": true,
        "language": dt_language,
        "order": [
            [ 0, "asc" ]
        ],

        "lengthMenu": [
            [10, 25, 50, 100],
            [10, 25, 50, 100]
        ],
        "iDisplayLength": $show_entries.val(),
        "sDom": '<"dt_top" <"dt_left"f><"dt_right"l><"clear">>rt<"dt_bottom" <"dt_left"i><"dt_right"p><"clear">>',
        "createdRow": function (row, data, index) {
            $(row).addClass('deleteduserInfo');
            $(row).attr('data-id', data[0]);
        },
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

    $("body").on('click',".deleteduserInfo",function(){
        $('body .loader').show();
        $.ajax({
            url: base_url + '/admin/deleted/attendee-history/',
            type: "POST",
            data: {
                attendee_id: $(this).attr('data-id'),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.success) {
                    var activity_history = result.history;
                    $("#deleted-att-name").text(result.name);
                    $('#deleted-attendee-history').html(activity_history);
                    $('body .loader').hide();
                    $("#deleted-attende-history").modal();
                }
            }
        });
    });


});