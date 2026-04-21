window.loadCourses = async function () {
  const myContainer = document.querySelector("#myCourses .container");
  const newContainer = document.querySelector("#newCourses .container");

  if (!myContainer || !newContainer) return;

  myContainer.innerHTML = '<p style="color:var(--text-secondary);padding:16px;">Загрузка...</p>';
  newContainer.innerHTML = '<p style="color:var(--text-secondary);padding:16px;">Загрузка...</p>';

  try {
    const res = await API.get("/courses/");
    const courses = res.data;

    const subscribed = courses.filter(c => c.is_subscribed);
    const available = courses.filter(c => !c.is_subscribed);

    renderCourseCards(myContainer, subscribed, "Вы не подписаны ни на один курс");
    renderCourseCards(newContainer, available, "Нет новых курсов");
  } catch (e) {
    console.error("Ошибка загрузки курсов:", e);
    myContainer.innerHTML = '<p style="color:var(--text-secondary);padding:16px;">Ошибка загрузки</p>';
    newContainer.innerHTML = "";
  }

  const createBtn = document.getElementById("createCourseBtn");
  if (createBtn) createBtn.onclick = openCreateCourseModal;
};

function renderCourseCards(container, courses, emptyMsg) {
  container.innerHTML = "";

  if (!courses.length) {
    container.innerHTML = `<p style="color:var(--text-secondary);padding:16px;">${emptyMsg}</p>`;
    return;
  }

  courses.forEach(course => {
    const block = document.createElement("div");
    block.className = "g-block";
    block.innerHTML = `
      <img src="https://img.freepik.com/premium-photo/blue-sky-with-tiny-clouds_87394-4391.jpg?semt=ais_hybrid&w=740" alt="${escHtml(course.name)}" />
      <h2>${escHtml(course.name)}</h2>
      <p style="font-size:13px;color:var(--text-secondary);margin:4px 0 8px;white-space:normal;">${escHtml(course.description || "")}</p>
      <p style="font-size:12px;color:var(--text-secondary);">📄 ${course.material_count} материалов</p>
      <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
        <button class="button-z" onclick="location.href='course_page.html?id=${course.id}'">Открыть</button>
        <button class="button-z ${course.is_subscribed ? "subbed" : ""}"
          id="csub-${course.id}"
          onclick="toggleCourseSub('${course.id}', this)"
          style="${course.is_subscribed ? "background:var(--accent);border-color:var(--accent);" : "background:none;color:var(--accent);border:2px solid var(--accent);"}">
          ${course.is_subscribed ? "🔔 Подписан" : "🔕 Подписаться"}
        </button>
      </div>
    `;
    container.appendChild(block);
  });
}

window.toggleCourseSub = async function (courseId, btn) {
  const isSubbed = btn.classList.contains("subbed");
  btn.disabled = true;
  try {
    if (isSubbed) {
      await API.delete(`/courses/${courseId}/subscribe`);
      btn.classList.remove("subbed");
      btn.textContent = "🔕 Подписаться";
      btn.style.cssText = "background:none;color:var(--accent);border:2px solid var(--accent);";
      const block = btn.closest(".g-block");
      const newContainer = document.querySelector("#newCourses .container");
      if (block && newContainer) {
        const empty = newContainer.querySelector("p");
        if (empty) empty.remove();
        newContainer.appendChild(block);
      }
    } else {
      await API.post(`/courses/${courseId}/subscribe`);
      btn.classList.add("subbed");
      btn.textContent = "🔔 Подписан";
      btn.style.cssText = "background:var(--accent);border-color:var(--accent);color:#fff;";
      const block = btn.closest(".g-block");
      const myContainer = document.querySelector("#myCourses .container");
      if (block && myContainer) {
        const empty = myContainer.querySelector("p");
        if (empty) empty.remove();
        myContainer.appendChild(block);
      }
    }
  } catch (e) {
    const detail = e.response?.data?.detail;
    alert(typeof detail === "string" ? detail : "Ошибка изменения подписки");
  } finally {
    btn.disabled = false;
  }
};

function openCreateCourseModal() {
  const existing = document.getElementById("create-course-modal");
  if (existing) { existing.style.display = "flex"; return; }

  const modal = document.createElement("div");
  modal.id = "create-course-modal";
  modal.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:1000;display:flex;align-items:center;justify-content:center;";
  modal.innerHTML = `
    <div style="background:var(--panel-bg);border-radius:16px;padding:32px;max-width:480px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.2);">
      <h3 style="margin:0 0 20px;color:var(--text-primary);">Создать курс</h3>
      <input id="cc-name" placeholder="Название курса" style="width:100%;padding:10px 14px;border:1px solid var(--card-border);border-radius:8px;font-size:14px;margin-bottom:12px;box-sizing:border-box;background:var(--card-bg);color:var(--text-primary);" />
      <textarea id="cc-desc" placeholder="Описание" rows="3" style="width:100%;padding:10px 14px;border:1px solid var(--card-border);border-radius:8px;font-size:14px;margin-bottom:20px;box-sizing:border-box;resize:vertical;background:var(--card-bg);color:var(--text-primary);"></textarea>
      <div style="display:flex;gap:12px;">
        <button id="cc-submit" style="flex:1;padding:10px;background:linear-gradient(90deg,var(--gradient-start),var(--gradient-end));color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;">Создать</button>
        <button onclick="document.getElementById('create-course-modal').style.display='none'" style="flex:1;padding:10px;border:1px solid var(--card-border);border-radius:8px;background:none;cursor:pointer;color:var(--text-secondary);">Отмена</button>
      </div>
      <p id="cc-error" style="color:#ff6b6b;font-size:13px;margin-top:12px;display:none;"></p>
    </div>
  `;
  document.body.appendChild(modal);

  document.getElementById("cc-submit").onclick = async () => {
    const name = document.getElementById("cc-name").value.trim();
    const desc = document.getElementById("cc-desc").value.trim();
    const err = document.getElementById("cc-error");
    if (!name) { err.textContent = "Введите название"; err.style.display = "block"; return; }
    try {
      document.getElementById("cc-submit").disabled = true;
      await API.post("/courses/", { name, description: desc });
      modal.style.display = "none";
      await window.loadCourses();
    } catch (e) {
      err.textContent = e.response?.data?.detail || "Ошибка создания курса";
      err.style.display = "block";
      document.getElementById("cc-submit").disabled = false;
    }
  };
}

function escHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
