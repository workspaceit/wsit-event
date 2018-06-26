$(function () {

    $(document).ready(function () {
        attendeegroup_statistic($('.attendee-column-control').select().val());
    });

    $('.attendee-column-control').on('change', function () {
        clog("loaded");
        var selectedColumns = $(this).val();
        resetCanvasattendeegroup();
        attendeegroup_statistic(selectedColumns);


    });


    function resetCanvasattendeegroup() {
        $('#graph-container-attendeegroup').html("");
        $('#chart-graph-attendeegroup').remove();
        $('#graph-container-attendeegroup').append('<canvas id="chart-graph-attendeegroup"><canvas>');
    }

    function attendeegroup_statistic(groups) {
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var data = {
            groups: JSON.stringify(groups),
            csrfmiddlewaretoken: csrfToken
        };

        $.ajax({
            url: base_url + '/admin/dashboard/attendeegroup-statistic/',
            type: 'POST',
            data: data,
            dataType: "json",
            success: function (response) {

                var cartdata = {
                    labels: response.groups,
                    datasets: [{
                        label: response.label[0],
                        data: response.attendee_by_groups,
                        borderWidth: 1,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255,99,132,1)',
                        borderDash: [5, 2],
                        fill: false
                    }],
                };

                new Chart(document.getElementById('chart-graph-attendeegroup').getContext("2d"), {
                    type: 'bar',
                    data: cartdata,
                    maintainAspectRatio:true
                });

            },
            error: function (e) {
                clog(e);
            }
        });
    }
});