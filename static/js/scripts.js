/* global $, io, location, moment */

// This file implemts client-side websocket functionality
$(document).ready(function () {
  var room = document.location.href.split('/').pop()

  // Connect to websocket
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, { transports: ['websocket'] })

  // Let the server know which room the user is in
  socket.emit('join', { 'username': $('#username').html(), 'room': room })

  /* Once the client has connected to the websocket, add functionality for the buttons
  to change channels and post message */
  socket.on('connect', function () {
    console.log('client connected')

    // Add event listeners to the channel buttons to allow the user to change channels
    document.querySelectorAll('.channel').forEach(channel => {
      channel.onclick = () => {
        socket.emit('leave', { 'username': $('#username').html(), 'room': room })
        room = channel.textContent
        window.location.href = room
      }
    })

    // When the user posts a message emit the message to the server
    document.querySelector('#send-message').onclick = () => {
      const message = document.querySelector('#message').value
      socket.emit('submit post', { 'message': message, 'room': room })
    }
  })

  // When a user posts a message, add it to the body
  socket.on('announce post', data => {
    // Create a div to contain the message, username and timestamp
    const div = document.createElement('div')
    div.className = 'message'
    document.querySelector('.message_body').append(div)

    // span to contain the username
    const usernameSpan = document.createElement('span')
    usernameSpan.innerHTML = $('#username').html() + ': '

    // span to contain the message
    const messageSpan = document.createElement('span')
    messageSpan.innerHTML = `${data['message']}`

    // span to contain the timestamp
    const datetimeSpan = document.createElement('span')
    datetimeSpan.innerHTML = '(' + moment().calendar() + ') '

    // add the timestamp, username and message to the div
    div.append(datetimeSpan)
    div.append(usernameSpan)
    div.append(messageSpan)
  })
})
