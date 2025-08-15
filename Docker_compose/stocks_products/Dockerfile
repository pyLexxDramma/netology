FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Применяем миграции
# RUN python manage.py migrate

# Указываем порт, который будет использовать приложение
EXPOSE 5000

# Команда для запуска сервера
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "stocks_ptoducts.wsgi"]
