from io import StringIO
from datetime import datetime
from urllib.parse import urlparse

import requests

from aiogram import types
from aiogram.dispatcher.filters import CommandHelp, CommandStart, Text

from .. import dp, bot, db
from ..config import URL_SPLITTER

from ..util import open_recursive
from ..util.telegram import answer_parsed, build_menu


@dp.message_handler(CommandStart())
async def user_start(msg):
	url = msg.get_args()

	if url:
		req = requests.get(url)
		await answer_parsed(msg, req.content)
	else:
		await msg.answer(
			"""Добро пожаловать!
			Загрузите файл (.html) для начала работы
			Или воспользуйтесь командой /start <URL>
			/help - команды
			""")


@dp.message_handler(CommandHelp())
async def user_start(msg):
	await msg.answer(
	"""📜 *Список команд*
	/start *<URL>* - парсит HTML с указанного сайта
	/blacklist - открывает черный список ссылок
	/blacklist_add - добавляет ссылку в черный список
	/blacklist_remove - удаляет ссылку из черного списка
	/replace_url *<URL>* *<URL>* - заменяет одну ссылку на другую в HTML
	/download_file - скачивает выходной файл

	При загрузке *.html* файла бот начинает работать
	*<URL>* необходимо указывать в формате *http(s)://...*
	""", parse_mode = "markdown"
	)


@dp.message_handler(content_types = types.message.ContentType.DOCUMENT)
async def func(msg):
	doc = msg.document

	if doc.file_name.endswith(".html"):
		file = await bot.get_file(doc.file_id)
		text = await bot.download_file(file.file_path)

		await answer_parsed(msg, str(text.getvalue()))
	else:
		await msg.answer("Необходимо загрузить файл с расширением *.html*", parse_mode = "markdown")


@dp.message_handler(commands = ["blacklist"])
async def open_blacklist(msg):
	blacklist = await db.get_blacklist(msg.chat.id)
	menu = build_menu("blacklist", 0, "❌ Запрещенные ссылки ❌", list(blacklist))

	await msg.answer(**menu, parse_mode = "markdown")


@dp.message_handler(commands = ["blacklist_add", "blacklist_remove"])
async def add_rem_url(msg):
	urls = msg.get_args().split(" ")
	_id = msg.chat.id

	parsed_url = urlparse(urls[0])

	if not parsed_url.scheme or not parsed_url.netloc:
		await msg.answer("Ошибка. Необходимо указать ссылку в аргументе ❌")
		return

	if "add" in msg.text:
		added = await db.add_black_url(_id, urls[0])
		await msg.answer(
			added != 1 and "Не удалось добавить ссылку в черный список ❌" or "Ссылка добавлена в черный список ✅"
		)
	else:
		removed = await db.rem_black_url(_id, urls[0])
		await msg.answer(
			removed != 1 and "Не удалось удалить ссылку из черного списка (ссылка не найдена) ❌" or "Ссылка удалена из черного списка ✅"
		)


@dp.message_handler(commands = ["replace_url"])
async def replace_url(msg):
	urls = msg.get_args().split(" ")
	_id = msg.chat.id

	parsed_url = urlparse(urls[0])

	if len(urls) < 2 or not parsed_url.scheme or not parsed_url.netloc:
		await msg.answer("Ошибка ❌\n Формат команды /replace_url <url1> <url2>")
		return

	try:
		with open_recursive(f"userdata/d{msg.chat.id}/all_links.txt", "r") as f:
			found = f.read().split("\n")
			count = 0

			for a in range(len(found)):
				val = found[a]

				if len(val.split(URL_SPLITTER)) > 1:
					continue

				if val.startswith(urls[0]) and urlparse(val).netloc == parsed_url.netloc:
					found[a] = f"{val}{URL_SPLITTER}{urls[1]}"
					count += 1

			await msg.answer(
				count < 1 and f"Не удалось найти {urls[0]} в HTML ❌" or f"Успешно заменено {count} ✅"
			)

			with open_recursive(f"userdata/d{msg.chat.id}/all_links.txt", "w+") as f:
				f.write("\n".join(found))
	except FileNotFoundError:
		await msg.answer(text = "Для начала запустите бота (/help)")


@dp.message_handler(commands = ["download_file"])
async def download_result(msg):
	new_msg = await msg.answer("Подготовка файла...")
	
	try:
		with open_recursive(f"userdata/d{msg.chat.id}/file.txt", "r") as fin:
			data = fin.read()

			with open_recursive(f"userdata/d{msg.chat.id}/all_links.txt", "r") as frep:
				links = sorted(frep.read().split("\n"), key = len, reverse = True)

				for u in links:
					sp = u.split(URL_SPLITTER)

					if len(sp) > 1:
						data = data.replace(sp[0], sp[1], 1)
					
		with open_recursive(f"userdata/d{msg.chat.id}/file.txt", "w+") as fout:
			fout.write(data)
		
		b_data = StringIO()
		b_data.write(data)
		b_data.seek(0)

		cur_time = datetime.now().strftime("%d_%m_%Y_%H%M%S")

		await msg.answer_document(
			types.InputFile(b_data, filename = f"result{cur_time}.html"),
			caption = u"Файл готов ✅"
		)
		await new_msg.delete()
	except FileNotFoundError:
		await new_msg.edit_text(text = "Файл не найден ❌")