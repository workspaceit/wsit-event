$(function () {

    var $body = $('body');

    $('.section').on('click', '.btn-add-rule', function (e) {
        e.preventDefault();
        $(this).closest('.filter-list').append($('#filter-li-html').html());
        $("[data-role=datepicker]").kendoDatePicker();
        //$(".filter-session-selector").dropdown();
        ////var options = {
        //    todayBtn: "linked",
        //    orientation: $('body').hasClass('right-to-left') ? "auto right" : 'auto auto',
        //    setDate: new Date()
        //};
        //$('.filter-datepicker').datepicker(options);
        //$('.filter-datepicker').html("");

        //$('.filter-datepicker').each(function () {
        //   $(this).kendoDatePicker('destroy').kendoDatePicker();
        //});
        //var today = new Date();
        //clog(today.getYear());
        //clog(today.getFullYear());
        //$(this).closest('.filter-list').find('.filter-datepicker:last').children('input[type="text"]').val(today.getMonth() + '/' + today.getDate() + '/' + today.getFullYear());
        //$('.filter-datepicker-range').datepicker(options);
        $('.filter-datepicker-range').kendoDatePicker();
        //$('.datepicker-start, .datepicker-end, .datepicker-registration-available').datepicker();
        $('.datepicker-start, .datepicker-end, .datepicker-registration-available').kendoDatePicker();
        //var options2 = {
        //    minuteStep: 15,
        //    showMeridian: false,
        //    showInputs: false,
        //    orientation: $('body').hasClass('right-to-left') ? {x: 'right', y: 'auto'} : {x: 'auto', y: 'auto'}
        //};
        //$('.timepicker-start, .timepicker-end').timepicker(options2);
        $('.timepicker-start, .timepicker-end').kendoDatePicker();

    });

    $('.section').on('click', '.btn-delete-rule', function (e) {
        e.preventDefault();
        var li = $(this).closest('li');
        var ul = li.parent();
        var lis = ul.children('li');
        if (lis.length > 1) {
            li.remove();
        }
        else {
            $.growl.error({message: 'Rule set needs at least one rule to match'});
        }
    });

    $('.section').on('click', '.btn-delete-nested-rule', function (e) {
        e.preventDefault();
        var li = $(this).closest('li');
        var ul = li.parent();
        var lis = ul.children('li');
        if (lis.length > 1) {
            li.remove();
        }
        else {
            $.growl.error({message: 'Rule set needs at least one rule to match'});
        }
    });

    $('.section').on('click', '.btn-add-nested-rule', function (e) {
        e.preventDefault();
        $('#filter-nested-html .filter-rule-list').html($('#filter-li-html').html());
        $(this).siblings('.filter-list').append($('#filter-nested-html').html());
        $("[data-role=datepicker]").kendoDatePicker();
        //var options = {
        //    todayBtn: "linked",
        //    orientation: $('body').hasClass('right-to-left') ? "auto right" : 'auto auto',
        //    update: new Date()
        //};
        //
        //$('.filter-datepicker').datepicker(options);
        //var today = new Date();
        //$(this).siblings('ul').children('li:last').children('ul').find('.filter-datepicker').children('input[type="text"]').val(today.getMonth() + '/' + today.getDate() + '/' + today.getYear());
        //$('.filter-datepicker-range').datepicker(options);
        //$('.datepicker-start, .datepicker-end, .datepicker-registration-available').datepicker();
        //var options2 = {
        //    minuteStep: 15,
        //    showMeridian: false,
        //    showInputs: false,
        //    orientation: $('body').hasClass('right-to-left') ? {x: 'right', y: 'auto'} : {x: 'auto', y: 'auto'}
        //}
        //$('.timepicker-start, .timepicker-end').timepicker(options2);
    });

    $body.on('click', '#btn-filter-attendee', function (e) {
        e.preventDefault();
        $('.f-row').removeClass('visited');
        var c = [];
        var fi = $('#filter-list');
        traverse(fi, c);
        var rule_id = $('#btn-filter-attendee').attr('data-id');
        if (rule_id != undefined && rule_id != '') {
            var data = {
                rule_id: rule_id,
                filters: JSON.stringify(c),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            };
        } else {
            var data = {
                rule_id: '',
                filters: JSON.stringify(c),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            };
        }
        $.ajax({
            url: base_url + '/admin/filter/',
            type: 'POST',
            data: data,
            success: function (response) {
                if (response.success) {
                    clog(response.attendees)
                    clog('s');
                    $.growl.notice({message: response.success});
                }
                else {
                    var errors = response.message;
                    clog(errors);
                }
            },
            error: function (e) {
                clog(e);
            }
        });

    });

    function saveRules(name, group_id, is_limit, limit_amount, id) {

        $('#filter-list').children('li').each(function () {
            $(this).removeClass('visited');
        });
        var preset_name = name;
        //$('.f-row').removeClass('visited');
        var c = [];
        var fi = $('#filter-list');
        traverse(fi, c);
        // c
        if (group_id != undefined && group_id != '') {
            $.map(c, function (elementOfArray, indexInArray) {
                if (elementOfArray.length == 0) {
                    c.splice(indexInArray, 1);
                }
            });
            if (preset_name != '') {
                if (id) {
                    var data = {
                        filters: JSON.stringify(c),
                        id: id,
                        is_limit: is_limit,
                        limit_amount: limit_amount,
                        group_id: group_id,
                        preset_name: preset_name,
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                    };
                } else {

                    var data = {
                        filters: JSON.stringify(c),
                        preset_name: preset_name,
                        is_limit: is_limit,
                        limit_amount: limit_amount,
                        group_id: group_id,
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                    };
                }
                clog(data)
                $.ajax({
                    url: base_url + '/admin/save_filter/',
                    type: 'POST',
                    data: data,
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else {
                            $.growl.notice({message: result.success});

                            var filter = result.filter;
                            var treeview = $("#add-filter-treeview").data("kendoTreeView");
                            item = treeview.findByText(filter.group.name);
                            //abc = treeview.dataItem(item)
                            treeview.append({
                                    text: filter.name,
                                    spriteCssClass: "question",
                                    data_type: "filter",
                                    data_id: filter.id
                                }, item
                            );
                            selectitem = treeview.findByText(filter.name)
                            treeview.select(selectitem);
                            $('#dialoge').removeClass('visible');

                        }
                    },
                    error: function (e) {
                        clog(e);
                    }
                });
            } else {
                $.growl.error({message: "You need to add Preset Name First"});
                activeDatePicker();
            }
        }
        else {
            $.growl.error({message: "You need to add Filter Group First"});
            activeDatePicker();
        }
    }

    $('.section').on('click', '#btn-save-filter', function (event) {
        var preset_name = $('#preset_name').val();
        var group_id = $('#preset_filter_group').val()
        clog("group id :" + group_id)
        var is_limit = "0";
        if ($('#is_limit').prop('checked'))
            is_limit = "1";
        var limit_amount = $('#limit_amount').val();
        if (limit_amount == '')
            limit_amount = 0;
        saveRules(preset_name, group_id, is_limit, limit_amount);
    });

    $('.section').on('click', '#btn-update-filter', function (event) {
        var preset_name = $('#preset_name').val();
        var group_id = $('#preset_filter_group').select2('val');
        var rule_id = $('#preset_name').attr('data-id');

        var is_limit = "0";
        if ($('#is_limit').prop('checked'))
            is_limit = "1";

        var limit_amount = $('#limit_amount').val();
        if (limit_amount == '')
            limit_amount = 0;
        if (rule_id != undefined && rule_id != '') {
            saveRules(preset_name, group_id, is_limit, limit_amount, rule_id);
        }
    });

    $body.on('click', '.btn-delete-filter', function (event) {
        var $this = $(this);
        var rule_preset = $this.parent().prev('td').html();
        bootbox.confirm("Are you sure you want to delete " + rule_preset + "?", function (result) {
            if (result) {
                var id = $this.attr('data-id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    url: base_url + '/admin/filter/delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.error) {
                            $.growl.error({message: result.error});
                        } else {
                            $.growl.notice({message: result.success});
                            $this.closest('tr').remove();
                        }
                    }
                });
            }
        });
    });

    $body.on('click', '.btn-edit-filter', function () {
        var filter_id = $(this).data('id');
        var modal_class = 'filters-add-filter';
        showFilterData(filter_id, modal_class);
        $('#filters-add-filter').find('.modal-title').html('Edit Filter');
    });

    $body.on('click', '.btn-view-filter', function () {
        var filter_id = $(this).data('id');
        var modal_class = 'filters-view-filter';
        showFilterData(filter_id, modal_class);
    });

    function showFilterData(filter_id, modal_class) {
        $.ajax({
            url: base_url + '/admin/filter/' + filter_id + '/',
            type: "GET",
            data: {},
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $('#quick-save-div').hide();
                    $('#filter-list').html("");
                    var preset = $.parseJSON(result.rule.preset);
                    clog(result.rule.name)
                    $('#preset_name').val(result.rule.name);
                    $('.filter-panel-title').html(result.rule.name);
                    $('#preset_name').attr('data-id', result.rule.id);

                    if (result.rule.is_limit)
                        $("#is_limit").prop("checked", true);

                    $('#limit_amount').val(result.rule.limit_amount);
                    var filter_group = result.rule.group.id;
                    $('#preset_filter_group').select2('val', filter_group);
                    $('#preset_filter_group').attr('data-id', filter_group);
                    $('.filter-list').find('li:last').remove();
                    filterShow(preset, $('#filter-list'));
                    $('#btn-save-filter').hide();
                    $('#btn-update-filter').show();
                    $('#' + modal_class).modal();
                    activeDatePicker();
                }
            },
            error: function (e) {
                clog(e);
            }
        });
    }

    $body.on('click', '#trav', function () {
        $body.find('.f-row').removeClass('visited');
        var cd = [];
        var fi = $('#filter-list');
        traverse(fi, cd);
        clog(cd);
    });

    $body.on('click', '.quick-filter',
        function () {

            $.ajax({
                url: base_url + '/admin/filters/quick_filter_exists/',
                success: function (response) {
                    if (response.status) {
                        var modal_class = 'filters-add-filter';
                        $('#quick-save-div').show();
                        $('#filter-grp-div').hide();
                        $('#preset-name-div').hide();
                        showQuickFilterData(response.filter.id, modal_class);
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
                        //$('#filters-add-filter').modal('show');
                        $('[data-remodal-id=modal]').remodal().open();
                        $('#preset_name').attr('data-id', '');
                        var rowCount = 0;
                        $('.filter-list').html($('#filter-li-html').html());
                        activeDatePicker();


                    }
                }
            });


        }
    );

    $('.section').on('click', '#is_save', function () {
        if ($(this).prop('checked')) {
            $('#filter-grp-div').show();
            $('#preset-name-div').show();

        } else {
            $('#filter-grp-div').hide();
            $('#preset-name-div').hide();
        }
    });
    function updateQuickFilter(is_limit, limit_amount, type) {
        $('#filter-list').children('li').each(function () {
            $(this).removeClass('visited');
        });
        var preset_name = 'quick-filter';
        var c = [];
        var fi = $('#filter-list');
        traverse(fi, c);
        $.map(c, function (elementOfArray, indexInArray) {
            if (elementOfArray.length == 0) {
                c.splice(indexInArray, 1);
            }
        });
        var data = {
            filters: JSON.stringify(c),
            preset_name: preset_name,
            is_limit: is_limit,
            limit_amount: limit_amount,
            type: type,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        };
        $.ajax({
            url: base_url + '/admin/save_filter/',
            type: 'POST',
            data: data,
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    //$('#filters-add-filter').modal('hide');
                    //$('#dialoge').removeClass('visible');
                    $('[data-remodal-id=modal]').remodal().close();

                    var treeview = $("#add-filter-treeview").data("kendoTreeView");
                    item = treeview.findByText('Temporary-Filter');
                    //abc = treeview.dataItem(item)
                    treeview.append({
                            text: result.quick_filter.name,
                            spriteCssClass: "filter",
                            data_type: "filter",
                            data_id: result.quick_filter.id
                        }, item
                    );
                    selectitem = treeview.findByText(result.quick_filter.name)
                    treeview.select(selectitem);
                    //$('.quick-filter').attr('value', result.quick_filter.id);
                    //$('#rule').val(result.quick_filter.id);
                    //if ($('#filter-rules-switcher').prop('checked')) {
                    //    $('#filter-search-table').DataTable().draw();
                    //}
                    //
                    //
                    ////menu quick filter
                    //$('#menu-rule').find("optgroup").each(
                    //    function () {
                    //        if ($(this).attr('label') == result.quick_filter.group.name) {
                    //            var newState = new Option(result.quick_filter.name, result.quick_filter.id, true, true);
                    //            $(this).append(newState).trigger('change');
                    //        }
                    //    }
                    //);
                    //
                    //$('#filter').find("optgroup").each(
                    //    function () {
                    //        if ($(this).attr('label') == result.quick_filter.group.name) {
                    //            var newState = new Option(result.quick_filter.name, result.quick_filter.id, true, true);
                    //            $(this).append(newState).trigger('change');
                    //        }
                    //    }
                    //);

                }
            },
            error: function (e) {
                clog(e);
            }
        });


    }

    $('#btn-update-quick-filter').click(function () {
        if ($('#is_save').prop('checked')) {
            var preset_name = $('#preset_name').val();
            var group_id = $('#preset_filter_group').select2('val');
            var is_limit = "0";
            if ($('#is_limit').prop('checked'))
                is_limit = "1";
            var limit_amount = $('#limit_amount').val();
            if (limit_amount == '')
                limit_amount = 0;
            //alert(preset_name)
            saveRules(preset_name, group_id, is_limit, limit_amount);
        } else {
            var is_limit = "0";
            if ($('#is_limit').prop('checked'))
                is_limit = "1";
            var limit_amount = $('#limit_amount').val();
            if (limit_amount == '')
                limit_amount = 0;
            updateQuickFilter(is_limit, limit_amount);
        }
    });

    $('#btn-update-quick-filter-name-required').click(function () {
        if ($('#is_save').prop('checked')) {
            var preset_name = $('#preset_name').val();
            //var group_id = $('#preset_filter_group').select2('val');
            var group_id = $('#preset_filter_group').val();
            var is_limit = "0";
            if ($('#is_limit').prop('checked'))
                is_limit = "1";
            var limit_amount = $('#limit_amount').val();
            if (limit_amount == '')
                limit_amount = 0;
            //alert(preset_name)
            saveRules(preset_name, group_id, is_limit, limit_amount);
        } else {
            var type = $(this).data('id');
            var is_limit = "0";
            if ($('#is_limit').prop('checked'))
                is_limit = "1";
            var limit_amount = $('#limit_amount').val();
            if (limit_amount == '')
                limit_amount = 0;
            updateQuickFilter(is_limit, limit_amount, type);
        }
    });

});
function showQuickFilterData(filter_id, modal_class, name) {
    $.ajax({
        url: base_url + '/admin/filter/' + filter_id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            if (result.error) {
                $.growl.error({message: result.error});
            } else {
                $('#filter-list').html("");
                var preset = $.parseJSON(result.rule.preset);
                $('#preset_name').val("");
                $('.filter-panel-title').html(result.rule.name);
                //$('#preset_name').attr('data-id', result.rule.id);

                if (result.rule.is_limit)
                    $("#is_limit").prop("checked", true);

                $('#limit_amount').val(result.rule.limit_amount);
                var filter_group = result.rule.group.id;
                $('#preset_filter_group').select2('val', "");
                //$('#preset_filter_group').attr('data-id', filter_group);
                $('.filter-list').find('li:last').remove();
                filterShow(preset, $('#filter-list'));
                $('#btn-save-filter').hide();
                if (name != '' || name == undefined) {
                    clog(name)
                    $('#btn-update-quick-filter-name-required').attr('data-id', name)
                    $('#btn-update-quick-filter-name-required').show();
                } else {
                    $('#btn-update-quick-filter').show();
                }

                //$('#dialoge').addClass('visible');
                $('[data-remodal-id=modal]').remodal().open();
                //inst.open();
                activeDatePicker();
            }
        },
        error: function (e) {
            clog(e);
        }
    });
}


