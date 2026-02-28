# Dockerfile multi-stage

# Fase 1: Build (no es estrictamente necesario para Python pero bueno para el orden)
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias de compilación si fueran necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Fase 2: Final
FROM python:3.11-slim

WORKDIR /app

# Copiar solo lo necesario de la fase anterior
COPY --from=builder /root/.local /root/.local
COPY . .

# Asegurar que el PATH incluya los binarios instalados
ENV PATH=/root/.local/bin:$PATH

# Render usa la variable PORT por defecto
ENV PORT=8000
EXPOSE $PORT

# Comando para ejecutar FastAPI
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
