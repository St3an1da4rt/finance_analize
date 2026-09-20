# EvenMonth — учёт финансов по фото чеков

Монорепозиторий из двух частей: бэкенд на FastAPI, который читает данные с фото чеков через OpenAI, и iOS-клиент на SwiftUI, который отправляет фото и показывает список операций.

```
.
├── backend/      # FastAPI + SQLAlchemy + OpenAI (см. backend/README.md)
├── ios-client/   # Xcode-проект EvenMonth (SwiftUI)
├── .env.example  # пример переменных окружения
└── .claude/      # команды и навыки OpenSpec для Claude Code
```

## Как это работает

```
iOS-клиент ──POST /images──▶ FastAPI ──▶ файл в uploads/ + запись Operation (status=pending)
                                │
                                └─▶ очередь в памяти ─▶ OpenAI (vision) ─▶ category / amount / description
                                                                          status = done | failed
iOS-клиент ──GET /operations──▶ список операций
```

1. Клиент загружает фото чека на `POST /images`.
2. Сервер сохраняет файл, создаёт операцию со статусом `pending` и ставит её в очередь.
3. Фоновый воркер отправляет изображение в OpenAI, получает структурированный ответ (категория, сумма, описание) и обновляет операцию: `done` или `failed`.
4. Клиент читает `GET /operations` (с пагинацией).

Очередь хранится в памяти. При перезапуске сервера все операции-изображения со статусом `pending` ставятся в очередь заново.

Категории: `transfer`, `salary`, `groceries`, `restaurants`, `transport`, `housing`, `utilities`, `health`, `entertainment`, `shopping`, `travel`, `education`, `subscriptions`.

> Загрузка аудио (`POST /audio`) уже принимает и сохраняет файлы, но распознавание голоса пока не реализовано — такие операции остаются в статусе `pending`.

## Бэкенд

Подробности — в [backend/README.md](backend/README.md). Быстрый старт:

```bash
cp .env.example backend/.env      # укажите OPENAI_TOKEN
cd backend
docker compose up --build         # PostgreSQL 16 + приложение на :8000
```

Документация API: http://localhost:8000/docs

| Метод | Путь          | Описание                                              |
|-------|---------------|-------------------------------------------------------|
| POST  | `/images`     | Фото чека (jpeg, png, webp, до 10 МБ)                 |
| POST  | `/audio`      | Аудио (ogg, mp3, m4a, wav, до 25 МБ)                  |
| GET   | `/operations` | Список операций (`limit` 1–100, `offset`)             |

Тесты:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## iOS-клиент

Проект: `ios-client/EvenMonth/EvenMonth.xcodeproj`. Требуются Xcode с поддержкой iOS 26 (deployment target 26.0).

Экраны: инструкция при первом запуске, добавление операции (отправка фото), аналитика (список операций). Архитектура — SwiftUI + ViewModel'ы (`Presentation/View`, `Presentation/ViewModel`), состояние приложения в `App/AppState.swift`.

**Адрес сервера сейчас зашит в коде** (ngrok-URL) в `AddOperationViewModel.swift` и `AnalyticsViewModel.swift`. Чтобы работать со своим бэкендом, замените его на свой адрес — например, на туннель ngrok к `localhost:8000` или на IP машины в локальной сети.

## Разработка со спецификациями

Изменения API описываются через [OpenSpec](https://github.com/Fission-AI/OpenSpec): см. `backend/openspec/`. В Claude Code доступны команды `/opsx:propose`, `/opsx:apply`, `/opsx:explore`, `/opsx:archive`, `/opsx:sync`, `/opsx:update`.

## Лицензия

См. [backend/LICENSE](backend/LICENSE).
