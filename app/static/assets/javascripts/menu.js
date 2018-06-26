$(function () {
    $(".menu-rule-selector").select2({
        placeholder: "Select a question"
    });
    $('#menu-start-date').datepicker('setDate', new Date());
    $('#menu-end-date').datepicker('setDate', new Date());
    //$('#menu-rule').select2().on('select2-selecting',function(e){
    //    if(e.object.css=='quick-filter'){
    //        $.ajax({
    //            url: base_url + '/admin/filters/quick_filter_exists/',
    //            success: function (response) {
    //                if (response.status) {
    //                    var modal_class = 'filters-add-filter';
    //                    $('#quick-save-div').show();
    //                    $('#filter-grp-div').hide();
    //                    $('#preset-name-div').hide();
    //                    showQuickFilterData(response.filter.id, modal_class);
    //                } else {
    //                    $('#quick-save-div').show();
    //                    $('#filter-grp-div').hide();
    //                    $('#preset-name-div').hide();
    //
    //                    $('#btn-update-quick-filter').show();
    //                    $('#btn-update-filter').hide();
    //                    $('.any-or-all').val(1);
    //                    $('#filters-add-filter').find('.modal-title').html('Quick Filter');
    //                    $('#preset_filter_group').select2('val', '');
    //
    //                    $('.filter-panel-title').html("New Filter");
    //                    $('#filters-add-filter').modal('show');
    //                    $('#preset_name').attr('data-id', '');
    //                    var rowCount = 0;
    //                    $('.filter-list').html($('#filter-li-html').html());
    //                    activeDatePicker();
    //
    //
    //                }
    //            }
    //        });
    //    }
    //
    //});
    $('.quick-filter-btn').click(function () {

        $.ajax({
            url: base_url + '/admin/filters/quick_filter_exists/',
            success: function (response) {
                if (response.status) {
                    var modal_class = 'filters-add-filter';
                    $('#quick-save-div').show();
                    $('#filter-grp-div').hide();
                    $('#preset-name-div').hide();
                    var name = "menu";
                    showQuickFilterData(response.filter.id, modal_class, name);
                } else {
                    $('#quick-save-div').show();
                    $('#filter-grp-div').hide();
                    $('#preset-name-div').hide();

                    $('#btn-update-quick-filter').show();
                    $('#btn-update-filter').hide();
                    $('.any-or-all').val(1);
                    $('#filters-add-filter').find('.modal-title').html('Quick Filter');
                    $('#preset_filter_group').select2('val', '');

                    $('.filter-panel-title').html("New Filter");
                    $('#filters-add-filter').modal('show');
                    $('#preset_name').attr('data-id', '');
                    var rowCount = 0;
                    $('.filter-list').html($('#filter-li-html').html());
                    activeDatePicker();


                }
            }
        });
    });

    $body.on('click', '#btn-add-menuitem', function () {
        var fieldsToClear = [
            'menu-title', 'menu-parent', 'menu-url', 'menu-content'
        ];
        clearForm(fieldsToClear);

        $('#menu-start-date').data('datepicker').setDate(new Date());
        $('#menu-end-date').data('datepicker').setDate($("#event-end-date").val());
        $('#menu-start-time').val('00:00');
        $('#menu-end-time').val('23:59');

        $.ajax({
            url: base_url + '/admin/menus/get-parents/',
            type: "GET",
            success: function (response) {
                if (response.success) {
                    var parent_items = response.parent_items;
                    var options = "";
                    options += "<option value=''></option>";
                    for (i = 0; i < parent_items.length; i++) {
                        options += "<option value=" + parent_items[i].id + ">" + parent_items[i].title + "</option>";
                    }
                    $('#menu-parent').html(options);
                    $('#menu-rule').select2();
                    $('#menu-rule').select2("val", "");
                    $('#btn-save-menuitem').show();
                    $('#btn-update-menuitem').hide();
                    $('#content').hide();
                    $('#menus-edit-item').find('.modal-title').html('Add Menu Item');
                    $('#menus-edit-item').modal();
                }
                else {
                    var errors = response.message;
                }
            },
            error: function (error) {
                console.log(error);
            }
        });


    });

    $('#menu-start-date').click(function () {
        $('#menu-start-date').data('datepicker').setDate($('#menu-start-date').val());
    });
    $('#menu-end-date').click(function () {
        $('#menu-end-date').data('datepicker').setDate($('#menu-end-date').val());
    });

    $("#menu-start-time").click(function () {
        $('#menu-start-time').timepicker('setTime', $('#menu-start-time').val());
    });
    $("#menu-end-time").click(function () {
        $('#menu-end-time').timepicker('setTime', $('#menu-end-time').val());
    });

    $('#menu-rule').attr('placeholder', 'Select a Permission Group');

    $("#menu-content-type").change(function () {
        type = $(this).val()
        if (type == "url") {
            $('#content').hide();
            $('#menu-uid-include').prop('checked', false);
            $('#menu-accept-login').prop('checked', false);
            $('#uid_include').hide();
            $('#accept_login').hide();
            $('#menu-content').val('');
            $('#menu-url').val('');
            $('#url').show();


        } else if (type == "page_content") {
            $('#content').show();
            $('#uid_include').show();
            $('#accept_login').show();
            $('#url').hide();
            $('#menu-url').val('');
            $('#menu-content').val('');
        }
    });

    function clearForm(fieldsToClear) {
        for (var i = 0; i < fieldsToClear.length; i++) {
            var Id = fieldsToClear[i];
            $('#' + Id).val('');
        }
        $('#menu-start-date').data('datepicker').setDate(null);
        $('#menu-end-date').data('datepicker').setDate(null);
        $('#menu-visibility').attr('checked', true);
        $('#menu-availability').attr('checked', false);
        $('#allow-unregistered').attr('checked', false);
        $('#menu-uid-include').attr('checked', false);
        $('#menu-accept-login').attr('checked', false);
        $('#menu-only-speaker').attr('checked', false);
        $('.menu-language-preset-selector').select2("val", "");
        $('.language-preset-selector').hide();

    }

    $body.on('click', '.btn-edit-menu', function () {
        var fieldsToClear = [
            'menu-title', 'menu-parent', 'menu-url', 'menu-content'
        ];
        clearForm(fieldsToClear);
        var menuitem_id = $(this).data('id');
        showMenuDetails(menuitem_id);
    });

    $body.on('click', '.btn-view-menu', function () {
        var fieldsToClear = [
            'menu-title', 'menu-parent', 'menu-url', 'menu-content'
        ];
        clearForm(fieldsToClear);
        var menuitem_id = $(this).data('id');
        showMenuDetails(menuitem_id);
        $("body #menus-edit-item").find("input, select").attr('disabled', 'disabled');
    });

    function showMenuDetails(menuitem_id) {
        $('.language-preset-selector').show();
        $('#menuitem-id').val(menuitem_id);
        $.ajax({
            url: base_url + '/admin/menuitems/' + menuitem_id + '/',
            type: "GET",
            success: function (response) {

                if (response.success) {
                    var current_language_id = response.current_language_id;
                    default_language_id = current_language_id;
                    $('.menu-language-presets-selector').select2('val',current_language_id);
                    var menuitem = response.menuitem;
                    menu_language = response.menuitem;
                    var groups = response.groups;
                    clog(groups);
                    var start = menuitem.start_time
                    var end = menuitem.end_time
                    var start_date = moment(start).format('MM/DD/YYYY'),
                        end_date = moment(end).format('MM/DD/YYYY');

                    var start_time = moment(start).format('HH:mm');
                    var end_time = moment(end).format('HH:mm');

                    var parent_items = response.parent_items;
                    manu_parent_items_language = response.parent_items;
                    var options = "";
                    options += "<option value=''></option>";
                    for (i = 0; i < parent_items.length; i++) {
                        options += "<option value=" + parent_items[i].id + ">" + getcontentByLanguage(parent_items[i].title, parent_items[i].title_lang, current_language_id) + "</option>";
                    }
                    $('#menu-parent').html(options);
                    $('#menu-title').val(getcontentByLanguage(menuitem.title, menuitem.title_lang, current_language_id));
                    $('#menu-parent').val(menuitem.parent.id);

                    if (menuitem.url != null) {
                        $('#menu-content-type').val("url");
                        $('#menu-url').val(menuitem.url);
                        $('#url').show();
                        $('#content').hide();
                        $('#uid_include').hide();
                        $('#accept_login').hide();
                    }
                    if (menuitem.content.id != null) {
                        $('#menu-content-type').val("page_content");
                        $('#menu-content').val(menuitem.content.id);
                        $('#url').hide();
                        $('#content').show();
                        $('#uid_include').show();
                        $('#accept_login').show();
                    }

                    $('#menu-start-date').val(start_date);
                    $('#menu-start-date').datepicker('setDate', new Date(start_date));
                    $('#menu-start-time').val(start_time);
                    $('#menu-end-date').val(end_date);
                    $('#menu-end-date').datepicker('setDate', new Date(end_date));
                    $('#menu-end-time').val(end_time);

                    $('#menu-rule').select2('data', groups);
                    $('#menu-visibility').prop('checked', menuitem.is_visible);
                    $('#menu-availability').prop('checked', menuitem.available_offline);
                    $('#allow-unregistered').prop('checked', menuitem.allow_unregistered);
                    $('#menu-uid-include').prop('checked', menuitem.uid_include);
                    $('#menu-accept-login').prop('checked', menuitem.accept_login);
                    $('#menu-only-speaker').prop('checked', menuitem.only_speaker);


                    $('#btn-save-menuitem').hide();
                    $('#btn-update-menuitem').show();
                    $('#menus-edit-item').find('.modal-title').html('Edit Menu Item');
                    $('#menus-edit-item').modal();


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

    $body.on('click', '.btn-delete-menu', function () {
        var menuitem_id = $(this).data('id');
        var $this = $(this);
        $('#menuitem-id').val(menuitem_id);
        bootbox.confirm("Are you sure you want to delete this Menu item?", function (result) {
            if (result) {
                var id = menuitem_id;
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/menuitem/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (response) {
                        if (response.success) {
                            $.growl.notice({message: response.success});
                            if ($this.closest('li').find('ol')) {
                                $this.closest('li').find('ol').children('li').each(function () {
                                    ($(this)).insertBefore($this.closest('li'));
                                });
                                $this.closest('li').remove();
                            } else {
                                $this.closest('li').remove();
                            }
                        }
                        else {
                            $.growl.error({message: response.error});
                        }
                    }
                });
            }
        });
    });

    function addOrUpdateMenuItem(button) {
        var visibility = $('#menu-visibility').prop('checked');
        var is_visible = 0;
        if (visibility == true) {
            is_visible = 1;
        }

        var is_avilable = $('#menu-availability').prop('checked');
        var allow_unregistered = $('#allow-unregistered').prop('checked');
        //var is_avilable = 0;
        //if (available_offline == true) {
        //    is_avilable = 1;
        //}


        var uid_yes_no = $('#menu-uid-include').prop('checked');
        var uid_included = 0;
        if (uid_yes_no == true) {
            uid_included = 1;
        }
        var accept_login = $('#menu-accept-login').prop('checked');
        var only_speaker = $('#menu-only-speaker').prop('checked');
        //var accept_login = 0;
        //if (login_yes_no == true) {
        //    accept_login = 1;
        //}

        var title = $('#menu-title').val(),
            parent = $('#menu-parent').val(),
            content = $('#menu-content').val(),
            content_type = $('#menu-content-type').val(),
            url = $('#menu-url').val(),
            start_date = $('#menu-start-date').val(),
            start_time = $('#menu-start-time').val(),
            end_date = $('#menu-end-date').val(),
            end_time = $('#menu-end-time').val(),
            group = $('#menu-rule').select2('val'),
            csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        var title_lang = valueWithSpecialCharacter(title);
        var requiredFields = [
            {fieldId: 'menu-title', message: 'Title'},
            //{fieldId: 'menu-rule', message: 'Rule'},
            {fieldId: 'menu-content-type', message: 'Content Type'},
            {fieldId: 'menu-start-date', message: 'Start date'},
            {fieldId: 'menu-end-date', message: 'End Date'}

        ];
        var content_url = $('#menu-content option:selected').text();


        if (content_type == "url") {
            requiredFields.push({fieldId: 'menu-url', message: 'Url'})
        } else if (content_type == "page_content") {
            requiredFields.push({fieldId: 'menu-content', message: 'Content'})
        }
        if (parent == '' || parent == null) {
            parent = 0;
        }
        var start = moment(start_date + ' ' + start_time, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD HH:mm:ss'),
            end = moment(end_date + ' ' + end_time, 'MM/DD/YYYY HH:mm').format('YYYY-MM-DD HH:mm:ss');

        var data = {
            title: title,
            title_lang: title_lang,
            parent: parent,
            url: url,
            start_time: start,
            end_time: end,
            is_visible: is_visible,
            available_offline: is_avilable,
            allow_unregistered: allow_unregistered,
            group_id: JSON.stringify(group),
            content_id: content,
            content_url: content_url,
            uid_include: uid_included,
            accept_login: accept_login,
            only_speaker: only_speaker,
            csrfmiddlewaretoken: csrfToken
        };

        if (!requiredFieldValidator(requiredFields)) {
            return;
        }

        if (button.attr('id') == 'btn-update-menuitem') {
            var menuitem_id = $('#menuitem-id').val();
            data['id'] = menuitem_id;
            var current_language_id = $('.menu-language-presets-selector').select2('val');
            data['current_language_id'] = current_language_id;
        }

        $.ajax({
            url: base_url + '/admin/menus/',
            type: 'POST',
            data: data,
            dataType: "json",
            success: function (response) {

                if (response.success) {
                    $.growl.notice({message: response.success});
                    $('#menus-edit-item').modal('hide');
                    var menu = response.menu_item;
                    clog(menu);
                    var list = '<li class="dd-item dd3-item" data-id="' + menu.id + '">' +
                        '<div class="dd-handle dd3-handle"></div><div class="dd3-content">' + menu.title +
                        '<div style="float:right;">' +
                        '<button class="btn btn-xs btn-edit-menu" data-id="' + menu.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                        '<button class="btn btn-xs btn-danger btn btn-delete-menu" data-id="' + menu.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                        '</div>' +
                        '</div>' +
                        '</li>';
                    if (button.attr('id') === 'btn-update-menuitem') {
                        if (response.parent_changed) {
                            $('.dd-item').each(function () {
                                $this = $(this)
                                if ($this.attr('data-id') == menu.id) {
                                    $this.remove();
                                }
                                if (menu.parent != '') {
                                    if ($(this).attr('data-id') == menu.parent.id) {
                                        if ($(this).parent('ol')) {
                                            $(this).append('<ol class="dd-list">' + list + '</ol>');
                                        } else {
                                            $(this).children('ol').append(list);
                                        }
                                    }
                                } else {
                                    $('#nestable3 ol').first().append(list);
                                }
                            });
                        } else {
                            $('.dd-item').each(function () {
                                if ($(this).attr('data-id') == menu.id) {
                                    var content = '' + menu.title +
                                        '<div style="float:right;">' +
                                        '<button class="btn btn-xs btn-edit-menu" data-id="' + menu.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Edit"><i class="dropdown-icon fa fa-cog"></i></button>' +
                                        '<button class="btn btn-xs btn-danger btn btn-delete-menu" data-id="' + menu.id + '" data-toggle="tooltip" data-placement="top" title="" data-original-title="Delete"><i class="dropdown-icon fa fa-times-circle"></i></button>' +
                                        '</div>'
                                    $(this).children('.dd3-content').html(content);
                                }
                            });
                        }
                    } else {
                        clog('ok');
                        if (menu.parent != '') {
                            $('.dd-item').each(function () {
                                if ($(this).attr('data-id') == menu.parent.id) {
                                    if ($(this).parent('ol')) {
                                        clog('ok1');
                                        $(this).append('<ol class="dd-list">' + list + '</ol>');
                                    } else {
                                        $(this).children('ol').append(list);
                                        clog('ok2');
                                    }
                                }
                            });
                        } else {
                            $('#nestable3 ol').first().append(list);
                        }
                    }
                }
                else {
                    var errors = response.error;
                    $.growl.warning({message: errors});
                }
            },
            error: function (e) {
                clog(e);
            }
        })
        ;
    }

    $body.on('click', '#btn-save-menuitem', function () {
        addOrUpdateMenuItem($(this));
    });

    $body.on('click', '#btn-update-menuitem', function () {
        addOrUpdateMenuItem($(this));
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

})
;