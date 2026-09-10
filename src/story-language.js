(() => {
    const archive = document.querySelector("[data-story-language]");
    if (!archive) {
        return;
    }

    const controls = archive.querySelector("[data-story-controls]");
    const buttons = Array.from(archive.querySelectorAll(".lang-option"));
    const storyItems = Array.from(archive.querySelectorAll("[data-story-item]"));

    function setLanguage(language) {
        buttons.forEach((button) => {
            const isActive = button.dataset.language === language;
            button.classList.toggle("active", isActive);
            button.setAttribute("aria-pressed", String(isActive));
        });

        storyItems.forEach((item) => {
            const titleLink = item.querySelector(".story-title-link");
            if (!titleLink) {
                return;
            }

            const suffix = language === "it" ? "It" : "En";
            const title = titleLink.dataset[`title${suffix}`];
            const url = titleLink.dataset[`url${suffix}`];
            const activeLanguage = title && url
                ? language
                : titleLink.dataset.defaultLanguage;

            titleLink.textContent = title && url
                ? title
                : titleLink.dataset.defaultTitle;
            titleLink.href = title && url
                ? url
                : titleLink.dataset.defaultUrl;
            titleLink.lang = activeLanguage;

            item.querySelectorAll(".story-inline-lang").forEach((link) => {
                link.classList.toggle(
                    "active",
                    link.dataset.language === activeLanguage,
                );
            });
        });
    }

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            setLanguage(button.dataset.language || "en");
        });
    });

    if (controls) {
        controls.hidden = false;
    }
    setLanguage("en");
})();
