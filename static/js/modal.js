/* global $ */

// This file adds the client-side modal functionality for adding new channels
$(document).ready(function () {
  var modal = document.getElementById('channel-modal')
  var btn = document.getElementById('add-channel')

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName('close')[0]

  // When the user clicks on the add channel button, open the modal
  btn.onclick = function () {
    modal.style.display = 'block'
  }

  $('#channel-name').focus()

  // When the user clicks on <span> (x), close the modal
  span.onclick = function () {
    modal.style.display = 'none'
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = 'none'
    }
  }
})
