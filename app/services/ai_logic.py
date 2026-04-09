from groq import Groq
import asyncio
import os

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

async def analyze_voice_message(ogg_path: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)
    
    # Распознавание через API Groq
    with open(ogg_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(ogg_path, file.read()),
            model="whisper-large-v3",
            language="en"
        )
    text = transcription.text.strip()
    add_message(user_id, "user", f"(Голосовое) {text}")

    # Ответ модели
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=get_chat_history(user_id)
    )
    bot_reply = completion.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)
    return text, bot_reply

async def analyze_text_message(text: str, api_key: str, user_id: int):
    client = Groq(api_key=api_key)
    add_message(user_id, "user", text)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=get_chat_history(user_id)
    )
    bot_reply = completion.choices[0].message.content
    add_message(user_id, "assistant", bot_reply)
    return bot_reply