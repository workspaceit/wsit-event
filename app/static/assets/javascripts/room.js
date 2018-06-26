/* bookings Match Start */

/* pair matched bookings */

$('body').on('click', '.btn-pair-up', function (e) {
    var unmatchedTable = $('.match-table-unmatched');
    var rows = unmatchedTable.find('tbody tr');
    var bookingIds = [];
    rows.each(function () {
        var row = $(this);
        var checkbox = row.find('td:first').find('input[type="checkbox"]');
        var checked = checkbox.prop('checked');
        if (checked) {
            var bookingId = checkbox.data('id');
            bookingIds.push(bookingId);
        }
    });
    clog('booking ids: ' + JSON.stringify(bookingIds));
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: base_url + '/admin/hotels/match/pairup/',
        type: "POST",
        data: {
            bookings: JSON.stringify(bookingIds),
            csrfmiddlewaretoken: csrf_token
        },
        success: function (response) {
            if (response.success) {
                clog(response)
                $.growl.notice({message: response.message});
                $('.match-table-matched tbody').append(response.view)
                var rows = unmatchedTable.find('tbody tr');
                rows.each(function () {
                    var row = $(this);
                    var checkbox = row.find('td:first').find('input[type="checkbox"]');
                    var id = checkbox.data('id')
                    if($.inArray(id,bookingIds)!=-1){
                        row.remove();
                    }
                });
            }
            else {
                $.growl.error({message: response.message});
            }
        }
    });
});

/* break the pair */

$('body').on('click', '.btn-break-up', function (e) {
    var tbody = $(this).closest('tbody');
    var totalBookings = $(this).parent().attr('rowspan');
    var n = $(this).closest('tr').index();
    clog(n);
    var rows = tbody.find('tr').slice(n, n + 2);
    var bookingIds = [];
    rows.each(function () {
        var row = $(this);
        bookingIds.push(row.data('booking-id'));
    });
    clog(bookingIds);
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: base_url + '/admin/hotels/match/breakup/',
        type: "POST",
        data: {
            bookings: JSON.stringify(bookingIds),
            csrfmiddlewaretoken: csrf_token
        },
        success: function (response) {

            if (response.success) {
                 clog(response);
                $.growl.notice({message: response.message});
                $('.match-table-unmatched tbody').append(response.data);
                 rows.each(function () {
                     var row = $(this);
                     row.remove();
                 });
                //setTimeout(function () {
                //    window.location = ''
                //}, 500);
            }
            else {
                $.growl.error({message: response.message});
            }
        }
    });
});

/* bookings Match End */


/* Hotel and Room Start */

/* Add new room */

$('body').on('click', '.addRoom', function (event) {

    var allotment_datas = [];
    var allotment_table = $("#hotel-details-room-allotments tbody").html();
    var validation_flag = false;
    $.each($("#hotel-details-room-allotments tbody tr"), function (i, tr) {
        var allotment_data = [];
        allotment_data[0] = $('td:nth-child(1)', tr).text();
        allotment_data[1] = $('td:nth-child(2)', tr).text();
        var room_allotment_cost = $(this).find('input[name="room-allotment-cost"]').val();
        var room_allotment_vat = $(this).find('.edit-room-allotment-vat').val();
        if(room_allotment_cost > 0){
            if (room_allotment_vat == undefined || room_allotment_vat == 0 || room_allotment_vat == ''){
                $.growl.warning({message: "Allotment cost or vat not set properly."});
                validation_flag = true;
                return
            }
        }
        allotment_data[2] = room_allotment_cost;
        allotment_data[3] = room_allotment_vat;
        allotment_datas.push(allotment_data);
    });
    if (validation_flag){
        return;
    }
    allotment_datas = JSON.stringify(allotment_datas);

    var pushArray = true;
    var description = $(".room-name").val();
    var bed = $(".bed-no").val();
    //var vatWithPercent = $('.room-vat option:selected').text();
    var vat = $('.room-vat option:selected').val();
    if (vat != ''){
        var vat = vat.split('%')[0];
    }
    //var vat = vatWithPercent.split('%')[0];
    // var vat = $('.room-vat option:selected').val();
    var cost = $('.room-cost').val();
    if (cost > 0){
        if(vat == ''){
            alert("Cost required VAT");
            return;
        }
    }
    var pay_whole_hotel_amount = $('.filter-question-selector-pay-whole-hotel-amount').is(":checked");
    var $roomList = $("#roomList");
    var $roomListView = $(".hotel-room");

    if (description != "" && bed != "") {
    // if (description != "" && bed != "") {
        if (bed < 1){
            alert("beds should be more than 0");
            return;
        }
        var roomList = JSON.parse($roomList.val());
        var roomListTemp = {
            description: description,
            bed: parseInt(bed),
            occupancy: 0,
            vat: vat,
            cost: cost,
            pay_whole_hotel_amount: pay_whole_hotel_amount,
            allotments: allotment_datas
        };
        if (pushArray) {
            roomList.push(roomListTemp);
            $roomListView.append('<tr id="roomRow' + roomList.length + '">' +
                '<td>' + roomListTemp.bed + '</td>' +
                '<td>' + roomListTemp.description + '</td>' +
                '<td>' + roomListTemp.occupancy + '%</td>' +
                '</tr>');
        }
        $roomList.val(JSON.stringify(roomList));
        $('#hotel-details-add-room').modal('hide');
        $('#hotel-details-room-allotments tbody').html('');
        var table = $("#hotel-details-room-allotments").DataTable();
        table.clear().draw();
    } else {
        alert("All room fields required !");

    }
});

