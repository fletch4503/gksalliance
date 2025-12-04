# Команды, используемые в проекте

<a name="top"></a>

<!-- TOC -->
* [Команды, используемые в проекте](#команды-используемые-в-проекте)
  * [Работа с UV-окружением](#работа-с-uv-окружением)
  * [Работа с Docker и Docker-Compose](#работа-с-docker-и-docker-compose)
  * [Работа с БД PostgreSQL (через Docker)](#работа-с-бд-postgresql-через-docker)
<!-- TOC --> 

## Работа с UV-окружением

1. Установите UV (если не установлен):

    ```bash
    pip install uv
    ```

2. Синхронизируйте зависимости:

   ```bash
   uv sync
   ```

3. Активируйте виртуальное окружение (опционально, если вы планируете запускать команды вручную):

    - На Windows:

   ```bash
   .venv\Scripts\activate
   ```

4. Настройте переменные окружения (создайте `.env`):

   ```bash
   DJANGO_SETTINGS_MODULE=macroemc_wmp.settings
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=macrogroup
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://localhost:6379/0
   ```

5. Примените миграции:

   ```bash
   uv run python manage.py migrate
   ```

6. Создайте суперпользователя:

   ```bash
   uv run python manage.py createsuperuser
   ```

## Работа с Docker и Docker-Compose

[↑](#top)

1. Удаление ненужных образов Docker

```bash
docker image rm $(docker image ls -f dangling=true -q)
```

2. Запустите контейнеры в docker desktop

   ```bash
   docker-compose up --build -d
   ```

3. Остановить контейнеры в docker

   ```bash
   docker-compose stop
   ```

4. Остановить и удалить контейнеры

   ```bash
   docker-compose down -v
   ```

## Работа с БД PostgreSQL (через Docker)

1. Применение миграций внутри контейнера

   ```bash
   docker-compose exec web uv run python manage.py migrate
   ```