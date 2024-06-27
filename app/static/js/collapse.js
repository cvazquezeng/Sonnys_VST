document.addEventListener("DOMContentLoaded", function() {
    // Highlight current page
    const currentUrl = window.location.pathname;
    document.querySelectorAll(".list-group-item-action").forEach(function(link) {
        if (link.getAttribute("href") === currentUrl) {
            link.classList.add("active");
            const collapseElement = link.closest(".collapse");
            if (collapseElement) {
                collapseElement.classList.add("show");
                const caretIcon = link.querySelector('.fas.fa-caret-down');
                if (caretIcon) {
                    caretIcon.classList.add('fa-caret-up');
                }
            }
        }
    });

    // Retain collapsible state
    const submenu = document.getElementById("submenu1");
    if (localStorage.getItem("submenuExpanded") === "true" && submenu) {
        submenu.classList.add("show");
        const submenuToggle = document.querySelector('a[href="#submenu1"] .fas.fa-caret-down');
        if (submenuToggle) {
            submenuToggle.classList.add('fa-caret-up');
        }
    }

    // Listen for submenu toggle clicks
    const submenuToggleLink = document.querySelector('a[href="#submenu1"]');
    if (submenuToggleLink) {
        submenuToggleLink.addEventListener("click", function() {
            if (submenu) {
                const isExpanded = submenu.classList.contains("show");
                localStorage.setItem("submenuExpanded", !isExpanded);
                const caretIcon = this.querySelector('.fas.fa-caret-down');
                if (caretIcon) {
                    caretIcon.classList.toggle('fa-caret-up', !isExpanded);
                }
            }
        });
    }

    // Toggle sidebar collapse
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const sidebarContainer = document.getElementById('sidebar-container');
            if (sidebarContainer) {
                sidebarContainer.classList.toggle('d-none');
            }
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.classList.toggle('full-width');
            }
            const navbar = document.querySelector('.navbar');
            if (navbar) {
                navbar.classList.toggle('full-width');
            }
        });
    }

    // Collapse the navbar when clicking outside
    document.addEventListener('click', function(event) {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const sidebarContainer = document.querySelector('#sidebar-container');
        const navbarToggler = document.querySelector('.navbar-toggler');

        if (navbarCollapse && sidebarContainer && navbarToggler) {
            const isClickInsideNavbar = navbarCollapse.contains(event.target);
            const isClickInsideSidebar = sidebarContainer.contains(event.target);
            const isNavbarToggler = navbarToggler.contains(event.target);

            if (!isClickInsideNavbar && !isClickInsideSidebar && !isNavbarToggler) {
                $(navbarCollapse).collapse('hide');
            }
        }
    });
});
