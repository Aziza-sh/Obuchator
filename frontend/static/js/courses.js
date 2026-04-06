window.loadCourses = async function () {
  const container = document.querySelector("#myCourses .container");

  if (!container) return;

  try {
    const res = await api.get("/courses");

    container.innerHTML = "";

    res.data.forEach((course) => {
      const block = document.createElement("div");

      block.className = "g-block";

      block.innerHTML = `
        <h2>${course.name}</h2>
        <p>Уроков: ${course.lesson_count}</p>
      `;

      container.appendChild(block);
    });
  } catch (e) {
    console.error("Ошибка загрузки курсов");
  }
};
