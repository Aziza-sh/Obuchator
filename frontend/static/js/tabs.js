function initTabs() {
  const menuButtons = document.querySelectorAll(".menu-btn");
  const contentSections = document.querySelectorAll(".content-section");

  if (!menuButtons.length) return;

  menuButtons.forEach((button) => {
    button.addEventListener("click", function () {
      menuButtons.forEach((btn) => btn.classList.remove("active"));

      this.classList.add("active");

      contentSections.forEach((section) => section.classList.remove("active"));

      const tabId = this.dataset.tab;

      const target = document.getElementById(tabId);

      if (target) target.classList.add("active");
    });
  });
}
window.initTabs = function () {
  const buttons = document.querySelectorAll(".menu-btn");
  const sections = document.querySelectorAll(".content-section");

  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      sections.forEach((s) => s.classList.remove("active"));

      btn.classList.add("active");

      const id = btn.dataset.tab;

      const target = document.getElementById(id);

      if (target) target.classList.add("active");
    });
  });
};
