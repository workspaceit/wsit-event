$(function () {
    $('body').find('.form-plugin-photo-gallery').each(function () {
        $(this).find('.photo-pagination a:first').addClass('disabled');
        $(this).find('.photo-pagination a:nth-child(2)').addClass('active');
        if ($(this).find('.photo-pagination a').eq(-2).hasClass('active')) {
            $(this).find('.photo-pagination a:last').addClass('disabled');
        }
    });
    // var element_id, full_size_photo, only_my_photos, show_comment, uploader_name, photo_per_page, photo_groups, previous_page, pagination_text, lang_comment_text, lang_uploader_text, lang_image_details_text;


    $('body').on('click', '.photo-pagination a', function (e) {
        var $this = $(this).closest('.form-plugin-photo-gallery');
        var previous_page = parseInt($this.find('.pagination_previous_page').val());
        if ($.isNumeric($(this).text()) && previous_page != $(this).text()) {
            $(this).parent('.photo-pagination').find('a').each(function () {
                $(this).removeClass('active');
            });
            $(this).addClass('active');
            $this.find('.pagination_previous_page').val($(this).text());
            $this.find(".photo-gallery-section").empty();
            get_photos($this, $(this).text());
            $this.find('.photo-pagination a[data-value=prev]').removeClass('disabled');
        } else {
            if ($(this).attr('data-value') == 'prev') {
                var prev = $(this).closest('.photo-pagination').find('.active').prev();
                if ($.isNumeric(prev.text())) {
                    $(this).parent('.photo-pagination').find('a').each(function () {
                        $(this).removeClass('active');
                    });
                    prev.addClass('active');
                    get_photos($this, prev.text());
                    $this.find('.pagination_previous_page').val(prev.text());

                    // if (prev.prev().attr('data-value') == 'prev') {
                    //     prev.prev().css('cursor', 'not-allowed');
                    // } else {
                    //     prev.prev().css('cursor', 'pinter');
                    // }
                }
            } else if ($(this).attr('data-value') == 'next') {
                var next = $(this).closest('.photo-pagination').find('.active').next();
                if ($.isNumeric(next.text())) {
                    $(this).parent('.photo-pagination').find('a').each(function () {
                        $(this).removeClass('active');
                    });
                    next.addClass('active');
                    $this.find(".photo-gallery-section").empty();
                    get_photos($this, next.text());
                    $this.find('.pagination_previous_page').val(next.text());
                    $this.find('.photo-pagination a[data-value=prev]').removeClass('disabled');
                    // if (next.next().attr('data-value') == 'next') {
                    //     next.next().css('cursor', 'not-allowed');
                    // } else {
                    //     next.next().css('cursor', 'pointer');
                    // }
                }
            }
        }
        $this.find('.photo-pagination a').removeClass('disabled');
        if ($this.find('.photo-pagination a:nth-child(2)').hasClass('active')) {
            $this.find('.photo-pagination a:first').addClass('disabled');
        } else if ($this.find('.photo-pagination a').eq(-2).hasClass('active')) {
            $this.find('.photo-pagination a:last').addClass('disabled');
        }
    });

    $('body').find('.form-plugin-photo-gallery').each(function () {
        get_photos($(this), 1);
    });

    // $('body').on('click', '.photo-gallery-section img', function () {
    // $('body').on('click', '.form-plugin-photo-gallery img', function () {
    //     $('.loader').show();
    //     var photo_id = $(this).closest('.form-plugin-item').attr('data-id');
    //     $.ajax({
    //         url: base_url + '/get-gallery-photo-details/',
    //         type: "GET",
    //         data: {'id': photo_id, 'show_comment': show_comment, 'uploader_name': uploader_name},
    //         success: function (result) {
    //             if (result) {
    //                 var image_src = result.src;
    //                 var html = "<div class='dialogue-content'><div class='dialogue-menu-wrapper'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div><div class='section image-details' data-id='image-details'></div></div></div>";
    //                 $('#dialoge').html(html);
    //                 $("#dialoge .dialoge-menu").append('<li class="active" data-section="image-details" data-id="image-details"><a>'+ lang_image_details_text +'</a><span class="dialoge-menu-close-button"></span></li>');
    //                 $("#dialoge .image-details").append("<div class='full-size-photo'><img class='photo " + result.photo_group + "' style='max-width:100%; max-height:100%;' src='" + image_src + "'></div>");
    //                 if (result.comment.length > 0 && result.uploader.length > 0) {
    //                     $("#dialoge .image-details .full-size-photo").append('<div class="form-plugin-description"><div class="photo-submitter"><label>' + lang_uploader_text + ': </label><span>' + result.uploader + '</span></div><div class="photo-comment"><label>' + lang_comment_text + ': </label><span>' + result.comment + '</span></div></div>');
    //                 } else {
    //                     if (result.comment.length > 0) {
    //                         $("#dialoge .image-details .full-size-photo").append('<div class="form-plugin-description"><div class="photo-comment"><label>' + lang_comment_text + ': </label><span>' + result.comment + '</span></div></div>');
    //                     } else if (result.uploader.length > 0) {
    //                         $("#dialoge .image-details .full-size-photo").append('<div class="form-plugin-description"><div class="photo-submitter"><label>' + lang_uploader_text + ': </label><span>' + result.uploader + '</span></div></div>');
    //                     }
    //                 }
    //                 $('#dialoge').removeClass("_visible").addClass("visible");
    //             }
    //         }
    //     });
    //     $('.loader').hide();
    // });
    $('body').on('click', '.form-plugin-photo-gallery .form-plugin-item', function (e) {
        $('.loader').show();
        var photo_id = $(this).attr('data-id');
        var show_comment = $(this).closest('.form-plugin-photo-gallery').find('.pg_show_comment').val();
        var uploader_name = $(this).closest('.form-plugin-photo-gallery').find('.pg_uploader_name').val();
        var lang_comment_text = $(this).closest('.form-plugin-photo-gallery').find('.comment_lang_text').val();
        var lang_uploader_text = $(this).closest('.form-plugin-photo-gallery').find('.uploader_lang_text').val();
        var lang_image_details_text = $(this).closest('.form-plugin-photo-gallery').find('.image_details_lang_text').val();
        $.ajax({
            url: base_url + '/get-gallery-photo-details/',
            type: "GET",
            data: {'id': photo_id, 'show_comment': show_comment, 'uploader_name': uploader_name},
            success: function (result) {
                if (result) {
                    var image_src = result.src;
                    var html = "<div class='dialogue-content'><div class='dialogue-menu-wrapper'><ul class='dialoge-menu'></ul><div class='close-dialouge'></div></div><div class='section image-details-wrapper' data-id='image-details'></div></div>";
                    $('#dialoge').html(html);
                    $("#dialoge .dialoge-menu").append('<li class="active" data-section="image-details" data-id="image-details"><a>' + lang_image_details_text + '<span class="dialoge-menu-close-button"></span></a></li>');
                    $("#dialoge .image-details-wrapper").append("<div class='image-section'><div class='photo-full-size' style='background-image: url(" + image_src + ")'><img class='photo " + result.photo_group + "' style='max-width:100%; max-height:100%;' src='" + image_src + "'></div></div>");
                    if (result.comment.length > 0 && result.uploader.length > 0) {
                        $("#dialoge .image-details-wrapper").append('<div class="image-details-section"><div class="photo-submitter"><label class="form-question-label">' + lang_uploader_text + ': </label><span class="value">' + result.uploader + '</span></div><div class="photo-comment"><label class="form-question-label">' + lang_comment_text + ': </label><span class="value">' + result.comment + '</span></div></div>');
                    } else {
                        if (result.comment.length > 0) {
                            $("#dialoge .image-details-wrapper").append('<div class="image-details-section"><div class="photo-comment"><label class="form-question-label">' + lang_comment_text + ': </label><span class="value">' + result.comment + '</span></div></div>');
                        } else if (result.uploader.length > 0) {
                            $("#dialoge .image-details-wrapper").append('<div class="image-details-section"><div class="photo-submitter"><label class="form-question-label">' + lang_uploader_text + ': </label><span class="value">' + result.uploader + '</span></div></div>');
                        }
                    }
                    $('#dialoge').removeClass("_visible").addClass("visible");
                }
            }
        });
        $('.loader').hide();
    });
});

