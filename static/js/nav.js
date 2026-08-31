(function () {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector("#site-nav");
    const megaItem = document.querySelector(".has-mega");
    const megaTrigger = document.querySelector(".mega-trigger");
    let hideTimer = null;

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
        return window.matchMedia("(min-width: 960px)").matches;
    }

    function cancelHide() {
        window.clearTimeout(hideTimer);
        hideTimer = null;
    }

    function scheduleHide() {
        cancelHide();
        hideTimer = window.setTimeout(closeMega, 200);
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
        megaItem.addEventListener("mouseenter", function () {
            if (!usesHoverMega()) {
                return;
            }
            cancelHide();
            setMegaOpen(true);
        });

        megaItem.addEventListener("mouseleave", function () {
            if (!usesHoverMega()) {
                return;
            }
            scheduleHide();
        });

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

    const header = document.querySelector(".site-header");
    if (header) {
        const onScroll = function () {
            header.classList.toggle("is-scrolled", window.scrollY > 8);
        };
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
    }
})();
