$(function () {
    var $body = $('body');
    $body.find('.hotel-table tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.hotel-table').attr('id');
                allRowOrder = [];
                var count = 0;
                $('#' + group + ' tbody tr').each(function () {
                    var room_id = $(this).children('td:first').attr('data-id');
                    if (room_id != '&nbsp;') {
                        id = parseInt(room_id);
                        count++;
                        rowOrder = {'order': count, 'room_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/rooms_order/',
                        type: "POST",
                        data: {
                            rooms_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    // $body.find('#edit-session-queue tbody')
    //     .sortable({
    //         revert: true,
    //         connectWith: ".sortable",
    //         stop: function (event, ui) { /* do whatever here */
    //             var session_id = $(this).closest('#edit-session-queue').attr('data-id');
    //             queueRowOrder = [];
    //             var count = 0;
    //             $('#edit-session-queue tbody tr').each(function () {
    //                 var seminar_id = $(this).find('#btn-remove-session-queue').attr('data-id');
    //                 count++;
    //                 rowOrder = {'order': count, 'seminar_id': seminar_id};
    //                 queueRowOrder.push(rowOrder);
    //
    //             });
    //             console.log(queueRowOrder);
    //             if (queueRowOrder.length > 0) {
    //                 var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    //                 $.ajax({
    //                     url: base_url + '/admin/sessions/queue_order/',
    //                     type: "POST",
    //                     data: {
    //                         queue_order: JSON.stringify(queueRowOrder),
    //                         session_id: session_id,
    //                         csrfmiddlewaretoken: csrf_token
    //                     },
    //                     success: function (result) {
    //                         if (result.error) {
    //                             $.growl.error({message: result.error});
    //                             setTimeout(function () {
    //                                 window.location.href = '';
    //                             }, 1000);
    //                         } else {
    //                             $.growl.notice({message: result.success});
    //
    //                         }
    //                     }
    //                 });
    //             }
    //         }
    //     });


    $body.find('.settings-groups-table tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.settings-groups-table').attr('id');
                var type = group.split("-")[1];
                groupRowOrder = [];
                var count = 0;
                $('#' + group + ' tbody tr').each(function () {
                    var group_id = $(this).children('td:first').find('input[type=checkbox]').attr('data-id');
                    clog(group_id);
                    if (group_id != '&nbsp;') {
                        id = parseInt(group_id);
                        count++;
                        rowOrder = {'order': count, 'group_id': id};
                        groupRowOrder.push(rowOrder);
                    }

                });
                if (groupRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/groups_order/',
                        type: "POST",
                        data: {
                            groups_order: JSON.stringify(groupRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
//                                $.growl.notice({message: result.success});
//                                setTimeout(function () {
//                                    window.location.href = '';
//                                }, 3000);
                            }
                        }
                    });
                }
            }
        });

//    $body.find('#edit-travel-queue tbody')
//        .sortable({
//            revert: true,
//            connectWith: ".sortable",
//            stop: function (event, ui) { /* do whatever here */
//                var session_id = $(this).closest('#edit-session-queue').attr('data-id');
//                queueRowOrder = [];
//                var count = 0;
//                $('#edit-session-queue tbody tr').each(function () {
//                    var seminar_id = $(this).find('#btn-remove-session-queue').attr('data-id');
//                    count++;
//                    rowOrder = {'order': count, 'seminar_id': seminar_id};
//                    queueRowOrder.push(rowOrder);
//
//                });
//                console.log(queueRowOrder);
//                if (queueRowOrder.length > 0) {
//                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
//                    $.ajax({
//                        url: base_url + '/admin/sessions/queue_order/',
//                        type: "POST",
//                        data: {
//                            queue_order: JSON.stringify(queueRowOrder),
//                            session_id: session_id,
//                            csrfmiddlewaretoken: csrf_token
//                        },
//                        success: function (result) {
//                            if (result.error) {
//                                $.growl.error({message: result.error});
//                            } else {
//                                $.growl.notice({message: result.success});
//
//                            }
//                        }
//                    });
//                }
//            }
//        });


    $body.find('.showQuestions tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.showQuestions').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('table').find('tbody tr').each(function () {
                    var question_id = $.trim($(this).children('td:first').html());
                    if (question_id != '&nbsp;') {
                        var id = parseInt(question_id);
                        count++;
                        var rowOrder = {'order': count, 'question_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/questions/question_order/',
                        type: "POST",
                        data: {
                            questions_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    $body.find('.data-table-location tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.data-table-location').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('table').find('tbody tr').each(function () {
                    var location_id = $.trim($(this).children('td:first').html());
                    if (location_id != '&nbsp;') {
                        var id = parseInt(location_id);
                        count++;
                        var rowOrder = {'order': count, 'location_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/locations/location_order/',
                        type: "POST",
                        data: {
                            locations_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    $body.find('.seminar-table tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.seminar-table').closest('.dataTables_wrapper').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('div').find('table').find('tbody tr').each(function () {
                    var session_id = $.trim($(this).children('td:first').html());
                    clog(session_id);
                    if (session_id != '&nbsp;') {
                        var id = parseInt(session_id);
                        count++;
                        var rowOrder = {'order': count, 'session_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                clog(allRowOrder.length);
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/sessions/session_order/',
                        type: "POST",
                        data: {
                            sessions_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    $body.find('.data-table-filter tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.data-table-filter').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('table').find('tbody tr').each(function () {
                    var filter_id = $.trim($(this).children('td:first').html());
                    if (filter_id != '&nbsp;') {
                        var id = parseInt(filter_id);
                        count++;
                        var rowOrder = {'order': count, 'filter_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/filters/filter_order/',
                        type: "POST",
                        data: {
                            filters_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    $body.find('.travel-table tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.travel-table').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('table').find('tbody tr').each(function () {
                    var travel_id = $.trim($(this).children('td:first').html());
                    if (travel_id != '&nbsp;') {
                        var id = parseInt(travel_id);
                        count++;
                        var rowOrder = {'order': count, 'travel_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/travels/travel_order/',
                        type: "POST",
                        data: {
                            travels_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });

    $body.find('.data-table-filter-export tbody')
        .sortable({
            revert: true,
            connectWith: ".sortable",
            stop: function (event, ui) { /* do whatever here */
                var group = $(this).closest('.data-table-filter-export').prev('.table-header').attr('id');
                var allRowOrder = [];
                var count = 0;
                $('#' + group).next('table').find('tbody tr').each(function () {
                    var filter_export_id = $.trim($(this).children('td:first').html());
                    if (filter_export_id != '&nbsp;') {
                        var id = parseInt(filter_export_id);
                        count++;
                        var rowOrder = {'order': count, 'filter_export_id': id};
                        allRowOrder.push(rowOrder);
                    }

                });
                if (allRowOrder.length > 0) {
                    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                    $.ajax({
                        url: base_url + '/admin/export-filter/export_order/',
                        type: "POST",
                        data: {
                            filter_export_order: JSON.stringify(allRowOrder),
                            csrfmiddlewaretoken: csrf_token
                        },
                        success: function (result) {
                            if (result.error) {
                                $.growl.error({message: result.error});
                                setTimeout(function () {
                                    window.location.href = '';
                                }, 1000);
                            } else {
                                $.growl.notice({message: result.success});
                            }
                        }
                    });
                }
            }
        });


});