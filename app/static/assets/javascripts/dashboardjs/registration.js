$(function () {

    $(document).ready(function () {
        reg_statistic($('#reg_start_date').val(), $('#reg_end_date').val());
        $('#reg-daterange-btn').daterangepicker(
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
                $('#reg-daterange-btn span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                $('#reg_start_date').val(start.format('YYYY-MM-DD'));
                $('#reg_end_date').val(end.format('YYYY-MM-DD'));
                clog($('#reg_start_date').val());
                clog($('#reg_end_date').val());
                resetCanvasreg();
                reg_statistic($('#reg_start_date').val(), $('#reg_end_date').val());
            }
        );
        var start_date = new Date($('#reg_start_date').val());
        var end_date = new Date($('#reg_end_date').val());
        $("#reg-daterange-btn").data('daterangepicker').setStartDate((start_date.getMonth() + 1) + "/" + start_date.getDate() + "/" + start_date.getFullYear());
        $("#reg-daterange-btn").data('daterangepicker').setEndDate((end_date.getMonth() + 1) + "/" + end_date.getDate() + "/" + end_date.getFullYear());
    });

    $('.reg-time')
        .on("click", function (e) {
            clog($(this).data("id"))
            $(".active .reg-time").parents('li').removeClass('active');
            $(this).parents('li').addClass('active');
            resetCanvasreg();
            reg_statistic($('#reg_start_date').val(), $('#reg_end_date').val());
        });


    function resetCanvasreg() {
        $('#graph-container-reg').html("");
        $('#chart-graph-reg').remove();
        $('#graph-container-reg').append('<canvas id="chart-graph-reg"><canvas>');
    }

    function reg_statistic(start_time, end_time) {
        try {
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var data = {
                start_time: start_time,
                end_time: end_time,
                csrfmiddlewaretoken: csrfToken
            };

            $.ajax({
                url: base_url + '/admin/dashboard/reg-statistic/',
                type: 'POST',
                data: data,
                dataType: "json",
                success: function (response) {
                    clog(response.time);
                    var cartdata = {
                        labels: response.time,
                        datasets: [{
                            label: response.label[0],
                            data: response.reg_by_date,
                            borderWidth: 1,
                            backgroundColor: "#58C2E1",
                            borderColor: "#142536",
                            borderDash: [5, 2],
                            fill: false
                        }],
                    };

                    new Chart(document.getElementById('chart-graph-reg').getContext("2d"), {
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