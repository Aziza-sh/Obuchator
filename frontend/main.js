// Функция для переключения аккордеона
function toggleAccordion(sectionId) {
  const container = document.getElementById(sectionId);
  const header = container.previousElementSibling;
  const icon = header.querySelector(".toggle-icon");

  // Сохраняем позицию скролла
  const scrollPosition =
    window.pageYOffset || document.documentElement.scrollTop;

  // Переключаем классы
  container.classList.toggle("hidden");
  header.classList.toggle("collapsed");

  // Меняем иконку
  if (container.classList.contains("hidden")) {
    icon.textContent = "▶";
  } else {
    icon.textContent = "▼";
  }

  // Восстанавливаем позицию скролла
  setTimeout(() => {
    window.scrollTo(0, scrollPosition);
  }, 10);
}

// Функция для переключения вкладок
function setupTabNavigation() {
  const menuButtons = document.querySelectorAll(".menu-btn");
  const contentSections = document.querySelectorAll(".content-section");

  if (menuButtons.length === 0 || contentSections.length === 0) {
    console.error("Не найдены элементы для переключения вкладок");
    return;
  }

  menuButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Убираем активный класс у всех кнопок
      menuButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // Скрываем все разделы
      contentSections.forEach((section) => {
        section.classList.remove("active");
      });

      // Показываем выбранный раздел
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

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
  console.log("Документ загружен, инициализация...");

  // Настройка переключения вкладок
  setupTabNavigation();

  // Если хотите, чтобы аккордеоны были свернуты по умолчанию, раскомментируйте:
  // toggleAccordion('newCourses');
  // toggleAccordion('completedCourses');
});
