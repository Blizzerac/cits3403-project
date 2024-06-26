// Set verbosity
const verbose = true;

// When page is loaded
$(document).ready(function() {
  // Change signup to login form
  $('.toggle-login').click(swapLoginForm);

  // Show the toast if any exist
  $('.toast').toast('show');

  // Initialise Bootstrap dropdowns and other events
  handleDropdownMenu();

  // Handle quest search form
  handleSearchInput();

  // Handle quest modification buttons
  handleQuestView();

  // Handle quest post form checking
  handleQuestPost();

  // Handle gold farming
  $('#coin-stack').click(addGold);
  $('#cash-in-button').click(cashIn);
});

// Collapse navbar when clicking outside restraints
$(document).click(function(event) {
  let clickover = $(event.target);
  let $navbar = $(".navbar-collapse");               
  let _opened = $navbar.hasClass("show");
  if (_opened === true && !clickover.hasClass("navbar-toggler") && $(window).width() < 992) {
    $navbar.collapse('hide');
  }
});

// Swap between account login and account creation
function swapLoginForm() {
  $('#login-form-container').toggleClass('hidden');
  $('#signup-form-container').toggleClass('hidden');
}


// Handle dropdown menu
function handleDropdownMenu() {
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
function handleQuestPost() {
  // Disable initially
  $('#submit-post').prop('disabled', true);

  // If refreshing page and keeping inputs, checks inputs
  questPostCheckFields();

  // Call checkFields() when  input fields change
  $('#first-post-input, #second-post-input, #third-post-input').on('input', questPostCheckFields);
}

// Function to check if inputs for posting are filled
function questPostCheckFields() {
  let field1 = $('#first-post-input').val();
  let field2 = $('#second-post-input').val();
  let field3 = $('#third-post-input').val();

  // Minimum length of 5 for each
  if (field1 && field2 && field3 && field1.length >= 5 && field2.length >= 5 && field3 >= 0) {
    $('#submit-post').prop('disabled', false);
      $('#submit-post').removeClass('disabled');
      $('#disabled-info').addClass('hidden');
  } else {
      $('#submit-post').prop('disabled', true);
      $('#submit-post').addClass('disabled');
      $('#disabled-info').removeClass('hidden');
  }
}

// Function to handle search input
function handleSearchInput() {
  // Disable initially
  $('#submit-search').prop('disabled', true);
  
  // Call checkSearchInput initially in case the input retains values from a previous session
  checkSearchInput();

  // Monitor changes to the input field
  $('#search-input').on('input', checkSearchInput);
}

// Function to check if the search input has enough characters
function checkSearchInput() {
  let searchInput = $('#search-input').val();

  // Minimum length of 1 for enabling the search
  if (searchInput && searchInput.length >= 1) {
      $('#submit-search').prop('disabled', false);
      $('#submit-search').removeClass('disabled');
  } else {
      $('#submit-search').addClass('disabled');
      $('#submit-search').prop('disabled', true);
  }
}

let coins = 0;
function addGold() {
  coins += 10;
  console.log("Added 10 gold! Coins now at: " + coins + "g");
  document.getElementById("gold").innerHTML = coins;
}

function cashIn() {
  const coinsValue = coins;
  fetch('/gold-farm', {
    method: 'POST',
    body: JSON.stringify({coins: coinsValue}),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(data => {
    console.log(data);
    coins = 0;
    document.getElementById("gold").innerHTML = coins;
    location.reload(true);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

function ajaxPost(url, data) {
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

function handleQuestView() {
  // Get the URL from the button before sending ajax
  $('#claim-request').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#finalise-request').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#relinquish-claim').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#approve-submission').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#deny-submission').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#private-request').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#unprivate-request').click(function() {
    ajaxPost($(this).data('url'), {});
  });

  $('#cancel-request').click(function() {
    ajaxPost($(this).data('url'), {});
  });
}