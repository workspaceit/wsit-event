var base_url = window.location.origin;
var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
$('body').on('click', '.allow_btn', function (event) {
//    alert($(this).attr('data-photoId'));
    var photoId = $(this).attr('data-photoId');
    var page_name = $("#pagename").attr('data-val');
    var this_btn = $(this);

    var current_li = $(this).parent().parent();
    $.ajax({
        url: base_url + '/admin/change-photo-status/',
        type: "POST",
        data: {
            changestatus: 1,
            id: photoId,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.success});
                if (page_name == 'all') {
//                    this_btn.remove();
                    delete_button = ' <button class="btn btn-xs delete_btn btn-danger" data-photoId="' + photoId + '"><i class="fa fa-times-circle"></i></button> ';
                    deny_button = ' <button class="btn btn-xs deny_btn " data-photoId="' + photoId + '"><i class="fa fa-ban"></i></button> ';
                    this_btn.parent().html(deny_button + delete_button);
                }
                else {
                    current_li.remove();
                    clog(pagename);
                }

            }
            else {
                clog(result.error);
                $.growl.error({message: "Failed to update!!!"});
            }
        }
    });
});

$('body').on('click', '.deny_btn', function (event) {
//    alert($(this).attr('data-photoId'));
    var photoId = $(this).attr('data-photoId');
    var current_li = $(this).parent().parent();
    var page_name = $("#pagename").attr('data-val');
    var this_btn = $(this);
    $.ajax({
        url: base_url + '/admin/change-photo-status/',
        type: "POST",
        data: {
            changestatus: 2,
            id: photoId,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.success});
                if (page_name == 'all') {
                    delete_button = ' <button class="btn btn-xs delete_btn btn-danger" data-photoId="' + photoId + '"><i class="fa fa-times-circle"></i></button> ';
                    allow_button = ' <button class="btn btn-xs allow_btn btn-success" data-photoId="' + photoId + '" ><i class="fa fa-check"></i></button> ';
                    this_btn.parent().html(allow_button + delete_button);
                }
                else {
                    current_li.remove();
                    clog(pagename);
                }
            }
            else {
                clog(result.error);
                $.growl.error({message: "Failed to update!!!"});
            }
        }
    });
});

$('body').on('click', '.delete_btn', function (event) {
    var photoId = $(this).attr('data-photoId');
    var current_li = $(this).parent().parent();
    $.ajax({
        url: base_url + '/admin/delete-photo/',
        type: "POST",
        data: {
            id: photoId,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (result) {
            if (result.success) {
                $.growl.notice({message: result.success});
                current_li.remove();
            }
            else {
                clog(result.error);
                $.growl.error({message: "Failed to Delete!!!"});
            }
        }
    });
});


$(function () {

    $(".photo-table").dataTable({
        "paging": false,
        "ordering": false,
        "info": false,
        "searching": false,
        "autoWidth": false,
    });
    $('.table-header').closest('.clearfix').hide();
});