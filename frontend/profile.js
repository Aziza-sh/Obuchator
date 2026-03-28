document.addEventListener("DOMContentLoaded", function () {
  // ===== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =====
  const themeToggle = document.getElementById("theme-toggle");
  const body = document.body;

  if (themeToggle) {
    const savedTheme = localStorage.getItem("site-theme") || "light";
    if (savedTheme === "dark") {
      body.classList.add("dark-theme");
      themeToggle.textContent = "☀️";
    }

    themeToggle.addEventListener("click", () => {
      body.classList.toggle("dark-theme");
      const isDark = body.classList.contains("dark-theme");
      themeToggle.textContent = isDark ? "☀️" : "🌙";
      localStorage.setItem("site-theme", isDark ? "dark" : "light");
    });
  }

  const changeAvatarBtn = document.querySelector(".change-avatar");
  const editBtn = document.querySelector(".edit-btn");

  if (!changeAvatarBtn || !editBtn) {
    console.error("Не найдены необходимые элементы на странице");
    return;
  }

  changeAvatarBtn.addEventListener("click", handleAvatarChange);
  editBtn.addEventListener("click", handleEditProfile);

  initProgressBars();
});

function handleAvatarChange() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const avatar = document.querySelector(".avatar");
        if (avatar) {
          avatar.src = e.target.result;
        }
      };
      reader.readAsDataURL(file);
    }
  };
  input.click();
}

function handleEditProfile() {
  alert("Редактирование профиля будет доступно в следующем обновлении!");
}

function initProgressBars() {
  const progressBars = document.querySelectorAll(".progress-fill");

  progressBars.forEach((bar) => {
    const width = bar.style.width || getComputedStyle(bar).width;
    bar.style.transition = "width 0.8s ease-in-out";
    bar.style.width = "0%";

    setTimeout(() => {
      bar.style.width = width;
    }, 50);
  });
}
