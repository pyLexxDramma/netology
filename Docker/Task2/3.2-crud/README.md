# Django REST API Docker

## Запуск контейнера

1.  **Сборка Docker image:**

    ```bash
    docker build -t my-django-api .
    ```

2.  **Запуск контейнера:**

    ```bash
    docker run -d -p 8000:8000 -e SECRET_KEY=<your_secret_key> -e DEBUG=True -e ALLOWED_HOSTS=* my-django-api
    ```

    Замени `<your_secret_key>` на твой сгенерированный секретный ключ.  Также замени `ALLOWED_HOSTS=*` на список разрешенных хостов, если это необходимо для продакшена.

    **ИЛИ (лучше):**  Используй `.env` файл с `docker-compose.yml` (см. ниже)

## Отправка запросов

Используйте VS Code REST Client или Postman для отправки запросов к API по адресу `http://localhost:8000`.  Например:

*   `GET http://localhost:8000/api/ складов/`
*   `POST http://localhost:8000/api/ склады/`
