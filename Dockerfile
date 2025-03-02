# Dockerfile (розташувати в корені проекту)
FROM python:3.12-slim

# Встановлюємо Poetry
RUN pip install --no-cache-dir poetry

# Встановлюємо робочу директорію (буде перезаписуватися для різних сервісів у docker-compose)
WORKDIR /app

# Копіюємо файли залежностей
COPY pyproject.toml poetry.lock ./

# Встановлюємо залежності через Poetry (без dev, якщо потрібні лише продакшн залежності)
RUN poetry install --no-root

# Копіюємо весь код у контейнер
COPY . .

# За замовчуванням запускаємо тести (цей CMD можна перевизначати через docker-compose)
CMD ["poetry", "run", "pytest", "testing/test_name.py"]
