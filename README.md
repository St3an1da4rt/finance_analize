# EvenMonth — учёт финансов по фото чеков и голосовым заметкам

Монорепозиторий из двух частей: бэкенд на FastAPI, который читает данные с фото чеков и голосовых заметок через OpenAI, и iOS-клиент на SwiftUI, который отправляет файлы и показывает список операций.

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
iOS-клиент ──POST /audio ──▶         │
                                     │
                                     └─▶ очередь в памяти ─▶ OpenAI ─▶ category / amount / description
                                            фото  ─▶ vision                  status = done | failed
                                            аудио ─▶ Whisper ─▶ текст ─▶ chat
iOS-клиент ──GET /operations──▶ список операций
```

1. Клиент загружает фото чека на `POST /images` или голосовую заметку на `POST /audio`.
2. Сервер сохраняет файл, создаёт операцию со статусом `pending` и ставит её в очередь.
3. Фоновый воркер обращается к OpenAI, получает структурированный ответ (категория, сумма, описание) и обновляет операцию: `done` или `failed`.
   - **Фото** → одна операция: данные читаются с чека моделью vision.
   - **Аудио** → запись расшифровывается в текст (Whisper), из текста извлекаются траты. Если в заметке названо несколько покупок, первая заполняет исходную операцию, а остальные создаются как отдельные операции по тому же файлу.
4. Клиент читает `GET /operations` (с пагинацией).

Очередь хранится в памяти. При перезапуске сервера все операции со статусом `pending` ставятся в очередь заново.

Категории: `transfer`, `salary`, `groceries`, `restaurants`, `transport`, `housing`, `utilities`, `health`, `entertainment`, `shopping`, `travel`, `education`, `subscriptions`.

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

## Дизайн

Макеты интерфейса — в [Figma](https://www.figma.com/design/m80Tn4xCPwAcIc9EFaFXlc/%D1%85%D0%B0%D0%BA%D1%82%D0%BE%D0%BD-%D0%BB%D0%BE%D0%BB?node-id=0-1).

## Разработка со спецификациями

Изменения API описываются через [OpenSpec](https://github.com/Fission-AI/OpenSpec): см. `backend/openspec/`. В Claude Code доступны команды `/opsx:propose`, `/opsx:apply`, `/opsx:explore`, `/opsx:archive`, `/opsx:sync`, `/opsx:update`.

## Лицензия

См. [backend/LICENSE](backend/LICENSE).
