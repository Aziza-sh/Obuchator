// ================= API INSTANCE =================
const API_BASE = "http://localhost:8000";

const API = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ================= AUTH GUARD =================
function requireAuth() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    alert("Сначала войдите в аккаунт");
    window.location.href = "login_page.html";
    return false;
  }
  return true;
}

// ================= FORMAT FUNCTIONS =================
function formatDoc(cmd, value = null) {
  document.execCommand(cmd, false, value);
}

function insertBlock(html) {
  const sel = window.getSelection();
  if (!sel.rangeCount) return;

  const range = sel.getRangeAt(0);
  range.deleteContents();

  const el = document.createElement("div");
  el.innerHTML = html;

  const frag = document.createDocumentFragment();
  let node;
  while ((node = el.firstChild)) {
    frag.appendChild(node);
  }

  range.insertNode(frag);

  // перемещаем курсор после вставленного блока
  range.collapse(false);
  sel.removeAllRanges();
  sel.addRange(range);
}

// ================= INITIALIZE EDITOR TOOLBAR =================
function initEditorToolbar() {
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
}

// ================= INIT ADD NEWS =================
window.initAddNews = function () {
  const btn = document.getElementById("createNews");
  if (!btn) return;

  if (!requireAuth()) return;

  // Инициализируем toolbar
  initEditorToolbar();

  btn.addEventListener("click", async () => {
    const title = document.getElementById("news-title").value.trim();
    const category = document.getElementById("news-category").value.trim();
    const excerpt = document.getElementById("news-excerpt").value.trim();
    const content = document.getElementById("news-content").innerHTML.trim();

    if (!title || !category || !content) {
      alert("Заполните заголовок, категорию и содержание новости");
      return;
    }

    try {
      await API.post("/news", {
        title,
        category,
        excerpt,
        content,
      });

      alert("Новость создана!");
      window.location.href = "news_page.html";
    } catch (e) {
      console.error("ERROR CREATING NEWS:", e);
      let message = "Ошибка создания новости";
      if (e.response?.data?.detail) {
        message = e.response.data.detail;
      }
      alert(message);
    }
  });
};

// ================= AUTO-INIT =================
document.addEventListener("DOMContentLoaded", () => {
  window.initAddNews();
});
