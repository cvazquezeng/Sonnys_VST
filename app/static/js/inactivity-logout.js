let logoutTimer;
const logoutAfter = 30 * 60 * 1000; // 35 minutes of inactivity

function resetTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(logout, logoutAfter);
}

function logout() {
    window.location.href = "/logout"; // Change to your logout route if different
}

window.onload = resetTimer;
document.onmousemove = resetTimer;
document.onkeypress = resetTimer;
document.onscroll = resetTimer;
document.onclick = resetTimer;
