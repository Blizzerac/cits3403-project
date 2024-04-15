// toggle button for account creation or login
const changeButton = document.getElementById("create-account-button");
changeButton.addEventListener("click", toggleForm);

// changes between account creation and login forms using the button id
function toggleForm() {
    const creatingAccount = (changeButton.id === "create-account-button");
    const loginForm = document.getElementById("login-form");
    const legend = document.getElementById("legend");
    const hiddenElements = document.getElementsByClassName("account-creation");

    if (creatingAccount) {
        loginForm.setAttribute("action", "/submit_new_account");

        for (let i = 0; i < hiddenElements.length; i++) {
            hiddenElements[i].classList.remove("hidden");
        }

        legend.textContent = "Account Creation";
        changeButton.textContent = "Back to Login";
        changeButton.id = "login-button";
    } else {
        loginForm.setAttribute("action", "/submit_login");

        for (let i = 0; i < hiddenElements.length; i++) {
            hiddenElements[i].classList.add("hidden");
        }

        legend.textContent = "Login";
        changeButton.textContent = "Create Account";
        changeButton.id = "create-account-button";
    }
}