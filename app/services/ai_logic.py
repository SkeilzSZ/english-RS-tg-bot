import asyncio
import os
from groq import Groq

# ==========================================
# 🧠 СИСТЕМА ПАМЯТИ БОТА
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
                    "1. Веди диалог и задавай все встречные вопросы СТРОГО НА АНГЛИЙСКОМ языке. "
                    "Снизу СТРОГО НА РУССКОМ спрашивай, понял ли ученик вопрос. "
                    "2. Используй русский язык ТОЛЬКО для объяснения грамматических ошибок. "
                    "3. НИКОГДА не здоровайся повторно. "
                    "4. Отвечай прямо, коротко и живо."
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
# ФУНКЦИЯ 1: ОБРАБОТКА ГОЛОСА (ЧЕРЕЗ GROQ API)
# ==========================================
async def analyze_voice_message(ogg_path: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)

    # 1. Транскрибация голоса через API Groq (модель Whisper-large)
    with open(ogg_path, "rb") as file:
        transcription = await asyncio.to_thread(
            client.audio.transcriptions.create,
            file=(ogg_path, file.read()),
            model="whisper-large-v3",
            language="en"
        )
    
    text = transcription.text.strip()
    add_message(user_id, "user", f"(Voice) {text}")

    # 2. Получение ответа от языковой модели
    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=get_chat_history(user_id),
        model="llama-3.3-70b-versatile",
    )
    
    bot_reply = response.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)

    return text, bot_reply

# ==========================================
# ФУНКЦИЯ 2: ОБРАБОТКА ТЕКСТА
# ==========================================
async def analyze_text_message(text: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)
    add_message(user_id, "user", text)

    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=get_chat_history(user_id),
        model="llama-3.3-70b-versatile",
    )
    
    bot_reply = response.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)

    return bot_reply