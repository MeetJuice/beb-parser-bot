from . import parse_html, count_dict, open_recursive

from aiogram.utils.callback_data import CallbackData
from aiogram.types import \
	InlineKeyboardButton as button, \
	InlineKeyboardMarkup as markup

cbd = CallbackData("menu", "tag", "footer", "action", "value")

def build_menu(tag, page, text, arr):
	larr = len(arr)
	max_pages = larr // 10
	
	if page > max_pages:
		return {"text": "Меню устарело.", "reply_markup": None}

	text_res = f"*{text}* (Всего: {larr}) ({page + 1}/{max_pages + 1})\n"
	
	a = markup(row_width = 5).row()

	start = page * 10
	end = min(start + 10, larr)

	for i in range(start, end):
		text_res += f"*({i + 1})* `{arr[i]}`\n"

	if page > 0:
		a = a.insert(button("\u2B05",
			callback_data = cbd.new(footer = text, tag = tag, action = "list", value = page - 1))
		)
	if page < max_pages:
		a = a.insert(button("\u27A1",
			callback_data = cbd.new(footer = text, tag = tag, action = "list", value = page + 1))
		)

	return {"text": text_res, "reply_markup": a}


async def answer_parsed(msg, text):
	try:
		li, img = map(count_dict, await parse_html(msg, text))

		with open_recursive(f"userdata/d{msg.chat.id}/links.txt", "w+") as f:
			f.write("\n".join(li))

		with open_recursive(f"userdata/d{msg.chat.id}/images.txt", "w+") as f:
			f.write("\n".join(img))

		await msg.reply("HTML обработан.")

		await msg.answer(
			**build_menu("links", 0, "Список сайтов", li),
			parse_mode = "markdown"
		)

		await msg.answer(
			**build_menu("images", 0, "Список изображений", img),
			parse_mode = "markdown"
		)
		
	except Exception as e:
		await msg.reply(f"Не удалось обработать HTML {str(e)}")