/* Edit room */

$('body').on('click', '.editRoom', function (event) {
    var id = $('#room-edit-id').val();
    var description = $(".edit-room-name").val();
    var description_lang = valueWithSpecialCharacter(description);
    var current_language_id = $('.hotel-language-presets-selector').select2('val');
    var bed = $(".edit-bed-no").val();
    //var vatWithPercent = $('.edit-room-vat option:selected').text();
    //var vat = vatWithPercent.split('%')[0];
    var vat = $('.edit-room-vat option:selected').val();
    if (vat != ''){
        var vat = vat.split('%')[0];
    }
    var cost = $('.edit-room-cost').val();
    if (cost > 0){
        if(vat == ''){
            alert("Cost required VAT");
            return;
        }
    }
    var pay_whole_hotel_amount = $('.filter-question-selector-pay-whole-hotel-amount').is(":checked");
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var error = false;
    var validation_flag = false;

    var allotment_datas = [];
    $.each($("#hotel-details-room-allotments_edit tbody tr.new_data"), function (i, tr) {
        var allotment_data = [];
        allotment_data[0] = $('td:nth-child(1)', tr).text();
        allotment_data[1] = $('td:nth-child(2)', tr).text();
        var room_allotment_cost = $(this).find('input[name="room-allotment-cost"]').val();
        var room_allotment_vat = $(this).find('.edit-room-allotment-vat').val();
        if(room_allotment_cost > 0) {
            if (room_allotment_vat == undefined || room_allotment_vat == 0 || room_allotment_vat == '') {
                $.growl.warning({message: "Allotment cost or vat not set properly."});
                validation_flag = true;
                return
            }
        }
        allotment_data[2] = $(this).find('input[name="room-allotment-cost"]').val();
        allotment_data[3] = $(this).find('.edit-room-allotment-vat').val();
        allotment_datas.push(allotment_data);
    });

    /**
     *  Checking all room allotment cost
     */
    var room_allotment_cost_array=$('input[name^="room-allotment-cost"]');
    var room_allotment_cost_have=[];
    room_allotment_cost_array.each(function() {
        if ($(this).val().length>0 && $(this).val()!="0") {
            room_allotment_cost_have.push(true);
        }
        else{room_allotment_cost_have.push(false);}
    });
    room_allotment_cost_have.forEach(function (value) {
        if(room_allotment_cost_have[0]!=value && !error){
            error=true;
            $.growl.warning({message: "All allotment cost not set properly."});
        }
    });

    /**
     *  Checking all room allotment vat
     */
    var room_allotment_vat_array=$(".edit-room-allotment-vat");
    var room_allotment_vat_have=[];
    room_allotment_vat_array.each(function() {
        room_allotment_vat_have.push(($(this).val()));
    });
    room_allotment_vat_have.forEach(function (value) {
        if(room_allotment_vat_have[0]!=value && !error){
            error=true;
            $.growl.warning({message: "All allotment vat not set same properly."});
        }
    });

    if (validation_flag){
        return;
    }
    allotment_datas = JSON.stringify(allotment_datas);
    validation_flag = false;
    check_existing_allotment_cost_vat_changes();
    var update_allotment_datas = [];
    $.each($("#hotel-details-room-allotments_edit tbody tr.update_tr"), function (i, tr) {
        var update_allotment_data = [];
        update_allotment_data[0] = $(tr).attr("tr-allotment_id");
        update_allotment_data[1] = $.trim($('td:nth-child(2) a.room-allotments', tr).text());
        var room_allotment_cost = $(this).find('input[name="room-allotment-cost"]').val();
        var room_allotment_vat = $(this).find('.edit-room-allotment-vat').val();
        if(room_allotment_cost > 0) {
            if (room_allotment_vat == undefined || room_allotment_vat == 0 || room_allotment_vat == '') {
                $.growl.warning({message: "Allotment cost or vat not set properly."});
                validation_flag = true;
                return
            }
        }
        update_allotment_data[2] = room_allotment_cost;
        update_allotment_data[3] = room_allotment_vat;
        update_allotment_datas.push(update_allotment_data);
    });
    if (validation_flag){
        return;
    }
    update_allotment_datas = JSON.stringify(update_allotment_datas);

    if ($.trim(description) == "" || $.trim(description) == "Empty") {
        error = true;
        $.growl.warning({message: "Please fill up Description field"});
    } else if ($.trim(bed) == "" || $.trim(bed) == 0) {
        error = true;
        $.growl.warning({message: "Please fill up Bed# field"});
    }

    if (!error) {
        $.ajax({
            url: base_url + '/admin/rooms/',
            type: "POST",
            data: {
                id: id,
                description: description,
                description_lang: description_lang,
                bed: bed,
                //vat: vat,
                vat: vat,
                cost: cost,
                pay_whole_hotel_amount: pay_whole_hotel_amount,
                csrfmiddlewaretoken: csrf_token,
                allotments: allotment_datas,
                update_allotment_datas: update_allotment_datas,
                current_language_id: current_language_id
            },
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    $('#hotel-details-edit-room').modal('hide');
                    var room = result.room;
                    console.log(room.description_lang);
                    var row = '' +
                        '<td>' + room.beds + '</td>' +
                        '<td class="room-description" data-lang=\''+room.description_lang.replace(/'/g, "\\'")+'\'>' + getcontentByLanguage(room.description, room.description_lang, current_language_id) + '</td>' +
                        '<td>' + room.occupancy + '%</td>';
                    $('.hotel-room tr').each(function () {
                        if ($(this).data('id') == room.id) {
                            $(this).html(row);
                        }
                    });
                    $("#hotel-details-room-allotments_edit tbody").html("");
                }
            }
        });
    }
});

