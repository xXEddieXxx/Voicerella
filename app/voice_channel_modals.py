import discord
from discord import ui, Interaction

from logger import logger


def build_panel_embed(owner: discord.Member, channel: discord.VoiceChannel) -> discord.Embed:
    member_count = len(channel.members)
    user_limit = channel.user_limit if channel.user_limit > 0 else "∞"
    info_lines = [
        f"👑 **Besitzer:** {owner.mention}",
        f"🔊 **Kanal:** {channel.name}",
        f"👥 **Nutzer:** {member_count}/{user_limit}",
    ]
    embed = discord.Embed(
        title="🎛️ Sprachkanal-Panel",
        description="\n".join(info_lines),
        color=discord.Color.from_rgb(108, 83, 245)
    )
    embed.set_thumbnail(url=owner.display_avatar.url)
    embed.set_footer(text="Verwalte deinen Sprachkanal ganz einfach!")
    logger.debug(f"Panel-Embed gebaut: Besitzer={owner.display_name}, Kanal={channel.name}, Nutzer={member_count}, Limit={user_limit}")
    return embed

class RenameChannelModal(ui.Modal, title="Kanal umbenennen"):
    new_name = ui.TextInput(
        label="Neuer Kanalname",
        placeholder="Gib hier den neuen Namen für den Sprachkanal ein.",
        max_length=100,
        style=discord.TextStyle.short
    )

    def __init__(self, channel: discord.VoiceChannel, panel):
        super().__init__()
        self.channel = channel
        self.panel = panel

    async def on_submit(self, interaction: Interaction):
        try:
            old_name = self.channel.name
            await self.channel.edit(name=self.new_name.value)
            logger.info(f"Kanal umbenannt: '{old_name}' -> '{self.new_name.value}' durch {interaction.user.display_name}")
            await interaction.response.send_message(
                f"✅ Der Kanal wurde zu **{self.new_name.value}** umbenannt.",
                ephemeral=True
            )
            if self.panel.panel_message:
                new_embed = build_panel_embed(self.panel.owner, self.channel)
                await self.panel.panel_message.edit(embed=new_embed)
                logger.debug(f"Panel-Embed nach Umbenennung aktualisiert für Kanal '{self.channel.name}'")
        except Exception as e:
            logger.error(f"Fehler beim Umbenennen des Kanals '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Umbenennen des Kanals.",
                ephemeral=True
            )

class SetUserLimitModal(ui.Modal, title="Nutzerlimit festlegen"):
    limit = ui.TextInput(
        label="Maximale Nutzerzahl",
        placeholder="Trage eine Zahl ein (z.B. 5)",
        max_length=3,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, channel: discord.VoiceChannel, panel):
        super().__init__()
        self.channel = channel
        self.panel = panel

    async def on_submit(self, interaction: Interaction):
        try:
            num = int(self.limit.value)
            if num < 0 or num > 99:
                raise ValueError("Limit außerhalb des gültigen Bereichs.")
            await self.channel.edit(user_limit=num)
            logger.info(f"Nutzerlimit für Kanal '{self.channel.name}' auf {num} gesetzt durch {interaction.user.display_name}")
            await interaction.response.send_message(
                f"✅ Das Nutzerlimit wurde auf **{num}** gesetzt.",
                ephemeral=True
            )
            if self.panel.panel_message:
                new_embed = build_panel_embed(self.panel.owner, self.channel)
                await self.panel.panel_message.edit(embed=new_embed)
                logger.debug(f"Panel-Embed nach Nutzerlimit-Update aktualisiert für Kanal '{self.channel.name}'")
        except ValueError:
            logger.warning(f"Ungültiges Nutzerlimit eingegeben von {interaction.user.display_name}: '{self.limit.value}'")
            await interaction.response.send_message(
                "❌ Bitte gib eine gültige Zahl zwischen 0 und 99 ein.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Fehler beim Setzen des Nutzerlimits für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Setzen des Nutzerlimits.",
                ephemeral=True
            )
