document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    // Mobile sidebar
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }

    // Close sidebar after selecting a menu item on mobile
    document.querySelectorAll(".menu-link").forEach(function (link) {
        link.addEventListener("click", function () {

            document.querySelectorAll(".menu-link").forEach(function (item) {
                item.classList.remove("active");
            });

            this.classList.add("active");

            if (window.innerWidth <= 760 && sidebar) {
                sidebar.classList.remove("open");
            }
        });
    });


document.addEventListener("DOMContentLoaded", function () {
    console.log("CareerEquity dashboard JavaScript loaded.");

    // Dashboard JavaScript can be added here.
});


});
