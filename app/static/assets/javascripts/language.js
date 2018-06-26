$(function () {
    // Create the tree inside the <div id="tree"> element.
    $("#tree").fancytree({
        activate: function (event, data) {

            // previous code

            var tab = data.node.data.id;
            var activateTab = '#' + tab.toLowerCase();

            $('.tab-content').children('div').attr('class', 'tab-pane');
            $(activateTab).addClass('active');


        },
        beforeSelect: function (event, data) {
            // A node is about to be selected: prevent this for folders:
            if (data.node.isFolder()) {
                return false;
            }
        },
        extensions: ["glyph"],
        glyph: {
            map: {
                checkbox: "fa fa-square-o",
                checkboxSelected: "fa fa-check-square-o",
                checkboxUnknown: "fa fa-square",
                dragHelper: "fa fa-arrow-right",
                dropMarker: "fa fa-long-arrow-right",
                error: "fa fa-warning",
                expanderClosed: "fa fa-plus-square-o",
                expanderLazy: "fa fa-angle-right",
                expanderOpen: "fa fa-minus-square-o",
                nodata: "fa fa-meh-o",
                loading: "fa fa-spinner fa-pulse",
                // Default node icons.
                // (Use tree.options.icon callback to define custom icons based on node data)
                doc: "fa fa-file-o",
                docOpen: "fa fa-file-o",
                folder: "fa fa-folder-o",
                folderOpen: "fa fa-folder-open-o"
            }
        }
    });

    $('body').on('click', '.btn-save-general-language', function () {
        var menus = {};
        var questions = {};
        var options = {};
        var sessions = {};
        var travels = {};
        var locations = {};
        var hotels = {};
        var rooms = {};
        var groups = {};
        var emails = {};
        var submit_buttons = {};
        var pdf_buttons = {};

        var $elem = $('#presetdata');

        $elem.find('.menus-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    console.log(value);
                    menus[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.questions-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    questions[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.lang-option-input').each(function () {
            var id = $(this).attr('data-id');
            var lang_values = {};
            lang_values['id'] = id;
            var key = $(this).attr('data-name');
            var value = $(this).val();
            if (value != "") {
                options[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
            }
        });

        $elem.find('.sessions-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    sessions[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.travels-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    travels[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.locations-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    locations[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.hotels-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    hotels[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.rooms-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    rooms[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.groups-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    groups[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });

        $elem.find('.emails-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    emails[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });
        $elem.find('.submit-buttons-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    submit_buttons[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });
        $elem.find('.pdf-buttons-lang').each(function () {
            var $type_elem = $(this).closest('.tab-pane');
            var id = $type_elem.attr('data-id');
            var $lang = $(this);
            var lang_values = {};
            lang_values['id'] = id;
            $lang.find('.lang-input').each(function () {
                var key = $(this).attr('data-name');
                var value = $(this).val();
                if (value != "") {
                    pdf_buttons[key + '_' + id] = valueWithSpecialLanguageCharacter(value);
                }
            });
        });
        console.log(submit_buttons);
        console.log(JSON.stringify(submit_buttons));

        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var preset_id = $("#preset").val();
        var data = {
            preset_id: preset_id,
            menus: JSON.stringify(menus),
            questions: JSON.stringify(questions),
            options: JSON.stringify(options),
            sessions: JSON.stringify(sessions),
            travels: JSON.stringify(travels),
            locations: JSON.stringify(locations),
            hotels: JSON.stringify(hotels),
            rooms: JSON.stringify(rooms),
            groups: JSON.stringify(groups),
            emails: JSON.stringify(emails),
            submit_buttons: JSON.stringify(submit_buttons),
            pdf_buttons: JSON.stringify(pdf_buttons),
            csrfmiddlewaretoken: csrfToken
        };

        $.ajax({
            url: base_url + '/admin/language/save-general-language/',
            type: "POST",
            data: data,
            ContentType: 'application/x-www-form-urlencoded',
            success: function (response) {
                if (response.success) {
                    $.growl.notice({message: response.message})
                } else {
                    $.growl.error({message: response.message});
                }
            }
        });
    });

    $('body').on('click', '#addPreset', function (event) {
        var hiddenInputSelector = '#preset',
            select2 = $(hiddenInputSelector).data('select2'),
            searchInput = select2.search;

        var preset = $("#preset_name").val()
        var requiredFields = [
            {fieldId: 'preset_name', message: 'Language Name'},
        ];
        if (!requiredFieldValidator(requiredFields)) {
            return;
        }
        if (preset != null) {
            var data = {
                preset: preset,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            };
            var request = $.ajax({
                url: base_url + '/admin/language/add_preset/',
                type: 'POST',
                data: data
            });

            request.done(function (response_data) {
                if (response_data.success) {
                    $.growl.notice({
                        message: response_data.message
                    });
                    $('#preset').append('<option data-value="'+preset+'" value="'+response_data.preset_id+'">'+preset+"("+response_data.preset_id+")"+'</option>');
                    $('#add-preset-modal').modal('toggle')
                } else {
                    $.growl.error({
                        message: response_data.message
                    });
                }

            });

            request.fail(function (jqXHR, textStatus) {
                $.growl.error({message: "Request failed: " + textStatus});

            });

        }
    });
    $('body').on('click', '#renamePreset', function (event) {
        var hiddenInputSelector = '#preset',
            select2 = $(hiddenInputSelector).data('select2'),
            searchInput = select2.search;

        var preset = $("#rename_preset_name").val()
        var preset_id = $("#rename_preset_name").attr('data-id')
        var requiredFields = [
            {fieldId: 'rename_preset_name', message: 'Language Name'},
        ];
        if (!requiredFieldValidator(requiredFields)) {
            return;
        }
        if (preset != null) {
            var data = {
                preset_id: preset_id,
                preset: preset,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            };
            var request = $.ajax({
                url: base_url + '/admin/language/rename_preset_name/',
                type: 'POST',
                data: data
            });

            request.done(function (response_data) {
                if (response_data.success) {
                    $.growl.notice({
                        message: response_data.message
                    });
                    $('#preset option[value="' + preset_id + '"]').text(preset+"("+preset_id+")");
                    $('#preset option[value="' + preset_id + '"]').attr("data-value",preset);
                    $('#rename-preset-modal').modal('toggle')
                    $('#preset').trigger('change');
                } else {
                    $.growl.error({
                        message: response_data.message
                    });
                }

            });

            request.fail(function (jqXHR, textStatus) {
                $.growl.error({message: "Request failed: " + textStatus});

            });

        }
    });

    $('body').on('click', '#delete-preset', function (event) {

        var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var id = $("#preset").val();
        var data = {
            csrfmiddlewaretoken: csrfToken,
            id: id
        };
        bootbox.confirm("Are you sure you want to delete this Preset?", function (result) {
            if (result) {


                var request = $.ajax({
                    url: base_url + '/admin/language/delete_preset/',
                    type: "POST",
                    data: data
                });

                request.done(function (result) {
                    if (result.success) {
                        var id = result.id;
                        $("#preset option[value='" + id + "']").remove();
                        $("#preset").find("option[value=" + id + "]").html()
                        if ($("#preset").find("option[value=" + id + "]").val() == id) {
                            $("#preset").find("option[value=" + id + "]").remove()
                        }
                        $('#preset').select2("val", "")
                        $('#presetdata').html("")
                        $.growl.notify({message: "Preset deleted"});
                    } else {
                        $.growl.error({message: result.message});
                    }
                });

                request.fail(function (jqXHR, textStatus) {
                    $.growl.error({message: "Request failed: " + textStatus});

                });
            } else {
                return;
            }
        });
    });
});
function requiredFieldValidator(requiredFields) {
    var message = '';
    var valid = true;
    for (var i = 0; i < requiredFields.length; i++) {
        var Id = requiredFields[i].fieldId;
        if ($.trim($('#' + Id).val()) == '') {
            message += "*" + requiredFields[i].message + " can't be blank" + "<br>";
            valid = false;
        }
    }

    if (!valid) {
        $.growl.warning({message: message});
    }
    return valid;
}


function valueWithSpecialLanguageCharacter(value) {
    return value.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}