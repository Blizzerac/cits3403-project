const createAccountButton = document.getElementById("create-account-button");
createAccountButton.addEventListener("click", handleAccount);

//will add an email field to the form, change action value of the form, change legend
function handleAccount() {

    let loginForm = document.getElementById("login-form");
    loginForm.setAttribute("action", "/submit_new_account");

    let emailLabel = document.getElementById("email-label");
    let emailInput = document.getElementById("email-input");

    emailLabel.classList.remove("hidden");
    emailInput.classList.remove("hidden");

    let legend = document.getElementById("legend");
    legend.textContent = "Account Creation";
}