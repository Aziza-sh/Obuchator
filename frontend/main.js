document.addEventListener('DOMContentLoaded', function() {
  // ===== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =====
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;

  if (themeToggle) {
    const savedTheme = localStorage.getItem('site-theme') || 'light';
    if (savedTheme === 'dark') {
      body.classList.add('dark-theme');
      themeToggle.textContent = '☀️';
    }

    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-theme');
      const isDark = body.classList.contains('dark-theme');
      themeToggle.textContent = isDark ? '☀️' : '🌙';
      localStorage.setItem('site-theme', isDark ? 'dark' : 'light');
    });
  }

  // ===== ФУНКЦИЯ АККОРДЕОНА =====
  function toggleAccordion(sectionId) {
    const container = document.getElementById(sectionId);
    if (!container) return;
    const header = container.previousElementSibling;
    const icon = header.querySelector('.toggle-icon');

    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

    container.classList.toggle('hidden');
    header.classList.toggle('collapsed');

    icon.textContent = container.classList.contains('hidden') ? '▶' : '▼';

    setTimeout(() => {
      window.scrollTo(0, scrollPosition);
    }, 10);
  }

  // ===== ОБРАБОТЧИКИ ДЛЯ ЗАГОЛОВКОВ АККОРДЕОНОВ =====
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', function(e) {
      if (e.target.closest('.action-btn')) return;
      const container = this.nextElementSibling;
      if (container && container.id) {
        toggleAccordion(container.id);
      }
    });
  });

  // ===== ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК =====
  function setupTabNavigation() {
    const menuButtons = document.querySelectorAll('.menu-btn');
    const contentSections = document.querySelectorAll('.content-section');

    if (menuButtons.length === 0 || contentSections.length === 0) {
      console.error('Не найдены элементы для переключения вкладок');
      return;
    }

    menuButtons.forEach(button => {
      button.addEventListener('click', function() {
        menuButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');

        contentSections.forEach(section => {
          section.classList.remove('active');
        });

        const tabId = this.getAttribute('data-tab');
        const targetSection = document.getElementById(tabId);
        if (targetSection) {
          targetSection.classList.add('active');
        } else {
          console.error('Раздел с id "' + tabId + '" не найден');
        }
      });
    });
  }
  setupTabNavigation();

  // ===== РАБОТА С КУРСАМИ (БЭКЕНД) =====
  const API_BASE = 'http://localhost:8000'; // адрес вашего FastAPI сервера

  // Функция загрузки и отображения курсов
  async function loadCourses() {
    try {
      const response = await fetch(`${API_BASE}/courses`);
      if (!response.ok) throw new Error('Ошибка загрузки курсов');
      const courses = await response.json();
      
      const container = document.querySelector('#myCourses .container');
      if (!container) return;
      
      // Очищаем контейнер
      container.innerHTML = '';
      
      if (courses.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">У вас пока нет курсов.</p>';
      } else {
        courses.forEach(course => {
          const block = document.createElement('div');
          block.className = 'g-block';
          block.dataset.courseId = course.id; // сохраняем ID для удаления
          block.innerHTML = `
            <img src="https://img.freepik.com/premium-photo/blue-sky-with-tiny-clouds_87394-4391.jpg?semt=ais_hybrid&w=740" alt="${course.name}">
            <h2>${course.name}</h2>
            <p>Уроков: ${course.lesson_count}</p>
            <button class="button-z" onclick="location.href='course_page.html?id=${course.id}'">Выбрать</button>
          `;
          container.appendChild(block);
        });
      }
      
      // Если режим управления активен, добавляем крестики к новым карточкам
      if (isManageMode) addDeleteButtons();
    } catch (error) {
      console.error('Ошибка:', error);
    }
  }

  // ===== УПРАВЛЕНИЕ КУРСАМИ (КНОПКА "УПРАВЛЯТЬ") =====
  const manageBtn = document.getElementById('manageCoursesBtn');
  let isManageMode = false;

  function addDeleteButtons() {
    document.querySelectorAll('#myCourses .g-block').forEach(block => {
      if (!block.querySelector('.delete-course-btn')) {
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-course-btn';
        deleteBtn.innerHTML = '×';
        deleteBtn.setAttribute('aria-label', 'Удалить курс');
        block.appendChild(deleteBtn);
      }
    });
  }

  function removeDeleteButtons() {
    document.querySelectorAll('#myCourses .delete-course-btn').forEach(btn => btn.remove());
  }

  // Обработчик удаления (через делегирование)
  document.addEventListener('click', async function(e) {
    const deleteBtn = e.target.closest('.delete-course-btn');
    if (!deleteBtn) return;

    const courseBlock = deleteBtn.closest('.g-block');
    if (!courseBlock) return;

    const courseId = courseBlock.dataset.courseId;
    const courseName = courseBlock.querySelector('h2')?.textContent || 'этот курс';
    
    if (!confirm(`Вы уверены, что хотите удалить курс "${courseName}"?`)) return;

    try {
      const response = await fetch(`${API_BASE}/courses/${courseId}`, {
        method: 'DELETE'
      });
      if (response.status === 204) {
        courseBlock.remove(); // удаляем из DOM
        // Если не осталось курсов, показываем заглушку
        if (document.querySelectorAll('#myCourses .g-block').length === 0) {
          const container = document.querySelector('#myCourses .container');
          container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">У вас пока нет курсов.</p>';
        }
      } else {
        alert('Не удалось удалить курс');
      }
    } catch (error) {
      console.error('Ошибка при удалении:', error);
    }
  });

  if (manageBtn) {
    manageBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      isManageMode = !isManageMode;
      if (isManageMode) {
        addDeleteButtons();
        manageBtn.textContent = 'Готово';
      } else {
        removeDeleteButtons();
        manageBtn.textContent = 'Управлять';
      }
    });
  }

  // ===== МОДАЛЬНОЕ ОКНО СОЗДАНИЯ КУРСА =====
  const createBtn = document.getElementById('createCourseBtn');
  const modal = document.getElementById('courseModal');
  const closeModal = document.querySelector('.close-modal');
  const createForm = document.getElementById('createCourseForm');

  if (createBtn) {
    createBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      modal.style.display = 'block';
    });
  }

  if (closeModal) {
    closeModal.addEventListener('click', function() {
      modal.style.display = 'none';
    });
  }

  window.addEventListener('click', function(e) {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });

  if (createForm) {
    createForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const courseName = document.getElementById('courseName').value.trim();
      const lessonCount = document.getElementById('lessonCount').value;
      const courseDesc = document.getElementById('courseDesc').value.trim();

      if (!courseName) {
        alert('Введите название курса');
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/courses`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: courseName,
            lesson_count: parseInt(lessonCount),
            description: courseDesc || null
          })
        });

        if (response.ok) {
          const newCourse = await response.json();
          alert('Курс успешно создан!');
          modal.style.display = 'none';
          createForm.reset();
          // Перезагружаем список курсов, чтобы новый появился
          await loadCourses();
          // Если нужно сразу перейти на страницу курса:
          // window.location.href = `course_page.html?id=${newCourse.id}`;
        } else {
          alert('Ошибка при создании курса');
        }
      } catch (error) {
        console.error('Ошибка:', error);
      }
    });
  }

  // Загружаем курсы при старте
  loadCourses();
});