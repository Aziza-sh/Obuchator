// ========== Переключение темы ==========
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

// ========== Регистрация ==========
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Собираем данные формы (убедитесь, что в HTML есть поля с id first_name и last_name)
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const first_name =
      document.getElementById("first_name")?.value.trim() || "";
    const last_name = document.getElementById("last_name")?.value.trim() || "";

    // Валидация
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
      const response = await axios.post(
        "/api/v1/auth/register",
        {
          email: email,
          password: password,
          first_name: first_name,
          last_name: last_name,
        },
        {
          headers: { "Content-Type": "application/json" },
        },
      );

      if (response.status === 201) {
        alert("Регистрация прошла успешно!");
        registerForm.reset();
        setTimeout(() => {
          window.location.href = "/static/login_page.html";
        }, 1000);
      } else {
        alert(`Неожиданный ответ сервера: ${response.status}`);
      }
    } catch (error) {
      let errorMessage = "Ошибка при регистрации. Попробуйте позже.";
      if (error.response) {
        const detail = error.response.data.detail;
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((err) => err.msg).join("; ");
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.request) {
        errorMessage = "Сервер не отвечает. Проверьте соединение.";
      } else {
        errorMessage = error.message;
      }
      alert(`Ошибка: ${errorMessage}`);
    } finally {
      submitButton.textContent = originalText;
      submitButton.disabled = false;
    }
  });
}

// ========== Логин ==========
const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            alert('Заполните все поля');
            return;
        }

        const submitButton = loginForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Вход...';
        submitButton.disabled = true;

        try {
            // Создаём объект FormData или URLSearchParams для отправки как форма
            const formData = new URLSearchParams();
            formData.append('grant_type', 'password');
            formData.append('email', email);
            formData.append('password', password);

            const response = await axios.post('/api/v1/auth/token', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            if (response.status === 201 || response.status === 200) {
                const { access_token, refresh_token } = response.data;
                localStorage.setItem('access_token', access_token);
                if (refresh_token) {
                    localStorage.setItem('refresh_token', refresh_token);
                }
                alert('Вход выполнен успешно!');
                window.location.href = '/static/profile_page.html'; // измените на нужную страницу
            } else {
                alert(`Неожиданный ответ: ${response.status}`);
            }
        } catch (error) {
            let errorMessage = 'Ошибка при входе';
            if (error.response) {
                const detail = error.response.data.detail;
                errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
            } else if (error.request) {
                errorMessage = 'Сервер не отвечает';
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

// ========== Пример запроса к защищённому эндпоинту ==========
async function fetchProtectedData() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    console.warn("Нет токена");
    return;
  }

  try {
    const response = await axios.get("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    console.log("Профиль:", response.data);
    alert("Данные профиля получены (см. консоль)");
  } catch (error) {
    console.error("Ошибка при запросе защищённых данных:", error);
    if (error.response?.status === 401) {
      alert("Сессия истекла. Войдите снова.");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/static/login_page.html";
    }
  }
}

// Вызовите fetchProtectedData() там, где нужно, например, на странице профиля.
