import asyncio
import random
import aioredis as redis

class BotDatabase:
	def __init__(self, _url):
		self.con = redis.from_url(_url, decode_responses = True)

	async def add_black_url(self, user_id, url):
		return await self.con.sadd(f"user{user_id}_blacklist", url)


	async def rem_black_url(self, user_id, url):
		return await self.con.srem(f"user{user_id}_blacklist", url)

	async def get_blacklist(self, user_id):
		return await self.con.smembers(f"user{user_id}_blacklist")