/**
 * Created by sunno on 5/18/16.
 */
$(function(){
    var window_location = window.location.href;
    var window_location_array = window_location.split("/");
    var id = window_location_array[window_location_array.length-2] ;
    headerlist = [];
    $('#filter-search-table thead tr th').each(function () {
        var id = $(this).data('id');
        if (typeof id !== 'undefined') {
            headerlist.push({q_id: id});
        }
    });
    $('body .loader').show();
    $.ajax({
        url: base_url + '/admin/attendee/' + id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            var activity_history = result.activity_history;
            $('#edit-attendee-history').html(activity_history);
            var attendee_sessions = result.attendee_sessions;
            var attendee_travels = result.attendee_travels;
            var attendee_groups = result.attendee_groups;
            var outbound_flights = result.outbound_flights;
            var homebound_flights = result.homebound_flights;
            var user = result.user;
            questions_groups = result.question_groups;
            answers = result.answers;
            //attendee_group = user.group.id;
            attendee_group = result.attendee_selected_groups;

            var bookingsBuddies = result.bookings_buddies;
            var attendeeTags = result.attendee_tags;
            $('.attendee-panel-title strong').html(user.firstname + ' ' + user.lastname);

            $('#edit-registration-date').html(moment.tz(user.created, timeZone).format('MM/DD/YYYY HH:mm A'));
            $('#edit-update-date').html(moment.tz(user.updated, timeZone).format('MM/DD/YYYY HH:mm A'));

            //$('#edit-registration-date').html(moment(user.created, 'YYYY-MM-DD HH:mm').format('MM/DD/YYYY HH:mm A'));
            //$('#edit-update-date').html(moment(user.updated, 'YYYY-MM-DD HH:mm').format('MM/DD/YYYY HH:mm A'));
            $('#edit-user-id').html(user.id);
            $('#edit-external-user-id').html(user.secret_key);
            $('#login-uid').attr('href',$('#login-uid').attr('data-href')+"?uid="+user.secret_key);
            $('#edit-attendee-question-password').html(user.password);
//            $('#edit-attendee-question-attendee-groups').attr('data-value', user.group.id);
//            $('#edit-attendee-question-attendee-groups').editable('setValue',user.group.id);
            $('#edit-attendee-question-first-name').html(user.firstname);
            $('#edit-attendee-question-last-name').html(user.lastname);
            $('#edit-attendee-question-company').html(user.company);
            $('#edit-attendee-question-email').html(user.email);
            $('#edit-attendee-question-phone-number').html(user.phonenumber);
            var appendDiv = "search-edit-attende";
            for (var i = 0; i < questions_groups.length; i++) {
                var appendClass = "attendee-group-" + questions_groups[i].group.id + "-allQuestions";
                showAttendeeQuestions(questions_groups[i].questions[0], appendDiv, appendClass, outbound_flights, homebound_flights, answers);
            }
//            var appendClass = "attendee-info-allQuestions";
//            showAttendeeQuestions(questions_information, appendDiv, appendClass, answers);
//            appendClass = "attendee-food-allQuestions";
////            $('.attendee-info-allQuestions').html(info_questions);
//            showAttendeeQuestions(questions_food, appendDiv, appendClass, answers);
//            $('.attendee-food-allQuestions').html(food_questions);
            var session_row = '';
            if (result.assign_session_write_access) {
                for (var i = 0; i < attendee_sessions.length; i++) {
                    var created = "N/A";
                    if (attendee_sessions[i].created != 'None') {
                        created = moment.tz(attendee_sessions[i].created, timeZone).format('YYYY-MM-DD HH:mm:ss');
                    }

                    session_row += '<tr>' +
                        '<td></td>' +
                        '<td>' + attendee_sessions[i].session.name + '</td>' +
                        '<td>' + moment(attendee_sessions[i].session.start, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + moment(attendee_sessions[i].session.end, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + attendee_sessions[i].status + '</td>' +
                            //'<td>' + moment.tz(created ,timeZone).format('MM/DD/YYYY HH:mm A')+ '</td>' +
                        '<td>' + created + '</td>' +

//                    '<td>€120</td>' +
//                    '<td>€20 (Student)</td>' +
//                    '<td>€100</td>' +
//                    '<td>25%</td>' +
//                    '<td>€125</td>' +
                        '</tr>';

                }
            } else {
                for (var i = 0; i < attendee_sessions.length; i++) {
                    var created = "N/A";
                    if (attendee_sessions[i].created != 'None') {
                        created = moment.tz(attendee_sessions[i].created, timeZone).format('YYYY-MM-DD hh:mm:ss');
                    }

                    session_row += '<tr>' +
                        '<td></td>' +
                        '<td>' + attendee_sessions[i].session.name + '</td>' +
                        '<td>' + moment(attendee_sessions[i].session.start, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + moment(attendee_sessions[i].session.end, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + attendee_sessions[i].status + '</td>' +
                        '<td>' + created + '</td>' +
                        '</tr>';

                }
            }
            $('#edit-attendee-sessions').find('.attendee-sessions').html(session_row);

            var travel_row = '';
            if (result.assign_travel_write_access) {
                for (var i = 0; i < attendee_travels.length; i++) {
                    var created = "N/A";
                    if (attendee_travels[i].created != 'None') {
                        created = moment.tz(attendee_travels[i].created, timeZone).format('YYYY-MM-DD HH:mm:ss');

                    }
                    travel_row += '<tr>' +
                        '<td></td>' +
                        '<td>' + attendee_travels[i].travel.name + '</td>' +
                        '<td>' + moment(attendee_travels[i].travel.departure, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + moment(attendee_travels[i].travel.arrival, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + attendee_travels[i].status + '</td>' +
                            //'<td>' +moment.tz(created ,timeZone).format('MM/DD/YYYY HH:mm A')+ '</td>' +
                        '<td>' + created + '</td>' +
//                    '<td>€120</td>' +
//                    '<td>€20 (Student)</td>' +
//                    '<td>€100</td>' +
//                    '<td>25%</td>' +
//                    '<td>€125</td>' +
                        '</tr>';
                }
            } else {
                for (var i = 0; i < attendee_travels.length; i++) {
                    var created = "N/A";
                    if (attendee_travels[i].created != 'None') {
                        created = moment.tz(attendee_travels[i].created, timeZone).format('YYYY-MM-DD hh:mm:ss');

                    }
                    travel_row += '<tr>' +
                        '<td></td>' +
                        '<td>' + attendee_travels[i].travel.name + '</td>' +
                        '<td>' + moment(attendee_travels[i].travel.departure, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + moment(attendee_travels[i].travel.arrival, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss') + '</td>' +
                        '<td>' + attendee_travels[i].status + '</td>' +
                        '<td>' + created + '</td>' +
                        '</tr>';
                }
            }

            $('#edit-attendee-travels').find('.attendee-travels').html(travel_row);
            var attendee_groupList = [];
            for (var j = 0; j < attendee_groups.length; j++) {
                var group = {value: attendee_groups[j].id, text: attendee_groups[j].name}
                attendee_groupList.push(group);
            }
            var tagList = [];
            for (var k = 0; k < attendeeTags.length; k++) {
                tagList.push({id: attendeeTags[k].tag.id, text: attendeeTags[k].tag.name});
            }
            $('#edit-attendee-questions').find('.attendee-question-attendee-tags').select2('data', tagList);

            var addTable = $('#attendee-edit-hotels');
            addTable.find('.total').html('');
            addTable.find('tbody').html('');

            for (var i = 0; i < bookingsBuddies.length; i++) {
                var booking = bookingsBuddies[i]['booking'];
                var buddies = bookingsBuddies[i].buddies;

                var room_id = booking.room.id;
                var room_description = booking.room.description + '-' + booking.room.hotel.name;
//                var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('MM/DD/YYYY');
//                var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('MM/DD/YYYY');
                var check_in = moment(booking.check_in, 'YYYY-MM-DD').format('YYYY-MM-DD');
                var check_out = moment(booking.check_out, 'YYYY-MM-DD').format('YYYY-MM-DD');
                var cost = Number(booking.room.cost);
                //var vat = Number(booking.room.vat.name);
                var total = cost;
                var allHotels = $('#hotel-selector').html();
                if (result.assign_hotel_write_access) {
                    var row = '' +
                        '<tr">' +
                        '<td></td>' +
                        '   <td>' + room_description +
                        '   </td>' +
                        '   <td>' +
                        '       <div class="form-group">' +
                        '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
                        '               <input type="text" class="input-sm form-control" name="start" placeholder="Start date" value="' + check_in + '">' +
                        '               <span class="input-group-addon">to</span>' +
                        '               <input type="text" class="input-sm form-control" name="end" placeholder="End date" value="' + check_out + '">' +
                        '           </div>' +
                        '       </div>' +
                        '   </td>' +
                        '   <td>' +
                        '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies"></a>' +
                        '   </td>' +
//                    '   <td class="cost">' + cost + '</td>' +
//                    '   <td class="">€20 (Student)</td>' +
//                    '   <td>' + cost + '</td>' +
//                    '   <td>' + vat + '</td>' +
//                    '   <td>' + total + '</td>' +
                        '</tr>';
                } else {
                    var row = '' +
                        '<tr data-booking-id="' + booking.id + '">' +
                        '   <td></td>' +
                        '   <td>' + room_description +
                        '   </td>' +
                        '   <td>' +
                        '       <div class="form-group">' +
                        '           <div class="input-daterange input-group add-attendee-hotels-datepicker-range">' +
                        '               <input type="text" class="input-sm form-control" name="start" placeholder="Start date" value="' + check_in + '" disabled>' +
                        '               <span class="input-group-addon">to</span>' +
                        '               <input type="text" class="input-sm form-control" name="end" placeholder="End date" value="' + check_out + '" disabled>' +
                        '           </div>' +
                        '       </div>' +
                        '   </td>' +
                        '   <td>' +
                        '       <a href="#" class="add-attendee-hotel-select-room-buddies" data-type="select2" data-pk="1" data-title="Room Buddies" style="pointer-events:none;"></a>' +
                        '   </td>' +
                        '</tr>';
                }

                var lastRow = '';
//                    '<td colspan="4">TOTAL</td>' +
//                    '<td>$310</td>' +
//                    '<td>$50</td>' +
//                    '<td>$260</td>' +
//                    '<td>25%</td>' +
//                    '<td>€325</td>';
                addTable.find('.total').html(lastRow);
                addTable.find('tbody').append(row);

                $('.add-attendee-hotels-datepicker-range').datepicker({format: 'yyyy-mm-dd'});
                activateAutoSuggestForBuddies();
                var lastInsertedRow = addTable.find('tbody').children('tr:last').find('.add-attendee-hotel-select-room-buddies');
                addTable.find('tbody').children('tr:last').find('select').val(room_id);
                var alraedyThere = [];
                for (var j = 0; j < buddies.length; j++) {
                    if (buddies[j].exists == 1) {
                        alraedyThere.push({
                            id: buddies[j].buddy.id,
                            text: buddies[j].buddy.firstname + ' ' + buddies[j].buddy.lastname
                        });
                    }
                    else {
                        alraedyThere.push({id: buddies[j].email, text: buddies[j].email});
                    }
                }
                lastInsertedRow.select2('data', alraedyThere);
            }
//            $('.text-question-information').editable({
//                validate: function (value) {
//                    if ($.trim(value) == '') return 'This field is required';
//                }
//            });
//            $('.radio-question-information').editable({
//                source: [
//                    {value: 1, text: 'Yes'},
//                    {value: 2, text: 'No'}
//                ]
//            });

            $('body .loader').hide();
            //$("#search-edit-attende").modal();
        }
    });

});