function check_existing_allotment_cost_vat_changes() {
    $('.existing_allotment_tr').each(function () {
        var tr = $(this);
        var flag = false;
        if(tr.find('input[name="room-allotment-cost"]').val() != tr.find('input[name="room-allotment-cost"]').attr('data-cost')){
            flag = true;
        }else if(tr.find('.edit-room-allotment-vat').val() != tr.find('.edit-room-allotment-vat').attr('data-vat')){
            flag = true;
        }
        if(flag && !tr.hasClass('update_tr')){
            tr.addClass('update_tr');
        }
    })
}

/* Delete room */

$('body').on('click', '.deleteRoom', function (event) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Room?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/rooms/delete/',
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
                        if ($this.data('page') == 'hotel') {
                            $this.closest('tr').remove();
                        } else {
                            $('#hotel-details-edit-room').modal('hide');
                            $('body .hotel-room tr').each(function () {
                                if ($(this).data('id') == id) {
                                    $(this).remove();
                                }
                            });
                        }
                    }
                }
            });
        }
    });
});
/* Create new Hotel */

$('body').on('click', '.createHotel', function (event) {

//        alert("hi");
//        var allotment_datas = [];
//        $.each($("#hotel-details-room-allotments tbody tr"), function (i, tr) {
//            var allotment_data = [];
//            allotment_data[0] = $('td:nth-child(1)', tr).text();
//            allotment_data[1] = $('td:nth-child(2)', tr).text();
////            allotment_data[2] = $('td:nth-child(3)', tr).text();
//            allotment_datas.push(allotment_data);
//        });
//        allotment_datas = JSON.stringify(allotment_datas);


    var name = $('.hotel-name').val();
    var name_lang = valueWithSpecialCharacter(name);
    var location = $('.hotel-location option:selected').val();
    var group = $('.hotel-category option:selected').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var error = false;
    var msg = "";
    var rooms = $('#roomList').val();
    if ($.trim(name) == "" || $.trim(name) == "Empty") {
        error = true;
        msg = "Please fill up Hotel Name field";
    } else if ($.trim(location) == "" || $.trim(location) == "Empty") {
        error = true;
        msg = "Please fill up Location field";
    } else if ($.trim(group) == "" || $.trim(group) == "Empty") {
        error = true;
        msg = "Please fill up Category field";
    }
    if (error) {
        $.growl.warning({message: msg});
    } else {
        $.ajax({
            url: base_url + '/admin/hotels/',
            type: "POST",
            data: {
                name: name,
                name_lang: name_lang,
                location: location,
                group: group,
                rooms: rooms,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $.growl.notice({message: result.success});
                    setTimeout(function () {
                        window.location.href = base_url + '/admin/hotels/';
                    }, 1000);
                }
            }
        });
    }
});

