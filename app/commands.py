import discord
from discord import app_commands


def register_general_commands(bot):
    @app_commands.command(name="list_channels", description="List all channels in the server.")
    async def list_channels(interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        all_channels = guild.channels

        lines = [f"{channel.name} ({channel.type.name})" for channel in all_channels]
        text = "\n".join(lines)

        if len(text) > 1900:
            text = text[:1900] + "\n...and more."

        await interaction.response.send_message(f"**Channels in `{guild.name}`:**\n```{text}```")

    bot.tree.add_command(list_channels)
