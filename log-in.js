// toggle button for account creation or login
const changeButton = document.getElementById("create-account-button");
changeButton.addEventListener("click", toggleForm);

// changes between account creation and login forms using the button id
function toggleForm() {
    const creatingAccount = (changeButton.id === "create-account-button");

    const loginForm = document.getElementById("login-form");
    const emailLabel = document.getElementById("email-label");
    const emailInput = document.getElementById("email-input");
    const legend = document.getElementById("legend");

    if (creatingAccount) {
        loginForm.setAttribute("action", "/submit_new_account");
        emailLabel.classList.remove("hidden");
        emailInput.classList.remove("hidden");
        legend.textContent = "Account Creation";
        changeButton.textContent = "Back to login";
        changeButton.id = "login-button";
    } else {
        loginForm.setAttribute("action", "/submit_login");
        emailLabel.classList.add("hidden");
        emailInput.classList.add("hidden");
        legend.textContent = "Login";
        changeButton.textContent = "Create Account";
        changeButton.id = "create-account-button";
    }
}