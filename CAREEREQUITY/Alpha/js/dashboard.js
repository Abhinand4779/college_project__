
document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");
    const overlay = document.getElementById("sidebarOverlay");

    if (!sidebar || !menuToggle || !overlay) {
        return;
    }

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("show");
        menuToggle.setAttribute("aria-expanded", "true");
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("show");
        menuToggle.setAttribute("aria-expanded", "false");
    }

    menuToggle.addEventListener("click", function () {
        if (sidebar.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 760) {
            closeSidebar();
        }
    });

});
