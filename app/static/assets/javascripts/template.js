$(function () {
    var $body = $('body');
    $body.on('click', '.btn-delete-template', function (event) {
        var $this = $(this);
        bootbox.confirm("Are you sure you want to delete this Template?", function (result) {
            if (result) {
                var id = $this.attr('data-id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/templates/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else if (result.warning) {
                            $.growl.warning({message: result.warning});
                        } else {
                            $.growl.notice({message: result.success});
                            $this.closest('tr').remove();
                        }
                    }
                });
            }
        });
    });

    $body.on('click', '#btn-add-template', function () {
        var fieldsToClear = [
            'template_name', 'template_category'
        ];
        clearTemplateForm(fieldsToClear);
        $('#btn-save-template').show();
        $('#btn-update-template').hide();
        $('#templates-edit-template').find('.modal-title').html('Add New Template');
        $('#templates-edit-template').modal();

    });

    $body.on('click', '.btn-edit-template', function () {
        var template_id = $(this).data('id');
        showTemplateDetails(template_id);
    });

    $body.on('click', '.btn-view-template', function () {
        var template_id = $(this).data('id');
        showTemplateDetails(template_id);
        $("body #templates-edit-template").find("input, select").attr('disabled', 'disabled');
    });

    function showTemplateDetails(template_id) {
        $('#edit-template-id').val(template_id);
        $.ajax({
            url: base_url + '/admin/templates/edit/' + template_id + '/',
            type: "GET",
            success: function (response) {
                if (response.success) {
                    var template = response.template;
                    $('#template_name').val(template.name);
                    $('#template_category').select2('val', template.category);
                    $('#template_category').attr('data-category', template.category);
                    $('#btn-save-template').hide();
                    $('#btn-update-template').show();
                    $('#templates-edit-template').find('.modal-title').html('Edit Template');
                    $('#templates-edit-template').modal();
                }
                else {
                    var errors = response.message;
                }
            },
            error: function () {
                //alert();
            }
        });
    }

    function clearTemplateForm(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).select2("val", "");
        }
        $('#is-login-required').prop('checked', false);
    }

    $body.on('click', '#btn-save-template', function () {
        addOrUpdateTemplate($(this));
    });

    $body.on('click', '#btn-update-template', function () {
        addOrUpdateTemplate($(this));
    });

    function requiredFieldValidator(requiredFields) {
        var message = '';
        var valid = true;
        for (var i = 0; i < requiredFields.length; i++) {
            var Id = requiredFields[i].fieldId;
            if ($('#' + Id).val() == '' || $('#' + Id).val() == null) {
                message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
                valid = false;
            }
        }
        if (!valid) {
            $.growl.warning({message: message});
        }
        return valid;
    }

    function addOrUpdateTemplate(button) {

        var template_name = slug($('#template_name').val()),
            template_category = $('#template_category').val(),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val()

        var requiredFields = [
            {fieldId: 'template_name', message: 'Template Name'},
            {fieldId: 'template_category', message: 'Template Category'}
        ];
        clog(template_name);

        if (!requiredFieldValidator(requiredFields)) {
            return;
        }

        var data = {
            template_name: template_name,
            template_category: template_category,
            csrfmiddlewaretoken: csrfToken
        };
        if (button.attr('id') == 'btn-update-template') {
            var template_id = $('#edit-template-id').val();
            data['id'] = template_id;
        }

        $.ajax({
            url: base_url + '/admin/templates/',
            type: 'POST',
            data: data,
            success: function (response) {
                if (response.success) {
                    var updated_template = response.template;
                    var row = '' +
                        '<td>' + updated_template.id + '</td>' +
                        '      <td>' + updated_template.name + '</td>' +
                        '      <td>' +
                        '          <button class="btn btn-xs btn-edit-template" data-id="' + updated_template.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Template Settings"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '          <a href="' + base_url + '/admin/templates/' + updated_template.id + '" target="_blank" class="btn btn-xs btn-edit-content" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit Template"><i class="dropdown-icon fa fa-pencil"></i></a>' +
                        '          <button class="btn btn-xs btn-danger btn-delete-template" data-id="' + updated_template.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '      </td>';
                    if (button.attr('id') === 'btn-update-template') {
                        var old_category = $('#template_category').attr('data-category')
                        if (old_category == updated_template.category) {
                            $('body .data-table-templates tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_template.id) {
                                    $(this).html(row);
                                }
                            });
                        } else {
                            $('body .data-table-templates tbody tr').each(function () {
                                if ($(this).find('td:first-child').html() == updated_template.id) {
                                    $(this).remove();
                                }
                            });
                            $('body #template_' + updated_template.category).find('tbody').append('<tr>' + row + '</tr>');
                        }
                    } else {
                        $('body #template_' + updated_template.category).find('tbody').append('<tr>' + row + '</tr>');
                    }
                    $.growl.notice({message: response.message});
                    $('#templates-edit-template').modal('hide');
                }
                else {
                    $.growl.error({message: response.message});
                }
            },
            error: function (e) {
            }

        });
    }

    var slug = function (str) {
        var $slug = '';
        var trimmed = $.trim(str);
        $slug = trimmed.replace(/[^a-z0-9-]/gi, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
        return $slug.toLowerCase();
    }

});