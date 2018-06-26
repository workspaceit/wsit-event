$(function () {
    var $body = $('body');
    var $loader = $('.loader');
    var base_url = window.location.origin;
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $body.on('click', '#btn-all-export', function () {
        $loader.show();
        $.ajax({
            url: base_url + '/admin/export-all/',
            type: "GET",
            data: {},
            success: function (result) {
                $loader.hide();
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.message});
                }
            }
        });
    });

    $body.on('click', "#import-wait-for-response", function () {
        try {
            if ($('#file')[0].files[0] == undefined) {
                return false;
            } else if (!$('#file')[0].files[0].name.endsWith('.xlsx')) {
                $.growl.warning({message: "File must be in excel format."});
                return false;
            }
            var formdata = new FormData();
            formdata.append('upload_file', $('#file')[0].files[0]);
            formdata.append('csrfmiddlewaretoken', csrf_token);
            $loader.show();
            $('#import-wait-for-response').prop('disabled', true);

            $.ajax({
                url: base_url + '/admin/import-from-excel/',
                type: 'POST',
                data: formdata,
                async: false,
                cache: false,
                contentType: false,
                processData: false,
                success: function (result) {
                    $.growl.notice({message: 'Please wait few moment, your request is being processed in lambda.'});
                    import_status(result.id);
                },
                error: function (err) {
                    clog(err);
                    $("#import-excel-modal").modal('hide');
                    $('#import-wait-for-response').prop('disabled', false);
                    $.growl.error({message: "Something went wrong."});
                }
            });
            $loader.hide();
        }
        catch (err) {
            clog(err);
            $loader.hide();
        }

        return false;
    });

    function import_status(id) {
        $.ajax({
            url: base_url + '/admin/import-status-check/',
            type: "POST",
            data: {import_status_id: id, csrfmiddlewaretoken: csrf_token},
            success: function (result) {
                if (result.status == 0) { // which means not done yet
                    setTimeout(function () {
                        import_status(id);
                    }, 4000);
                } else {
                    $loader.hide();
                    window.location.href = base_url + '/admin/render_import_change_page/' + id;
                }
            }
        });
    }


    var import_approve_row;
    $(".btn-view-approve-item").click(function () {
        var id = $(this).attr("data-id");
        import_approve_row = $(this).parent('td').parent('tr');
        $('.loader').show();
        $.ajax({
            url: base_url + '/admin/view-import/' + id + "/",
            type: "GET",
            success: function (result) {
                $('#approve-item .modal-body').html(result);
                $('#approve-item').modal();
                importChangeFunctionalities();
                $('.loader').hide();
            }
        });
    });

    $(document).on('click', '.save-import-change', function (e) {
        $('.loader').show();
        var element_id = $(this).attr("data-save-for");
        var data_name = $(this).attr("data-name");
        var all_attribute = [];
        $(".alldata:checked").each(function () {
            var new_attribue = {};
            new_attribue['attendee_id'] = $(this).attr("data-att-id");
            new_attribue['attribute_id'] = $(this).attr("data-attribute-id");
            new_attribue['attribute_name'] = $(this).attr("data-attribute-name");
            new_attribue['new_value'] = $(this).attr("data-val");
            new_attribue['defination'] = $(this).attr("data-attribute-defination");
            all_attribute.push(new_attribue)
        });
        $.ajax({
            url: base_url + '/admin/save-import/',
            data: {
                id: element_id,
                data_name: data_name,
                data: JSON.stringify(all_attribute),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            type: "POST",
            success: function (result) {
                if (result.result) {
                    $('#approve-item').modal('hide');
                    import_approve_row.remove();
                    $.growl.notice({message: result.message});
                    $("#import-save-progressbar").progressbar({
                        value: 0
                    });
                    $('.loader').hide();
                    get_import_saving_stats();
                }
            }
        });

    });

    function get_import_saving_stats() {
        $.ajax({
            url: base_url + '/admin/get-import-save-stats/',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            type: "POST",
            success: function (result) {
                if (result.complete) {
                    $.growl.notice({message: "Import Completed"});
                    $("#import-save-progressbar").hide();
                } else {
                    $("#import-save-progressbar").progressbar({
                        value: result.percentage
                    });
                    setTimeout(function () {
                        get_import_saving_stats();
                    }, 2000);
                }
            }
        });
    }

    $(document).on('click', '.btn-delete-import-file', function (e) {
        $('.loader').show();
        var element_id = $(this).attr("data-id");
        var element = $(this);
        var all_attribute = [];
        $.ajax({
            url: base_url + '/admin/delete-import-changes/',
            data: {
                id: element_id,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            type: "POST",
            success: function (result) {
                $('.loader').hide();
                if (result.success) {
                    $.growl.notice({message: result.success});
                    element.parent().parent().remove();
                }
                else {
                    $.growl.error({message: result.error});
                }
            }
        });

    });

    function importChangeFunctionalities() {
        $('#selecctall').click(function (event) {  //on click
            if (this.checked) { // check select status
                $('.allselect').each(function () { //loop through each checkbox
                    this.checked = true;  //select all checkboxes with class "checkbox1"
                });
            } else {
                $('.allselect').each(function () { //loop through each checkbox
                    this.checked = false; //deselect all checkboxes with class "checkbox1"
                });
            }
        });

        $('#question-all').click(function (event) {  //on click
            if (this.checked) { // check select status
                $('.question').each(function () { //loop through each checkbox
                    this.checked = true;  //select all checkboxes with class "checkbox1"
                });
            } else {
                $('.question').each(function () { //loop through each checkbox
                    this.checked = false; //deselect all checkboxes with class "checkbox1"
                });
            }
        });

        $('#session-all').click(function (event) {  //on click
            if (this.checked) { // check select status
                $('.session').each(function () { //loop through each checkbox
                    this.checked = true;  //select all checkboxes with class "checkbox1"
                });
            } else {
                $('.session').each(function () { //loop through each checkbox
                    this.checked = false; //deselect all checkboxes with class "checkbox1"
                });
            }
        });

        $('#travel-all').click(function (event) {  //on click
            if (this.checked) { // check select status
                $('.travel').each(function () { //loop through each checkbox
                    this.checked = true;  //select all checkboxes with class "checkbox1"
                });
            } else {
                $('.travel').each(function () { //loop through each checkbox
                    this.checked = false; //deselect all checkboxes with class "checkbox1"
                });
            }
        });

        $('.selection').click(function (event) {  //on click

            if (this.checked) { // check select status
                $(this).parent().siblings()
                    .find("input[type='checkbox']")
                    .prop('checked', this.checked);
            } else {
                $(this).parent().siblings()
                    .find("input[type='checkbox']")
                    .prop('checked', false);
            }
            event.stopPropagation();
        });
    }

});

function onSubmit_scanExport() {
    try {
        $('.loader').show();
        $.ajax({
            url: base_url + '/admin/export-scanlist/',
            type: "POST",
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (result) {
                $('.loader').hide();
                $.growl.notice({message: result.msg});
                check_export_status();
            }
        });
    } catch (err) {
    }
    return false;
}
