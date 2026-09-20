# Finance Tracker — backend

FastAPI-сервис для учёта финансовых операций. Принимает фото чеков и голосовые сообщения, извлекает из них данные через OpenAI и сохраняет операции в базу данных.

## API

| Метод | Путь          | Описание                                              |
|-------|---------------|-------------------------------------------------------|
| POST  | `/images`     | Загрузка изображения чека (jpeg, png, webp, до 10 МБ) |
| POST  | `/audio`      | Загрузка аудио (ogg, mp3, m4a, wav, до 25 МБ)         |
| GET   | `/operations` | Список операций (`limit` 1–100, `offset`)             |

Интерактивная документация: http://localhost:8000/docs

## Требования

- Docker и Docker Compose **или** Python 3.12
- Ключ OpenAI API

## Настройка

Файл `.env.example` лежит в корне репозитория. Скопируйте его в `backend/.env` и заполните:

```bash
cp ../.env.example .env
```

```env
OPENAI_TOKEN=sk-your-openai-api-key
POSTGRES_USER=finance
POSTGRES_PASSWORD=change-me
POSTGRES_DB=finance
```

Дополнительные переменные (необязательные):

| Переменная       | По умолчанию              | Описание                    |
|------------------|---------------------------|-----------------------------|
| `DATABASE_URL`   | `sqlite:///./finance.db`  | Строка подключения к БД     |
| `UPLOAD_DIR`     | `uploads`                 | Папка для загруженных файлов |
| `OPENAI_MODEL`   | `gpt-4o-mini`             | Модель OpenAI               |
| `MAX_IMAGE_SIZE` | `10485760`                | Макс. размер изображения, байт |
| `MAX_AUDIO_SIZE` | `26214400`                | Макс. размер аудио, байт    |

## Запуск через Docker (рекомендуется)

Из папки `backend`:

```bash
docker compose up --build
```

Поднимутся PostgreSQL 16 и приложение. Сервер доступен на http://localhost:8000. Таблицы создаются автоматически при старте.

Остановить:

```bash
docker compose down        # данные сохраняются в volume
docker compose down -v     # вместе с данными
```

## Локальный запуск без Docker

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt "uvicorn[standard]"

export OPENAI_TOKEN=sk-your-openai-api-key
uvicorn app.main:app --reload --port 8000
```

По умолчанию используется SQLite (`finance.db` в текущей папке). Чтобы работать с PostgreSQL из compose, задайте:

```bash
export DATABASE_URL=postgresql+psycopg://finance:change-me@localhost:5432/finance
```

и запустите только БД: `docker compose up db`.

## Тесты

```bash
pytest
```

## Проверка

```bash
curl http://localhost:8000/operations
curl -F "file=@receipt.jpg" http://localhost:8000/images
```
