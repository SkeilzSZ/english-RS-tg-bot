import os

# Берем токен из переменных окружения Railway
TOKEN = os.getenv('TOKEN')

# Берем ключ Groq из переменных окружения Railway
GROQ_KEY = os.getenv('GROQ_KEY')

# Настройка базы данных
DB_URL = os.getenv('DB_URL', 'sqlite+aiosqlite:///db.sqlite3')