async function loadNewsDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");

  if (!id) {
    console.error("Нет ID новости");
    return;
  }

  try {
    const res = await API.get(`/news/${id}`);
    const news = res.data;

    console.log("Новость:", news);

    const title = document.getElementById("news-title");
    const content = document.getElementById("news-content");

    if (title) title.innerText = news.title || "Без заголовка";
    if (content) content.innerHTML = news.content || "";
  } catch (e) {
    console.error("Ошибка загрузки новости", e);
  }
}

document.addEventListener("DOMContentLoaded", loadNewsDetail);
