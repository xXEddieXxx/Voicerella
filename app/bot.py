import os
import asyncio
import discord
from discord.ext import commands

from app.admin_commands import register_admin_commands
from app.commands import register_general_commands
from app.events import register_events
from logger import logger

PRODUCTION = False

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

register_admin_commands(bot)
register_events(bot)
register_general_commands(bot)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        logger.error(f"Error syncing slash commands: {e}")

async def main():
    if PRODUCTION:
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("No DISCORD_TOKEN set in environment variables.")
    else:
        with open("../token.txt", "r") as f:
            token = f.read().strip()

    logger.info("Starting bot...")
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
