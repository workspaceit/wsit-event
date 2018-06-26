$('body').on('click', '#default_answer', function (event) {
    var id = $(this).attr('data-id');
    headerlist = [];
    $('#filter-search-table thead tr th').each(function () {
        var id = $(this).data('id');
        if (typeof id !== 'undefined') {
            headerlist.push({q_id: id});
        }
    });
    $('body .loader').show();
    $.ajax({
        url: base_url + '/admin/attendee/default-answer/',
        type: "GET",
        data: {},
        success: function (result) {
            //var attendee_groups = result.attendee_groups;
            var questions_groups = result.question_groups;
            var date_format = result.datepicker_date_format;
            //var answers = result.answers;
            //var default_group= JSON.parse(result.default_group) ;
            var default_group= result.attendee_groups ;

            var default_group_options = [];
            for (var j = 0; j < default_group.length; j++) {
                var default_group_option = {value: default_group[j].id, text: replaceValueWithSpecialCharacter(default_group[j].name)};
                default_group_options.push(default_group_option);
            }

            var attendeeTags = result.attendee_tags;

            var tagList = [];
            for (var k = 0; k < attendeeTags.length; k++) {
                tagList.push({id: attendeeTags[k].id, text: attendeeTags[k].name});
            }
            clog(tagList);
            $('.attendee-question-attendee-tags').select2('data', tagList);

            $('#default-answer-group-selection').editable({
                value: result.default_selected_group,
                source: default_group_options
            });

            var appendDiv = "edit-attendee-questions";
            for (var i = 0; i < questions_groups.length; i++) {
                var appendClass = "attendee-group-" + questions_groups[i].group.id + "-allQuestions";
                showAttendeeQuestionsDefault(questions_groups[i].questions[0], appendDiv, appendClass, date_format);
            }

            showAttendeeSessionDefault(result.sessions,appendDiv,"allSessions","session")
            showAttendeeSessionDefault(result.travels,appendDiv,"allTravels","travel")


            //var attendee_groupList = [];
            //for (var j = 0; j < attendee_groups.length; j++) {
            //    var group = {value: attendee_groups[j].id, text: attendee_groups[j].name}
            //    attendee_groupList.push(group);
            //}


            var addTable = $('#attendee-edit-hotels');
            addTable.find('.total').html('');
            addTable.find('tbody').html('');

            //$('#edit-attendee-question-attendee-groups').editable({
            //    limit: 1,
            //    source: attendee_groupList
            //});


            //$('#edit-attendee-question-company').editable({
            //    validate: function (value) {
            //        if ($.trim(value) == '') return 'This field is required';
            //    }
            //});
            //$('#edit-attendee-question-email').editable({
            //    validate: function (value) {
            //        if ($.trim(value) == '') return 'This field is required';
            //    }
            //});
            //$('#edit-attendee-question-phone-number').editable({
            //    validate: function (value) {
            //        if ($.trim(value) == '') return 'This field is required';
            //    }
            //});
            //$('#edit-attendee-question-information1').editable({
            //    source: [
            //        {value: 1, text: 'Yes'},
            //        {value: 2, text: 'No'},
            //        {value: 3, text: 'Unsure'}
            //    ]
            //});
            //$('#edit-attendee-question-information2').editable({
            //    validate: function (value) {
            //        if ($.trim(value) == '') return 'This field is required';
            //    }
            //});
            //$('#edit-attendee-question-information3').editable({
            //    showbuttons: 'bottom'
            //});
            //$('#edit-attendee-question-food1').editable({
            //    source: [
            //        {value: 1, text: 'No'},
            //        {value: 2, text: 'Vegetarian'},
            //        {value: 3, text: 'Vegan'}
            //    ]
            //});
            //$('#edit-attendee-question-food2').editable({
            //    showbuttons: 'bottom'
            //});
            $('body .loader').hide();
        }
    });
});





