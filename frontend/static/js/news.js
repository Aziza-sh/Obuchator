// ================= ЗАГРУЗКА НОВОСТЕЙ =================

window.loadNews = async function () {

  const container = document.getElementById("news-feed");

  if (!container) return;

  try {

    const res = await API.get("/news");

    container.innerHTML = "";

    if (!res.data.length) {
      document.getElementById("no-news").style.display = "block";
      return;
    }

    res.data.forEach(addNewsCard);

  } catch (e) {

    console.error("Ошибка загрузки новостей", e);

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