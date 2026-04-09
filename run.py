import sys
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

# Трюк для Python 3.14
try:
    import audioop
except ImportError:
    try:
        import audioop_lts
        sys.modules["audioop"] = audioop_lts
    except ImportError:
        pass

from app.user import user
from app.admin import admin
from app.database.models import async_main

# --- ПОЛУЧЕНИЕ ТОКЕНА ---
try:
    import config
    CONFIG_TOKEN = getattr(config, 'TOKEN', None)
except ImportError:
    CONFIG_TOKEN = None

TOKEN = os.getenv('TOKEN') or CONFIG_TOKEN
# ------------------------

async def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Токен не найден! Проверь Variables в Railway.")
        return

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    commands = [
        BotCommand(command="start", description="Запустить бота / Главное меню"),
        BotCommand(command="lesson", description="Получить новый урок"),
        BotCommand(command="test", description="Мини-тест по английскому"),
        BotCommand(command="help", description="Как пользоваться учителем"),
        BotCommand(command="topic", description="Сменить тему общения")
    ]
    await bot.set_my_commands(commands)
    
    dp = Dispatcher()
    dp.include_routers(user, admin)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    
    await dp.start_polling(bot)

async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Бот запущен...')

async def shutdown(dispatcher: Dispatcher):
    print('Бот остановлен...')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass