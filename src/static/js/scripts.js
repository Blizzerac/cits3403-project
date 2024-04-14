// Set verbosity
const verbose = true;

// Password requirements (global so only gotten once)
let passRequirements = null;

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