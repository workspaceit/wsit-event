$(function () {
    var $body = $('body');
    $body.on('click', '#btn-add-filter', function () {
        $('#quick-save-div').hide();
        $('#btn-save-filter').show();
        $('#btn-update-filter').hide();
        $('.any-or-all').val(1);
        $('#filters-add-filter').find('.modal-title').html('Add Filter');
        $('#preset_filter_group').select2('val', '');

        $('.filter-panel-title').html("New Filter");
        $('#filters-add-filter').modal('show');
        $('#preset_name').attr('data-id', '');
        var rowCount = 0;
        $('.filter-list').html($('#filter-li-html').html());
        activeDatePicker();
    });

    //start filter changing logic

    $body.on('change', '.filter-list .rule', function () {
        $(this).closest('li').find('.option-select').hide();
        $(this).closest('li').find('.page-input-div').hide();
        $(this).closest('li').find('.second').hide();
        $(this).closest('li').find('.third').hide();
        $(this).closest('li').find('.forth').hide();
        var filter = $(this).val();
        if (filter == 1) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.t-1').show();

            $(this).closest('li').find('.third').show();
            var selectedValue = $(this).closest('li').find('.second-' + filter).val();
            if (selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-1').show();
            }
            else if (selectedValue == 5 || selectedValue == 6) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-2').show();
            }
            else if (selectedValue == 7) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-3').show();
            }
        } else if (filter == 2) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.t-1').show();


            $(this).closest('li').find('.third').show();
            var selectedValue = $(this).closest('li').find('.second-' + filter).val();
            if (selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-1').show();
            }
            else if (selectedValue == 5 || selectedValue == 6) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-2').show();
            }
            else if (selectedValue == 7) {
                $(this).closest('li').find('.third').hide();
                $(this).closest('li').find('.t-3').show();
            }
        }
        else if (filter == 6) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.third-' + filter).show();
            $(this).closest('li').find('.third-' + filter).select2({
                placeholder: "Select a session"
            });
        }
        else if (filter == 7) {
            $(this).closest('li').find('.second-' + filter).show();

            if (!$(this).closest('li').find('.second-' + filter).data('select2')) {
                $(this).closest('li').find('.second-' + filter).select2({
                    placeholder: "Select a question"
                });
            } else {
                $(this).closest('li').find('.second-' + filter).show();
            }

            $(this).closest('li').find('.condition-2').show();
            clog($(this).closest('li').find('.condition-2').val())
            if ($(this).closest('li').find('.condition-2').val() != 7 && $(this).closest('li').find('.condition-2').val() != 8) {
                $(this).closest('li').find('.answer-text-container').show();
            }
            $(this).closest('li').find('.second-7').change();

        } else if (filter == 9) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.condition-3').show();
            //$(this).closest('li').find('.hotel-group').show();


            var selectedValue = $(this).closest('li').find('.second-' + filter).val();
            $(this).closest('li').find('.answer-number-container').hide();
            //$('.matched-unmatched').hide();
            //$('.hotel-group').hide();
            //$('.date-div').hide();
            $(this).siblings('.matched-unmatched').hide();
            $(this).siblings('.hotel-group').hide();
            $(this).siblings('.date-div').hide();

            if (selectedValue == 1 || selectedValue == 6) {
                $(this).closest('li').find('.condition-3').show();
                $(this).closest('li').find('.condition-4').hide();
                $(this).closest('li').find('.condition-5').hide();
                $(this).closest('li').find('.answer-number-container').hide();

                if (selectedValue == 1) {
                    //$('.hotel-group').show();
                    $(this).siblings('.hotel-group').show();
                } else {
                    //$('.matched-unmatched').show();
                    $(this).siblings('.matched-unmatched').show();
                }


            }
            else if (selectedValue == 4 || selectedValue == 5) {
                $(this).closest('li').find('.condition-4').show();
                $(this).closest('li').find('.condition-3').hide();
                $(this).closest('li').find('.condition-5').hide();
                $(this).closest('li').find('.answer-number-container').show();

            }
            else if (selectedValue == 2 || selectedValue == 3) {
                $(this).closest('li').find('.condition-5').show();
                $(this).closest('li').find('.condition-3').hide();
                $(this).closest('li').find('.condition-4').hide();
                $(this).closest('li').find('.answer-number-container').hide();

                //$('.date-div').show();
                $(this).siblings('.date-div').show();
                var Value = $(this).closest('li').find('.condition-5').val();
                clog(Value)
                if (Value == 1 || Value == 2 || Value == 3 || Value == 4) {
                    $(this).closest('li').find('.forth').hide();
                    $(this).closest('li').find('.tt-1').show();
                }
                else if (Value == 5 || Value == 6) {
                    $(this).closest('li').find('.forth').hide();
                    $(this).closest('li').find('.tt-2').show();
                }
                else if (Value == 7) {
                    $(this).closest('li').find('.forth').hide();
                    $(this).closest('li').find('.tt-3').show();
                }
            }

        } else if (filter == 11) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.condition-6').show();
        } else if (filter == 12) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.condition-6').show();
        } else if (filter == 13) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.condition-7').show();
            if ($(this).closest('li').find('.condition-7').val() == 3 || $(this).closest('li').find('.condition-7').val() == 4 || $(this).closest('li').find('.condition-7').val() == 5) {
                $(this).closest('li').find('.page-input-div').show();
            }
        } else if (filter == 14) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.third-7').show();
        } else if (filter == 15) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.third-8').show();
        } else if (filter == 16) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.second-' + filter).val('1');
            $(this).closest('li').find('.condition-3').show();
            $(this).closest('li').find('.forth-' + filter).show();
        }else if (filter == 18) {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.condition-9').show();
        } else {
            $(this).closest('li').find('.second-' + filter).show();
            $(this).closest('li').find('.third-' + filter).show();
        }
    });

    $body.on('change', '.filter-list .second-1,.filter-list .second-2', function () {
        $(this).closest('li').find('.third').show();
        var selectedValue = $(this).val();
        if (selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
            $(this).closest('li').find('.third').hide();
            $(this).closest('li').find('.t-1').show();
        }
        else if (selectedValue == 5 || selectedValue == 6) {
            $(this).closest('li').find('.third').hide();
            $(this).closest('li').find('.t-2').show();
        }
        else if (selectedValue == 7) {
            $(this).closest('li').find('.third').hide();
            $(this).closest('li').find('.t-3').show();
        }
    });

    $body.on('change', '.filter-list .second-15', function () {
        if ($(this).val() == '3') {
            $(this).closest('li').find('.third-8').hide();
            $(this).closest('li').find('.third-9').show();
            $(this).closest('li').find(' .value-for-group-registration').show();
        } else {
            $(this).closest('li').find('.third-8').show();
            $(this).closest('li').find('.third-9').hide();
            $(this).closest('li').find('.value-for-group-registration').hide();
        }
    });

    $body.on('change', '.filter-list .second-16', function () {
        $(this).closest('li').find('.third').hide();
        $(this).closest('li').find('.forth').hide();
        if ($(this).val() == '1') {
            $(this).closest('li').find('.condition-3').show();
            $(this).closest('li').find('.forth-16').show();
        } else if ($(this).val() == '2' || $(this).val() == '3') {
            $(this).closest('li').find('.condition-5').show();
            $(this).closest('li').find('.condition-5').val('1');
            $(this).closest('li').find('.date-div').show();
            $(this).closest('li').find('.tt-1').show();
        } else if ($(this).val() == '4' || $(this).val() == '5' || $(this).val() == '8') {
            $(this).closest('li').find('.third-8').show();
        } else if ($(this).val() == '6' || $(this).val() == '7') {
            $(this).closest('li').find('.condition-8').show();
            $(this).closest('li').find('.condition-8').val('1');
            $(this).closest('li').find('.answer-number-container').show();
        }
    });

    $body.on('change', '.condition-2', function () {
        var selectedValue = $(this).val();
        if (selectedValue == 7 || selectedValue == 8) {
            $(this).closest('li').find('.answer-text-container').hide();
        } else {
            $(this).closest('li').find('.answer-text-container').show();
        }
    });
    $body.on('change', '.condition-1', function () {
        $(this).closest('li').find('.country-group').hide();
        $(this).closest('li').find('.country-select').hide();
        var select = $(this).closest('li').find('.second-7');
        var selectedValue = $(this).val();
        var selectedOption = select.find('option:selected');
        var questionType = selectedOption.data('type');
        if(questionType == 'country') {
            if (selectedValue == 3 || selectedValue == 4) {
                $(this).closest('li').find('.country-group').hide();
                $(this).closest('li').find('.country-select').hide();
            }else {
                $(this).closest('li').find('.country-group').show();
                $(this).closest('li').find('.country-select').show();
                $(this).closest('li').find('.country-select').select2({
                    placeholder: 'Select A Country',
                    data: country_list
                });

            }
        }
        else {
            //console.log(selectedValue);
            if (selectedValue == 3 || selectedValue == 4) {
                $(this).closest('li').find('.option-select').hide();
            } else {
                var optionSelected = $(this).closest('li').find('.second-7:visible').select2('val');
                $(this).closest('li').find('.qid-' + optionSelected).show();
            }
        }
    });

    $body.on('change', '.condition-5', function () {
        //$('.matched-unmatched').hide();
        //$('.hotel-group').hide();
        //$('.date-div').show();
        $(this).closest('.matched-unmatched').hide();
        $(this).closest('.hotel-group').hide();
        var selectedValue = $(this).val();
        clog(selectedValue);
        if (selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
            $(this).siblings('.date-div').show();
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-1').show();
        }
        else if (selectedValue == 5 || selectedValue == 6) {
            $(this).siblings('.date-div').show();
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-2').show();
        }
        else if (selectedValue == 7) {
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-3').show();
        }
        else if (selectedValue == 8 || selectedValue == 9) {
            $(this).closest('li').find('.forth').hide();
        }
    });
    $body.on('change', '.condition-10', function () {
        //$('.matched-unmatched').hide();
        //$('.hotel-group').hide();
        //$('.date-div').show();
        $(this).siblings('.matched-unmatched').hide()
        $(this).siblings('.hotel-group').hide();
        $(this).siblings('.date-div').show();
        var selectedValue = $(this).val();
        if (selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-4').show();
        }
        else if (selectedValue == 5 || selectedValue == 6) {
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-5').show();
        }
        else if (selectedValue == 7) {
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.tt-6').show();
        }
        else if(selectedValue == 8 || selectedValue == 9) {
            $(this).siblings('.date-div').hide();
        }
    });

    $body.on('change', '.condition-11', function () {
        var select = $(this).closest('li').find('.second-7');
        var selectedOption = select.find('option:selected');
        var questionType = selectedOption.data('type');
        $(this).closest('li').find('.date-div').hide();
        $(this).closest('li').find('.forth').hide();
        $(this).closest('li').find('.tt-3').hide();
        $(this).closest('li').find('.tt-6').hide();
        var selectedValue = $(this).val();
        if(selectedValue == 1 || selectedValue == 2 || selectedValue == 3 || selectedValue == 4) {
            $(this).closest('li').find('.date-div').show();
            if(questionType == 'date_range') $(this).closest('li').find('.tt-3').show();
            else if(questionType == 'time_range') $(this).closest('li').find('.tt-6').show();
        }
    });

    $body.on('change', '.condition-7', function () {
        //$('.matched-unmatched').hide();
        //$('.hotel-group').hide();
        $(this).siblings('.matched-unmatched').hide();
        $(this).siblings('.hotel-group').hide();
        var selectedValue = $(this).val();
        if (selectedValue == 1 || selectedValue == 2) {
            $(this).closest('li').find('.forth').hide();
            $(this).closest('li').find('.page-input-div').hide();
        } else {
            $(this).closest('li').find('.page-input-div').show();
        }

    });
    $body.on('change', '.condition-8', function () {
        var selectedValue = $(this).val();
        if (selectedValue == 5) {
            $(this).closest('li').find('.answer-number-container').hide();
            $(this).closest('li').find('.answer-number-within-container').show();
        } else {
            $(this).closest('li').find('.answer-number-container').show();
            $(this).closest('li').find('.answer-number-within-container').hide();
        }

    });

    $body.on('change', '.filter-list .second-7', function () {
        var selectedValue = $(this).val();
        var selectedOption = $(this).find('option:selected');
        var questionType = selectedOption.data('type');
        clog(selectedValue);
        clog(questionType);

        $(this).closest('li').find('.option-select').hide();
        $(this).closest('li').find('.condition-1').hide();
        $(this).closest('li').find('.condition-2').hide();
        $(this).closest('li').find('.condition-5').hide();
        $(this).closest('li').find('.condition-10').hide();
        $(this).closest('li').find('.condition-11').hide();
        $(this).closest('li').find('.answer-text-container').hide();
        $(this).closest('li').find('.date-div').hide();
        $(this).closest('li').find('.date-div').find('.tt-1').hide();
        $(this).closest('li').find('.date-div').find('.tt-2').hide();
        $(this).closest('li').find('.date-div').find('.tt-3').hide();
        $(this).closest('li').find('.date-div').find('.tt-4').hide();
        $(this).closest('li').find('.date-div').find('.tt-5').hide();
        $(this).closest('li').find('.date-div').find('.tt-6').hide();
        $(this).closest('li').find('.qid-' + selectedValue).hide();
        $(this).closest('li').find('.third').hide();
        $(this).closest('li').find('country-group').hide();
        $(this).closest('li').find('country-select').hide();


        if (questionType == 'text' || questionType == 'textarea') {
            // $(this).closest('li').find('.condition-1').hide();
            $(this).closest('li').find('.condition-2').show();

            if ($(this).closest('li').find('.condition-2').val() != 7 && $(this).closest('li').find('.condition-2').val() != 8) {
                $(this).closest('li').find('.answer-text-container').show();
            }
        }else if(questionType == 'date'){
            $(this).closest('li').find('.condition-5').show();
            $(this).closest('li').find('.date-div').show();
            var condition = $(this).closest('li').find('.condition-5').val();
            if(condition==1 || condition==2 || condition==3 || condition==4){
                $(this).closest('li').find('.date-div').find('.tt-1').show();
            }else if(condition == 5 || condition==6) {
                $(this).closest('li').find('.date-div').find('.tt-2').show();
            }else if(condition == 7) {
                $(this).closest('li').find('.date-div').find('.tt-3').show();
            }else{
                $(this).closest('li').find('.date-div').hide();
            }
        }else if(questionType=='time'){
            $(this).closest('li').find('.condition-10').show();
            $(this).closest('li').find('.date-div').show();
            var condition = $(this).closest('li').find('.condition-10').val();
            if(condition==1 || condition==2 || condition==3 || condition==4){
                $(this).closest('li').find('.date-div').find('.tt-4').show();
            }else if(condition == 5 || condition==6){
                $(this).closest('li').find('.date-div').find('.tt-5').show();
            }else if(condition ==7){
                $(this).closest('li').find('.date-div').find('.tt-6').show();
            }else if(condition ==8 || condition == 9) {
                $(this).closest('li').find('.date-div').hide();
            }
        }else if(questionType=='date_range'){
            $(this).closest('li').find('.condition-11').show();
            var condition = $(this).closest('li').find('.condition-11').val();
            $(this).closest('li').find('.date-div').show();
            $(this).closest('li').find('.date-div').find('.tt-3').show();
            if(condition == 5 || condition == 6) {
                $(this).closest('li').find('.date-div').hide();
            }
        }
        else if(questionType=='time_range'){
            $(this).closest('li').find('.condition-11').show();
            var condition = $(this).closest('li').find('.condition-11').val();
            $(this).closest('li').find('.date-div').show();
            $(this).closest('li').find('.date-div').find('.tt-6').show();
            if(condition == 5 || condition == 6) {
                $(this).closest('li').find('.date-div').hide();
            }
        }
        else if(questionType == 'country') {
            $(this).closest('li').find('.answer-text-container').hide();
            $(this).closest('li').find('.condition-1').show();
            if($(this).closest('li').find('.condition-1').val() ==1 || $(this).closest('li').find('.condition-1').val() ==2) {
                $(this).closest('li').find('.country-group').show();
                $(this).closest('li').find('.country-select').show();
                $(this).closest('li').find('.country-select').select2({
                    placeholder: 'Select A Country',
                    data: country_list
                });
            }
        }
        else {
            // $(this).closest('li').find('.condition-2').hide();
            $(this).closest('li').find('.answer-text-container').hide();
            $(this).closest('li').find('.condition-1').show();
            $(this).closest('li').find('.qid-' + selectedValue).show();
            $(this).closest('li').find('.condition-1').change();

        }
    });

    $body.on('change', '.filter-list .second-9', function () {
        var selectedValue = $(this).val();
        $(this).closest('li').find('.answer-number-container').hide();
        //$('.matched-unmatched').hide();
        //$('.hotel-group').hide();
        //$('.date-div').hide();
        $(this).siblings('.matched-unmatched').hide();
        $(this).siblings('.hotel-group').hide();
        $(this).siblings('.date-div').hide();

        if (selectedValue == 1 || selectedValue == 6) {
            $(this).closest('li').find('.condition-3').show();
            $(this).closest('li').find('.condition-4').hide();
            $(this).closest('li').find('.condition-5').hide();
            $(this).closest('li').find('.answer-number-container').hide();

            if (selectedValue == 1) {
                //$('.hotel-group').show();
                $(this).siblings('.hotel-group').show();
            } else {
                //$('.matched-unmatched').show();
                $(this).siblings('.matched-unmatched').show();
            }


        }
        else if (selectedValue == 4 || selectedValue == 5) {
            $(this).closest('li').find('.condition-4').show();
            $(this).closest('li').find('.condition-3').hide();
            $(this).closest('li').find('.condition-5').hide();
            $(this).closest('li').find('.answer-number-container').show();

        }
        else if (selectedValue == 2 || selectedValue == 3) {
            $(this).closest('li').find('.condition-5').show();
            $(this).closest('li').find('.condition-3').hide();
            $(this).closest('li').find('.condition-4').hide();
            $(this).closest('li').find('.answer-number-container').hide();

            //$('.date-div').show();
            $(this).siblings('.date-div').show();
            var Value = $(this).closest('li').find('.condition-5').val();
            clog(Value)
            if (Value == 1 || Value == 2 || Value == 3 || Value == 4) {
                $(this).closest('li').find('.forth').hide();
                $(this).closest('li').find('.tt-1').show();
            }
            else if (Value == 5 || Value == 6) {
                $(this).closest('li').find('.forth').hide();
                $(this).closest('li').find('.tt-2').show();
            }
            else if (Value == 7) {
                $(this).closest('li').find('.forth').hide();
                $(this).closest('li').find('.tt-3').show();
            }
        }
    });


    //end filter changing logic
});
function traverse(elem, par) {
    elem.children('li').each(function () {
            if ($(this).hasClass('f-row')) {
                if (!$(this).hasClass('visited')) {
                    $(this).addClass('visited');
                    var rule = $(this).find('.rule').val();
                    var second = $(this).find('.second:visible');
                    var third;
                    var filter;
                    if (second.hasClass('second-1') || second.hasClass('second-2')) {
                        if (second.val() == 1 || second.val() == 2 || second.val() == 3 || second.val() == 4) {
                            third = $(this).closest('li').find('.t-1:visible').find('input[type=text]').val();
                            var date = moment(third, 'MM/DD/YYYY').format('YYYY-MM-DD');
                            if (date == '') {
                                $.growl.error();
                            }
                            filter = {
                                field: rule,
                                condition: second.val(),
                                values: [date]
                            };
                        } else if (second.val() == 5 || second.val() == 6) {
                            var amount = $(this).closest('li').find('.t-2:visible').find('input[type="number"]').val();
                            var unit = $(this).closest('li').find('.t-2:visible').find('select').val();
                            third = amount + ' ' + unit;
                            filter = {
                                field: rule,
                                condition: second.val(),
                                values: [amount, unit]
                            };
                        } else if (second.val() == 7) {
                            var start = $(this).closest('li').find('.t-3:visible').find('input[name="start"]').val();
                            var end = $(this).closest('li').find('.t-3:visible').find('input[name="end"]').val();
                            third = start + ' ' + end;
                            start = moment(start, 'MM/DD/YYYY').format('YYYY-MM-DD');
                            end = moment(end, 'MM/DD/YYYY').format('YYYY-MM-DD');
                            filter = {
                                field: rule,
                                condition: second.val(),
                                values: [start, end]
                            };
                        }
                    }
                    else if (second.hasClass('second-7')) {
                        var selectedOption = second.find('option:selected');
                        var questionType = selectedOption.data('type');
                        if (questionType == 'text' || questionType == 'textarea') {
                            var condition = $(this).closest('li').find('.condition-2:visible').val();
                            var answerText = $(this).closest('li').find('.answer-text:visible').val();
                            if (answerText == '') {
                                $.growl.error();
                            }
                            filter = {
                                field: rule,
                                condition: second.select2('val'),
                                type: 'text',
                                values: [condition, answerText]
                            };
                        }
                        else if(questionType == 'date') {
                            var condition = $(this).closest('li').find('.condition-5').val();
                            if(condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                                var fourth = $(this).closest('li').find('.tt-1:visible').find('input[type=text]').val();
                                var date = moment(fourth, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                filter = {
                                    field: rule,
                                    condition: second.select2('val'),
                                    type: 'date',
                                    values: [condition, date]
                                };
                            }
                            else if(condition == 5 || condition == 6) {
                                var amount = $(this).closest('li').find('.tt-2:visible').find('input[type="number"]').val();
                                var unit = $(this).closest('li').find('.tt-2:visible').find('select').val();
                                filter = {
                                    field: rule,
                                    type: 'date',
                                    condition: second.select2('val'),
                                    values: [condition, amount, unit]
                                };
                            }
                            else if(condition == 7) {
                                var start = $(this).closest('li').find('.tt-3:visible').find('input[name="start"]').val();
                                var end = $(this).closest('li').find('.tt-3:visible').find('input[name="end"]').val();
                                start = moment(start, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                end = moment(end, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                filter = {
                                    field: rule,
                                    type: 'date',
                                    condition: second.select2('val'),
                                    values: [condition, start, end]
                                };
                            }
                            else if(condition == 8 || condition == 9) {
                                filter = {
                                    field: rule,
                                    type: 'date',
                                    condition: second.select2('val'),
                                    values: [condition, null]
                                }
                            }
                        }
                        else if(questionType == 'date_range') {
                            var condition = $(this).closest('li').find('.condition-11').val();
                            if(condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                                var start = $(this).closest('li').find('.tt-3:visible').find('input[name="start"]').val();
                                var end = $(this).closest('li').find('.tt-3:visible').find('input[name="end"]').val();
                                start = moment(start, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                end = moment(end, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                filter = {
                                    field: rule,
                                    type: 'date_range',
                                    condition: second.select2('val'),
                                    values: [condition, start, end]
                                };
                            }
                            else if(condition == 5 || condition == 6) {
                                filter = {
                                    field: rule,
                                    type: 'date_range',
                                    condition: second.select2('val'),
                                    values: [condition, null]
                                };
                            }

                        }
                        else if(questionType == 'time') {
                            var condition = $(this).closest('li').find('.condition-10').val();
                            if(condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                                var time = $(this).closest('li').find('.tt-4:visible').find('input[type=text]').val();
                                filter = {
                                    field: rule,
                                    type: 'time',
                                    condition: second.select2('val'),
                                    values: [condition, time]
                                }
                            }
                            else if(condition == 5 || condition == 6) {
                                var amount = $(this).closest('li').find('.tt-5:visible').find('input[type="number"]').val();
                                var unit = $(this).closest('li').find('.tt-5:visible').find('select').val();
                                filter = {
                                    field: rule,
                                    type: 'time',
                                    condition: second.select2('val'),
                                    values: [condition, amount, unit]
                                };
                            }
                            else if(condition == 7) {
                                var start = $(this).closest('li').find('.tt-6:visible').find('.filter-timepicker-range-from').val();
                                var end = $(this).closest('li').find('.tt-6:visible').find('.filter-timepicker-range-to').val();
                                filter = {
                                    field: rule,
                                    type: 'time',
                                    condition: second.select2('val'),
                                    values: [condition, start, end]
                                };
                            }
                            else if(condition == 8 || condition == 9) {
                                filter = {
                                    field: rule,
                                    type: 'time',
                                    condition: second.select2('val'),
                                    values: [condition, null]
                                }
                            }
                        }
                        else if(questionType=='time_range') {
                            var condition = $(this).closest('li').find('.condition-11').val();
                            if(condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                                var start = $(this).closest('li').find('.tt-6:visible').find('.filter-timepicker-range-from').val();
                                var end = $(this).closest('li').find('.tt-6:visible').find('.filter-timepicker-range-to').val();
                                filter = {
                                    field: rule,
                                    type: 'time_range',
                                    condition: second.select2('val'),
                                    values: [condition, start, end]
                                };
                            }
                            else if(condition == 5 || condition == 6) {
                                filter = {
                                    field: rule,
                                    type: 'time_range',
                                    condition: second.select2('val'),
                                    values: [condition, null]
                                }
                            }
                        }
                        else if(questionType == 'country') {
                            var condition = $(this).closest('li').find('.condition-1').val();
                            if(condition == 1 || condition == 2) {
                                var value = $(this).closest('li').find('.country-select').select2('val');
                                filter = {
                                    field: rule,
                                    type: 'country',
                                    condition: second.select2('val'),
                                    values: [condition, value]
                                }
                            }
                            else {
                                filter = {
                                    field: rule,
                                    type: 'country',
                                    condition: second.select2('val'),
                                    values: [condition, null]
                                }
                            }
                        }
                        else {
                            var condition = $(this).closest('li').find('.condition-1').val();
                            var option = $(this).closest('li').find('.qid-' + second.select2('val') + ' option:selected').text().trim();
                            var option_id = $(this).closest('li').find('.qid-' + second.select2('val')).val();
                            filter = {
                                field: rule,
                                condition: second.select2('val'),
                                type: 'select',
                                values: [condition, option, option_id]
                            };
                        }
                    }
                    else if (second.hasClass('second-9')) {
                        var selectedOption = second.find('option:selected').val();
                        if (selectedOption == 1 || selectedOption == 6) {
                            var condition = $(this).closest('li').find('.condition-3:visible').val();
                            clog(condition)
                            if (selectedOption == 1) {
                                var answer = $(this).closest('li').find('.hotel-group select').val();
                            } else {
                                var answer = $(this).closest('li').find('.matched-unmatched select').val();
                            }
                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [condition, answer]
                            };
                        }
                        else if (selectedOption == 4 || selectedOption == 5) {
                            var condition = $(this).closest('li').find('.condition-4:visible').val();
                            var answer = $(this).closest('li').find('.answer-number-container .answer-text').val();

                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [condition, answer]
                            };
                        }
                        else if (selectedOption == 2 || selectedOption == 3) {
                            var condition = $(this).closest('li').find('.condition-5:visible').val();
                            if (condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                                third = $(this).closest('li').find('.tt-1:visible').find('input[type=text]').val();
                                var date = moment(third, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                if (date == '') {
                                    $.growl.error();
                                }
                                filter = {
                                    field: rule,
                                    condition: selectedOption,
                                    values: [condition, date]
                                };
                            } else if (condition == 5 || condition == 6) {
                                var amount = $(this).closest('li').find('.tt-2:visible').find('input[type="number"]').val();
                                var unit = $(this).closest('li').find('.tt-2:visible').find('select').val();
                                third = amount + ' ' + unit;
                                filter = {
                                    field: rule,
                                    condition: selectedOption,
                                    values: [condition, amount, unit]
                                };
                            } else if (condition == 7) {
                                var start = $(this).closest('li').find('.tt-3:visible').find('input[name="start"]').val();
                                var end = $(this).closest('li').find('.tt-3:visible').find('input[name="end"]').val();
                                third = start + ' ' + end;
                                start = moment(start, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                end = moment(end, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                filter = {
                                    field: rule,
                                    condition: selectedOption,
                                    values: [condition, start, end]
                                };
                            }

                        }
                        clog(filter)

                    } else if (second.hasClass('second-13')) {
                        var selectedOption = second.find('option:selected').val();
                        var condition = $(this).closest('li').find('.condition-7:visible').val();
                        if (condition == 3 || condition == 4 || condition == 5) {

                            var answer = $(this).closest('li').find('.page-input-div input').val();

                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [condition, answer]
                            };
                        } else {

                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [condition]
                            };
                        }


                    } else if (second.hasClass('second-15')) {
                        var selectedOption = second.find('option:selected').val();
                        condition = second.val();
                        third = $(this).find('.third:visible option:selected').val();
                        if (condition == 3) {
                            var answer = $(this).closest('li').find('.value-for-group-registration input').val();
                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [third, answer]
                            };
                        } else {
                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [third]
                            };
                        }


                    } else if (second.hasClass('second-16')) {
                        var selectedOption = second.find('option:selected').val();
                        condition = second.val();
                        third = $(this).find('.third:visible option:selected').val();
                        if (condition == 1) {
                            var answer = $(this).closest('li').find('.forth-16').val();
                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [third, answer]
                            };
                        } else if (condition == 2 || condition == 3) {
                            if (third == 1 || third == 2 || third == 3 || third == 4) {
                                var fourth = $(this).closest('li').find('.tt-1:visible').find('input[type=text]').val();
                                var date = moment(fourth, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                clog(date);
                                if (date == '' || date == undefined || date == 'Invalid date') {
                                    $.growl.error({message: "The date filed is Invalid"});
                                    validate_filter = false;
                                }
                                filter = {
                                    field: rule,
                                    condition: condition,
                                    values: [third, date]
                                };
                            } else if (third == 5 || third == 6) {
                                var amount = $(this).closest('li').find('.tt-2:visible').find('input[type="number"]').val();
                                var unit = $(this).closest('li').find('.tt-2:visible').find('select').val();
                                var fourth = amount + ' ' + unit;
                                filter = {
                                    field: rule,
                                    condition: condition,
                                    values: [third, amount, unit]
                                };
                            } else if (third == 7) {
                                var start = $(this).closest('li').find('.tt-3:visible').find('input[name="start"]').val();
                                var end = $(this).closest('li').find('.tt-3:visible').find('input[name="end"]').val();
                                var fourth = start + ' ' + end;
                                start = moment(start, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                end = moment(end, 'MM/DD/YYYY').format('YYYY-MM-DD');
                                filter = {
                                    field: rule,
                                    condition: condition,
                                    values: [third, start, end]
                                };
                                clog(filter);
                            }
                        } else if (condition == 6 || condition == 7) {
                            if (third == 5) {
                                var lowest = $(this).closest('li').find('.answer-number-within-container').find('input[name="lowest"]').val();
                                var highest = $(this).closest('li').find('.answer-number-within-container').find('input[name="highest"]').val();
                                filter = {
                                    field: rule,
                                    condition: condition,
                                    values: [third, lowest, highest]
                                };
                            } else {
                                var answer = $(this).closest('li').find('.answer-number-container input').val();
                                filter = {
                                    field: rule,
                                    condition: selectedOption,
                                    values: [third, answer]
                                };
                            }
                        } else {
                            filter = {
                                field: rule,
                                condition: selectedOption,
                                values: [third]
                            };
                        }


                    } else {
                        third = $(this).find('.third:visible option:selected').val();
                        filter = {
                            field: rule,
                            condition: second.val(),
                            values: [third]
                        };
                    }
                    filter['matchFor'] = elem.parent().children().children('.any-or-all').val();
                    var ruleArr = [filter];
                    clog(ruleArr);
                    par.push(ruleArr);
                }
            }
            else {
                var uls = $(this).children('ul');
                uls.each(function () {
                    var arr = [];
                    par.push(arr);
                    traverse($(this), arr);
                });
            }
        }
    );
}
function filterShow(preset, ul) {
    clog(preset);
    for (var i = 0; i < preset.length; i++) {
        if(preset[i].length > 0) {
            if (preset[i][0].length != undefined) {
                ul.append($('#filter-nested-html').html());
                filterShow(preset[i], ul.find('li:last').find('ul'));
            }
            else {
                var rules_html = $('#filter-li-html').html();
                ul.append(rules_html);
                ul.siblings('.filter-nested-rule-form-group').find('.any-or-all').show();
                ul.siblings('.filter-nested-rule-form-group').find('.any-or-all').val(preset[i][0].matchFor);
                var lastAdded = ul.find('li:last');
                lastAdded.find('.condition-5').hide();
                lastAdded.find('.condition-4').hide();
                lastAdded.find('.condition-3').hide();
                ul.find('li:last').find('.rule').val(preset[i][0].field);
                if (preset[i][0].field == 1 || preset[i][0].field == 2) {
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.third').hide();
                    if (preset[i][0].field == 1) {
                        lastAdded.find('.second-2').hide();
                    } else {
                        lastAdded.find('.second-1').hide();
                    }
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    if (preset[i][0].condition == 5 || preset[i][0].condition == 6) {
                        lastAdded.find('.t-2').find('.form-control').val(preset[i][0].values[1]);
                        lastAdded.find('.t-2').find('input[type="number"]').val(preset[i][0].values[0]);
                        lastAdded.find('.t-2').show();
                        lastAdded.find('.t-1').hide();
                        lastAdded.find('.t-3').hide();
                    }
                    else if (preset[i][0].condition == 7) {
                        var start_date = moment(preset[i][0].values[0], 'YYYY-MM-DD').format('MM/DD/YYYY');
                        var end_date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                        lastAdded.find('.t-3').find('input[name="start"]').val(start_date);
                        lastAdded.find('.t-3').find('input[name="end"]').val(end_date);
                        lastAdded.find('.t-3').show();
                        lastAdded.find('.t-1').hide();
                        lastAdded.find('.t-2').hide();
                    } else {
                        var date = moment(preset[i][0].values[0], 'YYYY-MM-DD').format('MM/DD/YYYY');
                        lastAdded.find('.t-1').find('input[type="text"]').val(date);
                        lastAdded.find('.t-1').show();
                        lastAdded.find('.t-2').hide();
                        lastAdded.find('.t-3').hide();
                    }
                }
                else if (preset[i][0].field == 6) {
                    lastAdded.find('.rule').val(6);
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.second-' + preset[i][0].field).show().val(preset[i][0].condition);
                    lastAdded.find('.third-' + preset[i][0].field).show()
                        .val(preset[i][0].values[0])
                        .select2({
                            placeholder: "Select a session"
                        });
                }
                else if (preset[i][0].field == 7) {
                    lastAdded.find('.rule').val(7);
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();

                    lastAdded.find('.second-' + preset[i][0].field).show().val(preset[i][0].condition).select2();

                    if (preset[i][0].type == 'text' || preset[i][0].type == 'textarea') {

                        lastAdded.find('.condition-2').show().val(preset[i][0].values[0]);
                        if (preset[i][0].values[0] != 7 && preset[i][0].values[0] != 8) {
                            lastAdded.find('.answer-text-container').show().find('.answer-text').val(preset[i][0].values[1]);
                        }
                    }
                    else if (preset[i][0].type == 'date') {
                        var condition = preset[i][0].values[0];
                        lastAdded.find('.date-div').show();
                        lastAdded.find('.condition-5').show().val(preset[i][0].values[0]);
                        if (condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                            var date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-1').find('input[type=text]').val(date);
                        }
                        else if (condition == 5 || condition == 6) {
                            lastAdded.find('.tt-2').find('.form-control').val(preset[i][0].values[2]);
                            lastAdded.find('.tt-2').find('input[type="number"]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-2').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-3').hide();
                        }
                        else if (condition == 7) {
                            var start_date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            var end_date = moment(preset[i][0].values[2], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-3').find('input[name="start"]').val(start_date);
                            lastAdded.find('.tt-3').find('input[name="end"]').val(end_date);
                            lastAdded.find('.tt-3').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                        }
                        else if (condition == 8 || condition == 9) {
                            lastAdded.find('.date-div').hide();
                        }
                    }
                    else if (preset[i][0].type == 'date_range') {
                        var condition = preset[i][0].values[0];
                        lastAdded.find('.condition-11').show().val(preset[i][0].values[0]);
                        if (condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                            lastAdded.find('.date-div').show();
                            var start_date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            var end_date = moment(preset[i][0].values[2], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-3').find('input[name="start"]').val(start_date);
                            lastAdded.find('.tt-3').find('input[name="end"]').val(end_date);
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-3').show();
                        }
                        if (condition == 5 || condition == 6) {
                            lastAdded.find('.date-div').hide();
                            lastAdded.find('.tt-3').hide();
                        }
                    }
                    else if (preset[i][0].type == 'time') {
                        clog('time');
                        lastAdded.find('.condition-10').show().val(preset[i][0].values[0]);
                        lastAdded.find('.date-div').show();
                        var condition = preset[i][0].values[0];
                        if (condition == 1 || condition == 2 || condition == 3 || condition == 4) {
                            lastAdded.find('.tt-4').find('input[type=text]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-3').hide();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-4').show();
                        }
                        else if (condition == 5 || condition == 6) {
                            lastAdded.find('.tt-5').find('.form-control').val(preset[i][0].values[2]);
                            lastAdded.find('.tt-5').find('input[type="number"]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-3').hide();
                            lastAdded.find('.tt-4').hide();
                            lastAdded.find('.tt-5').show();
                            lastAdded.find('.tt-6').hide();
                        }
                        else if (condition == 7) {
                            lastAdded.find('.tt-6').find('.filter-timepicker-range-from').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-6').find('.filter-timepicker-range-to').val(preset[i][0].values[2]);
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-3').hide();
                            lastAdded.find('.tt-4').hide();
                            lastAdded.find('.tt-5').hide();
                            lastAdded.find('.tt-6').show();
                        }
                        else if (condition == 8 || condition == 9) {
                            lastAdded.find('.date-div').hide();
                        }
                    }
                    else if (preset[i][0].type == 'time_range') {
                        var condition = preset[i][0].values[0];
                        lastAdded.find('.condition-11').show().val(preset[i][0].values[0]);
                        lastAdded.find('.date-div').show();
                        lastAdded.find('.tt-6').find('.filter-timepicker-range-from').val(preset[i][0].values[1]);
                        lastAdded.find('.tt-6').find('.filter-timepicker-range-to').val(preset[i][0].values[2]);
                        lastAdded.find('.tt-1').hide();
                        lastAdded.find('.tt-2').hide();
                        lastAdded.find('.tt-3').hide();
                        lastAdded.find('.tt-4').hide();
                        lastAdded.find('.tt-5').hide();
                        lastAdded.find('.tt-6').show();
                        if (condition == 5 || condition == 6) {
                            lastAdded.find('.date-div').hide();
                            lastAdded.find('.tt-6').hide();
                        }
                    }
                    else if (preset[i][0].type == 'country') {
                        var condition = preset[i][0].values[0];
                        lastAdded.find('.condition-1').show().val(condition);
                        if (condition == 3 || condition == 4) {
                            lastAdded.find('.country-group').hide();
                            lastAdded.find('.country-select').hide();
                        }
                        else {
                            lastAdded.find('.country-group').show();
                            lastAdded.find('.country-select').show();
                            lastAdded.find('.country-select').select2({
                                placeholder: 'Select A Country',
                                data: country_list
                            });
                            lastAdded.find('.country-select').select2('val', preset[i][0].values[1]).trigger('change');
                        }
                    }
                    else {
                        lastAdded.find('.condition-1').show().val(preset[i][0].values[0]);
                        if (preset[i][0].values[0] == 1 || preset[i][0].values[0] == 2) {
                            lastAdded.find('.qid-' + preset[i][0].condition).show().val(preset[i][0].values[2]);
                        }

                    }
                } else if (preset[i][0].field == 9) {
                    lastAdded.find('.rule').val(9);
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.condition-5').hide();
                    lastAdded.find('.condition-4').hide();
                    lastAdded.find('.condition-3').hide();
                    lastAdded.find('.date-div').hide();
                    lastAdded.find('.hotel-group').hide();
                    lastAdded.find('.matched-unmatched').hide();
                    lastAdded.find('.answer-number-container').hide();
                    lastAdded.find('.second-' + preset[i][0].field).show().val(preset[i][0].condition);

                    if (preset[i][0].condition == 2 || preset[i][0].condition == 3) {
                        lastAdded.find('.condition-5').show().val(preset[i][0].values[0]);


                        if (preset[i][0].values[0] == 5 || preset[i][0].values[0] == 6) {
                            lastAdded.find('.date-div').show();
                            clog(preset[i][0].values[1]);
                            lastAdded.find('.tt-2').find('input[type="number"]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-2').find('.form-control').val(preset[i][0].values[2]);
                            lastAdded.find('.tt-2').find('input[type="number"]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-2').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-3').hide();
                        }
                        else if (preset[i][0].values[0] == 7) {
                            lastAdded.find('.date-div').show();
                            var start_date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            var end_date = moment(preset[i][0].values[2], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-3').find('input[name="start"]').val(start_date);
                            lastAdded.find('.tt-3').find('input[name="end"]').val(end_date);
                            lastAdded.find('.tt-3').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                        } else {
                            lastAdded.find('.date-div').show();
                            var date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-1').find('input[type="text"]').val(date);
                            lastAdded.find('.tt-1').show();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-3').hide();
                        }

                    } else if (preset[i][0].condition == 4 || preset[i][0].condition == 5) {
                        lastAdded.find('.condition-4').show().val(preset[i][0].values[0]);
                        lastAdded.find('.answer-number-container').find('input[type="number"]').val(preset[i][0].values[1]);
                        lastAdded.find('.answer-number-container').show();


                    } else if (preset[i][0].condition == 1 || preset[i][0].condition == 6) {
                        lastAdded.find('.condition-3').show().val(preset[i][0].values[0]);
                        if (preset[i][0].condition == 1) {
                            clog(preset[i][0].values[1])
                            lastAdded.find('.hotel-group').show();
                            lastAdded.find('.hotel-group').find('.form-control').val(preset[i][0].values[1]);

                        } else {
                            clog(preset[i][0].values[1])
                            lastAdded.find('.matched-unmatched').show();
                            lastAdded.find('.matched-unmatched').find('.form-control').val(preset[i][0].values[1]);
                        }

                    }


                } else if (preset[i][0].field == 11 || preset[i][0].field == 12) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    lastAdded.find('.condition-6').show();
                    lastAdded.find('.condition-6').val(preset[i][0].values[0]);

                } else if (preset[i][0].field == 13) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    lastAdded.find('.condition-7').show();
                    lastAdded.find('.condition-7').val(preset[i][0].values[0]);
                    if (preset[i][0].values[1]) {
                        lastAdded.find('.page-input-div').show();
                        lastAdded.find('.page-input-div').find('input[type="number"]').val(preset[i][0].values[1]);
                    }
                } else if (preset[i][0].field == 14) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    lastAdded.find('.third-7').show();
                    lastAdded.find('.third-7').val(preset[i][0].values[0]);
                } else if (preset[i][0].field == 15) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    if (preset[i][0].condition == '3') {
                        lastAdded.find('.third-9').show();
                        lastAdded.find('.third-9').val(preset[i][0].values[0]);
                        lastAdded.find(' .value-for-group-registration input').val(preset[i][0].values[1]);
                        lastAdded.find(' .value-for-group-registration').show();
                    } else {
                        lastAdded.find('.third-8').show();
                        lastAdded.find('.third-8').val(preset[i][0].values[0]);
                    }
                } else if (preset[i][0].field == 16) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    if (preset[i][0].condition == '1') {
                        lastAdded.find('.condition-3').show();
                        lastAdded.find('.condition-3').val(preset[i][0].values[0]);
                        lastAdded.find('.forth-16').show();
                        lastAdded.find('.forth-16').val(preset[i][0].values[1]);
                    } else if (preset[i][0].condition == '2' || preset[i][0].condition == '3') {
                        lastAdded.find('.condition-5').show();
                        lastAdded.find('.condition-5').val(preset[i][0].values[0]);
                        lastAdded.find('.date-div').show();
                        if (preset[i][0].values[0] == '5' || preset[i][0].values[0] == '6') {
                            lastAdded.find('.tt-2').find('.form-control').val(preset[i][0].values[2]);
                            lastAdded.find('.tt-2').find('input[type="number"]').val(preset[i][0].values[1]);
                            lastAdded.find('.tt-2').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-3').hide();
                        } else if (preset[i][0].values[0] == '7') {
                            var start_date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            var end_date = moment(preset[i][0].values[2], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-3').find('input[name="start"]').val(start_date);
                            lastAdded.find('.tt-3').find('input[name="end"]').val(end_date);
                            lastAdded.find('.tt-3').show();
                            lastAdded.find('.tt-1').hide();
                            lastAdded.find('.tt-2').hide();
                        } else {
                            var date = moment(preset[i][0].values[1], 'YYYY-MM-DD').format('MM/DD/YYYY');
                            lastAdded.find('.tt-1').find('input[type="text"]').val(date);
                            lastAdded.find('.tt-1').show();
                            lastAdded.find('.tt-2').hide();
                            lastAdded.find('.tt-3').hide();
                        }
                    } else if (preset[i][0].condition == '6' || preset[i][0].condition == '7') {
                        lastAdded.find('.condition-8').show();
                        lastAdded.find('.condition-8').val(preset[i][0].values[0]);
                        if (preset[i][0].values[0] == '5') {
                            lastAdded.find('.answer-number-within-container').show();
                            lastAdded.find('.answer-number-within-container input[name="lowest"]').val(preset[i][0].values[1]);
                            lastAdded.find('.answer-number-within-container input[name="highest"]').val(preset[i][0].values[2]);
                        } else {
                            lastAdded.find('.answer-number-container').show();
                            lastAdded.find('.answer-number-container input').val(preset[i][0].values[1]);
                        }
                    } else {
                        lastAdded.find('.third-8').show();
                        lastAdded.find('.third-8').val(preset[i][0].values[0]);
                    }
                } else if (preset[i][0].field == 18) {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    lastAdded.find('.condition-9').show();
                    lastAdded.find('.condition-9').val(preset[i][0].values[0]);
                }
                else {
                    lastAdded.find('.second').hide();
                    lastAdded.find('.third').hide();
                    lastAdded.find('.rule').val(preset[i][0].field);
                    lastAdded.find('.second-' + preset[i][0].field).show();
                    lastAdded.find('.second-' + preset[i][0].field).val(preset[i][0].condition);
                    lastAdded.find('.third-' + preset[i][0].field).show();
                    lastAdded.find('.third-' + preset[i][0].field).val(preset[i][0].values[0]);
                }
            }
        }
    }
}