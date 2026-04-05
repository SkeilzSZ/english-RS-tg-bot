import sys

# Трюк для Python 3.14: подменяем отсутствующий audioop на установленный lts
try:
    import audioop
except ImportError:
    try:
        import audioop_lts
        sys.modules["audioop"] = audioop_lts
        print("🔧 Исправление для Python 3.14 применено: audioop заменен на audioop_lts")
    except ImportError:
        print("❌ Ошибка: пакет audioop-lts не найден. Установи его через 'pip install audioop-lts'")
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.user import user
from app.admin import admin

from config import TOKEN

from app.database.models import async_main
from aiogram.types import BotCommand


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # --- НАСТРОЙКА МЕНЮ ---
    commands = [
        BotCommand(command="start", description="Запустить бота / Главное меню"),
        BotCommand(command="lesson", description="Получить новый урок"),
        BotCommand(command="test", description="Мини-тест по английскому"),
        BotCommand(command="help", description="Как пользоваться учителем"),
        BotCommand(command="topic", description="Сменить тему общения")
    ]
    await bot.set_my_commands(commands)
    # ----------------------
    
    dp = Dispatcher()
    dp.include_routers(user, admin)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    
    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    