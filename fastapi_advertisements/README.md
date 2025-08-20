## Задание

Вам нужно написать на FastAPI и докеризировать сервис объявлений купли/продажи.

У объявлений должны быть следующие поля:

*   заголовок
*   описание
*   цена
*   автор
*   дата создания

Должны быть реализованы следующие методы:

*   **Создание:** `POST /advertisement`
*   **Обновление:** `PATCH /advertisement/{advertisement_id}`
*   **Удаление:** `DELETE /advertisement/{advertisement_id}`
*   **Получение по id:** `GET /advertisement/{advertisement_id}`
*   **Поиск по полям:** `GET /advertisement?{query_string}`

Авторизацию и аутентификацию реализовывать не нужно.