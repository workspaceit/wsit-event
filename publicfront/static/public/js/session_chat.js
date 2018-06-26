swampdragon.ready(function () {

    var chat_room_id = $('#chat-room').val();
    var attendee_id = $('#attendee-id').val();
    console.log(attendee_id);
    var chatContainer = $('#chat-container');

    swampdragon.subscribe('message-item', 'messages', {chat_room_id: chat_room_id}, function (context, data) {
        console.log(context);
    }, function (context, data) {
        // subscription failed
    });

    swampdragon.getList('message-item', { chat_room_id: chat_room_id }, function (context, data) {
        console.log(data);
        var messages = '';
        for (var i = 0; i < data.length; i++) {
            var image = base_url + '/static/public/images/user_no_image.png';
            if (data[i].sender.avatar != '') {
                image = base_url + data[i].sender.avatar;
            }
            messages += '<div class="chat">' +
                '<img src="' + image + '">' +
                '<div class="chatContent">' +
                '<h4>' +
                '<a href="#">' + data[i].sender.firstname + ' ' + data[i].sender.lastname + '</a>' +
                ' <span class="date">' + moment(data[i].created_at, 'YYYY-MM-DD h:mm:ss').format('ddd, MMM D, H:mm') + '</span>' +
//                '<span class="report" data-message-id="' + data[i].id + '"><i class="fa fa-flag"></i></span>' +
                '</h4>' +
                '<p>' + data[i].text + '</p>' +
                '</div>' +
                '</div>';
        }
        chatContainer.html(messages);
    }, function (context, data) {
        console.log("failed");
    });

    swampdragon.onChannelMessage(function (channels, message) {
        console.log(message);
        var image = base_url + '/static/public/images/user_no_image.png';
        if (message.data.sender.avatar != '') {
            image = base_url + message.data.sender.avatar;
        }
        chatContainer.append('<div class="chat">' +
            '<img src="' + image + '">' +
            '<div class="chatContent">' +
            '<h4>' +
            '<a href="#">' + message.data.sender.firstname + ' ' + message.data.sender.lastname + '</a>' +
            ' <span class="date">' + moment(message.data.created_at, 'YYYY-MM-DD h:mm:ss').format('ddd, MMM D, H:mm') + '</span>' +
//            '<span class="report" data-message-id="' + message.id + '"><i class="fa fa-flag"></i></span>' +
            '</h4>' +
            '<p>' + message.data.text + '</p>' +
            '</div>' +
            '</div>');
    });

    $('#btn-send-message').click(function (e) {
        e.preventDefault();
        var text = $('#txt-message').val();
        var data = { chat_room_id: chat_room_id, text: text, sender_id: attendee_id};
        swampdragon.create('message-item', data, function (context, data) {
//            console.log(data);
        }, function (context, data) {
            console.log(data);
        });
    });

});
