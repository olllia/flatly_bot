# Flatly Bot (Timeweb Ready)

Telegram-бот для публикации объявлений аренды жилья:
- анкета через FSM;
- предпросмотр и редактирование;
- модерация админом;
- публикация в канал.

## Стек

- Python 3.11
- aiogram 3.x
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic

## Локальный запуск

1. Создай `.env` на основе `.env.example`.
2. Убедись, что PostgreSQL доступен и `DATABASE_URL` корректный.
3. Запусти:

```bash
./run_bot.sh
```

Остановить бота:

```bash
./stop_bot.sh
```

## Docker

Проект можно поднять локально или на VPS через Docker Compose:

1. Создай `.env` на основе `.env.example`.
2. Проверь `BOT_TOKEN`, `ADMIN_ID`, `CHANNEL_ID`, `DRAFT_CHANNEL_ID`, `POSTGRES_*`.
3. Запусти:

```bash
docker compose up -d --build
```

Проверить логи:

```bash
docker compose logs -f bot
```

Остановить:

```bash
docker compose down
```

Данные PostgreSQL хранятся в Docker volume `pg_data`.

## Timeweb деплой (Cloud Apps)

1. Запушь проект в GitHub.
2. В панели Timeweb открой `Cloud Apps` -> `Создать приложение` -> `Из GitHub`.
3. Выбери репозиторий с ботом.
4. В настройках приложения укажи:
   - Build command: `pip install -r requirements.txt`
   - Start command: `alembic upgrade head && python -m app.bot`
5. Создай PostgreSQL в Timeweb Cloud и скопируй строку подключения.
6. В переменные окружения приложения добавь:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `CHANNEL_ID`
   - `DRAFT_CHANNEL_ID`
   - `DATABASE_URL` в формате `postgresql+asyncpg://...`
7. Запусти деплой.

В логах должно быть:
- `Bot started`
- `Start polling`
- `Run polling for bot ...`

Если дали URL с префиксом `postgres://`, замени на `postgresql+asyncpg://`.

## Публикация на GitHub

- Файл `.env` уже в `.gitignore`, в репозиторий не попадет.
- Коммитить нужно `.env.example`, без реальных токенов.
- Если токен уже где-то светился, перевыпусти его через BotFather.
