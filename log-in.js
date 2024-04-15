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