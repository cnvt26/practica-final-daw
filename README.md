# 🎬 Mi Gestor de Películas (Despliegue Full Stack)

Este repositorio es una aplicación web completa (Gestor de Películas) construida para aprender a estructurar, dockerizar y desplegar siguiendo los principios de **CI/CD** con **GitHub Actions**, **Vercel**, **Render** y **Railway**.

## 🚀 Demo en Vivo
Puedes probar la aplicación desplegada en el siguiente enlace:
[👉 Ver Gestor de Películas en Vercel](https://practica-final-daw.vercel.app/)

## 🛠️ Tecnologías utilizadas

| Componente | Tecnología |
| :--- | :--- |
| **Frontend** | Vue 3 + Vite + Tailwind CSS |
| **Backend** | FastAPI (Python) + Pytest + Logging |
| **Base de Datos** | MySQL |
| **Desarrollo** | Docker Compose |
| **Despliegue** | GitHub Actions + Render + Vercel + Railway |

## 🌟 Características Avanzadas Implementadas

* ✅ **Tests Automatizados:** Pruebas unitarias en el backend utilizando `pytest`.
* ✅ **Monitorización y Logging:** Sistema de registro de eventos (logs) configurado en FastAPI.
* ✅ **Documentación API Automática:** Swagger UI disponible en `/docs`.
* ⏳ *Próximamente: Autenticación con JWT.*

## 1. Estructura del Proyecto

El repositorio está organizado siguiendo el patrón de monorepositorio sencillo:
```text
.
├── backend/                # API REST con FastAPI (Python)
│   ├── main.py             # Lógica de la API, CORS y Logging
│   ├── test_main.py        # Pruebas automatizadas (pytest)
│   ├── requirements.txt    # Dependencias del proyecto
│   └── Dockerfile          # Imagen optimizada para producción
├── frontend/               # Aplicación Web con Vue 3 + Vite
│   ├── src/
│   │   ├── App.vue         # Componente principal de Películas
│   │   └── services/api.ts # Llamadas HTTP (Axios)
│   ├── Dockerfile          # Imagen optimizada
│   └── ...
├── .github/workflows/      # Automatización (CI/CD)
├── compose.yaml            # Orquestación para desarrollo local
└── README.md               # Esta documentación
```

### 1.2. Implementar Monitorización (Logging) y los Tests 🧪

Para cumplir con el apartado 9 sin romper la app, vamos a hacer dos cosas en la carpeta `backend`: añadir `pytest` a los requerimientos y crear un archivo de pruebas.

#### A) Actualizar `backend/requirements.txt`
Abre ese archivo y añade estas líneas al final para poder usar los tests:

```text
pytest==8.0.0
httpx==0.26.0
```
## 2. Estructura del Backend y Endpoints

El backend expone una API RESTful para gestionar las películas.

- `GET /` - Estado del backend  
- `GET /api/movies` - Listar todas las películas  
- `POST /api/movies` - Añadir una nueva película  
- `PUT /api/movies/{id}` - Actualizar el estado (vista/no vista)  
- `DELETE /api/movies/{id}` - Eliminar una película  
- `GET /docs` - Documentación interactiva (Swagger / OpenAPI) generada automáticamente  

## 3. Estructura del Frontend

### Componentes principales

- **App.vue**: Componente raíz que consume datos del backend y muestra la lista de películas  
- **services/api.ts**: Servicio centralizador para peticiones HTTP con Axios  
- **style.css**: Estilos globales usando Tailwind CSS  

### Consumiendo datos del backend

```ts
// src/services/api.ts
import { apiService } from './services/api'

// En el componente Vue
onMounted(async () => {
  const movies = await apiService.listMovies()
  // Usar los datos de las películas
})
```

Variables de entorno necesarias
```
# Durante desarrollo (local)
VITE_API_URL=http://localhost:8000

# En producción (Vercel)
VITE_API_URL=https://tu-api.onrender.com
```

## 4. Guía de Despliegue (CI/CD)

El objetivo es que cada vez que hagas un git push a la rama main, la aplicación se actualice automáticamente en internet usando GitHub Actions.

### A. Base de Datos MySQL (Railway)

- Crea un proyecto en Railway y añade una base de datos MySQL

- Copia la cadena de conexión de la pestaña Variables (empieza por mysql://)

### B. Despliegue del Backend (Render)

- En Render, crea un nuevo Web Service conectado a tu repositorio

- Configura el Root Directory como ./backend

- Entorno de ejecución: Docker

- Añade la variable de entorno DATABASE_URL y pega la URL de Railway

Para el despliegue automático:

- Copia el Deploy Hook en Render

- Guárdalo en tu GitHub como un Secret llamado 
RENDER_DEPLOY_HOOK

### C. Despliegue del Frontend (Vercel)

- Importa el repositorio en Vercel

- Configura el Root Directory seleccionando la carpeta ./frontend

- Añade la variable de entorno VITE_API_URL apuntando a la URL pública de tu backend en Render

Para el despliegue automático:

- Genera un Token en los ajustes de tu cuenta de Vercel

- Guárdalo en tu GitHub como un Secret llamado VERCEL_TOKEN

## 5. Conceptos clave

**Docker Multi-stage:** Usado en los Dockerfile para compilar la app y luego mover solo lo estrictamente necesario a producción, reduciendo el tamaño y mejorando la seguridad

**CORS (Cross-Origin Resource Sharing):** El backend en FastAPI está configurado para aceptar peticiones de nuestro frontend en Vercel, evitando bloqueos de seguridad del navegador

**GitHub Secrets:** Utilizados para almacenar de forma segura las "llaves" de Render y Vercel, permitiendo a los robots de GitHub hacer los despliegues sin exponer contraseñas en el código público

## 6. Comandos útiles (Desarrollo local)

Si quieres ejecutar el proyecto en tu ordenador con Docker:

### Levantar todos los servicios (Frontend, Backend, DB)

`docker compose up --build`

### Detener todos los servicios

`docker compose down`

### Ver registros (logs) del backend en tiempo real

`docker compose logs -f backend`

## 7. Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.