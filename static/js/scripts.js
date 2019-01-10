/* global $, io, location, moment */

// This file implemts client-side websocket functionality

// Given a username and a message to display this function formats
// the contents and adds it to the DOM
function displayMessage (user, message) {
  // Create a div to contain the message, username and timestamp
  const div = document.createElement('div')
  div.className = 'message'
  document.querySelector('.message_body').append(div)

  // span to contain the username
  const usernameSpan = document.createElement('span')
  usernameSpan.innerHTML = user + ': '

  // span to contain the message
  const messageSpan = document.createElement('span')
  messageSpan.innerHTML = message

  // span to contain the timestamp
  const datetimeSpan = document.createElement('span')
  datetimeSpan.innerHTML = '(' + moment().calendar() + ') '

  // add the timestamp, username and message to the div
  div.append(datetimeSpan)
  div.append(usernameSpan)
  div.append(messageSpan)
}

$(document).ready(function () {
  var room = document.location.href.split('/').pop()

  // Connect to websocket
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, { transports: ['websocket'] })

  // Let the server know which room the user is in
  socket.emit('join', { 'username': $('#username').text(), 'room': room })

  $('.message_body').animate({ scrollTop: $('.message_body')[0].scrollHeight - $('.message_body')[0].clientHeight }, 1000)

  /* Once the client has connected to the websocket, add functionality for the buttons
  to change channels and post message */
  socket.on('connect', function () {
    console.log('client connected')

    // Add event listeners to the channel buttons to allow the user to change channels
    document.querySelectorAll('.channel').forEach(channel => {
      channel.onclick = () => {
        socket.emit('leave', { 'username': $('#username').text(), 'room': room })
        room = channel.textContent
        window.location.href = room
      }
    })

    // When the user posts a message emit the message to the server
    document.querySelector('#send-message').onclick = () => {
      const message = document.querySelector('#message').value
      socket.emit('submit post', { 'username': $('#username').text(), 'message': message, 'room': room })
    }
  })

  // When a user posts a message, add it to the body
  socket.on('announce post', data => {
    console.log('message announced')

    const user = data['username']
    const message = data['message']
    displayMessage(user, message)
  })

  // When a user joins a room announce it to the users in the room
  socket.on('join room', data => {
    const user = data['username']
    console.log(user + ' has joined the room')
    const message = 'joined the room'
    displayMessage(user, message)
  })

  // When a user joins a room announce it to the users in the room
  socket.on('leave room', data => {
    const user = data['username']
    console.log(user + ' has left the room')
    const message = 'left the room'
    displayMessage(user, message)
  })
})
