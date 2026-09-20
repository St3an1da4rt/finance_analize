## 1. Setup

- [x] 1.1 Добавить `python-multipart` в `requirements.txt`
- [x] 1.2 Добавить в `app/config` настройки: `DATABASE_URL`, `UPLOAD_DIR`, лимиты размера изображения и аудио
- [x] 1.3 Настроить engine/session и зависимость `get_db` в `app/database`, создание таблиц при старте

## 2. Модель и схемы

- [x] 2.1 Добавить enum `Category` и `OperationStatus` и модель `Operation` (id, category, status, file_path, source, created_at) в `app/models`
- [x] 2.2 Добавить Pydantic-схемы `OperationOut` и `OperationsPage` в `app/schemas`

## 3. Загрузка файлов

- [x] 3.1 Реализовать сервис сохранения файла (UUID-имя, чтение чанками, контроль размера, удаление при ошибке)
- [x] 3.2 Реализовать `POST /images` в `app/routes` с проверкой типа (415) и размера (413)
- [x] 3.3 Реализовать `POST /audio` в `app/routes` с проверкой типа (415) и размера (413)

## 4. Список операций

- [x] 4.1 Реализовать `GET /operations` с `limit`/`offset`, сортировкой и `total`

## 5. Интеграция и тесты

- [x] 5.1 Подключить роутеры в `app/main.py`
- [x] 5.2 Тесты на `POST /images` (успех, тип, размер, нет файла)
- [x] 5.3 Тесты на `POST /audio` (успех, тип, размер, нет файла)
- [x] 5.4 Тесты на `GET /operations` (страницы, пустой список, невалидные параметры, category)
