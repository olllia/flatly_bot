# Flatly Bot (Fly.io Ready)

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

## Fly.io деплой

1. Установи Fly CLI и залогинься:

```bash
fly auth login
```

2. (Опционально) измени имя приложения в `fly.toml` (`app = "flatly-bot"`), если имя занято.
3. Создай приложение:

```bash
fly apps create <your-app-name>
```

4. Создай Postgres на Fly:

```bash
fly postgres create --name <your-pg-name> --region waw
fly postgres attach --app <your-app-name> <your-pg-name>
```

5. Добавь секреты:

```bash
fly secrets set BOT_TOKEN=... ADMIN_ID=381232429 CHANNEL_ID=-1003983913190
```

6. Проверь `DATABASE_URL` в secrets и приведи к формату `postgresql+asyncpg://...`:
   - если в секрете `postgres://...`, замени префикс:

```bash
fly secrets set DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME
```

7. Запусти деплой:

```bash
fly deploy
```

8. Логи:

```bash
fly logs
```

В логах должно быть:
- `Bot started`
- `Start polling`
- `Run polling for bot ...`

## Публикация на GitHub

- Файл `.env` уже в `.gitignore`, в репозиторий не попадет.
- Коммитить нужно `.env.example`, без реальных токенов.
- Если токен уже где-то светился, перевыпусти его через BotFather.
