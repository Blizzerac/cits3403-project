// Set verbosity
const verbose = true;

$(document).ready(function() {
  // Change signup to login form
  $('#toggle-login').click(swapLoginForm)

  // Show the toast if any exist
  $('.toast').toast('show');
});

// Swap between account login and account creation
function swapLoginForm() {
  $('#login-form-container').toggleClass('hidden');
  $('#signup-form-container').toggleClass('hidden');
}