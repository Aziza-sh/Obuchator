const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

window.API = API;

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

API.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      const refresh = localStorage.getItem("refresh_token");

      if (!refresh) return Promise.reject(error);

      try {
        const res = await API.post(
          `${API_URL}/api/v1/auth/token`,
          new URLSearchParams({
            grant_type: "refresh_token",
            refresh_token: refresh,
          }),
        );

        localStorage.setItem("access_token", res.data.access_token);

        if (res.data.refresh_token) {
          localStorage.setItem("refresh_token", res.data.refresh_token);
        }

        original.headers.Authorization = `Bearer ${res.data.access_token}`;

        return api(original);
      } catch {
        localStorage.clear();
        window.location.href = "login_page.html";
      }
    }

    return Promise.reject(error);
  },
);
