import discord
from discord.ext import commands

from logger import logger
from app.voice_channel_panel import send_voice_channel_panel
from app.config import get

created_channels = set()
channel_panels = dict()
channel_owners = dict()

def possessive_name(name: str) -> str:
    if name.endswith('s'):
        return f"{name}’ Channel"
    else:
        return f"{name}'s Channel"

def register_events(bot: commands.Bot):
    @bot.event
    async def on_voice_state_update(
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState
    ):
        try:
            logger.info(f"VoiceStateUpdate: Member={member} | Before={getattr(before.channel, 'name', None)} | After={getattr(after.channel, 'name', None)}")

            if before.channel and before.channel != after.channel:
                if before.channel.id in created_channels:
                    if len(before.channel.members) == 0:
                        try:
                            await before.channel.delete()
                            logger.info(f"Gelöschter leerer Privatkanal: {before.channel.name}")
                            created_channels.remove(before.channel.id)
                            channel_panels.pop(before.channel.id, None)
                            channel_owners.pop(before.channel.id, None)
                        except discord.DiscordException as e:
                            logger.error(f"Fehler beim Löschen des Kanals {before.channel.name}: {e}")

            if before.channel and before.channel.id in created_channels:
                panel_message = channel_panels.get(before.channel.id)
                owner = channel_owners.get(before.channel.id)
                if panel_message and owner:
                    from app.voice_channel_modals import build_panel_embed
                    embed = build_panel_embed(owner, before.channel)
                    try:
                        await panel_message.edit(embed=embed)
                        logger.info(f"Panel-Embed für Kanal '{before.channel.name}' nach User-Leave aktualisiert.")
                    except discord.DiscordException as e:
                        logger.error(f"Fehler beim Aktualisieren des Embeds für Kanal '{before.channel.name}': {e}")

            if after.channel and after.channel.id in created_channels:
                panel_message = channel_panels.get(after.channel.id)
                owner = channel_owners.get(after.channel.id)
                if panel_message and owner:
                    from app.voice_channel_modals import build_panel_embed
                    embed = build_panel_embed(owner, after.channel)
                    try:
                        await panel_message.edit(embed=embed)
                        logger.info(f"Panel-Embed für Kanal '{after.channel.name}' nach User-Join aktualisiert.")
                    except discord.DiscordException as e:
                        logger.error(f"Fehler beim Aktualisieren des Embeds für Kanal '{after.channel.name}': {e}")

            if after.channel is None or after.channel == before.channel:
                logger.debug("User is not joining a new tracked channel; no further action taken.")
                return

            guild_id = str(member.guild.id)
            config = get(guild_id)

            for category_name, info in config.items():
                if not isinstance(info, dict):
                    continue

                tracked_voice_id = info.get("voice_channel_id")
                category_id = info.get("category_id")

                if after.channel.id == tracked_voice_id:
                    logger.info(f"Trigger-Kanal erkannt: {after.channel.name} (ID: {tracked_voice_id}). Starte Kanal-Erstellung.")

                    category = member.guild.get_channel(int(category_id))
                    if not category:
                        logger.warning(f"Kategorie-ID {category_id} nicht gefunden.")
                        return

                    channel_name = possessive_name(member.display_name)

                    try:
                        new_channel = await member.guild.create_voice_channel(
                            name=channel_name,
                            category=category,
                            overwrites={
                                member: discord.PermissionOverwrite(connect=True, manage_channels=True)
                            }
                        )
                        logger.info(f"Sprachkanal '{new_channel.name}' erstellt für {member.display_name} (sichtbar für alle mit Kategorie-Recht)")
                        created_channels.add(new_channel.id)
                    except discord.DiscordException as e:
                        logger.error(f"Fehler beim Erstellen des Kanals '{channel_name}': {e}")
                        return

                    try:
                        await member.move_to(new_channel)
                        logger.info(f"{member.display_name} wurde in seinen neuen Kanal '{new_channel.name}' verschoben.")
                    except discord.DiscordException as e:
                        logger.error(f"Fehler beim Verschieben von {member.display_name} in '{new_channel.name}': {e}")

                    if new_channel:
                        try:
                            panel_message = await send_voice_channel_panel(new_channel, member)
                            channel_panels[new_channel.id] = panel_message
                            channel_owners[new_channel.id] = member
                            logger.info(f"Panel für Kanal '{new_channel.name}' erfolgreich gesendet und registriert.")
                        except Exception as e:
                            logger.error(f"Fehler beim Senden des Panels für Kanal '{new_channel.name}': {e}")
                    break

        except Exception as e:
            logger.error(f"Unerwarteter Fehler im on_voice_state_update: {e}", exc_info=True)
