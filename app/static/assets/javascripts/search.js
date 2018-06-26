$(document).ready(
    function () {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $('#top_search_key').keypress(function (e) {
            if (e.which == 13) {
                $('form#search_on_top').submit();
                return false;
            }
        });
        //$('#search_key_seminar').keyup(
        //    function () {
        //        var key = $(this).val();
        //
        //        if (key.length >= 2) {
        //            $('#loader').show();
        //
        //            $.ajax({
        //                url: base_url + '/admin/session-search/',
        //                type: "POST",
        //                data: {
        //                    search_key: key,
        //                    csrfmiddlewaretoken: csrf_token
        //                },
        //                success: function (result) {
        //                    $('#sessions').html(result)
        //                    $('.seminar-table tbody').sortable()
        //                    $('#loader').hide();
        //                    loadDataTable();
        //                }
        //            });
        //        }
        //        if (key.length == 0) {
        //            $('#loader').show();
        //            $.ajax({
        //                url: base_url + '/admin/session-search/',
        //                type: "POST",
        //                data: {
        //                    search_key: key,
        //                    csrfmiddlewaretoken: csrf_token
        //                },
        //                success: function (result) {
        //                    $('#sessions').html(result)
        //                    $('.seminar-table tbody').sortable()
        //                    $('#loader').hide();
        //                    loadDataTable();
        //                }
        //            });
        //        }
        //    }
        //);
        $('#search_key_seminar').keyup(
            function () {
                var key = $(this).val();
                $('.seminar-table tbody tr').hide();
                $('.seminar-table tbody').each(function () {
                    var $this_tbody = $(this);
                    $this_tbody.find('tr').each(function () {
                        var $this_tr = $(this);
                        $this_tr.find('td').not('.dataTables_empty').each(function () {
                            if ($(this).text().toUpperCase().indexOf(key.toUpperCase()) != -1) {
                                $this_tr.show();
                            }
                        });
                    });
                    //if ($this_tbody.find('tr:visible').length == 0 && $this_tbody.find('tr td.dataTables_empty').length == 0) {
                    //    var empty_tr = '<tr class="odd"><td valign="top" colspan="9" class="dataTables_empty">No data available in table</td></tr>';
                    //    $this_tbody.append(empty_tr);
                    //}else if($this_tbody.find('tr:visible').length == 0 && $this_tbody.find('tr td.dataTables_empty').length > 0){
                    //    $this_tbody.find('tr td.dataTables_empty:first').closest('tr').show();
                    //}
                })
            }
        );
        $('#search_key_location').keyup(
            function () {
                var key = $(this).val();
                if (key.length >= 2) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/location-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#locations').html(result)
                            $('.data-table-location tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/location-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#locations').html(result)
                            $('.data-table-location tbody').sortable();
                            $('#loader').hide();

                        }
                    });
                }
            }
        );

        $('#search_key_hotel').keyup(
            function () {
                var key = $(this).val();
                if (key.length >= 2) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/hotel-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#hotellist').html(result)
                            $('.hotel-table tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/hotel-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#hotellist').html(result)
                            $('.hotel-table tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_question').keyup(
            function () {
                var key = $(this).val();
                if (key.length >= 2) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/question-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#questions').html(result)
                            $('.showQuestions tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/question-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#questions').html(result)
                            $('.showQuestions tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_travel').keyup(
            function () {
                var key = $(this).val();

                if (key.length >= 2) {
                    $('#loader').show();

                    $.ajax({
                        url: base_url + '/admin/travel-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#travels').html(result)
                            $('.travel-table tbody').sortable()
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/travel-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#travels').html(result)
                            $('.travel-table tbody').sortable()
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_filter').keyup(
            function () {
                var key = $(this).val();

                if (key.length >= 2) {
                    $('#loader').show();

                    $.ajax({
                        url: base_url + '/admin/filter-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#filters').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/filter-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#filters').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_export_filter').keyup(
            function () {
                var key = $(this).val();

                if (key.length >= 2) {
                    $('#loader').show();

                    $.ajax({
                        url: base_url + '/admin/export-filter-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#filters').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/export-filter-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#filters').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_checkpoint').keyup(
            function () {
                var key = $(this).val();

                if (key.length >= 2) {
                    $('#loader').show();

                    $.ajax({
                        url: base_url + '/admin/checkpoint-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#checkpoints').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/checkpoint-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#checkpoints').html(result)
                            $('.data-table-filter tbody').sortable();
                            $('#loader').hide();
                        }
                    });
                }
            }
        );

        $('#search_key_admin').keyup(
            function () {
                var key = $(this).val();

                if (key.length >= 2) {
                    $('#loader').show();

                    $.ajax({
                        url: base_url + '/admin/admin-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#admins').html(result)
                            $('#loader').hide();
                        }
                    });
                }
                if (key.length == 0) {
                    $('#loader').show();
                    $.ajax({
                        url: base_url + '/admin/admin-search/',
                        type: "POST",
                        data: {
                            search_key: key,
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            $('#admins').html(result)
                            $('#loader').hide();
                        }
                    });
                }
            }
        );
    }
);