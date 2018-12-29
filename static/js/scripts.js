$(document).ready(function() {

    // Get the modal for adding a new channel
    var modal = document.getElementById('channel-modal');

    // Get the button that opens the modal
    var btn = document.getElementById("add-channel");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on the add channel button, open the modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Client side websocket functionality
    // Connect to websocket
    var room;
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Change the room when a user clicks on a different channel
    document.querySelectorAll('.channel').forEach( channel => {
        channel.onclick = () => {

            socket.emit('on_leave', {'room': room})

            room = channel.textContent;

            socket.emit('on_join', {'room': room})

            // If browser supports localStorage save the current channel
            if (typeof(Storage) !== "undefined") {
                localStorage.setItem("current_channel", room);
            }
            window.location.href = room
        }
    })

    // emit the post when submit button is clicked 
    socket.on('connect', function() {
        document.querySelector('#send-message').onclick = () => {
            const message = document.querySelector('#message').value;
            room = window.location.pathname.split("/").pop();
            socket.emit('submit post', {'message': message, 'room': room});
  }
})
    // When a user posts a message, add it to the body
    socket.on('announce post', data => {
        
        // a div to contain the message and username
        const div = document.createElement('div');
        document.querySelector('.message_body').append(div);

        // span to contain the username
        const username_span = document.createElement('span')
        username_span.innerHTML = $('#username').html() + ': ';

        // span to contain the message
        const message_span = document.createElement('span')
        message_span.innerHTML = `${data['message']}`;

        // span to contain the timestamp
        const datetime_span = document.createElement('span');
        datetime_span.innerHTML = '(' + moment().calendar() + ') ';

        // add the timestamp, username and message to the div
        div.append(datetime_span)
        div.append(username_span)
        div.append(message_span)
  })
})
