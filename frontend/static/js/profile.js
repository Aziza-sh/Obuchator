// ================= ЗАГРУЗКА ДАННЫХ ПРОФИЛЯ =================
async function loadUserProfile() {
  // Проверяем, есть ли токен (залогинен ли пользователь)
  if (!window.isAuthenticated || !window.isAuthenticated()) {
    alert("Сессия не найдена. Пожалуйста, войдите снова.");
    window.location.href = "login_page.html";
    return;
  }

  try {
    const response = await window.api.get("/api/v1/auth/me");
    const user = response.data;

    // Заполняем поля, если они существуют на странице
    const fullNameElem = document.getElementById("profile-fullname");
    if (fullNameElem) {
      fullNameElem.textContent =
        `${user.first_name || ""} ${user.last_name || ""}`.trim() ||
        "Пользователь";
    }

    const roleElem = document.getElementById("profile-role");
    if (roleElem && user.role) {
      roleElem.textContent = user.role; // если бэкенд отдаёт role, иначе оставляем как есть
    }

    const emailElem = document.getElementById("profile-email");
    if (emailElem && user.email) {
      emailElem.textContent = user.email;
    }

    const phoneElem = document.getElementById("profile-phone");
    if (phoneElem) {
      phoneElem.textContent = user.phone || "Не указан";
    }

    const regdateElem = document.getElementById("profile-regdate");
    if (regdateElem && user.created_at) {
      // форматируем дату из ISO (например, "2023-03-15T10:00:00" -> "15.03.2023")
      const date = new Date(user.created_at);
      regdateElem.textContent = date.toLocaleDateString("ru-RU");
    }

    const groupElem = document.getElementById("profile-group");
    if (groupElem) {
      groupElem.textContent = user.group || "Не указана";
    }

    const statusElem = document.getElementById("profile-status");
    if (statusElem && user.is_active !== undefined) {
      statusElem.textContent = user.is_active ? "Активный" : "Неактивен";
      statusElem.style.color = user.is_active ? "#1cecd4" : "#ff8888";
    }
  } catch (error) {
    console.error("Ошибка загрузки профиля:", error);
    if (error.response?.status === 401) {
      alert("Сессия истекла. Войдите снова.");
      if (window.logout) window.logout();
    } else {
      alert("Не удалось загрузить данные профиля");
    }
  }
}

// ================= ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =================
function initTheme() {
  const themeToggle = document.getElementById("theme-toggle");
  const body = document.body;

  if (!themeToggle) return;

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

// ================= СМЕНА АВАТАРА (локально, без отправки на сервер) =================
function handleAvatarChange() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const avatar = document.querySelector(".avatar");
        if (avatar) {
          avatar.src = e.target.result;
          // можно сохранить в localStorage, но лучше отправлять на сервер
          localStorage.setItem("userAvatar", e.target.result);
        }
      };
      reader.readAsDataURL(file);
    }
  };
  input.click();
}

function initAvatar() {
  const changeAvatarBtn = document.querySelector(".change-avatar");
  if (changeAvatarBtn) {
    changeAvatarBtn.addEventListener("click", handleAvatarChange);
    // восстановить сохранённый аватар
    const savedAvatar = localStorage.getItem("userAvatar");
    if (savedAvatar) {
      const avatar = document.querySelector(".avatar");
      if (avatar) avatar.src = savedAvatar;
    }
  }
}

// ================= ПРОГРЕСС-БАРЫ (анимация) =================
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

// ================= РЕДАКТИРОВАНИЕ ПРОФИЛЯ =================
function initEditButton() {
  const editBtn = document.querySelector(".edit-btn");
  if (editBtn) {
    editBtn.addEventListener("click", () => {
      alert("Редактирование профиля будет доступно в следующем обновлении!");
      // Здесь можно открыть модальное окно с формой и отправлять PUT /api/v1/auth/me
    });
  }
}

// ================= ЗАПУСК ВСЕГО ПРИ ЗАГРУЗКЕ СТРАНИЦЫ =================
document.addEventListener("DOMContentLoaded", async () => {
  // Сначала загружаем данные пользователя
  await loadUserProfile();

  // Затем инициализируем все остальные виджеты
  initTheme();
  initAvatar();
  initProgressBars();
  initEditButton();
});
