// ================= API URL =================

const API_BASE = "http://localhost:8000";

// ================= AXIOS INSTANCE =================

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// ================= JWT INTERCEPTOR =================

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ================= AUTH FUNCTIONS =================

function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");

  window.location.href = "login_page.html";
}

window.logout = logout;

// ================= РЕГИСТРАЦИЯ =================

const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const first_name =
      document.getElementById("first_name")?.value.trim() || "";
    const last_name = document.getElementById("last_name")?.value.trim() || "";

    if (password.length < 6) {
      alert("Пароль должен содержать минимум 6 символов");
      return;
    }

    if (!first_name || !last_name) {
      alert("Имя и фамилия обязательны");
      return;
    }

    const submitButton = registerForm.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    submitButton.textContent = "Регистрация...";
    submitButton.disabled = true;

    try {
      const response = await api.post("/api/v1/auth/register", {
        email,
        password,
        first_name,
        last_name,
      });

      if (response.status === 201) {
        alert("Регистрация прошла успешно!");

        registerForm.reset();

        setTimeout(() => {
          window.location.href = "login_page.html";
        }, 1000);
      }
    } catch (error) {
      console.error("REGISTER ERROR:", error);

      let errorMessage = "Ошибка при регистрации";

      if (error.response) {
        const detail = error.response.data?.detail;

        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((err) => err.msg).join("; ");
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.request) {
        errorMessage = "Сервер не отвечает";
      } else {
        errorMessage = error.message;
      }

      alert(errorMessage);
    } finally {
      submitButton.textContent = originalText;
      submitButton.disabled = false;
    }
  });
}

// ================= ЛОГИН =================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
      alert("Заполните все поля");
      return;
    }

    const submitButton = loginForm.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    submitButton.textContent = "Вход...";
    submitButton.disabled = true;

    try {
      const formData = new URLSearchParams();

      formData.append("grant_type", "password");
      formData.append("email", email);
      formData.append("password", password);

      const response = await api.post("/api/v1/auth/token", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (response.status === 200 || response.status === 201) {
        const { access_token, refresh_token } = response.data;

        localStorage.setItem("access_token", access_token);

        if (refresh_token) {
          localStorage.setItem("refresh_token", refresh_token);
        }

        alert("Вход выполнен успешно!");

        window.location.href = "profile_page.html";
      }
    } catch (error) {
      console.error("LOGIN ERROR:", error);

      let errorMessage = "Ошибка входа";

      if (error.response) {
        const detail = error.response.data?.detail;

        errorMessage =
          typeof detail === "string" ? detail : JSON.stringify(detail);
      } else if (error.request) {
        errorMessage = "Сервер не отвечает";
      } else {
        errorMessage = error.message;
      }

      alert(errorMessage);
    } finally {
      submitButton.textContent = originalText;
      submitButton.disabled = false;
    }
  });
}

// ================= ПРОВЕРКА ПРОФИЛЯ =================

async function fetchProtectedData() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    console.warn("Нет токена");
    return;
  }

  try {
    const response = await api.get("/api/v1/auth/me");

    console.log("Профиль:", response.data);
  } catch (error) {
    console.error("PROFILE ERROR:", error);

    if (error.response?.status === 401) {
      alert("Сессия истекла. Войдите снова.");

      logout();
    }
  }
}

// Делаем api и функции глобальными для использования в других скриптах
window.api = api;
window.isAuthenticated = isAuthenticated;
window.logout = logout;
