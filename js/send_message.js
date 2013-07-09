"use strict";

function send_message_to_id() {
    console.log("send_message_to_id");
    var channel_id = $('#channel_id')[0].value;
    var message = $('#message')[0].value;
    var data = 'channel_id=' + channel_id + '&message=' + message;
    $.ajax({
        type: 'GET',
        url: '/SendMessage',
        data: data,
        dataType: 'json',
        error: send_message_error,
        success: send_message_success
        });
}

function send_message_error(request, status) {
    console.log("send_message_error");
    $('#result')[0].innerHTML = 'Error';
}

function send_message_success(resp) {
    console.log("send_message_success: " + resp);
    if (resp['result'] == 'success') {
        $('#result')[0].innerHTML = 'Success';
    } else {
        $('#result')[0].innerHTML = 'Error: ' + resp['message'];
    }
}