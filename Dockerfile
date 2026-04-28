# Берем готовую основу: linux и Python
FROM python:3.12-slim

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* 

# Задаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем requirements.txt отдельно, чтобы Docker мог кэшировать установку зависимостей
COPY requirements.txt .

# Устанавливаем зависимости без создания лишнего кэша
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Команда по умолчанию при запуске контейнера
CMD ["pytest", "-v"]