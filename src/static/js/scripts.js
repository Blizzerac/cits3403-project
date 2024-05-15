// Set verbosity
const verbose = true;

// When page is loaded
$(document).ready(function() {
  // Change signup to login form
  $('.toggle-login').click(swapLoginForm)

  // Show the toast if any exist
  $('.toast').toast({
    delay: 1500  // Delay in milliseconds
  }).toast('show');

  // Initialise Bootstrap dropdowns and other events
  handle_dropdownMenu()

  // Handle quest post form
  handle_questPost()

  // Handle control pannel (buttons) on quest view
  handle_questView()

  // Check for valid password on signup form
  //$('#signup-password-input').keyup(checkPass)
});

// Swap between account login and account creation
function swapLoginForm() {
  $('#login-form-container').toggleClass('hidden');
  $('#signup-form-container').toggleClass('hidden');
}


// Handle dropdown menu
function handle_dropdownMenu() {
  // Toggle dropdown visibility when clicking button
  $('.dropdown-toggle').click(function(event) {
    event.stopPropagation(); // Prevent click event from bubbling up (and triggering event to close menu)

    // Hide any other dropdown menus (only have one open at a time)
    let $dropdownMenu = $(this).next('.dropdown-menu');
    $('.dropdown-menu').not($dropdownMenu).hide();

    $dropdownMenu.toggle();
  });

  // Close dropdown when clicking anywhere on the page
  $(document).click(function(event) {
    let $target = $(event.target);
    if (!$target.closest('.dropdown').length) {
      $('.dropdown-menu').hide();
    }
  });
}


// Handle quest post form
function handle_questPost() {
  // Disable initially
  $('#submit-post').prop('disabled', true);

  // If refreshing page and keeping inputs, checks inputs
  questPost_checkFields();

  // Call checkFields() when  input fields change
  $('#first-post-input, #second-post-input').on('input', questPost_checkFields);
}

// Function to check if inputs for posting are filled
function questPost_checkFields() {
  let field1 = $('#first-post-input').val();
  let field2 = $('#second-post-input').val();

  // Minimum length of 5 for each
  if ((field1.length >= 5) && (field2.length >= 5)) {
      $('#submit-post').prop('disabled', false);
      $('#submit-post').removeClass('disabled');
      $('#disabled-info').addClass('hidden');
  } else {
      $('#submit-post').prop('disabled', true);
      $('#submit-post').addClass('disabled');
      $('#disabled-info').removeClass('hidden');
  }
}


// Redudent for now, may be used in future
function checkPass() {
  let password = $(this).val();
  let errors = [];

  // Check for length requirements (min=5, max=25)
  if (password.length < 5 && password.length > 2) {
    errors.push("Password must be between 5-25 characters long.");
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

    // Disable register button
    $('#signup-submit-button').prop('disabled', true)

  } else {
    // Enable register button
    $('#signup-submit-button').prop('disabled', false)
  }
}

function handle_questView() {
  $('#claim-request').click(function() {
    ajaxPost("{{ url_for('claim_request', post_id=post.postID) }}", {}, 'ReQuest claimed successfully!');
  });

  $('#finalise-request').click(function() {
    ajaxPost("{{ url_for('finalise_request', post_id=post.postID) }}", {}, 'ReQuest finalised successfully!');
  });

  $('#relinquish-claim').click(function() {
    ajaxPost("{{ url_for('relinquish_claim', post_id=post.postID) }}", {}, 'Claim relinquished successfully!');
  });

  $('#approve-submission').click(function() {
    ajaxPost("{{ url_for('approve_submission', post_id=post.postID) }}", {}, 'Submission approved successfully!');
  });

  $('#deny-submission').click(function() {
    ajaxPost("{{ url_for('deny_submission', post_id=post.postID) }}", {}, 'Submission denied.');
  });

  $('#cancel-request').click(function() {
    ajaxPost("{{ url_for('cancel_request', post_id=post.postID) }}", {}, 'ReQuest cancelled successfully.');
  });

  $('#response-form').submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    ajaxPost($(this).attr('action'), data, 'Response added successfully!');
  });
}

function ajaxPost(url, data, successMessage) {
  $.ajax({
    type: "POST",
    url: url,
    data: data,
    success: function(response) {
      // Flask will flash a message to the user.
      location.reload(); // Reload the page to update the content dynamically
    },
    error: function(response) {
      console.log(response)
      location.reload();
    }
  });
}