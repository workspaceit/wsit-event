$(function () {

    $(document).ready(function () {
        pagehit_statistic($('#pagehit').select2("val"), $('#page_hit_start_date').val(), $('#page_hit_end_date').val());
        $('#page-hit-daterange-btn').daterangepicker(
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
                $('#page-hit-daterange-btn span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                $('#page_hit_start_date').val(start.format('YYYY-MM-DD'));
                $('#page_hit_end_date').val(end.format('YYYY-MM-DD'));
                clog($('#page_hit_start_date').val());
                clog($('#page_hit_end_date').val());
                resetCanvaspagehit();
                pagehit_statistic($('#pagehit').select2("val"), $('#page_hit_start_date').val(), $('#page_hit_end_date').val());
            }
        );
        var start_date = new Date($('#page_hit_start_date').val());
        var end_date = new Date($('#page_hit_end_date').val());
        $("#page-hit-daterange-btn").data('daterangepicker').setStartDate((start_date.getMonth() + 1) + "/" + start_date.getDate() + "/" + start_date.getFullYear());
        $("#page-hit-daterange-btn").data('daterangepicker').setEndDate((end_date.getMonth() + 1) + "/" + end_date.getDate() + "/" + end_date.getFullYear());
    });

    $('#pagehit').select2();
    $('#pagehit').select2()
        .on("change", function (e) {
            resetCanvaspagehit();
            pagehit_statistic($('#pagehit').select2("val"), $('#page_hit_start_date').val(), $('#page_hit_end_date').val());
        });

    // $('.pagehit-time')
    //     .on("click", function (e) {
    //         // console.log($(this).data("id"))
    //         $(".active .pagehit-time").parents('li').removeClass('active');
    //         $(this).parents('li').addClass('active');
    //         resetCanvaspagehit();
    //         pagehit_statistic($('#pagehit').select2("val"), $(this).data("id"));
    //     });

    function resetCanvaspagehit() {
        $('#graph-container-pagehit').html("");
        $('#chart-graph-pagehit').remove();
        $('#graph-container-pagehit').append('<canvas id="chart-graph-pagehit"><canvas>');
    }


    function pagehit_statistic(pages, start_time, end_time) {

        try {
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var data = {
                page: pages,
                start_time: start_time,
                end_time: end_time,
                csrfmiddlewaretoken: csrfToken
            };

            $.ajax({
                url: base_url + '/admin/dashboard/pagehit-statistic/',
                type: 'POST',
                data: data,
                dataType: "json",
                success: function (response) {
                    clog(response)
                    var cartdata = {
                        labels: response.time,
                        datasets: [{
                            label: response.label[0],
                            data: response.hit_by_date,
                            borderWidth: 1,
                            backgroundColor: "#985623",
                            borderColor: "#142536",
                            borderDash: [5, 2],
                            fill: false
                        }, {
                            label: response.label[1],
                            data: response.unique_hit_by_date,
                            borderWidth: 2,
                            backgroundColor: "#2A94DB",
                            borderColor: "#963258",
                        }],
                    };

                    new Chart(document.getElementById('chart-graph-pagehit').getContext("2d"), {
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