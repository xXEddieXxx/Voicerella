import discord
from discord import app_commands

from app.config import get, add, delete


def register_admin_commands(bot):
    async def all_category_autocomplete(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=cat.name, value=cat.name)
            for cat in interaction.guild.categories
            if current.lower() in cat.name.lower()
        ][:25]

    async def tracked_category_autocomplete(interaction: discord.Interaction, current: str):
        guild_id = str(interaction.guild.id)
        categories = get(guild_id)
        return [
            app_commands.Choice(name=name, value=name)
            for name in categories
            if current.lower() in name.lower()
        ][:25]

    @app_commands.command(name="add_categorie", description="Track an existing category and create a voice channel in it.")
    @app_commands.describe(category_name="Name of an existing category to track")
    @app_commands.autocomplete(category_name=all_category_autocomplete)
    async def add_categorie(interaction: discord.Interaction, category_name: str):
        guild = interaction.guild
        guild_id = str(guild.id)
        category = discord.utils.get(guild.categories, name=category_name)

        if not category:
            await interaction.response.send_message(f"Category '{category_name}' does not exist.", ephemeral=True)
            return

        existing = get(guild_id)
        if category_name in existing:
            await interaction.response.send_message(f"Category '{category_name}' is already tracked.", ephemeral=True)
            return

        voice_channel = await guild.create_voice_channel(name="New Voice Channel", category=category)
        add(guild_id, category_name, {
            "category_id": category.id,
            "voice_channel_id": voice_channel.id
        })

        await interaction.response.send_message(f"Voice channel created in category '{category_name}' and tracking saved.")

    @app_commands.command(name="remove_categorie", description="Stop tracking a category and delete its voice channel.")
    @app_commands.describe(category_name="Name of a tracked category to untrack")
    @app_commands.autocomplete(category_name=tracked_category_autocomplete)
    async def remove_categorie(interaction: discord.Interaction, category_name: str):
        guild = interaction.guild
        guild_id = str(guild.id)
        config = get(guild_id)

        if category_name not in config:
            await interaction.response.send_message(f"Category '{category_name}' is not currently tracked.", ephemeral=True)
            return

        voice_channel_id = config[category_name].get("voice_channel_id")
        if voice_channel_id:
            channel = guild.get_channel(voice_channel_id)
            if channel and isinstance(channel, discord.VoiceChannel):
                try:
                    await channel.delete()
                except discord.DiscordException as e:
                    await interaction.response.send_message(f"Error deleting channel: {e}", ephemeral=True)
                    return

        delete(guild_id, category_name)
        await interaction.response.send_message(f"Tracking for category '{category_name}' has been removed and its voice channel deleted.")

    @app_commands.command(
        name="set_channel_name",
        description="Setze den Standardnamen für neue Sprachkanäle in einer Kategorie."
    )
    @app_commands.describe(
        category_name="Name einer getrackten Kategorie (erforderlich)",
        channel_name="Neuer Standardname für Sprachkanäle in dieser Kategorie (erforderlich)"
    )
    @app_commands.autocomplete(category_name=tracked_category_autocomplete)
    async def set_channel_name(
            interaction: discord.Interaction,
            category_name: str,
            channel_name: str
    ):
        guild = interaction.guild
        guild_id = str(guild.id)
        config = get(guild_id)

        if category_name not in config:
            await interaction.response.send_message(
                f"Die Kategorie '{category_name}' wird aktuell nicht getrackt.", ephemeral=True
            )
            return

        if not channel_name or channel_name.strip() == "":
            await interaction.response.send_message(
                "Bitte gib einen gültigen Standardnamen für Sprachkanäle an.", ephemeral=True
            )
            return

        config[category_name]["default_channel_name"] = channel_name
        add(guild_id, category_name, config[category_name])

        voice_channel_id = config[category_name].get("voice_channel_id")
        if not voice_channel_id:
            await interaction.response.send_message(
                f"Für die Kategorie '{category_name}' ist kein Sprachkanal zum Erstellen gefunden.", ephemeral=True
            )
            return

        channel = guild.get_channel(voice_channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            try:
                await channel.edit(name=channel_name)
                await interaction.response.send_message(
                    f"Der Standardname für neue Sprachkanäle in **{category_name}** ist jetzt: **{channel_name}**\n"
                    f"Der Vorlagen-Sprachkanal wurde umbenannt.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"Fehler beim Umbenennen des Vorlagekanals: {e}",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                f"Der Sprachkanal für die Kategorie '{category_name}' konnte nicht gefunden werden.",
                ephemeral=True
            )

    bot.tree.add_command(add_categorie)
    bot.tree.add_command(remove_categorie)
    bot.tree.add_command(set_channel_name)
