import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  getLoginUrl: () => api.get('/auth/login'),
  getMe: () => api.get('/auth/me'),
  refreshToken: () => api.post('/auth/refresh'),
  logout: () => api.post('/auth/logout'),
};

// User endpoints
export const userAPI = {
  getProfile: () => api.get('/users/me'),
  getMusicalProfile: () => api.get('/users/me/profile'),
  syncData: () => api.post('/users/me/sync'),
  getTopTracks: (limit = 50, offset = 0) => 
    api.get(`/users/me/tracks?limit=${limit}&offset=${offset}`),
  getTopArtists: (limit = 50, offset = 0) => 
    api.get(`/users/me/artists?limit=${limit}&offset=${offset}`),
  getRecentTracks: (limit = 50) => 
    api.get(`/users/me/recent?limit=${limit}`),
  getUserProfile: (userId: number) => api.get(`/users/${userId}`),
  searchUsers: (query: string) => api.get(`/users/search?query=${query}`),
};

// Compatibility endpoints
export const compatibilityAPI = {
  calculateCompatibility: (userId: number) => 
    api.post(`/compatibility/calculate/${userId}`),
  getScores: (limit = 20, offset = 0) => 
    api.get(`/compatibility/scores?limit=${limit}&offset=${offset}`),
  getTopMatches: (limit = 10) => 
    api.get(`/compatibility/top-matches?limit=${limit}`),
  getCompatibilityWithUser: (userId: number) => 
    api.get(`/compatibility/with/${userId}`),
  getSimilarUsers: (limit = 10) => 
    api.get(`/compatibility/similar-users?limit=${limit}`),
  deleteScore: (scoreId: number) => 
    api.delete(`/compatibility/scores/${scoreId}`),
};

// Analysis endpoints
export const analysisAPI = {
  getMyAnalysis: () => api.get('/analysis/my-profile'),
  getClusterAnalysis: () => api.get('/analysis/clusters'),
  performClustering: (minUsers = 10) => 
    api.post(`/analysis/clustering?min_users=${minUsers}`),
  getListeningPatterns: () => api.get('/analysis/listening-patterns'),
  getGenreAnalysis: () => api.get('/analysis/genre-analysis'),
  getAudioFeaturesRadar: () => api.get('/analysis/audio-features-radar'),
};
