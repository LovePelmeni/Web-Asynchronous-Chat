
console.log('started...');

var loc = window.location
var formData = $('#form');

var msgInput = $('#id_text');

var ChatHolder = $('#chat-items');
var withStart = 'ws://'

if (loc.protocol == 'https:'){
    withStart = 'wss://'
}

var endPoint = withStart + loc.host + loc.pathname

var username = document.getElementById('TestUsername').value
console.log(username, '- username');

var socket = new WebSocket(endPoint);

socket.onopen = function(event){

    console.log('on open...');

    form.addEventListener('submit', function(event){

        console.log('haha...');
        event.preventDefault();

        var finalData = {
            'username': username,
            'message': document.getElementById('id_text').value,
        }
        console.log(finalData, '-data');

        socket.send(JSON.stringify({'data': finalData}));
        console.log('data has been sended...');

formData[0].reset();
});
}

socket.onmessage = function(e){
    console.log('socket started work...')
    var msgData = JSON.parse(e.data);
    ChatHolder.append('<li>' + msgData['data'].author + ':' + msgData['data'].message + '</li>')
}

socket.onerror = function(e){
    console.log('error', e);
}

socket.onclose = function (e) {
    console.log('websocket is closed...');

};

