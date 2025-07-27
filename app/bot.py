import os
import discord
from discord.ext import commands

from app.admin_commands import register_admin_commands
from app.events import register_events
from app.tasks import register_tasks
from logger import logger

PRODUCTION = False

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.synced = False

register_admin_commands(bot)
register_events(bot)
register_tasks(bot)

@bot.event
async def on_ready():
    if not bot.synced:
        try:
            synced = await bot.tree.sync()
            logger.info(f"Slash-Befehle synchronisiert: {len(synced)}")
        except Exception as e:
            logger.error(f"Fehler beim Synchronisieren der Slash-Befehle: {e}")
        bot.synced = True
    logger.info(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    if hasattr(bot, "change_status_loop") and not bot.change_status_loop.is_running():
      bot.change_status_loop.start()
      logger.info("Started status rotation task.")

if __name__ == "__main__":
    if PRODUCTION:
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("No DISCORD_TOKEN set in environment variables.")
    else:
        with open("../token.txt", "r") as f:
            token = f.read().strip()

    logger.info("Starting bot...")
    bot.run(token)
