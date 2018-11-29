$(function () {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var $rebate_tr;

    $('body').on('click', '.btn-edit-rebate', function () {
        var $this = $(this);
        showRebateDetails($this);
    });

    $('body').on('click', '.btn-view-rebate', function () {
        var $this = $(this);
        showRebateDetails($this);
        $("body #add-rebate-modal").find("input, select").attr('disabled', 'disabled');
    });

    function showRebateDetails($this) {
        var $modal = $("#add-rebate-modal");
        var rebate_id = $this.attr('data-id');
        var name = $this.closest('tr').find('.rbt-name-val').text(),
            item_id = $this.closest('tr').find('.rbt-item-type-id').val(),
            rebate_type = $this.closest('tr').find('.rbt-rebatetype-val').text(),
            value = $this.closest('tr').find('.rbt-value-val').text();

        var json_obj = JSON.parse(item_id)
        var sessions = json_obj.sessions
        var travels = json_obj.travels
        var rooms = json_obj.rooms
        var all_values = []
        for (i = 0; i < sessions.length; i++) {
            all_values.push("session-" + sessions[i])
        }
        for (i = 0; i < travels.length; i++) {
            all_values.push("travel-" + travels[i])
        }
        for (i = 0; i < rooms.length; i++) {
            all_values.push("room-" + rooms[i])
        }

        $modal.find('#rebate-name').val(name);
        $modal.find('#rebate-for').selectpicker('val', all_values);
        $modal.find('#rebate-type').val(rebate_type);
        $modal.find('#rebate-value').val(value);
        $modal.find('.rebate-id-for-edit').val(rebate_id);
        $modal.modal('toggle');
        $rebate_tr = $this.closest('tr');
    }

    $('body').on('submit', '#add-edit-rebate-form', function (e) {
        e.preventDefault();
        var name = $('#rebate-name').val(), item_id = $('#rebate-for').val(), rebate_type = $('#rebate-type').val(), value = $('#rebate-value').val();

        var validation_msg = '';
        var rebate_id = $('.rebate-id-for-edit').val();
        if (name.length < 1) {
            validation_msg += '* Rebate name is required.<br>';
        }
        if (item_id == undefined) {
            validation_msg += '* Rebate for is required.<br>';
        } else if (item_id.length < 1) {
            validation_msg += '* Rebate for is required.<br>';
        }
        if (rebate_type == undefined) {
            validation_msg += '* Rebate type is required.<br>';
        } else if (rebate_type.length < 1) {
            validation_msg += '* Rebate type is required.<br>';
        }
        if (value == 0) {
            validation_msg += '* Rebate amount is required.<br>';
        }
        if (validation_msg.length > 0) {
            $.growl.warning({message: validation_msg});
        } else {
            $.ajax({
                url: base_url + '/admin/economy/rebate/add-edit-rebate/',
                type: "POST",
                data: {
                    name: name,
                    item_id: JSON.stringify(item_id),
                    rebate_type: rebate_type,
                    value: value,
                    rebate_id: rebate_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (response) {
                    if (response.success) {
                        if (rebate_id == '') {
                            var edit_button = '<button class="btn btn-xs btn-edit-rebate" data-id="' + response.rebate.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i> </button>';
                            var delete_button = '<button class="btn btn-xs btn-danger btn-delete-rebate" data-id="' + response.rebate.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>';
                            var actions = edit_button + delete_button;
                            $('#rebate-table').find('tbody').append('<tr><td class="rbt-name-val">' + response.rebate.name
                                + '</td><input type="hidden" value="" class="rbt-item-type-id"/> <td class="rbt-rebatetype-val">'
                                + response.rebate.rebate_type + '</td> <td class="rbt-value-val">' + response.rebate.value
                                + '</td> <td>' + actions + '</td> </tr>');
                            $('#rebate-table').find('tbody tr:last-child').find('.rbt-item-type-id').val(response.rebate.type_id);
                        } else {
                            $rebate_tr.find('.rbt-name-val').text(response.rebate.name);
                            $rebate_tr.find('.rbt-item-type-id').val(response.rebate.type_id);
                            $rebate_tr.find('.rbt-rebatetype-val').text(response.rebate.rebate_type);
                            $rebate_tr.find('.rbt-value-val').text(response.rebate.value);
                        }
                        $.growl.notice({message: response.msg});
                        $("#add-rebate-modal").modal('toggle');
                    } else {
                        $.growl.error({message: response.msg});
                    }
                }
            });
        }
    });

    $('body').on('click', '.btn-delete-rebate', function () {
        return;
        var $this = $(this);
        bootbox.confirm("Are you sure you want to delete this Rebate?", function (result) {
            if (result) {
                var id = $this.attr('data-id');
                $.ajax({
                    url: base_url + '/admin/economy/rebate/delete-rebate/',
                    type: "POST",
                    data: {
                        rebate_id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (response) {
                        if (response.success) {
                            $.growl.notice({message: response.msg});
                            $this.parent().parent().html('');
                        } else {
                            $.growl.error({message: response.msg});
                        }
                    }
                });
            }
        });
    });

    $('.download-all-event-pdf').click(function () {
        $.ajax({
            url: base_url + '/admin/economy/export/check-export-status/',
            type: "POST",
            data: {
                status_type: "export-request",
                pdf_type: $(this).attr('data-type'),
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.export) {
                    $.growl.notice({message: response.message});
                    $('.loader').show();
                    setTimeout(function () {
                        export_complete_checking();
                    }, 5000);
                } else {
                    $.growl.warning({message: response.message});
                    if(response.download_request){
                        window.open(base_url + "/admin/economy/export/download-zipfile/", '_blank');
                    }
                }
            }
        });
    });

    function export_complete_checking() {
        $.ajax({
            url: base_url + '/admin/economy/export/check-export-status/',
            type: "POST",
            data: {
                status_type: "export-complete",
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.complete) {
                    $('.loader').hide();
                    $.growl.notice({message: response.message});
                    // window.location = base_url + "/admin/economy/export/download-zipfile/";
                    window.open(base_url + "/admin/economy/export/download-zipfile/", '_blank');
                }else{
                    setTimeout(function () {
                        export_complete_checking();
                    }, 5000);
                }
            }
        });
    }

});