function showAttendeeQuestionsDefault(questions, appendDiv, appendClass, date_format) {
    $('.' + appendClass).html('');
//    console.log(appendClass);
//    console.log(questions);
//    console.log(answers);
//    alert("ok");
//    var allquestions = '';
    for (var i = 0; i < questions.length; i++) {
        var questionClass = "text-question-information";
        var dataType = "text";
        var value='';
        if (questions[i].options.length > 0) {
            for (var k = 0; k < questions[i].options.length; k++) {
                if (replaceValueWithSpecialCharacter(questions[i].question.default_answer) == replaceValueWithSpecialCharacter(questions[i].options[k].option)) {
                    value = questions[i].options[k].id;
                }
            }
        } else {
            value = questions[i].question.default_answer;
        }

        clog(questions[i].question.default_answer_status);
        var req = questions[i].question.required;
        var options = [];
        for (var j = 0; j < questions[i].options.length; j++) {
            var option = {value: questions[i].options[j].id, text: questions[i].options[j].option}
            options.push(option);
        }
        if (questions[i].question.type == "select") {
            questionClass = "select-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "radio_button") {
            questionClass = "radio-question-information-" + questions[i].question.id;
            dataType = "select";
        } else if (questions[i].question.type == "checkbox") {
            questionClass = "checkbox-question-information-" + questions[i].question.id;
            dataType = "checklist";
        } else if (questions[i].question.type == "date") {
            questionClass = "date-question-default date-question-information-" + questions[i].question.id;
            dataType = "date";
        } else if (questions[i].question.type == "textarea") {
            questionClass = "textarea-question-information-" + questions[i].question.id;
            dataType = "textarea";
        } else if (questions[i].question.type == "rate") {
            questionClass = "rate-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "image_upload") {
            questionClass = "image_upload-question-information-" + questions[i].question.id;
        } else if (questions[i].question.type == "password") {
            questionClass = "password-question-information-" + questions[i].question.id;
        } else if(questions[i].question.type == "time") {
            questionClass = "time-question-default time-question-information-" + questions[i].question.id;
            dataType = "time";
        } else if(questions[i].question.type == "date_range") {
            questionClass = "date-range-question-information-" + questions[i].question.id;
            dataType = "date";
            value = replaceValueWithSpecialCharacter(value);
        } else if(questions[i].question.type == "time_range") {
            questionClass = "time-range-question-default time-range-question-information-" + questions[i].question.id;
            dataType = "time";
            value = replaceValueWithSpecialCharacter(value);
        } else if(questions[i].question.type == "country") {
            questionClass = "country-question-default country-question-information-" + questions[i].question.id;
            dataType = "select";
        }
        if(questions[i].question.type == 'date' || questions[i].question.type == 'date-range') {
            var to_date = questions[i].question.to_date;
            var from_date = questions[i].question.from_date;
            from_date = moment(from_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
            to_date = moment(to_date, 'YYYY-MM-DD').format(date_format.toUpperCase());
        }
        var option_set='<option value="set">Set Value</option>';
        var option_leave='<option value="leave">Leave as is</option>';
        var option_empty='<option value="empty">Empty Value</option>';
        if(questions[i].question.default_answer_status=='set')
            option_set='<option value="set" selected>Set Value</option>';
        if(questions[i].question.default_answer_status=='leave') {
            option_leave='<option value="leave" selected>Leave as is</option>';
            value = '';
        }
        if(questions[i].question.default_answer_status=='empty') {
            option_empty = '<option value="empty" selected>Empty Value</option>';
            value = '';
        }
        var allquestions = '<tr>' +
                '<td style="width: 30%;"><select class="form-control answer-status" >'+option_leave+option_set+option_empty+'</select>'+'</td>'+
            '<td style="width: 30%;">' + questions[i].question.title + '</td>' +
            '<td><a href="#" class="' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value + '" data-title="' + questions[i].question.title + '" data-req=' + req + '></a></td>' +
            '</tr>';
        if(questions[i].question.type == "date_range") {
            if(value != null && value != '') value = JSON.parse(value);
            else if(value == null || value == '') value = ['',''];
            allquestions = '<tr>' +
                '<td style="width: 30%;"><select class="form-control answer-status" >'+option_leave+option_set+option_empty+'</select>'+'</td>'+
            '<td style="width: 30%;">' + questions[i].question.title + '</td>' +
            '<td>' +
            '<a href="#" class="date-range-from-default ' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value[0] + '" data-title="date-range-from" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a> to ' +
            '<a href="#" class="date-range-to-default ' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value[1] + '" data-title="date-range-to" data-req=' + req + ' data-range-from-date=' + questions[i].question.from_date + ' data-range-to-date=' + questions[i].question.to_date + '></a>' +
            '</td>' +
            '</tr>';
        }
        else if(questions[i].question.type == "time_range") {
            if(value != null && value != '') value = JSON.parse(value);
            else if(value == null || value == '') value = ['',''];
            allquestions = '<tr>' +
                '<td style="width: 30%;"><select class="form-control answer-status" >'+option_leave+option_set+option_empty+'</select>'+'</td>'+
            '<td style="width: 30%;">' + questions[i].question.title + '</td>' +
            '<td><a href="#" class="time-range-from-default ' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value[0] + '" data-title="time-range-from" data-req=' + req + '></a> to ' +
            '<a href="#" class="time-range-to-default ' + questionClass + '" name="questions[]" data-type="' + dataType + '" data-pk="' + questions[i].question.id + '" data-value="' + value[1] + '" data-title="time-range-to" data-req=' + req + '></a>' +
            '</td>' +
            '</tr>';
        }
        else if(questions[i].question.type == "country") {
            options = [];
            options.push({value: '', text: ''});
            for(var k=0;k<country_list.length;k++) {
                var option = {value: country_list[k].id, text: country_list[k].text};
                options.push(option);
            }
        }
        $('#' + appendDiv).find('.' + appendClass).append(allquestions);
        if (typeof questions[i].access != "undefined" && questions[i].access == 'write') {
            $('.text-question-information').editable({
//            validate: function (value) {
//                if ($.trim(value) == '') return 'This field is required';
//            }
            });

            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.country-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options
            });
            $('.date-question-information-' + questions[i].question.id).editable({
                mode: 'popup',
                format: 'yyyy-mm-dd',
                viewformat: date_format,
                datepicker: {
                    weekStart: 1,
                    startDate: from_date,
                    endDate: to_date
                }
            });
            $('.date-range-question-information-' + questions[i].question.id).editable({
                mode: 'popup',
                format: 'yyyy-mm-dd',
                viewformat: date_format,
                datepicker: {
                    weekStart: 1,
                    startDate: from_date,
                    endDate: to_date
                }
            });
            $('.time-question-information-' + questions[i].question.id).editable({
                mode: 'popup',
                format: 'hh:ii',
                viewformat: 'hh:ii'

            });
            $('.time-range-question-information-' + questions[i].question.id).editable({
                mode: 'popup',
                format: 'hh:ii',
                viewformat: 'hh:ii'

            });
            $('.textarea-question-information-' + questions[i].question.id).editable({
//            validate: function (value) {
//                if ($.trim(value) == '') return 'This field is required';
//            }
            });
        } else {
            $('.text-question-information').editable({
                disabled: true
            });

            $('.select-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.checkbox-question-information-' + questions[i].question.id).editable({
                type: "checklist",
                source: options,
                disabled: true
            });
            $('.radio-question-information-' + questions[i].question.id).editable({
                type: "select",
                source: options,
                disabled: true
            });
            $('.date-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
            $('.textarea-question-information-' + questions[i].question.id).editable({
                disabled: true
            });
        }


    }

}



