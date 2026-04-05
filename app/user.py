from aiogram.filters import CommandStart
from aiogram import F, types, Router, Bot
import os
import config

from app.services.ai_logic import analyze_voice_message, analyze_text_message

user = Router()

@user.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я твой ИИ-учитель английского.\n"
        "🎙️ Пришли мне голосовое на английском — я проверю произношение.\n"
        "✍️ Напиши текст — я проверю грамматику или проведу урок!"
    )

@user.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot):
    status = await message.answer("👂 Слушаю и думаю...")

    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_on_disk = f"{file_id}.ogg"
    await bot.download_file(file.file_path, file_on_disk)

    try:
        # Передаем ID пользователя, чтобы бот вспомнил историю
        recognized_text, bot_reply = await analyze_voice_message(file_on_disk, config.GROQ_KEY, message.from_user.id)
        ai_response = f"✅ Я услышал:\n{recognized_text}\n\n👩‍🏫 Ответ:\n{bot_reply}"
        await status.edit_text(ai_response)
    except Exception as e:
        await status.edit_text("Ой, не смог расшифровать звук или связаться с ИИ.")
        print(f"Voice Error: {e}")
        
    if os.path.exists(file_on_disk):
        os.remove(file_on_disk)


@user.message(F.text)
async def handle_text(message: types.Message):
    status = await message.answer("👩‍🏫 Читаю и думаю...")
    
    try:
        # Передаем ID пользователя
        ai_response = await analyze_text_message(message.text, config.GROQ_KEY, message.from_user.id)
        await status.edit_text(ai_response)
    except Exception as e:
        await status.edit_text("Ой, я немного задумался... Попробуй написать еще раз!")
        print(f"Text Error: {e}")