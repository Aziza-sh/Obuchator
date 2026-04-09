// ================= ПРОВЕРКА АВТОРИЗАЦИИ =================

// ================= ФОРМАТИРОВАНИЕ ТЕКСТА =================

function formatDoc(command, value = null) {
  document.execCommand(command, false, value);
}

function insertBlock(html) {
  const selection = window.getSelection();

  if (!selection.rangeCount) return;

  const range = selection.getRangeAt(0);
  range.deleteContents();

  const el = document.createElement("div");
  el.innerHTML = html;

  const frag = document.createDocumentFragment();

  let node;
  while ((node = el.firstChild)) {
    frag.appendChild(node);
  }

  range.insertNode(frag);

  range.collapse(false);
  selection.removeAllRanges();
  selection.addRange(range);
}

// ================= ПАНЕЛЬ ИНСТРУМЕНТОВ =================

function initToolbar() {
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
      }
    });
  });
}

// ================= СОЗДАНИЕ НОВОСТИ =================

function initAddNews() {
  const saveBtn = document.getElementById("save-btn");

  if (!saveBtn) return;

  saveBtn.addEventListener("click", async () => {
    const title = document.getElementById("news-title").value.trim();
    const category = document.getElementById("news-category").value;
    const excerpt = document.getElementById("news-excerpt").value.trim();
    const content = document.getElementById("news-content").innerHTML.trim();

    if (!title || !content) {
      alert("Заполните заголовок и текст новости");
      return;
    }

    try {
      await API.post("/news", {
        title: title,
        category: category,
        excerpt: excerpt,
        content: content,
      });

      alert("Новость успешно создана");

      window.location.href = "main_page.html";
    } catch (error) {
      console.error("Ошибка создания новости:", error);

      let message = "Ошибка создания новости";

      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }

      alert(message);
    }
  });
}

// ================= ПРЕДПРОСМОТР =================

function initPreview() {
  const previewBtn = document.getElementById("preview-btn");
  const modal = document.getElementById("preview-modal");
  const closeBtn = document.getElementById("close-preview");

  if (!previewBtn) return;

  previewBtn.addEventListener("click", () => {
    document.getElementById("preview-title").innerText =
      document.getElementById("news-title").value;

    document.getElementById("preview-category").innerText =
      document.getElementById("news-category").value;

    document.getElementById("preview-excerpt").innerText =
      document.getElementById("news-excerpt").value;

    document.getElementById("preview-full-content").innerHTML =
      document.getElementById("news-content").innerHTML;

    modal.style.display = "flex";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
}

// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {
  requireAuth();
  initToolbar();
  initAddNews();
  initPreview();
});
