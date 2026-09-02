(function () {
    const gallery = document.querySelector("[data-product-gallery]");
    if (!gallery) {
        return;
    }
    const main = gallery.querySelector("[data-gallery-main]");
    const thumbs = gallery.querySelectorAll(".product-thumb");
    if (!main || thumbs.length < 2) {
        return;
    }
    thumbs.forEach(function (thumb) {
        thumb.addEventListener("click", function () {
            const src = thumb.getAttribute("data-gallery-src");
            const alt = thumb.getAttribute("data-gallery-alt") || "";
            if (src) {
                main.setAttribute("src", src);
                main.setAttribute("alt", alt);
            }
            thumbs.forEach(function (item) {
                item.classList.toggle("is-active", item === thumb);
            });
        });
    });
})();
