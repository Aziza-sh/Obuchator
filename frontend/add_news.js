(function() {
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

  // ===== Данные новостей =====
  let newsList = [
    {
      id: "1",
      title: "Запуск нового курса",
      category: "Важное",
      excerpt: "Мы запускаем курс по веб-разработке!",
      content: "<h3>Детали</h3><p>Старт 1 апреля. Успейте записаться!</p>",
      image: null, // обложка (будет храниться как base64)
      date: new Date().toLocaleDateString('ru-RU')
    },
    {
      id: "2",
      title: "Обновление платформы",
      category: "Обновление",
      excerpt: "Добавлен тёмный режим и редактор новостей.",
      content: "<p>Теперь можно переключать тему и создавать новости прямо на сайте.</p>",
      image: null,
      date: new Date().toLocaleDateString('ru-RU')
    }
  ];
  let currentNewsId = "1";

  // Элементы DOM
  const newsListEl = document.getElementById("news-list");
  const newsCountEl = document.getElementById("news-count");
  const titleInput = document.getElementById("news-title");
  const categorySelect = document.getElementById("news-category");
  const excerptTextarea = document.getElementById("news-excerpt");
  const contentDiv = document.getElementById("news-content");
  const editorTitle = document.getElementById("editor-title");
  const saveStatus = document.getElementById("save-status");
  const addNewsBtn = document.getElementById("add-news-btn");
  const saveBtn = document.getElementById("save-btn");
  const previewBtn = document.getElementById("preview-btn");
  const previewModal = document.getElementById("preview-modal");
  const previewTitle = document.getElementById("preview-title");
  const previewCategory = document.getElementById("preview-category");
  const previewDate = document.getElementById("preview-date");
  const previewExcerpt = document.getElementById("preview-excerpt");
  const previewCardImage = document.getElementById("preview-card-image");
  const previewFullContent = document.getElementById("preview-full-content");
  const closePreview = document.getElementById("close-preview");

  // Изображение обложки
  const imageUploadArea = document.getElementById("image-upload-area");
  const imageInput = document.getElementById("news-image");
  const imagePreview = document.getElementById("image-preview");

  // ===== Работа со списком =====
  function renderNewsList() {
    newsListEl.innerHTML = "";
    newsList.forEach(news => {
      const item = document.createElement("div");
      item.className = `news-item ${news.id === currentNewsId ? "active" : ""}`;
      item.dataset.id = news.id;
      item.innerHTML = `
        <span class="news-item-title">${news.title}</span>
        <span class="news-item-date">${news.date} • ${news.category}</span>
        <button class="delete-news" data-id="${news.id}" title="Удалить">✕</button>
      `;
      item.addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-news")) return;
        selectNews(news.id);
      });
      newsListEl.appendChild(item);
    });

    document.querySelectorAll(".delete-news").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        deleteNews(id);
      });
    });

    newsCountEl.textContent = newsList.length;
  }

  function selectNews(id) {
    currentNewsId = id;
    const news = newsList.find(n => n.id === id);
    if (news) {
      titleInput.value = news.title;
      categorySelect.value = news.category;
      excerptTextarea.value = news.excerpt || "";
      contentDiv.innerHTML = news.content || "";

      // Восстанавливаем изображение, если оно есть
      if (news.image) {
        imagePreview.src = news.image;
        imagePreview.style.display = 'block';
        imageUploadArea.querySelector("span").style.display = 'none';
      } else {
        imagePreview.style.display = 'none';
        imageUploadArea.querySelector("span").style.display = 'inline';
      }

      editorTitle.textContent = `Редактирование: ${news.title}`;
    }
    renderNewsList();
    updateSaveStatus("✔ Все сохранено");
  }

  function deleteNews(id) {
    if (newsList.length <= 1) {
      alert("Нельзя удалить последнюю новость");
      return;
    }
    newsList = newsList.filter(n => n.id !== id);
    if (currentNewsId === id) {
      currentNewsId = newsList[0].id;
    }
    selectNews(currentNewsId);
  }

  function addNews() {
    const newId = Date.now().toString();
    const newNews = {
      id: newId,
      title: "Новая новость",
      category: "Важное",
      excerpt: "",
      content: "<p>Текст новости...</p>",
      image: null,
      date: new Date().toLocaleDateString('ru-RU')
    };
    newsList.push(newNews);
    currentNewsId = newId;
    selectNews(currentNewsId);
  }

  function saveCurrentNews() {
    const news = newsList.find(n => n.id === currentNewsId);
    if (news) {
      news.title = titleInput.value.trim() || "Без названия";
      news.category = categorySelect.value;
      news.excerpt = excerptTextarea.value;
      news.content = contentDiv.innerHTML;
      news.image = imagePreview.src && imagePreview.src !== '#' ? imagePreview.src : null;
      editorTitle.textContent = `Редактирование: ${news.title}`;
      renderNewsList();
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
    contentDiv.focus();
    updateSaveStatus("⏳ Несохранённые изменения");
  }

  function insertBlock(html) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0);
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const block = tempDiv.firstChild;
    range.deleteContents();
    range.insertNode(block);
    const p = document.createElement('p');
    p.innerHTML = '<br>';
    block.parentNode.insertBefore(p, block.nextSibling);
    const newRange = document.createRange();
    newRange.setStart(p, 0);
    newRange.collapse(true);
    selection.removeAllRanges();
    selection.addRange(newRange);
    updateSaveStatus("⏳ Несохранённые изменения");
  }

  // Вставка изображения в текст
  function insertImageIntoContent() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(ev) {
          const imgHTML = `<img src="${ev.target.result}" alt="image" style="max-width:100%;">`;
          const selection = window.getSelection();
          if (!selection.rangeCount) return;
          const range = selection.getRangeAt(0);
          range.deleteContents();
          const img = document.createElement('img');
          img.src = ev.target.result;
          img.style.maxWidth = '100%';
          range.insertNode(img);
          // Перемещаем курсор после картинки
          const p = document.createElement('p');
          p.innerHTML = '<br>';
          img.parentNode.insertBefore(p, img.nextSibling);
          const newRange = document.createRange();
          newRange.setStart(p, 0);
          newRange.collapse(true);
          selection.removeAllRanges();
          selection.addRange(newRange);
          updateSaveStatus("⏳ Несохранённые изменения");
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  }

  document.querySelectorAll('.editor-toolbar button').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.command;
      switch(cmd) {
        case 'h3': formatDoc('formatBlock', '<h3>'); break;
        case 'p': formatDoc('formatBlock', '<p>'); break;
        case 'bold': formatDoc('bold'); break;
        case 'italic': formatDoc('italic'); break;
        case 'code': {
          const selected = window.getSelection().toString();
          if (selected) insertBlock(`<div class="code-block"><pre>${selected}</pre></div>`);
          else insertBlock('<div class="code-block"><pre>Вставьте код</pre></div>');
          break;
        }
        case 'info': insertBlock('<div class="info-box"><strong>Важно:</strong> Текст</div>'); break;
        case 'ul': formatDoc('insertUnorderedList'); break;
        case 'ol': formatDoc('insertOrderedList'); break;
        case 'insertImage': insertImageIntoContent(); break;
        case 'removeFormat': formatDoc('removeFormat'); break;
        default: break;
      }
    });
  });

  // ===== Загрузка обложки =====
  imageUploadArea.addEventListener('click', () => imageInput.click());
  imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(ev) {
        imagePreview.src = ev.target.result;
        imagePreview.style.display = 'block';
        imageUploadArea.querySelector('span').style.display = 'none';
        updateSaveStatus("⏳ Несохранённые изменения");
      };
      reader.readAsDataURL(file);
    }
  });

  // ===== Предпросмотр =====
  previewBtn.addEventListener('click', () => {
    const news = newsList.find(n => n.id === currentNewsId);
    if (news) {
      previewTitle.textContent = titleInput.value || news.title;
      previewCategory.textContent = categorySelect.value;
      previewDate.textContent = new Date().toLocaleDateString('ru-RU');
      previewExcerpt.textContent = excerptTextarea.value || news.excerpt;
      previewFullContent.innerHTML = contentDiv.innerHTML;

      if (imagePreview.src && imagePreview.src !== '#') {
        previewCardImage.src = imagePreview.src;
        previewCardImage.style.display = 'block';
      } else {
        previewCardImage.style.display = 'none';
      }

      previewModal.style.display = 'flex';
    }
  });

  closePreview.addEventListener('click', () => {
    previewModal.style.display = 'none';
  });

  previewModal.addEventListener('click', (e) => {
    if (e.target === previewModal) previewModal.style.display = 'none';
  });

  // ===== Обработчики =====
  addNewsBtn.addEventListener('click', addNews);
  saveBtn.addEventListener('click', saveCurrentNews);
  titleInput.addEventListener('input', () => updateSaveStatus("⏳ Несохранённые изменения"));
  categorySelect.addEventListener('change', () => updateSaveStatus("⏳ Несохранённые изменения"));
  excerptTextarea.addEventListener('input', () => updateSaveStatus("⏳ Несохранённые изменения"));
  contentDiv.addEventListener('input', () => updateSaveStatus("⏳ Несохранённые изменения"));

  // Инициализация
  selectNews(currentNewsId);
  
})();