function get_photos($this, skip) {
    var full_size_photo = $this.find('.pg_full_size_photo').val();
    var only_my_photos = $this.find('.pg_only_my_photos').val();
    var show_comment = $this.find('.pg_show_comment').val();
    var uploader_name = $this.find('.pg_uploader_name').val();
    var photo_per_page = $this.find('.pg_photo_per_page').val();
    var photo_groups = $this.find('.pg_photo_groups').val();
    var pagination_text = $this.find('.pagination_text').val();
    var element_id = $this.closest('.box').attr('data-id');

    if ($.isNumeric(photo_per_page)) {
        if (parseInt(photo_per_page) < 0) {
            photo_per_page = '';
        }
    }
    var li_list = "";
    if (full_size_photo.length < 1) {
        return;
    }
    $('.loader').show();
    $.ajax({
        url: base_url + '/get-photo-gallery-images/',
        type: "GET",
        data: {
            skip: skip,
            full_size_photo: full_size_photo,
            only_my_photos: only_my_photos,
            show_comment: show_comment,
            uploader_name: uploader_name,
            photo_per_page: photo_per_page,
            photo_groups: photo_groups,
            element_id: element_id
        },
        success: function (result) {
            if (result) {
                if(parseInt(result.all_photo_no) > 0 && $this.find('.photo-pagination').length == 0){
                    var pagination_elm = '<span class="pagination-info"></span>'+
                                        '<div class="photo-pagination pagination">'+
                                        '<a data-value="prev" class="previous pagination-button">'+result.prev_lang+'</a>'+
                                        '<a class="pagination-button">1</a>'+
                                        '<a data-value="next" class="next pagination-button">'+result.next_lang+'</a>'+
                                        '</div>';
                    $this.find('.placeholder.empty').remove();
                    $this.append(pagination_elm);
                }
                if(parseInt(result.all_photo_no)%parseInt(photo_per_page)>0){
                    if(parseInt($this.find('.photo-pagination a.pagination-button').length-2)!=parseInt(parseInt(result.all_photo_no)/parseInt(photo_per_page))+1){
                        $('<a class="pagination-button">'+ parseInt(parseInt(result.all_photo_no)/parseInt(photo_per_page)+1) +'</a>').insertBefore($this.find('.photo-pagination a.pagination-button:last'));
                    }

                }
                $this.find(".form-plugin-list").html(result.photo_items);
                $this.find(".pagination-info").html(pagination_text.replace('{X}', result.from).replace('{Y}', result.to).replace('{Z}', result.all_photo_no));
            }
            $('.loader').hide();
        }
    });
}