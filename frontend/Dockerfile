# Dockerfile multi-stage para Vue.js + Vite

# Fase 1: Build
FROM node:20-slim AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci || npm install

# Copiar el resto de archivos
COPY . .

# Compilar la aplicación
RUN npm run build

# Fase 2: Servidor de producción
FROM node:20-slim AS runner

WORKDIR /app

# Instalar serve para servir la aplicación
RUN npm install -g serve

# Copiar la carpeta dist de la fase anterior
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# Comando para iniciar la aplicación
CMD ["serve", "-s", "dist", "-l", "3000"]

# Fase 3: Desarrollo
FROM node:20-slim AS development

WORKDIR /app

# Copiar package.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

EXPOSE 3000

# Comando para iniciar la aplicación en desarrollo
CMD ["npm", "run", "dev"]
