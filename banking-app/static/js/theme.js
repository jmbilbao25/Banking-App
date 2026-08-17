// Theme Toggle Logic

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    // Default to light mode if there's no saved preference, or if it's explicitly 'light'
    if (savedTheme !== 'dark') {
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    let newTheme = 'light';
    
    if (currentTheme === 'light') {
        newTheme = 'dark';
        document.documentElement.removeAttribute('data-theme');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
    }
    
    localStorage.setItem('theme', newTheme);
}

// Initialize theme immediately to prevent flashing
initTheme();

document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners to all theme toggles on the page
    const toggleBtns = document.querySelectorAll('.theme-toggle');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', toggleTheme);
    });
});
