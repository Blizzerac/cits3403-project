// Set verbosity
const verbose = true;

$(document).ready(function() {
  // Change signup to login form
  $('.toggle-login').click(swapLoginForm)

  // Show the toast if any exist
  $('.toast').toast({
    delay: 1500  // Delay in milliseconds
  }).toast('show');

  // Check for valid password on signup form
  $('#signup-password-input').keyup(checkPass)
});

// Swap between account login and account creation
function swapLoginForm() {
  $('#login-form-container').toggleClass('hidden');
  $('#signup-form-container').toggleClass('hidden');
}

function checkPass() {
  let password = $(this).val();
  let errors = [];

  // Check for minimum length
  if (password.length < 5) {
    errors.push("Password must be at least 5 characters long.");
  }

  // Check for allowed characters: letters, numbers, and specific special characters
  if (!/^[a-zA-Z0-9!?+_\-]+$/.test(password)) {
    errors.push("Password can only include letters, numbers, and the following special characters: !, ?, -, +, _.");
  }

  // Check for numbers
  if (!/[0-9]/.test(password)) {
    errors.push("Password must include at least one number.");
  }

  // Check for uppercase letters
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must include at least one uppercase letter.");
  }

  // Display errors
  let errorContainer = $('#password-errors');
  errorContainer.html(''); // Clear previous errors
  if (errors.length > 0) {
    var errorList = $('<ul>'); // Create an unordered list
    $.each(errors, function(i, error) {
      errorList.append($('<li>').text(error)); // Append each error as a list item
    });
    errorContainer.append(errorList);
    errorContainer.removeClass('alert-success').addClass('alert-danger');
  } else {
    errorContainer.html('<div>Password is valid.</div>'); // Display success message
    errorContainer.removeClass('alert-danger').addClass('alert-success');
  }
}