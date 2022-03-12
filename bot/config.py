import os

PORT = os.getenv("PORT", 3001)
BOT_TOKEN = os.getenv("TOKEN", "token_here")
PROJECT_NAME = os.getenv("PROJECT_NAME", "__local")
DATABASE_URL = os.getenv("REDIS_URL", "redis://127.0.0.1")

URL_SPLITTER = "~~~~"