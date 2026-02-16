document.addEventListener('DOMContentLoaded', function() {
  // ===== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =====
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;

  if (themeToggle) {
    const savedTheme = localStorage.getItem('site-theme') || 'light';
    if (savedTheme === 'dark') {
      body.classList.add('dark-theme');
      themeToggle.textContent = '☀️';
    }

    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-theme');
      const isDark = body.classList.contains('dark-theme');
      themeToggle.textContent = isDark ? '☀️' : '🌙';
      localStorage.setItem('site-theme', isDark ? 'dark' : 'light');
    });
  }

  // ===== ФУНКЦИЯ АККОРДЕОНА =====
  function toggleAccordion(sectionId) {
    const container = document.getElementById(sectionId);
    if (!container) return;
    const header = container.previousElementSibling;
    const icon = header.querySelector(".toggle-icon");

    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

    container.classList.toggle("hidden");
    header.classList.toggle("collapsed");

    icon.textContent = container.classList.contains("hidden") ? "▶" : "▼";

    setTimeout(() => {
      window.scrollTo(0, scrollPosition);
    }, 10);
  }

  // ===== ОБРАБОТЧИКИ ДЛЯ АККОРДЕОНОВ =====
  document.querySelectorAll('.courses-header, .accordion-header').forEach(header => {
    header.addEventListener('click', function() {
      const container = this.nextElementSibling;
      if (container && container.id) {
        toggleAccordion(container.id);
      }
    });
  });

  // ===== ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК =====
  function setupTabNavigation() {
    const menuButtons = document.querySelectorAll(".menu-btn");
    const contentSections = document.querySelectorAll(".content-section");

    if (menuButtons.length === 0 || contentSections.length === 0) {
      console.error("Не найдены элементы для переключения вкладок");
      return;
    }

    menuButtons.forEach((button) => {
      button.addEventListener("click", function () {
        menuButtons.forEach((btn) => btn.classList.remove("active"));
        this.classList.add("active");

        contentSections.forEach((section) => {
          section.classList.remove("active");
        });

        const tabId = this.getAttribute("data-tab");
        const targetSection = document.getElementById(tabId);
        if (targetSection) {
          targetSection.classList.add("active");
        } else {
          console.error('Раздел с id "' + tabId + '" не найден');
        }
      });
    });
  }

  setupTabNavigation();

  // Если нужно, чтобы аккордеоны были свёрнуты по умолчанию:
  // toggleAccordion('newCourses');
  // toggleAccordion('completedCourses');
});