document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('dark-mode-toggle');
    toggleButton.addEventListener('click', function () {
        const body = document.body;
        body.classList.toggle('dark-mode');
        const darkModeEnabled = body.classList.contains('dark-mode');
        document.cookie = `dark_mode=${darkModeEnabled}; path=/;`;
    });
});