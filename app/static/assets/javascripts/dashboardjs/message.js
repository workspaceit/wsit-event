$(function () {

    $(document).ready(function () {
        message_statistic($('#message_start_date').val(), $('#message_end_date').val());
        $('#message-daterange-btn').daterangepicker(
            {
                ranges: {
                    'Today': [moment(), moment()],
                    'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                    'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                    'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                    'This Month': [moment().startOf('month'), moment().endOf('month')],
                    'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
                },
                startDate: moment().subtract(29, 'days'),
                endDate: moment()
            },
            function (start, end) {
                $('#message-daterange-btn span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                $('#message_start_date').val(start.format('YYYY-MM-DD'));
                $('#message_end_date').val(end.format('YYYY-MM-DD'));
                clog($('#message_start_date').val());
                clog($('#message_end_date').val());
                resetCanvasmessage();
                message_statistic($('#message_start_date').val(), $('#message_end_date').val());
            }
        );
        var start_date = new Date($('#message_start_date').val());
        var end_date = new Date($('#message_end_date').val());
        $("#message-daterange-btn").data('daterangepicker').setStartDate((start_date.getMonth() + 1) + "/" + start_date.getDate() + "/" + start_date.getFullYear());
        $("#message-daterange-btn").data('daterangepicker').setEndDate((end_date.getMonth() + 1) + "/" + end_date.getDate() + "/" + end_date.getFullYear());
    });

    $('.message-time')
        .on("click", function (e) {
            $(".active .message-time").parents('li').removeClass('active');
            $(this).parents('li').addClass('active');
            resetCanvasmessage();

            message_statistic($('#message_start_date').val(), $('#message_end_date').val());

        });


    function resetCanvasmessage() {
        $('#graph-container-message').html("");
        $('#chart-graph-message').remove();
        $('#graph-container-message').append('<canvas id="chart-graph-message"><canvas>');
    }

    function message_statistic(start_time, end_time) {
        try {


            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var data = {
                start_time: start_time,
                end_time: end_time,
                csrfmiddlewaretoken: csrfToken
            };

            $.ajax({
                url: base_url + '/admin/dashboard/message-statistic/',
                type: 'POST',
                data: data,
                dataType: "json",
                success: function (response) {

                    var cartdata = {
                        labels: response.time,
                        datasets: [{
                            label: response.label[0],
                            data: response.email_by_date,
                            borderWidth: 1,
                            backgroundColor: 'rgba(75, 192, 192, 1)',
                            borderColor: "#142536",
                            borderDash: [5, 2],
                            fill: false
                        }, {
                            label: response.label[1],
                            data: response.sms_by_date,
                            borderWidth: 1,
                            backgroundColor: 'rgba(153, 102, 255, 1)',
                            borderColor: "#142536",
                            borderDash: [5, 2],
                            fill: false
                        }, {
                            label: response.label[2],
                            data: response.notification_by_date,
                            borderWidth: 1,
                            backgroundColor: 'rgba(255, 159, 64, 1)',
                            borderColor: "#142536",
                            borderDash: [5, 2],
                            fill: false
                        }],
                    };
                    clog(cartdata)
                    new Chart(document.getElementById('chart-graph-message').getContext("2d"), {
                        type: 'line',
                        data: cartdata,
                        maintainAspectRatio: true,
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero: true
                                    }
                                }]
                            }
                        }
                    });

                },
                error: function (e) {
                    clog(e);
                }
            });
        }
        catch (err) {
            clog(err.message);
        }
    }
});