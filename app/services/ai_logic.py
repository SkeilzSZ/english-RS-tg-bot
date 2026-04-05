import whisper
import asyncio
from pydub import AudioSegment
import os
from groq import Groq

# --- БЛОК НАСТРОЙКИ FFMPEG ---
ffmpeg_path = r"C:\Users\serez\Downloads\ffmpeg\ffmpeg\bin" 
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")

whisper_model = whisper.load_model("tiny")

# ==========================================
# 🧠 СИСТЕМА ПАМЯТИ БОТА
# ==========================================
# Словарь для хранения истории диалогов: {user_id: [история сообщений]}
conversation_history = {}

def get_chat_history(user_id: int):
    # Если пользователь пишет впервые, создаем для него скрытую системную инструкцию
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "Ты — профессиональный и современный репетитор по английскому языку. "
                    "Твои СТРОГИЕ правила: "
                    "1. Веди диалог и задавай все встречные вопросы СТРОГО НА АНГЛИЙСКОМ языке, чтобы ученик тренировался, а снизу СТРОГО НА РУССКОМ спрашивай понял ли ученик вопрос или нет, если ученик отвечает на русском, что не понял, переводи вопрос на русский, а если ученик отвечает на английский вопрос на английском, то продолжай диалог дальше."
                    "2. Используй русский язык ТОЛЬКО для объяснения грамматических ошибок или если ученик прямо просит что-то перевести/объяснить на русском. "
                    "3. НИКОГДА не здоровайся повторно и не пиши 'Привет, я твой ИИ-репетитор', если диалог уже начался. "
                    "4. Отвечай прямо на вопрос, коротко и живо. Не лей воду."
                )
            }
        ]
    return conversation_history[user_id]

def add_message(user_id: int, role: str, content: str):
    history = get_chat_history(user_id)
    history.append({"role": role, "content": content})
    # Храним только последние 15 сообщений, чтобы бот не путался
    if len(history) > 15:
        # Оставляем системный промпт (индекс 0) и последние 14 сообщений
        conversation_history[user_id] = [history[0]] + history[-14:]

# ==========================================
# ФУНКЦИЯ 1: ОБРАБОТКА ГОЛОСА
# ==========================================
async def analyze_voice_message(ogg_path: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)

    wav_path = ogg_path.replace(".ogg", ".wav")
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

    result = await asyncio.to_thread(whisper_model.transcribe, wav_path, language="en")
    text = result["text"].strip()

    if os.path.exists(wav_path):
        os.remove(wav_path)

    # Записываем то, что сказал пользователь, в память
    add_message(user_id, "user", f"(Голосовое сообщение) {text}")

    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=get_chat_history(user_id), # Передаем всю историю диалога!
        model="llama-3.3-70b-versatile",
    )
    
    bot_reply = response.choices[0].message.content
    # Записываем ответ бота в память
    add_message(user_id, "assistant", bot_reply)

    return text, bot_reply

# ==========================================
# ФУНКЦИЯ 2: ОБРАБОТКА ТЕКСТА
# ==========================================
async def analyze_text_message(text: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)

    # Записываем текст пользователя в память
    add_message(user_id, "user", text)

    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=get_chat_history(user_id), # Передаем всю историю диалога!
        model="llama-3.3-70b-versatile",
    )
    
    bot_reply = response.choices[0].message.content
    # Записываем ответ бота в память
    add_message(user_id, "assistant", bot_reply)

    return bot_reply