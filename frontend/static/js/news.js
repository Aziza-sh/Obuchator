// ================= ЗАГРУЗКА НОВОСТЕЙ =================

window.loadNews = async function () {
  const container = document.getElementById("news-feed");
  if (!container) return;

  try {
    const res = await API.get("/news");
    console.log("Новости от бэкенда:", res.data); // отладка

    container.innerHTML = "";
    const noNewsDiv = document.getElementById("no-news");
    if (!res.data.length) {
      if (noNewsDiv) noNewsDiv.style.display = "block";
      return;
    }
    if (noNewsDiv) noNewsDiv.style.display = "none";

    res.data.forEach(addNewsCard);
  } catch (e) {
    console.error("Ошибка загрузки новостей", e);
  }

  function addNewsCard(news) {
    const container = document.getElementById("news-feed");
    if (!container) return;

    const card = document.createElement("div");
    card.className = "news-card";

    // HEADER
    const header = document.createElement("div");
    header.className = "news-header";

    const categorySpan = document.createElement("span");
    let categoryClass = "news-category";
    if (news.category) {
      categoryClass += ` category-${news.category.toLowerCase()}`;
    } else {
      categoryClass += " category-important";
    }
    categorySpan.className = categoryClass;
    categorySpan.textContent = news.category || "Новость";

    const dateSpan = document.createElement("span");
    dateSpan.className = "news-date";
    const date = new Date(news.created_at);
    dateSpan.textContent = isNaN(date.getTime())
      ? news.created_at
      : date.toLocaleDateString("ru-RU");

    header.appendChild(categorySpan);
    header.appendChild(dateSpan);

    // CONTENT
    const contentDiv = document.createElement("div");
    contentDiv.className = "news-content";

    const title = document.createElement("h3");
    title.className = "news-headline";
    title.textContent = news.title || "Без заголовка";

    const excerpt = document.createElement("p");
    excerpt.className = "news-text";
    excerpt.textContent = news.excerpt || "";

    contentDiv.appendChild(title);
    contentDiv.appendChild(excerpt);

    // FOOTER
    const footer = document.createElement("div");
    footer.className = "news-footer";

    const authorDiv = document.createElement("div");
    authorDiv.className = "news-author";

    const avatar = document.createElement("div");
    avatar.className = "author-avatar";

    // Получаем имя автора из новой структуры
    let authorName = "Аноним";
    if (news.author) {
      if (news.author.first_name && news.author.last_name) {
        authorName = `${news.author.first_name} ${news.author.last_name}`;
      } else if (news.author.full_name) {
        authorName = news.author.full_name;
      } else if (news.author.name) {
        authorName = news.author.name;
      }
    } else if (news.author_name) {
      authorName = news.author_name;
    }

    let initials =
      authorName !== "Аноним"
        ? authorName
            .split(" ")
            .map((w) => w[0])
            .join("")
            .toUpperCase()
            .slice(0, 2)
        : "А";
    avatar.textContent = initials;

    const authorNameSpan = document.createElement("span");
    authorNameSpan.className = "news-card-author";
    authorNameSpan.textContent = authorName;

    authorDiv.appendChild(avatar);
    authorDiv.appendChild(authorNameSpan);

    const button = document.createElement("button");
    button.className = "news-button";
    button.textContent = "Подробнее";
    button.addEventListener("click", () => {
      window.location.href = `news_page.html?id=${news.id}`;
    });

    footer.appendChild(authorDiv);
    footer.appendChild(button);

    card.appendChild(header);
    card.appendChild(contentDiv);
    card.appendChild(footer);

    container.appendChild(card);
  }
};

// ================= СОЗДАНИЕ КАРТОЧКИ =================

window.addNewsCard = function (news) {
  const container = document.getElementById("news-feed");

  if (!container) return;

  const card = document.createElement("div");

  card.className = "news-card";

  card.innerHTML = `
  
    <h3 class="news-card-title">${news.title}</h3>

    <p class="news-card-author">
      Автор: ${news.author_name || "Администратор"}
    </p>

    <p class="news-card-excerpt">
      ${news.excerpt || ""}
    </p>

    <div class="news-card-meta">

      <span>❤️ ${news.likes || 0}</span>

      <span>👁 ${news.views || 0}</span>

    </div>

  `;

  // клик по карточке → открыть новость

  card.addEventListener("click", () => {
    window.location.href = `news_page.html?id=${news.id}`;
  });

  container.appendChild(card);
};

// ================= КНОПКА ДОБАВЛЕНИЯ =================

function initAddNewsButton() {
  const addBtn = document.getElementById("add-news-btn");

  if (!addBtn) return;

  addBtn.addEventListener("click", () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      alert("Сначала войдите");

      window.location.href = "login_page.html";

      return;
    }

    window.location.href = "add_news_page.html";
  });
}

// ================= ДРУГИЕ НОВОСТИ (СПИСОК) =================

async function loadOtherNews() {
  const container = document.getElementById("other-news-list");
  const noNewsDiv = document.getElementById("no-other-news");
  if (!container) return;

  try {
    const res = await API.get("/news");
    container.innerHTML = "";
    if (!res.data.length) {
      if (noNewsDiv) noNewsDiv.style.display = "block";
      return;
    }
    if (noNewsDiv) noNewsDiv.style.display = "none";

    // Сортируем по дате (новые сверху) и берём первые 5
    const newsList = [...res.data].sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at),
    );
    const otherNews = newsList.slice(0, 5);

    otherNews.forEach((news) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <a href="news_page.html?id=${news.id}">${escapeHtml(news.title)}</a>
        <small>${formatRelativeDate(news.created_at)}</small>
      `;
      container.appendChild(li);
    });
  } catch (e) {
    console.error("Ошибка загрузки списка других новостей", e);
    if (noNewsDiv) noNewsDiv.style.display = "block";
  }
}

// Защита от XSS
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>]/g, function (m) {
    if (m === "&") return "&amp;";
    if (m === "<") return "&lt;";
    if (m === ">") return "&gt;";
    return m;
  });
}

// Относительное время (сегодня, вчера, X дней назад)
function formatRelativeDate(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();

  // Отбрасываем время – сравниваем только даты
  const dateStart = new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
  );
  const nowStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  const diffDays = Math.floor((nowStart - dateStart) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "сегодня";
  if (diffDays === 1) return "вчера";
  if (diffDays < 7) return `${diffDays} дня назад`;
  return date.toLocaleDateString("ru-RU");
}

// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {
  loadNews();
  initAddNewsButton();
  loadOtherNews();
});
