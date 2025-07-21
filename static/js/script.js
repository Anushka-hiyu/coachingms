/*script.js */


// Check for saved mode on load
window.addEventListener('DOMContentLoaded', () => {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    // Optional: Automatically hide sidebar on mobile after navigation
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', () => {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            sidebar.classList.remove('show');
            overlay.classList.remove('active');
        });
    });
});

// Toggle theme (dark mode)
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    alert("Theme toggled!");

    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Confirm delete
function confirmDelete(name) {
    return confirm("Are you sure you want to delete ${name}?");
}

// Carousel logic
document.addEventListener("DOMContentLoaded", () => {
    let index = 0;
    const slides = document.querySelectorAll('.quote-slide');

    function showQuote() {
        slides.forEach((slide) => slide.classList.remove('active'));
        slides[index].classList.add('active');
        index = (index + 1) % slides.length;
    }

    if (slides.length > 0) {
        setInterval(showQuote, 6000);
    }
});

// Toggle sidebar visibility
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    sidebar.classList.toggle('show');
    overlay.classList.toggle('active');
}

// Hide sidebar when clicking outside of it
document.addEventListener('click', function (event) {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    // If sidebar is open and click is outside sidebar, close it
    if (
        sidebar.classList.contains('show') &&
        !sidebar.contains(event.target) &&
        !event.target.closest('.hamburger')
    ) {
        sidebar.classList.remove('show');
        overlay.classList.remove('active');
    }
});

// Confirm logout
function confirmLogged() {
    return confirm("Are you sure you want to logout?");
}

