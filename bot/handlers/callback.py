from .. import dp, db

from ..util import open_recursive
from ..util.telegram import cbd, build_menu

@dp.callback_query_handler(cbd.filter(action = ["list"]))
async def menu_handler(callback, callback_data):
	cb = callback_data
	msg = callback.message

	tag = cb["tag"]

	with open_recursive(f"userdata/d{msg.chat.id}/{tag}.txt", "r") as f:
		menu = build_menu(tag, int(cb["value"]), cb["footer"], f.read().split("\n"))

	await msg.edit_text(**menu, parse_mode = "markdown")