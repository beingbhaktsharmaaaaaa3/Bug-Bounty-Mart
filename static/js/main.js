// BugBountyMart v2.0 — Main JavaScript
// Contains client-side vulnerabilities for practice

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
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

    // Console hints for bug bounty hunters
    console.log('%c BugBountyMart v2.0 ', 'background: #6366f1; color: white; font-size: 20px; font-weight: bold; padding: 10px; border-radius: 5px;');
    console.log('%c Welcome, hunter! ', 'color: #6366f1; font-size: 14px;');
    console.log('Hint: Check the page source for hidden API endpoints and debug flags.');
    console.log('Hint: The admin panel is at /admin (credentials: admin / admin123)');
    console.log('Hint: Try modifying the #hash in product URLs for DOM XSS testing.');
    console.log('Hint: CTF Mode available at /ctf with 50+ challenges!');
    console.log('Hint: Check /api/debug?debug=true for hidden endpoints');
    console.log('Hint: Try prototype pollution via URL params: ?__proto__.isAdmin=true');

    // VULNERABLE: Prototype Pollution via query params
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.forEach((value, key) => {
        if (key.startsWith('__proto__') || key.startsWith('constructor')) {
            // In a real vulnerable app, this would pollute Object.prototype
            console.warn('Potential prototype pollution detected:', key, value);
        }
    });

    // VULNERABLE: PostMessage without origin validation
    window.addEventListener('message', function(event) {
        // VULNERABLE: No origin check!
        console.log('Received message:', event.data);
        if (event.data && event.data.action === 'setConfig') {
            if (event.data.config) {
                Object.assign(window.appConfig || {}, event.data.config);
                console.log('Config updated via postMessage');
            }
        }
        if (event.data && event.data.action === 'eval') {
            // EXTREMELY VULNERABLE: Remote code execution via postMessage
            try {
                eval(event.data.code);
            } catch(e) {}
        }
    });

    // VULNERABLE: DOM XSS via location.hash (for product page)
    const shareMsg = document.getElementById('share-msg');
    if (shareMsg) {
        var hash = location.hash.slice(1);
        if (hash) {
            // VULNERABLE: innerHTML with user-controlled input
            shareMsg.innerHTML = decodeURIComponent(hash);
        }
    }

    // VULNERABLE: Client-side template injection (CSTI) demo
    // If Vue.js or Angular is loaded, this could be exploited
    const cstiDemo = document.getElementById('csti-demo');
    if (cstiDemo) {
        const template = new URLSearchParams(window.location.search).get('template');
        if (template) {
            cstiDemo.innerHTML = template;
        }
    }

    // VULNERABLE: Clickjacking helper - page is frameable
    if (window.self !== window.top) {
        console.log('This page is being framed! Clickjacking is possible.');
    }
});

// Global config object for prototype pollution
window.appConfig = {
    theme: 'dark',
    admin: false,
    debug: false
};

// VULNERABLE: JSONP-like callback
function jsonpCallback(data) {
    console.log('JSONP data received:', data);
    if (data.redirect) {
        window.location = data.redirect;
    }
}
