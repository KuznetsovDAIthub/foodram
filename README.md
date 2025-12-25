# Foodgram
Foodgram — это веб-приложение для публикации и управления рецептами. В этом проекте реализованы возможности публикации рецептов, подписки на авторов и создания списков покупок.

## Стек технологий

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

## Содержание

- [Описание проекта](#описание-проекта)
- [Установка и настройка](#установка-и-настройка)
- [Автоматизация и развертывание](#автоматизация-и-развертывание)
- [Работа с проектом](#работа-с-проектом)
- [API Endpoints](#api-endpoints)
- [Автор](#автор)

## Описание проекта

Проект включает следующие компоненты:
- **Backend**: Разработан на Django и использует PostgreSQL для хранения данных.
- **Frontend**: SPA-приложение на React, предоставляет пользовательский интерфейс.
- **Gateway**: Nginx используется для проксирования запросов между клиентом и сервером.
- **Docker**: Используется для контейнеризации всех компонентов приложения.

## Установка и настройка

1. **Клонируйте репозиторий:**
   ```bash

   cd foodgram
   ```

2. **Настройте переменные окружения:**
   Создайте файл `.env` в директории `infra/` и добавьте следующие настройки:
   ```env
   DEBUG=False
   SECRET_KEY=your-secret-key
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Запустите Docker Compose:**
   ```bash
   cd infra
   docker compose up -d
   ```

4. **Примените миграции:**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Создайте суперпользователя:**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Соберите статические файлы:**
   ```bash
   docker compose exec backend python manage.py collectstatic --no-input
   ```

## Автоматизация и развертывание

Проект настроен для автоматического развертывания с помощью GitHub Actions:
- Сборка Docker образов и отправка их на Docker Hub
- Обновление образов на сервере и перезапуск приложения
- Сборка статики и выполнение миграций
- Уведомления о завершении деплоя в Telegram

## Работа с проектом

1. **Переход к интерфейсу приложения:**
   После запуска контейнеров, приложение доступно по [http://localhost:8080](http://localhost:8080)

2. **Обновление статики:**
   ```bash
   docker compose exec backend python manage.py collectstatic --no-input
   ```

3. **Миграции:**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

## API Endpoints

- `/api/users/` - регистрация и управление пользователями
- `/api/auth/token/login/` - получение токена авторизации
- `/api/recipes/` - управление рецептами
- `/api/tags/` - получение списка тегов
- `/api/ingredients/` - получение списка ингредиентов
- `/api/users/{id}/subscribe/` - подписка на пользователя
- `/api/recipes/{id}/favorite/` - добавление рецепта в избранное
- `/api/recipes/{id}/shopping_cart/` - добавление рецепта в список покупок
- `/api/recipes/download_shopping_cart/` - скачивание списка покупок

