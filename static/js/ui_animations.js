document.addEventListener('DOMContentLoaded', function() {
    // Fade in the main content on page load
    const mainContent = document.querySelector('main') || document.body;
    mainContent.style.opacity = '0';
    mainContent.style.transition = 'opacity 1s ease-in-out';

    setTimeout(() => {
        mainContent.style.opacity = '1';
    }, 100);
});