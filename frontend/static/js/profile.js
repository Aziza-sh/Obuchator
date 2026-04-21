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

// ================= TELEGRAM =================

async function loadTelegramStatus() {
  try {
    const [statusRes, subRes] = await Promise.all([
      window.api.get("/api/v1/telegram/status"),
      window.api.get("/news/subscribe"),
    ]);

    const linked = statusRes.data.linked;
    const subscribed = subRes.data.subscribed;

    document.getElementById("tg-not-linked").style.display = linked ? "none" : "block";
    document.getElementById("tg-linked").style.display = linked ? "block" : "none";

    const toggle = document.getElementById("news-sub-toggle");
    if (toggle) toggle.checked = subscribed;
  } catch (e) {
    console.error("Ошибка загрузки статуса Telegram:", e);
    // при ошибке показываем блок "не привязан"
    document.getElementById("tg-not-linked").style.display = "block";
    document.getElementById("tg-linked").style.display = "none";
  }
}

window.linkTelegram = async function () {
  try {
    const res = await window.api.post("/api/v1/telegram/link-token");
    const token = res.data.token;
    const expires = res.data.expires_in;

    document.getElementById("tg-link-command").textContent = `/start ${token}`;
    document.getElementById("tg-token-expire").textContent =
      `Ссылка действительна ${Math.floor(expires / 60)} минут`;

    const modal = document.getElementById("tg-modal");
    modal.style.display = "flex";
  } catch (e) {
    alert("Не удалось получить ссылку. Попробуйте ещё раз.");
  }
};

window.closeTgModal = async function () {
  document.getElementById("tg-modal").style.display = "none";
  await loadTelegramStatus();
};

window.unlinkTelegram = async function () {
  if (!confirm("Отвязать Telegram-аккаунт? Уведомления перестанут приходить.")) return;
  try {
    await window.api.delete("/api/v1/telegram/unlink");
    await loadTelegramStatus();
  } catch (e) {
    alert("Не удалось отвязать аккаунт.");
  }
};

window.toggleNewsSub = async function (checked) {
  try {
    if (checked) {
      await window.api.post("/news/subscribe");
    } else {
      await window.api.delete("/news/subscribe");
    }
  } catch (e) {
    const msg = e.response?.data?.detail || "Ошибка изменения подписки";
    alert(msg);
    // откатить тогл
    const toggle = document.getElementById("news-sub-toggle");
    if (toggle) toggle.checked = !checked;
  }
};

window.copyCommand = function (btn) {
  const text = document.getElementById("tg-link-command").textContent;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "Скопировано!";
    setTimeout(() => (btn.textContent = "Копировать"), 2000);
  });
};

// ================= ЗАПУСК ВСЕГО ПРИ ЗАГРУЗКЕ СТРАНИЦЫ =================
document.addEventListener("DOMContentLoaded", async () => {
  // Сначала загружаем данные пользователя
  await loadUserProfile();

  // Затем инициализируем все остальные виджеты
  initTheme();
  initAvatar();
  initProgressBars();
  initEditButton();

  // Telegram статус
  await loadTelegramStatus();
});
