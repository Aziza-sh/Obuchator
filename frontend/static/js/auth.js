window.isAuthenticated = function () {
  return !!localStorage.getItem("access_token");
};



window.logout = function () {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");

  window.location.href = "login_page.html";
};

document.addEventListener("DOMContentLoaded", () => {

  const logoutBtn = document.getElementById("logout-btn");

  if (!logoutBtn) return;

  logoutBtn.addEventListener("click", () => {

    localStorage.removeItem("access_token");

    alert("Вы вышли из аккаунта");

    window.location.href = "login_page.html";

  });

});

const token = localStorage.getItem("access_token");

const logoutBtn = document.getElementById("logout-btn");

