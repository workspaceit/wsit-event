$(function () {
    $('body').on('click', '.btn-add-attendee-to-group', function (event) {
        var group_id = $(this).attr('data-group-id');
        showGroupRegistrationSearchModal(group_id);
    });

    $('body').on('click', '.btn-create-new-registration-group', function (event) {
        showGroupRegistrationSearchModal();
    });

    $('body').find(".search-group-registration-attendees").select2({
        tags: true,
        tokenSeparators: [","],
        ajax: {
            multiple: true,
            url: base_url + '/admin/attendee/group-registration-attendee-search/',
            dataType: "json",
            type: "POST",
            data: function (term, page) {
                var data = {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    q: term
                };
                var group_id = $('#group-registration-search-modal').attr('data-group-id');
                var attendee_id = $('#group-registration-search-modal').attr('data-owner-id');
                data['attendee_id'] = attendee_id;
                if (group_id) {
                    data['group_id'] = group_id;
                }
                return data;
            },

            results: function (data, page) {
                return data;
            }
        }
    });

    $('body').on('click', '#btn-add-group-registration-attendee', function (event) {
        var attendees = $('.search-group-registration-attendees').select2('val');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var owner_id = $('#group-registration-search-modal').attr('data-owner-id');
        var $button = $(this);
        var data = {
            attendees: JSON.stringify(attendees),
            owner_id: owner_id,
            csrfmiddlewaretoken: csrf_token
        };
        var group_id = $('#group-registration-search-modal').attr('data-group-id');
        if (group_id) {
            data['group_id'] = group_id;
        }
        if (attendees.length > 0) {
            $('body .loader').show();
            $button.prop("disabled", true);
            $.ajax({
                url: base_url + '/admin/attendee/add-group-registration-attendee/',
                type: "POST",
                data: data,
                success: function (result) {
                    $('body .loader').hide();
                    $button.prop("disabled", false);
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        $('#edit-attendee-registration-group').html(result.group_html);
                        $('#group-registration-search-modal').modal('hide');
                    } else {
                        $.growl.error({message: result.message});
                    }
                }
            });
        } else {
            $.growl.warning({message: 'Please Select Attendee to add'});
        }

    });
    $('body').on('click', '.btn-delete-from-registration-group', function (event) {
        var group_id = $('.btn-add-attendee-to-group').attr('data-group-id');
        var $button = $(this);
        var attendee_id = $button.attr('data-id');
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var current_attendee = $('.attendee-panel-title').attr('data-attendee-id');
        if (attendee_id != undefined) {
            $.ajax({
                url: base_url + '/admin/attendee/delete-group-registration-attendee/',
                type: "POST",
                data: {
                    group_id: group_id,
                    attendee_id: attendee_id,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (result) {
                    if (result.success) {
                        $.growl.notice({message: result.message});
                        if (result.is_empty) {
                            addNewGroupRegistrationHtml($button);
                        } else if (attendee_id == current_attendee) {
                            addNewGroupRegistrationHtml($button);
                        } else {
                            $button.closest('tr').remove();
                        }
                    } else {
                        $.growl.error({message: result.message});
                    }
                }
            });
        } else {
            $.growl.warning({message: 'The Attendee input is None'});
        }
    });

    $('body').on('click', '.show-group-attendee', function (event) {
        var attendee_id = $(this).attr('data-id');
        var url = base_url+'/admin/attendee/#id'+attendee_id;
        window.open(url, '_blank');
    });

    function addNewGroupRegistrationHtml($button) {
        var group_html = '<button type="button" class="btn btn-create-new-registration-group" data-original-title="" title=""><i class="fa fa-plus"></i>&nbsp;&nbsp;Create a new group </button>';
        $button.closest('#edit-attendee-registration-group').html(group_html);
    }


    function showGroupRegistrationSearchModal(group_id) {
        var attendee_id = $('.attendee-panel-title').attr('data-attendee-id');
        $('#group-registration-search-modal').modal();
        $('#group-registration-search-modal').removeAttr('data-owner-id');
        $('#group-registration-search-modal').removeAttr('data-group-id');
        $('.search-group-registration-attendees').select2('val', '');
        $('#group-registration-search-modal').attr('data-owner-id', attendee_id);
        if (group_id) {
            $('#group-registration-search-modal').attr('data-group-id', group_id);
        }
    }

});