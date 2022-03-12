import os
from collections import Counter
from contextlib import contextmanager

from urllib.parse import urlparse

from .. import db
from ..config import URL_SPLITTER

from bs4 import BeautifulSoup

def count_dict(_dict):
	res = []

	for k, v in Counter(_dict).most_common():
		res.append(f"{k}: {v}")

	return res


@contextmanager
def open_recursive(path, mode = "r"):
	abs_path = os.path.abspath(path)
	_dir = os.path.dirname(abs_path)
	
	if not os.path.exists(_dir):
		os.makedirs(_dir)

	file = None
	try:
		file = open(abs_path, mode, encoding = "utf-8")
		yield file
	finally:
		if file:
			file.close()


async def parse_html(msg, text):
	images = []
	links = []	

	blacklist = await db.get_blacklist(msg.chat.id)
	soup = BeautifulSoup(text, "html.parser")

	for x in soup.select("[href^=http]"):
		links.append(x.get("href"))

	for x in soup.find_all("img", src = True):
		images.append(x.get("src"))

	with open_recursive(f"userdata/d{msg.chat.id}/file.txt", "w+") as f:
		f.write(soup.prettify())

	temp = links + images

	for a in range(len(temp)):
		val = temp[a]

		for black_url in blacklist:
			if val.startswith(black_url):
				temp[a] = f"{val}{URL_SPLITTER}[запрещенная ссылка]"
				break

	with open_recursive(f"userdata/d{msg.chat.id}/all_links.txt", "w+") as f:
		f.write("\n".join(temp))

	return (links, images)