from groq import Groq # Используем Groq вместо OpenAI
import asyncio
import os

# Удаляем жесткий путь C:\Users..., на сервере он не нужен
# На Railway мы просто добавим ffmpeg в переменные или билд

# ==========================================
# 🧠 СИСТЕМА ПАМЯТИ БОТА (ТВОЯ ЛОГИКА)
# ==========================================
conversation_history = {}

def get_chat_history(user_id: int):
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
    if len(history) > 15:
        conversation_history[user_id] = [history[0]] + history[-14:]

# ==========================================
# ФУНКЦИИ ОБРАБОТКИ (ТВОЯ СТРУКТУРА)
# ==========================================
async def analyze_voice_message(ogg_path: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key) # Меняем только клиента

    # Распознаем через Groq (быстрее и не требует Whisper на сервере)
    with open(ogg_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(ogg_path, file.read()),
            model="whisper-large-v3",
            language="en"
        )
    text = transcription.text.strip()

    add_message(user_id, "user", f"(Голосовое сообщение) {text}")

    response = client.chat.completions.create(
        messages=get_chat_history(user_id),
        model="llama-3.3-70b-versatile", # Мощная модель от Groq
    )
    
    bot_reply = response.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)
    return text, bot_reply

async def analyze_text_message(text: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)
    add_message(user_id, "user", text)

    response = client.chat.completions.create(
        messages=get_chat_history(user_id),
        model="llama-3.3-70b-versatile",
    )
    
    bot_reply = response.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)
    return bot_reply