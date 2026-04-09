const socket = new WebSocket("ws://localhost:8000/ws/news");

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);

  if (data.type === "new_news") {
    addNewsCard(data.data);
  }

  if (data.type === "update_likes") {
    const el = document.getElementById(`likes-${data.news_id}`);

    if (el) {
      el.innerText = data.likes;
    }
  }
};
