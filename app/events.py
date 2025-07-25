import discord
from discord.ext import commands
from logger import logger

def register_events(bot: commands.Bot):
    @bot.event
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        logger.info(
            f"on_voice_state_update triggered for {member} | before: {before.channel.id} -> after: {after.channel}"
        )

        if after.channel is not None:
            voice_channel = after.channel  # type: discord.VoiceChannel
            try:
                await voice_channel.send(f"📢 {member.mention} joined **{voice_channel.name}**")
                logger.info(f"Sent message to linked text chat for {voice_channel.name}")
            except discord.Forbidden:
                logger.warning(f"Missing permission to send message in linked chat for {voice_channel.name}")
            except discord.HTTPException as e:
                logger.error(f"HTTP error sending message in {voice_channel.name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error sending message in {voice_channel.name}: {e}")
