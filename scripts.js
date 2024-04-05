// Set verbosity
const verbose = true;

// Password requirements (global so only gotten once)
let passRequirements = null;

// Wait for page load and add listener event for form submission:
document.addEventListener('DOMContentLoaded', () => {
  if (verbose) { console.log("Page loaded!"); }

  // Get password requirements from server (TO DO LATER)
  passRequirements = get_passRequirements();

});

// Obtain current password requirements from server
function get_passRequirements() {
  return {
    'maxLength': 10,
    'minLength': 5,
    'regex': '^[a-zA-Z0-9?_!-]*$'
  };
}

// Ensure password submitted has the correct requirements
function check_passRequirements(pass) {
  // Ensure password requirements are obtained correctly.
  if (passRequirements === null || Object.keys(passRequirements).length > 1) {
    console.log("Password requirements incorrectly set!");
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
