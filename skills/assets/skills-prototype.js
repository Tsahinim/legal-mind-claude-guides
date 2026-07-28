(() => {
  "use strict";

  const copyButton = document.querySelector("[data-copy-target]");
  if (copyButton) {
    copyButton.addEventListener("click", async () => {
      const target = document.getElementById(copyButton.dataset.copyTarget);
      const status = copyButton.closest(".copy-block")?.querySelector(".copy-status");
      if (!target || !status) return;

      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        status.textContent = "שאלת הבדיקה הועתקה";
      } catch {
        status.textContent = "ההעתקה האוטומטית לא הצליחה. סמנו את הטקסט והעתיקו אותו ידנית.";
      }
    });
  }

  const sections = [...document.querySelectorAll(".guide-section[id]")];
  const tocLinks = [...document.querySelectorAll(".desktop-toc a[href^='#']")];
  if (!sections.length || !tocLinks.length) return;

  const setActiveLink = (id) => {
    tocLinks.forEach((link) => {
      if (link.getAttribute("href") === `#${id}`) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  };

  setActiveLink(sections[0].id);

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActiveLink(visible.target.id);
      },
      { rootMargin: "-15% 0px -65% 0px", threshold: [0, 0.15, 0.5] }
    );
    sections.forEach((section) => observer.observe(section));
  }
})();
