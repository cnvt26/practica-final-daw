<template>
  <div class="min-h-screen bg-gray-100 py-10">
    <div class="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-md">
      <h1 class="text-4xl font-bold text-center text-indigo-600 mb-8">🎬 Mi Colección de Películas</h1>

      <form @submit.prevent="addMovie" class="flex flex-wrap gap-2 mb-8 bg-indigo-50 p-4 rounded-md shadow-sm">
        <input v-model="newMovie.title" placeholder="Título" class="border p-2 rounded flex-1 min-w-[150px]" required />
        <input v-model="newMovie.director" placeholder="Director" class="border p-2 rounded flex-1 min-w-[150px]" required />
        <input v-model.number="newMovie.year" type="number" placeholder="Año" class="border p-2 rounded w-24" required />
        <button type="submit" class="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 transition font-bold">Añadir</button>
      </form>

      <ul class="space-y-4">
        <li v-for="movie in movies" :key="movie.id" class="flex items-center justify-between bg-white border p-4 rounded-lg shadow-sm hover:shadow-md transition">
          <div class="flex items-center gap-4">
            <input type="checkbox" :checked="movie.watched" @change="toggleWatched(movie)" class="w-6 h-6 text-indigo-600 cursor-pointer" />
            
            <div>
              <h3 class="text-xl font-semibold transition-all" :class="{'line-through text-gray-400': movie.watched, 'text-gray-800': !movie.watched}">
                {{ movie.title }}
              </h3>
              <p class="text-sm text-gray-500">{{ movie.director }} ({{ movie.year }})</p>
            </div>
          </div>
          <button @click="deleteMovie(movie.id!)" class="text-red-500 hover:text-white hover:bg-red-500 border border-red-500 px-3 py-1 rounded transition">
            Eliminar
          </button>
        </li>
      </ul>
      
      <div v-if="movies.length === 0" class="text-center text-gray-500 mt-10">
        Aún no tienes películas. ¡Añade tu película favorita arriba! 🍿
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { apiService, type Movie } from './services/api';

const movies = ref<Movie[]>([]);
const newMovie = ref<Movie>({ title: '', director: '', year: new Date().getFullYear(), watched: false });

const loadMovies = async () => {
  try {
    movies.value = await apiService.getMovies();
  } catch (error) {
    console.error("Error cargando películas:", error);
  }
};

const addMovie = async () => {
  try {
    await apiService.createMovie(newMovie.value);
    newMovie.value = { title: '', director: '', year: new Date().getFullYear(), watched: false };
    await loadMovies();
  } catch (error) {
    console.error("Error añadiendo película:", error);
  }
};

const toggleWatched = async (movie: Movie) => {
  try {
    const updatedMovie = { ...movie, watched: !movie.watched };
    await apiService.updateMovie(movie.id!, updatedMovie);
    await loadMovies();
  } catch (error) {
    console.error("Error actualizando película:", error);
  }
};

const deleteMovie = async (id: number) => {
  try {
    await apiService.deleteMovie(id);
    await loadMovies();
  } catch (error) {
    console.error("Error eliminando película:", error);
  }
};

// Cargar películas al abrir la página
onMounted(loadMovies);
</script>