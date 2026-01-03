# Многостадийный Dockerfile для Review Generator Web

# Стадия 1: Сборка React фронтенда
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY web/frontend/package*.json ./
RUN npm install
COPY web/frontend/ ./
RUN npm run build

# Стадия 2: Backend с Python
FROM python:3.10-slim AS backend
WORKDIR /app

# Устанавливаем зависимости Python
COPY web/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ядро (бизнес-логику) и веб-часть
COPY core/ ./core/
COPY config/ ./config/
COPY web/backend/ ./web/backend/

# Копируем собранный фронтенд
COPY --from=frontend-builder /app/frontend/build ./web/frontend/static

# Устанавливаем переменную окружения для импорта core
ENV PYTHONPATH=/app

# Открываем порт
EXPOSE 8080

# Команда для запуска сервера
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
