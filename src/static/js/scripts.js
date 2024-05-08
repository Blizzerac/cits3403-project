// Set verbosity
const verbose = true;

// Password requirements (global so only gotten once)
let passRequirements = null;

// Form change login/account creation
$(document).ready(function() {
  $("#create-account-button").click(function() {
      const creatingAccount = ($(this).text() === "Create New Account");
      const loginForm = $("#login-form");
      const legend = $("#legend");
      const creationElements = $(".account-creation");

      if (creatingAccount) {
          loginForm.attr("action", "/submit_new_account");
          creationElements.removeClass("hidden");
          legend.text("Account Creation");
          $(this).text("Back to Login").attr("id", "login-button");
      } else {
          loginForm.attr("action", "/submit_login");
          creationElements.addClass("hidden");
          legend.text("Login");
          $(this).text("Create New Account").attr("id", "create-account-button");
      }
  });
});

// Submit button disabling and enabling for posting
$(document).ready(function(){

  // Disable initially
  $('#submit-post').prop('disabled', true);

  // If refreshing page and keeping inputs, checks inputs
  checkFields();

  // Call checkFields() when  input fields change
  $('#first-post-input, #second-post-input').on('input', checkFields);
});

// Function to check if inputs for posting are filled
function checkFields() {
  let field1 = $('#first-post-input').val();
  let field2 = $('#second-post-input').val();

  // Minimum length of 5 for each
  if ((field1.length >=5) && (field2.length >=5)) {
      $('#submit-post').prop('disabled', false);
      $('#submit-post').removeClass('disabled');
      $('#disabled-info').addClass('hidden');
  } else {
      $('#submit-post').prop('disabled', true);
      $('#submit-post').addClass('disabled');
      $('#disabled-info').removeClass('hidden');
  }
}


// Wait for page load and add listener event for form submission:
document.addEventListener('DOMContentLoaded', () => {
  if (verbose) { console.log("Page loaded!"); }

  // Get password requirements from server (TO DO LATER)
  try {
    passRequirements = get_passRequirements();
  } catch (error) {
    // Handle failure of the request
    console.log('ERROR:', error.message);
  }

  // Add event listener for login submission
  document.getElementById('loginForm').addEventListener('submit',handle_login)
});

// Handle login submission
function handle_login(event) {
  event.preventDefault(); // Prevent default form submission

  const form      = document.getElementById('loginForm');
  const formData  = new FormData(form);

  const username  = formData.get('username');
  const pass      = formData.get('password');

  // If the password matches requirements, submit the account for validation from server.
  if (check_passRequirements(pass)) {
    // Server stuff
    console.log("Validate user login request...")
  }

  else {
    alert("Password Failed Requirements!");
  }
}


// Obtain current password requirements from server
function get_passRequirements() {
  // Throw new error on failure (example)
  if (false) {
    throw new Error("Failed to get password requirements from sever.");
  }

  const req = {
    'maxLength': 10,
    'minLength': 5,
    'regex': '^[a-zA-Z0-9?_!-]*$'
  };

  return req;
}

// Ensure password submitted has the correct requirements
function check_passRequirements(pass) {
  // Ensure password requirements are obtained correctly.
  if (passRequirements === null || Object.keys(passRequirements).length <= 1) {
    console.log("Password requirements incorrectly set!");
    if (verbose) { console.log("Password requirements:", passRequirements); }
    return false; 
  }

  // Ensure correct password length
  if (pass.length > passRequirements['minLength'] && pass.length < passRequirements['maxLength']) {
    // Check against current password regex requirements
    const regex = new RegExp(passRequirements['regex']);
    if (regex.test(pass)) {
      return true;
    }
  }

  return false;
}
