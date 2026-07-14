// BugBountyMart — Main JavaScript
// Contains hints for DOM XSS and other client-side vulnerabilities

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle (if needed)
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            document.querySelector('.nav-links').classList.toggle('active');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 300);
        }, 5000);
    });

    // Search input focus
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.focus();
    }

    // Console hint for bug bounty hunters
    console.log('%c BugBountyMart ', 'background: #6366f1; color: white; font-size: 20px; font-weight: bold; padding: 10px; border-radius: 5px;');
    console.log('%c Welcome, hunter! ', 'color: #6366f1; font-size: 14px;');
    console.log('Hint: Check the page source for hidden API endpoints and debug flags.');
    console.log('Hint: The admin panel is at /admin (credentials: admin / admin123)');
    console.log('Hint: Try modifying the #hash in product URLs for DOM XSS testing.');
});
