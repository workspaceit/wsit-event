$(document).ready(function () {
    $('body').on('click', '#dialoge .dialoge-menu a', function () {
        var section = $(this).parent("li").attr("data-section");
        $("#dialoge .dialoge-menu li").removeClass("active")
        $(this).parent("li").addClass("active");
        $("#dialoge .section").hide();
        $("#dialoge .section." + section).show();
    });

    $('body').on('click', '.dialoge-menu-close-button', function (e) {
        e.stopPropagation();
        var closeSection = $(this).parent("li").attr("data-section");
        $("." + closeSection).remove();
        $(this).parent("li").remove();
        if (!$("#dialoge .dialoge-menu").has("li").length) {
            $("#dialoge *").empty();
            $("#dialoge").removeClass("visible");
        } else {
            if (!$("#dialoge .dialoge-menu li").hasClass("active")) {
                $("#dialoge .dialoge-menu").find("li").first().addClass("active");
                var newSection = $("#dialoge .dialoge-menu .active").attr("data-section");
                $("#dialoge .section").hide();
                $("#dialoge .section." + newSection).show();
            } else {
                var newSection = $("#dialoge .dialoge-menu .active").attr("data-section");
                $("#dialoge .section").hide();
                $("#dialoge .section." + newSection).show();
            }

        }
    });

    $('#dialoge .dialoge-button-row').on('click', '.close-button', function () {
        var closeSection = $("#dialoge .dialoge-menu .active").attr("data-section");
        $("." + closeSection).remove();
        $("#dialoge .dialoge-menu .active").remove();
        $("#dialoge .dialoge-menu").find("li").first().addClass("active");
        var newSection = $("#dialoge .dialoge-menu .active").attr("data-section");
        $("#dialoge .section." + newSection).show();
        if (!$("#dialoge .dialoge-menu").has("li").length) {
            $("#dialoge *").empty();
            $("#dialoge").removeClass("visible");
        }
    });

    $('body').on('click', '.close-dialouge', function () {
        $("#dialoge *").empty();
        $("#dialoge").removeClass("visible");
    });

    function appendTab(title, name, resp) {
        $("#dialoge .dialoge-menu").append("<li data-section='" + name + "'><a>" + title + "</a><span class='dialoge-menu-close-button'></span></li>");
        $("#dialoge .dialogue-content").append("<div class='section " + name + "'>" + resp + "</div>");
        $("#dialoge .dialogue-content .section").not("." + name).hide();
        $("#dialoge .dialoge-menu li").removeClass("active");
        $("#dialoge .dialoge-menu [data-section='" + name + "']").addClass("active")
        $("#dialoge .dialoge-menu").animate({scrollLeft: $("#dialoge .dialoge-menu").width()}, 250);
    }
    var tempDivCounter = 0;

    $('body').on('click', '.location .location-details', function (event) {
        var $anchore = $(this);
        $('.submit-loader').show();
        var href = $anchore.attr('href');
        $anchore.attr('href', 'javascript:void(0)');
        $anchore.prop("disabled", true);
        try {
            event.preventDefault();
            event.stopPropagation();
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var box_id = $.trim($(this).attr('data-box-id'));
            var page_id = $.trim($(this).attr('data-page-id'));
            var location_id = $.trim($(this).attr('data-location-id'));

            $.ajax({
                url: base_url + '/get-location-details/' + parseInt(location_id) + '/',
                type: "POST",
                data: {
                    box_id: box_id,
                    page_id: page_id,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function (resp) {

                    if ($('#dialoge').hasClass('visible')) {

                        appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details);
                        tempDivCounter = tempDivCounter + 1;
                    } else {

                        var html = "<div class='dialogue-content'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div></div>"
                        $('#dialoge').html(html);
                        $('#dialoge').removeClass("_visible").addClass("visible");
                        appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details);
                        tempDivCounter = tempDivCounter + 1;
                    }
                    $('.submit-loader').hide();
                    $anchore.prop("disabled", false);
                    $anchore.attr('href', href);
                }
            });
        }
        catch (err) {
            console.log(err);
            $('.submit-loader').hide();
            $anchore.prop("disabled", false);
            $anchore.attr('href', href);
        }
    });

    $('body').on('click', '.speaker .attendee-details', function (event) {
        var $anchore = $(this);
        $('.submit-loader').show();
        var href = $anchore.attr('href');
        $anchore.attr('href', 'javascript:void(0)');
        $anchore.prop("disabled", true);
        try {
            event.preventDefault();
            event.stopPropagation();
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var box_id = $.trim($(this).attr('data-box-id'));
            var page_id = $.trim($(this).attr('data-page-id'));
            var attendee_id = $.trim($(this).attr('data-attendee-id'));

            $.ajax({
                url: base_url + '/get-attendee-details/' + parseInt(attendee_id) + '/',
                type: "POST",
                data: {
                    box_id: box_id,
                    page_id: page_id,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function (resp) {

                    if ($('#dialoge').hasClass('visible')) {

                        appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details);
                        tempDivCounter = tempDivCounter + 1;
                    } else {

                        var html = "<div class='dialogue-content'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div></div>"
                        $('#dialoge').html(html);
                        $('#dialoge').removeClass("_visible").addClass("visible");
                        appendTab(resp.lang_details, "test-tab" + tempDivCounter, resp.details);
                        tempDivCounter = tempDivCounter + 1;
                    }
                    $('.submit-loader').hide();
                    $anchore.prop("disabled", false);
                    $anchore.attr('href', href);
                }
            });
        }
        catch (err) {
            console.log(err);
            $('.submit-loader').hide();
            $anchore.prop("disabled", false);
            $anchore.attr('href', href);
        }
    });
});