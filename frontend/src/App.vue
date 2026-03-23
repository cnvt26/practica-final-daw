<template>
  <div class="min-h-screen bg-gray-100 p-8 font-sans">
    
    <div v-if="!isLoggedIn" class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6 mt-10">
      <h2 class="text-2xl font-bold text-center mb-6 text-gray-800">🎬 Gestor de Películas</h2>
      
      <form @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Usuario</label>
          <input v-model="authForm.username" type="text" required class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Contraseña</label>
          <input v-model="authForm.password" type="password" required class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500" />
        </div>
        
        <p v-if="authError" class="text-red-500 text-sm">{{ authError }}</p>
        <p v-if="authSuccess" class="text-green-500 text-sm">{{ authSuccess }}</p>
        
        <div class="flex space-x-2">
          <button type="submit" @click="isRegistering = false" class="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700 transition">Entrar</button>
          <button type="submit" @click="isRegistering = true" class="w-full bg-gray-200 text-gray-800 p-2 rounded hover:bg-gray-300 transition">Registrarse</button>
        </div>
      </form>
    </div>

    <div v-else class="max-w-3xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">🎬 Mi Colección</h1>
        <button @click="logout" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition">Cerrar Sesión</button>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 class="text-xl font-semibold mb-4">Añadir Nueva</h2>
        <form @submit.prevent="addMovie" class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input v-model="newMovie.title" placeholder="Título" required class="border p-2 rounded col-span-2" />
          <input v-model="newMovie.director" placeholder="Director" required class="border p-2 rounded" />
          <input v-model="newMovie.year" type="number" placeholder="Año" required class="border p-2 rounded" />
          <button type="submit" class="bg-green-500 text-white p-2 rounded col-span-1 md:col-span-4 hover:bg-green-600">Añadir Película</button>
        </form>
      </div>

      <ul class="space-y-4">
        <li v-for="movie in movies" :key="movie.id" class="bg-white p-4 rounded-lg shadow flex justify-between items-center" :class="{ 'opacity-60': movie.watched }">
          <div>
            <h3 class="font-bold text-lg" :class="{ 'line-through text-gray-500': movie.watched }">{{ movie.title }}</h3>
            <p class="text-sm text-gray-600">{{ movie.director }} ({{ movie.year }})</p>
          </div>
          <div class="space-x-2">
            <button @click="toggleWatched(movie)" class="px-3 py-1 rounded text-white text-sm" :class="movie.watched ? 'bg-gray-400' : 'bg-blue-500'">
              {{ movie.watched ? 'Vista' : 'Marcar vista' }}
            </button>
            <button @click="deleteMovie(movie.id)" class="px-3 py-1 rounded bg-red-500 text-white text-sm hover:bg-red-600">Borrar</button>
          </div>
        </li>
      </ul>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { apiService } from './services/api';

// Estados Auth
const isLoggedIn = ref(!!localStorage.getItem('token'));
const isRegistering = ref(false);
const authForm = ref({ username: '', password: '' });
const authError = ref('');
const authSuccess = ref('');

// Estados Películas
const movies = ref<any[]>([]);
const newMovie = ref({ title: '', director: '', year: new Date().getFullYear(), watched: false });

// Funciones Auth
const handleAuth = async () => {
  authError.value = '';
  authSuccess.value = '';
  try {
    if (isRegistering.value) {
      await apiService.register(authForm.value);
      authSuccess.value = 'Registro exitoso. Ahora haz clic en Entrar.';
    } else {
      const res = await apiService.login(authForm.value);
      localStorage.setItem('token', res.access_token);
      isLoggedIn.value = true;
      loadMovies();
    }
  } catch (error: any) {
    authError.value = error.response?.data?.detail || 'Error en la autenticación';
  }
};

const logout = () => {
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  movies.value = [];
};

// Funciones Películas
const loadMovies = async () => {
  try {
    movies.value = await apiService.listMovies();
  } catch (e : any) {
    if (e.response?.status === 401) logout();
  }
};

const addMovie = async () => {
  try {
    const created = await apiService.createMovie(newMovie.value);
    movies.value.push(created);
    newMovie.value = { title: '', director: '', year: new Date().getFullYear(), watched: false };
  } catch (e : any) {
    if (e.response?.status === 401) logout();
  }
};

const toggleWatched = async (movie: any) => {
  try {
    const updated = await apiService.updateMovie(movie.id, { ...movie, watched: !movie.watched });
    const index = movies.value.findIndex(m => m.id === movie.id);
    if (index !== -1) movies.value[index] = updated;
  } catch (e) {
    if (e.response?.status === 401) logout();
  }
};

const deleteMovie = async (id: number) => {
  try {
    await apiService.deleteMovie(id);
    movies.value = movies.value.filter(m => m.id !== id);
  } catch (e) {
    if (e.response?.status === 401) logout();
  }
};

// Inicio
onMounted(() => {
  if (isLoggedIn.value) loadMovies();
});
</script>