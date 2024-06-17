document.addEventListener("DOMContentLoaded", function() {
    const endpoint = window.location.pathname;

    const btn5605 = document.getElementById("nav-button-5605");
    const btn5607 = document.getElementById("nav-button-5607");

    if (btn5605 && btn5607) {
        const urlStackStatus5605 = btn5605.getAttribute('data-url-stack-status');
        const urlStackControl5605 = btn5605.getAttribute('data-url-stack-control');
        const urlStackStatus5607 = btn5607.getAttribute('data-url-stack-status');
        const urlStackControl5607 = btn5607.getAttribute('data-url-stack-control');

        if (endpoint.includes("stack_status")) {
            btn5605.onclick = function() {
                window.location.href = urlStackStatus5605;
            };
            btn5607.onclick = function() {
                window.location.href = urlStackStatus5607;
            };
        } else if (endpoint.includes("stack_control")) {
            btn5605.onclick = function() {
                window.location.href = urlStackControl5605;
            };
            btn5607.onclick = function() {
                window.location.href = urlStackControl5607;
            };
        }
    }
});