/* Edit Hotel */

$('body').on('click', '.editHotel', function (event) {
    var id = $('#hotel-edit-id').val();
    var name = $('.hotel-name').val();
    var name_lang = valueWithSpecialCharacter(name);
    var location = $('.hotel-location option:selected').val();
    var group = $('.hotel-category option:selected').val();
    var current_language_id = $('.hotel-language-presets-selector').select2('val');
    default_language_id = $('#hotel_defualt_language_id').val();
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var error = false;
    var msg = "";
    var rooms = $('#roomList').val();
    if ($.trim(name) == "" || $.trim(name) == "Empty") {
        error = true;
        msg = "Please fill up Hotel Name field";
    } else if ($.trim(location) == "" || $.trim(location) == "Empty") {
        error = true;
        msg = "Please fill up Location field";
    } else if ($.trim(group) == "" || $.trim(group) == "Empty") {
        error = true;
        msg = "Please fill up Category field";
    }
    if (error) {
        $.growl.warning({message: msg});
    } else {
        $.ajax({
            url: base_url + '/admin/hotels/',
            type: "POST",
            data: {
                id: id,
                name: name,
                name_lang: name_lang,
                location: location,
                group: group,
                rooms: rooms,
                current_language_id: current_language_id,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (result) {
                if (result.error) {
                    $.growl.error({message: result.error});
                } else {
                    $('#roomList').val("[]");
                    $.growl.notice({message: result.success});
                    $('#hotel-details').find('.hotel-name').attr('data-lang',result.name_lang);
                    var rooms = result.rooms;
                    var row = '';
                    for (var i = 0; i < rooms.length; i++) {
                        row +=
                            '<tr class="roomInfo" data-id="' + rooms[i].id + '">' +
                            '   <td>' + rooms[i].beds + '</td>' +
                            '   <td class="room-description" data-lang=\''+rooms[i].description_lang.replace(/'/g, "\\'")+'\'>' + getcontentByLanguage(rooms[i].description, rooms[i].description_lang, current_language_id) + '</td>' +
                            // '   <td>€' + rooms[i].cost + '</td>' +
                            '   <td>' + rooms[i].occupancy + '%</td>' +
                            '</tr>'
                    }
                    $('.hotel-room').html(row);

                }
            }
        });
    }
});

/* Delete Hotel */

$('body').on('click', '.deleteHotel', function (event) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Hotel?", function (result) {
        if (result) {
            var id = $this.attr('data-id');
            var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: base_url + '/admin/hotels/delete/',
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
                        setTimeout(function () {
                            window.location.href = base_url + '/admin/hotels/';
                        }, 1000);
                    }
                }
            });
        }
    });
});

/* Show Room details */

