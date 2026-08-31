(function () {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector("#site-nav");
    const megaItem = document.querySelector(".has-mega");
    const megaTrigger = document.querySelector(".mega-trigger");

    function setMegaOpen(open) {
        if (!megaItem || !megaTrigger) {
            return;
        }
        megaItem.classList.toggle("is-open", open);
        megaTrigger.setAttribute("aria-expanded", open ? "true" : "false");
    }

    function closeMega() {
        setMegaOpen(false);
    }

    function usesHoverMega() {
        return window.matchMedia("(hover: hover) and (min-width: 960px)").matches;
    }

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            const open = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
            if (!open) {
                closeMega();
            }
        });
    }

    if (megaTrigger && megaItem) {
        megaTrigger.addEventListener("click", function (event) {
            if (usesHoverMega()) {
                return;
            }
            event.preventDefault();
            setMegaOpen(!megaItem.classList.contains("is-open"));
        });

        document.addEventListener("click", function (event) {
            if (!megaItem.contains(event.target)) {
                closeMega();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeMega();
            }
        });
    }
})();
