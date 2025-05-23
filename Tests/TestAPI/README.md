# Тестирование API Яндекс.Диска

## 1. Позитивный тест: `test_create_folder_success`

**Цель:** Проверить успешное создание папки с использованием корректных параметров.

**Что проверяется:**
- Код ответа API равен 201 (Created). Это означает, что запрос на создание папки был успешно обработан.
- Папка действительно создана на Диске. Мы проверяем это, вызывая другой API-метод, чтобы убедиться, что папка существует.

## 2. Негативный тест: `test_create_folder_already_exists`

**Цель:** Проверить, что происходит при попытке создать папку с именем, которое уже существует.

**Что проверяется:**
- Код ответа API равен 409 (Conflict). Это означает, что ресурс (в данном случае папка) с указанным именем уже существует, и API не позволяет создать дубликат.

## 3. Негативный тест: `test_create_folder_invalid_token`

**Цель:** Проверить, что происходит при попытке создать папку с использованием недействительного токена авторизации.

**Что проверяется:**
- Код ответа API равен 401 (Unauthorized). Это означает, что запрос не был авторизован, и API отклонил его.

## 4. Негативный тест: `test_create_folder_invalid_path`

**Цель:** Проверить, что происходит при попытке создать папку с использованием некорректного пути.

**Что проверяется:**
- Код ответа API находится в диапазоне 400-599. Это означает, что API вернул какой-либо код ошибки, указывающий на то, что запрос был неверным (например, из-за недопустимых символов в пути, слишком длинного пути и т.д.). Мы не проверяем конкретный код ошибки, потому что API может возвращать разные коды в зависимости от типа некорректности пути.

## Вспомогательные функции:

- **`create_folder(path)`**: Отправляет PUT-запрос к API для создания папки по указанному пути.
- **`check_folder_exists(path)`**: Отправляет GET-запрос к API, чтобы проверить, существует ли папка по указанному пути.
- **`delete_folder(path)`**: Отправляет DELETE-запрос к API, чтобы удалить папку по указанному пути.

## Общий принцип тестирования:

Я использовал библиотеку `unittest` для организации тестов. Каждый тест - это отдельный метод в классе `TestYandexDiskAPI`. В методах `setUp` и `tearDown` подготовительные и завершающие действия (создание и удаление тестовой папки), чтобы обеспечить изоляцию тестов друг от друга.

## Что было улучшено в процессе:

- **Обработка ошибок:** Добавлены негативные тесты для проверки обработки ошибок API.
- **Изоляция тестов:** Тесты стали более независимыми друг от друга.
- **Информативные сообщения об ошибках:** В сообщения об ошибках включен текст ответа API, что упрощает отладку.
- **Гибкость теста `test_create_folder_invalid_path`:** Изменен тест `test_create_folder_invalid_path`, чтобы он был более устойчивым к изменениям в API. Вместо проверки конкретного кода ошибки, проверяется, что API вернул какой-либо код ошибки.
