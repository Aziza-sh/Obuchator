document.addEventListener("DOMContentLoaded", () => {
  if (window.initTheme) initTheme();

  if (window.initTabs) initTabs();

  if (window.loadCourses) loadCourses();

  if (window.loadNews) loadNews();

  if (window.initAddNews) initAddNews();

  if (window.connectNewsWS) connectNewsWS();
});
