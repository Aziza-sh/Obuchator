// ================= ЗАГРУЗКА НОВОСТЕЙ =================

window.loadNews = async function () {
  const container = document.getElementById("news-feed");
  if (!container) return;

  try {
    const res = await API.get("/news");
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
    let authorName = "Аноним";
    if (news.author && news.author.full_name) {
      authorName = news.author.full_name;
    } else if (news.author_name) {
      authorName = news.author_name;
    } else if (news.author) {
      authorName = news.author.name || news.author;
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
    // ИСПРАВЛЕНО: переход на страницу новости вместо alert
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

// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {
  loadNews();

  initAddNewsButton();
});