function activeDatePicker() {
    var options = {
        todayBtn: "linked",
        orientation: $('body').hasClass('right-to-left') ? "auto right" : 'auto auto',
        setDate: new Date(),
        format: 'mm/dd/yyyy'
    };
    //$('.filter-datepicker').datepicker(options);
    if (filter_datepicker) {
        $('.filter-datepicker').kendoDatePicker();
        $('.filter-datepicker-range-start').kendoDatePicker();
        $('.filter-datepicker-range-end').kendoDatePicker();
        filter_datepicker = false;
    }
    $("[data-role=datepicker]").kendoDatePicker();
    // $("[data-role=datepicker]").kendoDatePicker();
    //var today = new Date();
    //$(this).closest('.filter-list').find('.filter-datepicker:last').children('input[type="text"]').val(today.getMonth() + '/' + today.getDate() + '/' + today.getYear());
    //$('.filter-datepicker-range').datepicker(options);

    $('.datepicker-start, .datepicker-end, .datepicker-registration-available').datepicker();
    //$('.datepicker-start, .datepicker-end, .datepicker-registration-available').kendoDatePicker();
    var options2 = {
        minuteStep: 15,
        showMeridian: false,
        showInputs: false,
        orientation: $('body').hasClass('right-to-left') ? {x: 'right', y: 'auto'} : {x: 'auto', y: 'auto'}
    };
    //$('.timepicker-start, .timepicker-end').timepicker(options2);
    $('.timepicker-start, .timepicker-end').kendoTimePicker();
}