document.addEventListener('DOMContentLoaded', function() {
    let startY;
    const pullToRefreshThreshold = 150; // Amount of pixels the user needs to pull down

    document.addEventListener('touchstart', function(event) {
        if (window.scrollY === 0) {
            startY = event.touches[0].clientY;
        } else {
            startY = null;
        }
    }, { passive: true });

    document.addEventListener('touchmove', function(event) {
        if (startY !== null) {
            const currentY = event.touches[0].clientY;
            if (currentY - startY > pullToRefreshThreshold) {
                // User has pulled down more than the threshold, refresh the page
                window.location.reload();
                startY = null; // Reset startY to prevent multiple refreshes
            }
        }
    }, { passive: true });
});
