$(function () {

    $(document).ready(function () {
        $('body .session-loader').hide();
        session_statistic($('.session-column-control').val());
    });

    $('.session-column-control').on('change', function () {
        clog("loaded");
        var selectedColumns = $(this).val();
        session_statistic(selectedColumns);
    });


    function session_statistic(group) {
        try {
            if (group != "" && group != null && typeof(group) != 'undefined') {
                $('body .session-loader').show();
                var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/dashboard/session-statistic/' + group,
                    type: 'GET',
                    // data: data,
                    dataType: "json",
                    success: function (data) {
                        $('body .session-loader').hide();
                        var datahtml = "";
                        if (data.length) {
                            $.each(data, function (i, item) {
                                datahtml += '<tr>'
                                    + '<td align="left">' + item.session_name + '</td>'
                                    + '<td align="right">' + item.total_attendee + '</td>'
                                    + '</tr>';

                            });
                        } else {
                            datahtml += '<tr>'
                                + '<td colspan="2" align="center">No session found</td>'
                                + '</tr>';
                        }

                        $('#session-group-tbody').html(datahtml);
                    },
                    error: function (e) {
                        clog(e);
                    },
                    complete: function (e) {
                        $('body .session-loader').hide();
                    }
                });
            } else {
                $('body .session-loader').hide();
                datahtml = '<tr>'
                    + '<td colspan="2" align="center">No filter found</td>'
                    + '</tr>';
                $('#session-group-tbody').html(datahtml);
            }
        }
        catch (err) {
            clog(err.message);
        }
    }
});