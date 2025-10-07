# Используем официальный образ Python 3.9 на базе Debian Bullseye
FROM python:3.9-slim-bullseye

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 && \
    rm -rf /var/lib/pt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копируем только файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем папки для данных
RUN mkdir -p /app/images /app/labels /app/models /app/inference_image /app/backup

# Указываем порт, который будет использовать приложение
EXPOSE 8000

# Устанавливаем переменную окружения для mode production
ENV PYTHONUNBUFFERED=1

# Команда для запуска приложения
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]