let currentNewsId = null;
let isLiked = false;

async function loadNewsDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");

  if (!id) {
    console.error("Нет ID новости");
    return;
  }

  currentNewsId = id;

  try {
    const res = await API.get(`/news/${id}`);
    const news = res.data;

    const title = document.getElementById("news-title");
    const content = document.getElementById("news-content");
    const likes = document.getElementById("news-likes");

    // получаем элемент счётчика просмотров
    const viewsSpan = document.getElementById("news-views");

    if (title) title.innerText = news.title || "Без заголовка";
    if (content) content.innerHTML = news.content || "";

    //СЧЁТЧИК ЛАЙКОВ
    if (likes) likes.innerText = news.likes_count || 0;

    //отображаем количество просмотров
    if (viewsSpan) viewsSpan.innerText = news.views_count || 0;

    //СТАТУС ЛАЙКА
    isLiked = news.is_liked || false;
    updateLikeButton();

    //отправляем запрос на увеличение счётчика просмотров
    // Запрос отправляется без ожидания ответа, чтобы не блокировать отрисовку страницы
    API.post(`/news/${currentNewsId}/view`).catch((e) =>
      console.warn("Ошибка отправки просмотра", e),
    );
  } catch (e) {
    console.error("Ошибка загрузки новости", e);
  }
}

// ОБНОВЛЕНИЕ КНОПКИ ЛАЙКА
function updateLikeButton() {
  const btn = document.getElementById("like-btn");
  if (!btn) return;

  if (isLiked) {
    btn.innerText = "Убрать лайк";
  } else {
    btn.innerText = "👍 Поставить лайк";
  }
}

//TOGGLE ЛАЙКА
async function toggleLike() {
  if (!currentNewsId) return;

  const likesEl = document.getElementById("news-likes");

  try {
    if (isLiked) {
      await API.delete(`/news/${currentNewsId}/like`);
      isLiked = false;

      // уменьшаем счётчик лайков
      if (likesEl) likesEl.innerText = Number(likesEl.innerText) - 1;
    } else {
      await API.post(`/news/${currentNewsId}/like`);
      isLiked = true;

      // увеличиваем счётчик лайков
      if (likesEl) likesEl.innerText = Number(likesEl.innerText) + 1;
    }

    updateLikeButton();
  } catch (e) {
    console.error("Ошибка лайка", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadNewsDetail();

  const likeBtn = document.getElementById("like-btn");
  if (likeBtn) likeBtn.addEventListener("click", toggleLike);
});