$('body').on('click', '.roomInfo', function (event) {
    var id = $(this).attr('data-id');
    $('body .loader').show();
    var $this = $(this);
    $this.prop("disabled", true);
    $.ajax({
        url: base_url + '/admin/rooms/' + id + '/',
        type: "GET",
        data: {},
        success: function (result) {
            $('body .loader').hide();
            var current_language_id = $('.hotel-language-presets-selector').select2('val');
            $this.prop("disabled", false);
            $('#hotel-details-edit-room').html(result);
            var room_description_lang = $this.find('.room-description').attr('data-lang');
            var room_description = $this.find('.room-description').html();
            default_language_id = $('#hotel_defualt_language_id').val();
            $('#hotel-details-edit-room').find('.edit-room-name').val(getcontentByLanguage(room_description, room_description_lang, current_language_id));
            var options = {
                todayBtn: "linked",
                orientation: $('body').hasClass('right-to-left') ? "auto right" : 'auto auto'
            };
            $('.hotel-details-add-room-datepicker-range').datepicker(options);
            var hotel_access = $('#admin-hotel-write-access').val();
            if ($.trim(hotel_access) == '0') {
                $('#hotel-details-edit-room').find("input, select").attr('disabled', 'disabled');
                $('#allotment-type').closest('.table-footer').remove();
                $('.btn-group').closest('.row').remove();
                $('#hotel-details-edit-room').find('.room-allotments').editable({
                    disabled: true
                });
                $('#hotel-details-edit-room').find('.delete-allotment').remove();
                $('#hotel-details-edit-room').find('.modal-title').html("View Hotel Room");

            }
            else {
                $('.room-allotments').editable({
                    url: base_url + '/admin/allotment_edit/',
                    type: 'POST',
                    title: 'Allotment',
                    success: function (result) {
                        $.growl.notice({message: result.success_update});
                        var current_tr = $(this).closest("tr");
                        current_tr.find('td:nth-child(11)').html(result.free + ' <div class="col col-md-3 pull-right"> <button class="btn btn-xs btn-danger delete-allotment" data-allotment_id="' + result.new_amount + '"><i class="fa fa fa-times-circle pull-right"></i></button></div>');
                        clog(current_tr);

                    },
                    error: function () {
                        $.growl.warning({message: result.error});
                    }

                });
            }

            $('#hotel-details-edit-room').modal();
        }
    });
});


/* Add Room allotments */

