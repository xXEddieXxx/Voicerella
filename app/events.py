import discord
from discord.ext import commands

from app.voice_channel_panel import VoiceChannelPanel
from logger import logger
from app.config import get, get_required_role_id

created_channels = set()

def register_events(bot: commands.Bot):
    @bot.event
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        if before.channel and before.channel != after.channel:
            if before.channel.id in created_channels:
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                        logger.info(f"Deleted empty personal channel: {before.channel.name}")
                        created_channels.remove(before.channel.id)
                    except discord.DiscordException as e:
                        logger.error(f"Failed to delete channel {before.channel.name}: {e}")

        if after.channel is None or after.channel == before.channel:
            return

        guild_id = str(member.guild.id)
        config = get(guild_id)

        for category_name, info in config.items():
            if not isinstance(info, dict):
                continue

            tracked_voice_id = info.get("voice_channel_id")
            category_id = info.get("category_id")

            if after.channel.id == tracked_voice_id:
                required_role_id = get_required_role_id(guild_id)
                if required_role_id:
                    required_role = member.guild.get_role(int(required_role_id))
                    if required_role and required_role not in member.roles:
                        logger.info(f"{member} lacks required role to create personal channel.")
                        return

                category = member.guild.get_channel(int(category_id))
                if not category:
                    logger.warning(f"Category ID {category_id} not found.")
                    return

                new_channel = await member.guild.create_voice_channel(
                    name=f"{member.display_name}'s Room",
                    category=category,
                    overwrites={
                        member.guild.default_role: discord.PermissionOverwrite(connect=False),
                        member: discord.PermissionOverwrite(connect=True, manage_channels=True)
                    }
                )
                logger.info(f"Created voice channel '{new_channel.name}' for {member.display_name}")
                created_channels.add(new_channel.id)

                await member.move_to(new_channel)
                logger.info(f"Moved {member.display_name} to their new channel '{new_channel.name}'")

                if new_channel:
                    await new_channel.send(
                        content=f"{member.mention} Here is your channel control panel:",
                        view=VoiceChannelPanel(member, new_channel)
                    )

                break
