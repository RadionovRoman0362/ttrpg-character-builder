# Использовать официальный образ Python 3.11
FROM python:3.11-slim

# Отключить создание .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установить рабочую директорию внутри контейнера
WORKDIR /app

# Скопировать файл с зависимостями и установить их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать весь остальной код проекта в рабочую директорию
# Этот шаг выполняется после установки зависимостей для кэширования Docker
COPY . /app/