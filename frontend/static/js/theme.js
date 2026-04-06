window.initTheme = function () {
  const btn = document.getElementById("theme-toggle");
  const body = document.body;

  if (!btn) return;

  const saved = localStorage.getItem("site-theme") || "light";

  if (saved === "dark") {
    body.classList.add("dark-theme");
    btn.textContent = "☀️";
  }

  btn.addEventListener("click", () => {
    body.classList.toggle("dark-theme");

    const dark = body.classList.contains("dark-theme");

    btn.textContent = dark ? "☀️" : "🌙";

    localStorage.setItem("site-theme", dark ? "dark" : "light");
  });
};
