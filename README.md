# Flatly Bot (Render Ready)

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

## Render деплой

1. Создай GitHub-репозиторий и запушь проект.
2. В Render нажми `New +` -> `Background Worker`.
3. Подключи GitHub-репозиторий.
4. Render подхватит `render.yaml` и создаст worker со стартом:
   - `alembic upgrade head && python -m app.bot`
5. Создай PostgreSQL в Render (`New +` -> `PostgreSQL`) и скопируй `External Database URL`.
6. В Variables у воркера задай:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `CHANNEL_ID`
   - `DATABASE_URL` в формате `postgresql+asyncpg://...`
     (если Render дал `postgres://...`, замени префикс на `postgresql+asyncpg://`)
7. Нажми `Manual Deploy` -> `Deploy latest commit`.

## Публикация на GitHub

- Файл `.env` уже в `.gitignore`, в репозиторий не попадет.
- Коммитить нужно `.env.example`, без реальных токенов.
- Если токен уже где-то светился, перевыпусти его через BotFather.
