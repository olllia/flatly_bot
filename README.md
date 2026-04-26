# Flatly Bot (Railway Ready)

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

## Railway деплой

1. Создай GitHub-репозиторий и запушь проект.
2. В Railway создай проект `Deploy from GitHub Repo`.
3. Добавь PostgreSQL плагин в Railway.
4. В Variables у сервиса бота задай:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `CHANNEL_ID`
   - `DATABASE_URL` (в формате `postgresql+asyncpg://...`)
5. Railway использует `railway.json`/`Procfile` и запустит:
   - `alembic upgrade head && python -m app.bot`

## Публикация на GitHub

- Файл `.env` уже в `.gitignore`, в репозиторий не попадет.
- Коммитить нужно `.env.example`, без реальных токенов.
- Если токен уже где-то светился, перевыпусти его через BotFather.
