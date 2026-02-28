import axios from 'axios';

// Coge la URL de Vercel (o usa localhost en tu PC)
const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Estructura de nuestra Película
export interface Movie {
  id?: number;
  title: string;
  director: string;
  year: number;
  watched: boolean;
}

export const apiService = {
  getMovies: async () => {
    const response = await api.get('/api/movies');
    return response.data;
  },
  createMovie: async (movie: Movie) => {
    const response = await api.post('/api/movies', movie);
    return response.data;
  },
  updateMovie: async (id: number, movie: Movie) => {
    const response = await api.put(`/api/movies/${id}`, movie);
    return response.data;
  },
  deleteMovie: async (id: number) => {
    const response = await api.delete(`/api/movies/${id}`);
    return response.data;
  }
};