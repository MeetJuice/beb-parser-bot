import os
import asyncio
from urllib.parse import urljoin

from aiogram import Bot, Dispatcher, executor
from aiogram.utils.executor import start_webhook

from .database import BotDatabase
from .config import DATABASE_URL, BOT_TOKEN, PORT, PROJECT_NAME

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, loop = loop)

dp = Dispatcher(bot)
db = BotDatabase(DATABASE_URL)

def run_heroku():
	WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'  # Enter here your link from Heroku project settings
	WEBHOOK_URL_PATH = '/webhook/' + BOT_TOKEN
	WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

	async def on_startup(app):
		await bot.set_webhook(WEBHOOK_URL)
		
	async def on_shutdown(app):
		await bot.delete_webhook()

	start_webhook(
		dispatcher = dp,
		webhook_path = WEBHOOK_URL_PATH,
		on_startup = on_startup,
		on_shutdown = on_shutdown,
		skip_updates = True,
		host = "0.0.0.0",
		port = PORT,
	)


def run():
	from bot import handlers
	
	if PROJECT_NAME == "__local":
		executor.start_polling(dp, skip_updates = True)
	else:
		run_heroku()