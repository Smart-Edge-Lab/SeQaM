main = {

    ws: null,

    init: function() {
        const input = document.getElementById("messageText");
        const url = input.getAttribute("url");
        main.ws = new WebSocket(url);
        main.ws.onmessage = function(event) {
            main.showMessage(JSON.parse(event.data));
        };
    },

    showMessage: function(message) {
        var htmlMessages = document.getElementById('messages');
        var htmlMessage = document.createElement('li');
        const isMe = message.sender == 'me';
        var formattedMessage = isMe ? ("<<< " + message.text) : (message.sender + " >>> " + message.text);
        var content = document.createTextNode(new Date().toLocaleString() + " " + formattedMessage);
        if (isMe) {
            htmlMessage.classList.add('my-message');
        } else {
            htmlMessage.classList.add(message.error == 0 ? 'success' : 'error');
        }
        htmlMessage.appendChild(content);
        htmlMessages.appendChild(htmlMessage);

        // Scroll to bottom:
        const mainContent = document.getElementById("main");
        mainContent.scrollTop = mainContent.scrollHeight;
    },

    sendMessage: function(event) {
        var input = document.getElementById("messageText");
        var text = input.value;
        main.showMessage({"text": text, "error": 0, "sender": "me"});
        main.ws.send(text);
        input.value = '';
        event.preventDefault();
    }

};
