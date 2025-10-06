# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем папки для данных
RUN mkdir -p /app/images /app/labels /app/models /app/inference_image /app/backup

# Указываем порт, который будет использовать приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["echo", "Hello, World!"]