$('body').on('click', '#add_allotment', function (event) {


    if ($("#allotment-type_new").val() == "add") {

        var from_start = $.trim($("input[name='start']").val());
        var to_end = $.trim($("input[name='end']").val());
        var allotment_amount = $.trim($("input[name='room_amount']").val());

        //alert("hi");
        if (from_start != '' && to_end != '' && allotment_amount != '' && from_start <= to_end) {


            for (var d = moment(from_start); d <= moment(to_end); d.add(1, 'days')) {
                var flag = true;
                clog(moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD'));

                $.each($("#hotel-details-room-allotments tbody tr"), function (i, tr) {
                    var allotment_data = [];
                    var old_from = $('td:nth-child(1)', tr).text();
                    //                    old_to = $('td:nth-child(2)', tr).text();
                    if (old_from == moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD')) {
                        var old_amount = $('td:nth-child(2)', tr).text();
                        $('td:nth-child(2)', tr).html(parseInt(old_amount) + parseInt(allotment_amount));
                        flag = false;
                    }


                });
                if (flag) {
                    //$("#hotel-details-room-allotments tbody").append("<tr><td>" + moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD') + "</td><td>" + allotment_amount + " <button class='btn btn-xs btn-danger pull-right delete-allotment' data-allotment_id=''><i class='a fa fa-times-circle pull-right'></i></button></td></tr>");
                    var t = $("#hotel-details-room-allotments").DataTable();
                    var vat_select_box_element = $('.vat_select_box_element').val();
                    var del_allotment_btn = "<button class='btn btn-xs btn-danger pull-right delete-allotment' data-allotment_id=''><i class='a fa fa-times-circle pull-right'></i></button>";
                    var row_element = [moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD'),
                        allotment_amount,
                        '<input type="number" min="0" name="room-allotment-cost" class="form-control edit-room-allotment-cost" placeholder="" value="">',
                        vat_select_box_element + del_allotment_btn
                    ];
                    t.row.add(row_element).draw(false);

                }


            }


        }
        else
        //            alert("Please fill up all valid filelds");
            $.growl.warning({message: "Please fill up all valid filelds"});

    }
    else {
        $.growl.warning({message: "Please select Add"})
    }


});

/* Add Room allotments in Edit room */


$('body').on('click', '#add_allotment_edit_rooms', function (event) {

    if ($("#allotment-type").val() == "add") {
        var from_start = $.trim($('#hotel-details-edit-room').find("input[name='start']").val());
        var to_end = $.trim($('#hotel-details-edit-room').find("input[name='end']").val());
        var allotment_amount = $.trim($('#hotel-details-edit-room').find("input[name='room_amount']").val());
        var new_amount;
        var new_free;

        if (from_start != '' && to_end != '' && allotment_amount != '' && from_start <= to_end) {
            for (var d = moment(from_start); d <= moment(to_end); d.add(1, 'days')) {
                var flag = true;
                $.each($("#hotel-details-room-allotments_edit tbody tr"), function (i, tr) {
                    var cur_tr = $(this);
                    var old_from = $('td:nth-child(1)', tr).text();

                    if (old_from == moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD')) {
                        var booking = $('td:nth-child(6)', tr).text();
                        var old_amount = $('td:nth-child(2) a.room-allotments', tr).text();
                        allotment_amount = $.trim($('#hotel-details-edit-room').find("input[name='room_amount']").val());
                        new_amount = parseInt(old_amount) + parseInt(allotment_amount);
                        new_free = parseInt(old_amount) + parseInt(allotment_amount) - parseInt(booking);
                        $('td:nth-child(2) a.room-allotments', tr).text(new_amount);
//                            $('td:nth-child(2)', tr).html('<input type="number" min="' + booking + '" class="form-control allotments-total" value="' + new_amount + '">')
//                            $('td:nth-child(2)', tr).html('<a href="#" class="room-allotments editable editable-click" data-type="number" data-min="' + booking + '" data-name="update" data-title="Allotment">' + new_amount + '</a>')
//                            $('td:nth-child(2)', tr).html('<a href="#" class="room-allotments editable editable-click" data-type="number" data-min="' + booking + '" data-name="update" data-title="Allotment">' + new_amount + '</a>')
                        $('td:nth-child(11)', tr).html(new_free + ' <div class="col col-md-3 pull-right"> <button class="btn btn-xs btn-danger delete-allotment" data-allotment_id="' + new_amount + '"><i class="fa fa fa-times-circle pull-right"></i></button></div>');
                        if (!cur_tr.hasClass("new_data"))
                            cur_tr.addClass("update_tr");

                        flag = false;

                    }

                });
                if (flag) {
                    //clog(moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD'));
                    //                    d=moment(d);
                    //$("#hotel-details-room-allotments_edit tbody").append("<tr class='new_data'><td>" + moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD') + "</td><td> <a href='#' class='room-allotments'>" + allotment_amount + "</a></td><td>" + 0 + "</td><td> " + allotment_amount + "<div class='col col-md-3 pull-right'> <button class='btn btn-xs btn-danger delete-allotment' data-allotment_id=''><i class='a fa fa-times-circle'></i></button></div></td></tr>");
                    var to = $("#hotel-details-room-allotments_edit").DataTable();
                    var vat_select_box_element = $('.vat_select_box_element').val();
                    var node_elm = [
                        moment(d, 'MM/DD/YYYY').format('YYYY-MM-DD'),
                        "<a href='#' class='room-allotments'>" + allotment_amount + "</a>",
                        '<input type="number" min="0" name="room-allotment-cost" class="form-control edit-room-allotment-cost" placeholder="" value="">',
                        vat_select_box_element,
                        0,
                        0,
                        0,
                        0,
                        0,
                        "0%",
                        allotment_amount+"<div class='col col-md-3 pull-right'><button class='btn btn-xs btn-danger delete-allotment' data-allotment_id=''><i class='a fa fa-times-circle pull-right'></i></button></div>"

                    ];
                    var node = to.row.add(node_elm).draw().node();
                    $(node).addClass("new_data");
                }
            }
        }
        else
            $.growl.warning({message: "Please fill up all valid filelds"});
    }
    else {
        var allotment_datas = [];
        var allotment_amount = $.trim($('#hotel-details-edit-room').find("input[name='room_amount']").val());
        $.each($("#hotel-details-edit-room tbody tr"), function (i, tr) {
            //alert("come");
            var allotment_data = [];
            cur_date = $('td:nth-child(1)', tr).text();
//                allotment_amount=$('td:nth-child(2)', tr).text();
//                allotment_data[2]=$('td:nth-child(3)', tr).text();
            if (cur_date >= moment($.trim($('#hotel-details-edit-room').find("input[name='start']").val()), 'MM/DD/YYYY').format('YYYY-MM-DD') && cur_date <= moment($.trim($('#hotel-details-edit-room').find("input[name='end']").val()), 'MM/DD/YYYY').format('YYYY-MM-DD')) {
                var id = $(this).attr('tr-allotment_id');

                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                clog(id + " " + csrf_token);
                var current_tr = $(this).closest('tr');
                //current_tr.find('td:nth-child(2)').text("asd");

                $.ajax({
                    url: base_url + '/admin/allotment_update/',
                    type: "POST",
                    data: {
                        id: id,
                        allotment_amount: allotment_amount,
                        action: "remove",
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.success) {
                            $.growl.notice({message: result.success});
                            current_tr.remove();
                        }
                        else if (result.success_update) {
                            // current_tr.find('td:nth-child(2) a.room-allotment').text(result.new_allotment);
                            current_tr.find('td:nth-child(2) a.room-allotments').editable('setValue',result.new_allotment);
                            current_tr.find('td:nth-child(11)').html(result.free + ' <div class="col col-md-3 pull-right"> <button class="btn btn-xs btn-danger delete-allotment" data-allotment_id="' + new_amount + '"><i class="fa fa fa-times-circle pull-right"></i></button></div>');
                            //
                            $.growl.notice({message: result.success_update});
                        } else {
                            //                            <a href="#" class="room-allotments" data-type="number" data-min="'+booking+'" data-name="update" data-params="{csrfmiddlewaretoken:'{{csrf_token}}'}" data-pk="{{allotment.id}}" data-title="Allotment">'+new_amount+'</a>

//                                current_tr.find('td:nth-child(2)').text(result.new_allotment);
                            
                            // current_tr.find('td:nth-child(2)').text('<a href="#" class="room-allotments" data-type="number" data-min="' + result.booking + '" data-name="update" data-params="{csrfmiddlewaretoken:"' + csrf_token + '"}" data-pk="' + id + '" data-title="Allotment">' + result.new_amount + '</a>');
                            current_tr.find('td:nth-child(2) a.room-allotments').editable('setValue',result.new_allotment);
                            current_tr.find('td:nth-child(11)').html(result.free + ' <div class="col col-md-3 pull-right"> <button class="btn btn-xs btn-danger delete-allotment" data-allotment_id="' + id + '"><i class="fa fa fa-times-circle pull-right"></i></button></div>');
                            //
                            $.growl.error({message: result.error});
                        }
                    }
                });
            }


        });

        if (flag) {
            $("#hotel-details-room-allotments_edit tbody").append("<tr class='new_data'><td>" + moment(from_start, 'MM/DD/YYYY').format('YYYY-MM-DD') + "</td><td>" + moment(to_end, 'MM/DD/YYYY').format('YYYY-MM-DD') + "</td><td>" + allotment_amount + " <button class='btn btn-xs btn-danger pull-right delete-allotment' data-allotment_id=''><i class='a fa fa-times-circle pull-right'></i></button></td></tr>");
        }


        allotment_datas = JSON.stringify(allotment_datas);

    }


});

/* Delete Room allotments */

$('body').on('click', '.delete-allotment', function (event) {
    var $this = $(this);
    bootbox.confirm("Are you sure you want to delete this Allotment?", function (result) {
        if (result) {
            if ($(this).attr("data-allotment_id") != "") {
                //alert($(this).attr("data-allotment_id"));
                var id = $this.attr('data-allotment_id');
                var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                var current_tr = $this.closest('tr');
                $.ajax({
                    url: base_url + '/admin/allotment_delete/',
                    type: "POST",
                    data: {
                        id: id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    success: function (result) {
                        if (result.success) {
                            $.growl.notice({message: result.success});
                            current_tr.remove();
                        }
                        else {
                            $.growl.error({message: result.error});
                        }
                    }
                });
            }
            else {
                $(this).closest('tr').remove();
            }
        }
    });
});

/* Hotel and Room End */
