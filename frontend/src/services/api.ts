import axios from 'axios';

// @ts-ignore
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// INTERCEPTOR: Automáticamente añade el token JWT a las peticiones
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiService = {
  // --- AUTENTICACIÓN ---
  login: async (credentials: any) => {
    // FastAPI requiere que el login se envíe como Formulario, no como JSON
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await apiClient.post('/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  
  register: async (userData: any) => {
    const response = await apiClient.post('/register', userData);
    return response.data;
  },

  // --- PELÍCULAS ---
  listMovies: async () => {
    const response = await apiClient.get('/api/movies');
    return response.data;
  },
  createMovie: async (movie: any) => {
    const response = await apiClient.post('/api/movies', movie);
    return response.data;
  },
  updateMovie: async (id: number, movie: any) => {
    const response = await apiClient.put(`/api/movies/${id}`, movie);
    return response.data;
  },
  deleteMovie: async (id: number) => {
    const response = await apiClient.delete(`/api/movies/${id}`);
    return response.data;
  }
};