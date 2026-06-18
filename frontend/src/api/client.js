import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const client = axios.create({ baseURL: BASE_URL });

function getTokens() {
  try {
    return JSON.parse(localStorage.getItem('cps_tokens') || 'null');
  } catch {
    return null;
  }
}

function setTokens(tokens) {
  if (tokens) localStorage.setItem('cps_tokens', JSON.stringify(tokens));
  else localStorage.removeItem('cps_tokens');
}

client.interceptors.request.use((config) => {
  const tokens = getTokens();
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue = [];

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      const tokens = getTokens();
      if (!tokens?.refresh) {
        setTokens(null);
        return Promise.reject(error);
      }
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({ resolve, reject, original });
        });
      }

      isRefreshing = true;
      try {
        const { data } = await axios.post(`${BASE_URL}/auth/login/refresh/`, {
          refresh: tokens.refresh,
        });
        setTokens({ ...tokens, access: data.access });
        refreshQueue.forEach(({ resolve, original: o }) => {
          o.headers.Authorization = `Bearer ${data.access}`;
          resolve(client(o));
        });
        refreshQueue = [];
        original.headers.Authorization = `Bearer ${data.access}`;
        return client(original);
      } catch (refreshError) {
        setTokens(null);
        refreshQueue.forEach(({ reject }) => reject(refreshError));
        refreshQueue = [];
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: (username, password) => client.post('/auth/login/', { username, password }),
  register: (payload) => client.post('/auth/register/', payload),
  me: () => client.get('/auth/me/'),
};

export const complaints = {
  list: () => client.get('/complaints/'),
  detail: (id) => client.get(`/complaints/${id}/`),
  create: (payload) => client.post('/complaints/', payload),
  updateStatus: (id, status, notes = '') =>
    client.post(`/complaints/${id}/update_status/`, { status, notes }),
  escalate: (id, reason = '') => client.post(`/complaints/${id}/escalate/`, { reason }),
  resolve: (id, notes = '') => client.post(`/complaints/${id}/resolve/`, { notes }),
  history: (id) => client.get(`/complaints/${id}/history/`),
  stats: () => client.get('/complaints/stats/'),
};

export const notifications = {
  list: () => client.get('/notifications/'),
  unreadCount: () => client.get('/notifications/unread-count/'),
  markRead: (id) => client.post(`/notifications/${id}/read/`),
  markAllRead: () => client.post('/notifications/read-all/'),
};

export { getTokens, setTokens };
export default client;
