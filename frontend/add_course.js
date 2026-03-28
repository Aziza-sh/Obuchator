(function () {
  // ===== Переключение темы =====
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

  // ===== Данные уроков =====
  let lessons = [
    {
      id: "1",
      name: "Введение",
      content:
        "<h3>Введение</h3><p>Добро пожаловать на курс! Здесь будет вводный текст.</p>",
    },
    {
      id: "2",
      name: "Основы",
      content: "<h3>Основы</h3><p>Основные понятия и определения.</p>",
    },
  ];
  let currentLessonId = "1";

  // Элементы DOM
  const lessonListEl = document.getElementById("lesson-list");
  const lessonCountEl = document.getElementById("lesson-count");
  const lessonNameInput = document.getElementById("lesson-name");
  const lessonContentDiv = document.getElementById("lesson-content"); // contenteditable div
  const editorTitle = document.getElementById("editor-title");
  const saveStatus = document.getElementById("save-status");
  const addLessonBtn = document.getElementById("add-lesson-btn");
  const saveBtn = document.getElementById("save-btn");
  const previewBtn = document.getElementById("preview-btn");
  const previewModal = document.getElementById("preview-modal");
  const previewTitle = document.getElementById("preview-title");
  const previewContent = document.getElementById("preview-content");
  const closePreview = document.getElementById("close-preview");

  // ===== Вспомогательные функции =====

  function renderLessonList() {
    lessonListEl.innerHTML = "";
    lessons.forEach((lesson) => {
      const item = document.createElement("div");
      item.className = `lesson-item ${lesson.id === currentLessonId ? "active" : ""}`;
      item.dataset.id = lesson.id;
      item.innerHTML = `
        <span class="lesson-title">${lesson.name}</span>
        <button class="delete-lesson" data-id="${lesson.id}" title="Удалить урок">✕</button>
      `;
      item.addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-lesson")) return;
        selectLesson(lesson.id);
      });
      lessonListEl.appendChild(item);
    });

    document.querySelectorAll(".delete-lesson").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        deleteLesson(id);
      });
    });

    lessonCountEl.textContent = lessons.length;
  }

  function selectLesson(id) {
    currentLessonId = id;
    const lesson = lessons.find((l) => l.id === id);
    if (lesson) {
      lessonNameInput.value = lesson.name;
      lessonContentDiv.innerHTML = lesson.content;
      editorTitle.textContent = `Редактирование: ${lesson.name}`;
    }
    renderLessonList();
    updateSaveStatus("✔ Все сохранено");
  }

  function deleteLesson(id) {
    if (lessons.length <= 1) {
      alert("Нельзя удалить последний урок");
      return;
    }
    lessons = lessons.filter((l) => l.id !== id);
    if (currentLessonId === id) {
      currentLessonId = lessons[0].id;
    }
    selectLesson(currentLessonId);
  }

  function addLesson() {
    const newId = Date.now().toString();
    const newLesson = {
      id: newId,
      name: "Новый урок",
      content: "<h3>Новый урок</h3><p>Текст урока...</p>",
    };
    lessons.push(newLesson);
    currentLessonId = newId;
    selectLesson(currentLessonId);
  }

  function saveCurrentLesson() {
    const lesson = lessons.find((l) => l.id === currentLessonId);
    if (lesson) {
      lesson.name = lessonNameInput.value.trim() || "Без названия";
      lesson.content = lessonContentDiv.innerHTML; // сохраняем HTML
      editorTitle.textContent = `Редактирование: ${lesson.name}`;
      renderLessonList();
      updateSaveStatus("✔ Сохранено");
    }
  }

  function updateSaveStatus(text) {
    saveStatus.textContent = text;
    setTimeout(() => {
      saveStatus.textContent = "✔ Все сохранено";
    }, 2000);
  }

  // ===== Форматирование текста =====
  function formatDoc(command, value = null) {
    document.execCommand(command, false, value);
    lessonContentDiv.focus();
    updateSaveStatus("⏳ Несохранённые изменения");
  }

  // Вставка блока с автоматическим выходом наружу
  function insertBlock(html) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0);

    // Создаём временный контейнер для парсинга HTML
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = html;
    const block = tempDiv.firstChild;

    // Вставляем блок
    range.deleteContents();
    range.insertNode(block);

    // Создаём пустой параграф после блока
    const p = document.createElement("p");
    p.innerHTML = "<br>";
    block.parentNode.insertBefore(p, block.nextSibling);

    // Перемещаем курсор в новый параграф
    const newRange = document.createRange();
    newRange.setStart(p, 0);
    newRange.collapse(true);
    selection.removeAllRanges();
    selection.addRange(newRange);

    updateSaveStatus("⏳ Несохранённые изменения");
  }

  // Обработчики кнопок панели инструментов
  document.querySelectorAll(".editor-toolbar button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cmd = btn.dataset.command;
      switch (cmd) {
        case "h3":
          formatDoc("formatBlock", "<h3>");
          break;
        case "p":
          formatDoc("formatBlock", "<p>");
          break;
        case "bold":
          formatDoc("bold");
          break;
        case "italic":
          formatDoc("italic");
          break;
        case "code": {
          const selected = window.getSelection().toString();
          if (selected) {
            insertBlock(`<div class="code-block"><pre>${selected}</pre></div>`);
          } else {
            insertBlock(
              '<div class="code-block"><pre>Вставьте код</pre></div>',
            );
          }
          break;
        }
        case "info":
          insertBlock(
            '<div class="info-box"><strong>Важно:</strong> Текст информации</div>',
          );
          break;
        case "ul":
          formatDoc("insertUnorderedList");
          break;
        case "ol":
          formatDoc("insertOrderedList");
          break;
        case "removeFormat":
          formatDoc("removeFormat");
          break;
        default:
          break;
      }
    });
  });

  // ===== Предпросмотр =====
  previewBtn.addEventListener("click", () => {
    const lesson = lessons.find((l) => l.id === currentLessonId);
    if (lesson) {
      previewTitle.textContent = lesson.name;
      previewContent.innerHTML = lessonContentDiv.innerHTML; // показываем форматированный контент
      previewModal.style.display = "flex";
    }
  });

  closePreview.addEventListener("click", () => {
    previewModal.style.display = "none";
  });

  previewModal.addEventListener("click", (e) => {
    if (e.target === previewModal) previewModal.style.display = "none";
  });

  // ===== Инициализация =====
  selectLesson(currentLessonId);

  addLessonBtn.addEventListener("click", addLesson);
  saveBtn.addEventListener("click", saveCurrentLesson);

  lessonNameInput.addEventListener("input", () =>
    updateSaveStatus("⏳ Несохранённые изменения"),
  );
  lessonContentDiv.addEventListener("input", () =>
    updateSaveStatus("⏳ Несохранённые изменения"),
  );
})();
