$(function () {

    $(document).ready(function () {
        filter_statistic($('.filter-column-control').val());

    });

    $('.filter-column-control').on('change', function () {
        clog("loaded");
        var selectedColumns = $(this).val();
        filter_statistic(selectedColumns);

    });


    function filter_statistic(group) {
        try {
            if (group != "" && group != null && typeof(group) != 'undefined') {
                $('body .filter-loader').show();
                var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/dashboard/filter-statistic/' + group,
                    type: 'GET',
                    // data: data,
                    dataType: "json",
                    success: function (data) {
                        $('body .filter-loader').hide();
                        var datahtml = "";
                        if (data.length) {
                            $.each(data, function (i, item) {
                                datahtml += '<tr>'
                                    + '<td align="left">' + item.filter_name + '</td>'
                                    + '<td align="right">' + item.total_attendee + '</td>'
                                    + '</tr>';

                            });
                        } else {
                            datahtml += '<tr>'
                                + '<td colspan="2" align="center">No filter found</td>'
                                + '</tr>';
                        }

                        $('#filter-group-tbody').html(datahtml);
                    },
                    error: function (e) {
                        clog(e);
                    },
                    complete: function () {

                    }
                });
            } else {
                $('body .filter-loader').hide();
                datahtml = '<tr>'
                    + '<td colspan="2" align="center">No filter found</td>'
                    + '</tr>';
                $('#filter-group-tbody').html(datahtml);
            }
        }
        catch (err) {
            clog(err.message);
        }
    }
});