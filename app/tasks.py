import random

import discord
from discord.ext import tasks

from logger import logger


def register_tasks(bot):
	statuses = [
		"schiebe alle noobs in einen raum",
		"AFK, aber nur geistig",
		"Bots brauchen auch Urlaub",
		"Ich höre heimlich mit",
		"Warte auf meinen nächsten Kick",
		"Channel-Chaos Manager",
		"Bin nur für die Memes hier",
		"Voice-Karaoke heute Abend!",
		"Eigentlich wollte ich schlafen...",
		"Kann keine Musik, kann nur Leute verschieben"
	]

	@tasks.loop(seconds=86400)
	async def change_status():
		status = random.choice(statuses)
		await bot.change_presence(activity=discord.CustomActivity(name=status))
		logger.info(f"Changed status to: {status}")

	bot.change_status_loop = change_status
