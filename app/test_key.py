import os
from groq import Groq

# ВСТАВЬ СЮДА СВОЙ НОВЫЙ КЛЮЧ
TEST_KEY = "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"

try:
    client = Groq(api_key=TEST_KEY)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ КЛЮЧ РАБОТАЕТ! Ответ от ИИ получен.")
except Exception as e:
    print(f"❌ ОШИБКА: {e}")