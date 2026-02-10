document
  .querySelector(".search-center-button")
  .addEventListener("click", function () {
    const searchInput = document.querySelector(".search-center-input");
    if (searchInput.value.trim()) {
      alert("Поиск: " + searchInput.value);
    }
  });

document
  .querySelector(".search-center-input")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      document.querySelector(".search-center-button").click();
    }
  });

// Скрипт для навигации по урокам
document.querySelector(".nav-btn.next").addEventListener("click", function () {
  alert("Переход к следующему уроку...");
  // Здесь можно реализовать переход к следующему уроку
});

document.querySelector(".nav-btn.prev").addEventListener("click", function () {
  alert("Переход к предыдущему уроку...");
  // Здесь можно реализовать переход к предыдущему уроку
});

// Скрипт для обновления прогресса
document.querySelectorAll(".course-progress-item").forEach((item) => {
  item.addEventListener("click", function () {
    const courseTitle = this.querySelector(".course-title").textContent;
    alert("Открыть курс: " + courseTitle);
    // Здесь можно реализовать переход к выбранному курсу
  });
});