function showAttendeeSessionDefault(sessions, appendDiv, appendClass,sessionType) {
    $('.' + appendClass).html('');
    for (var i = 0; i < sessions.length; i++) {
        var sessionClass = sessionType+"-information";
        var dataType = "text";
        var value='';
        for (var k = 0; k < sessions[i].options.length; k++) {
            if (sessions[i].session.default_answer == sessions[i].options[k].id) {
                value = sessions[i].options[k].id;
            }
        }


        var options = [];
        for (var j = 0; j < sessions[i].options.length; j++) {
            var option = {value: sessions[i].options[j].id, text: sessions[i].options[j].value}
            options.push(option);
        }
        sessionClass = "select-"+sessionType+"-information-" + sessions[i].session.id;
        dataType = "select";
        var option_set='<option value="set">Set Value</option>';
        var option_leave='<option value="leave">Leave as is</option>';
        var option_empty='<option value="empty">Empty Value</option>';
        if(sessions[i].session.default_answer_status=='set')
            option_set='<option value="set" selected>Set Value</option>';
        if(sessions[i].session.default_answer_status=='leave')
            option_leave='<option value="leave" selected>Leave as is</option>';
        if(sessions[i].session.default_answer_status=='empty')
            option_empty='<option value="empty" selected>Empty Value</option>';
        var allquestions = '<tr>' +
                '<td style="width: 30%;"><select class="form-control answer-status" >'+option_leave+option_set+option_empty+'</select>'+'</td>'+
            '<td  style="width: 30%;">' + sessions[i].session.name + '</td>' +
            '<td><a href="#" class="' + sessionClass+ '" name="'+sessionType+'[]" data-type="' + dataType + '" data-pk="' + sessions[i].session.id + '" data-value="' + value + '" data-title="' + sessions[i].session.name + '" ></a></td>' +
            '</tr>';
        $('#' + appendDiv).find('.' + appendClass).append(allquestions);



        $('.select-session-information-' + sessions[i].session.id).editable({
            type: "select",
            source: options
        });

        $('.select-travel-information-' + sessions[i].session.id).editable({
            type: "select",
            source: options
        });



    }

}


