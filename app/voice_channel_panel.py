import discord
from discord import ui, Interaction, ButtonStyle
from app.voice_channel_modals import RenameChannelModal, SetUserLimitModal, TransferOwnershipModal

EMOJI_RENAME = "✏️"
EMOJI_LIMIT = "👥"
EMOJI_KICK = "🥾"
EMOJI_TRANSFER = "🔄"
EMOJI_CHANNEL = "🔊"
EMOJI_OWNER = "⭐"
EMOJI_INFO = "ℹ️"

class VoiceChannelPanel(ui.View):
    def __init__(self, member: discord.Member, channel: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.owner = member
        self.channel = channel

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message(
                "Nur der Besitzer kann dieses Panel benutzen.", ephemeral=True)
            return False
        return True

    @ui.button(emoji=EMOJI_RENAME, style=ButtonStyle.primary, label=None, row=0)
    async def rename(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(RenameChannelModal(self.channel))

    @ui.button(emoji=EMOJI_LIMIT, style=ButtonStyle.secondary, label=None, row=0)
    async def set_limit(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(SetUserLimitModal(self.channel))

    @ui.button(emoji=EMOJI_KICK, style=ButtonStyle.danger, label=None, row=0)
    async def kick_all(self, interaction: Interaction, button: ui.Button):
        kicked_count = 0
        for member in self.channel.members:
            if member != self.owner:
                await member.move_to(None)
                kicked_count += 1
        await interaction.response.send_message(
            f"{EMOJI_KICK} {kicked_count} Nutzer{' wurden' if kicked_count != 1 else ' wurde'} aus dem Kanal entfernt.",
            ephemeral=True
        )

    @ui.button(emoji=EMOJI_TRANSFER, style=ButtonStyle.success, label=None, row=0)
    async def transfer(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(TransferOwnershipModal(self.channel, self))


async def send_voice_channel_panel(channel: discord.VoiceChannel, owner: discord.Member):
    member_count = len(channel.members)
    user_limit = channel.user_limit if channel.user_limit > 0 else "∞"
    voice_icon = EMOJI_CHANNEL
    info_lines = [
        f"{EMOJI_OWNER} **Besitzer:** {owner.mention}",
        f"{voice_icon} **Kanal:** {channel.name}",
        f"👥 **Nutzer:** {member_count}/{user_limit}",
    ]
    controls_lines = [
        f"{EMOJI_RENAME} **Umbenennen**\n> Ändere den Namen deines Kanals",
        f"{EMOJI_LIMIT} **Limit setzen**\n> Max. Nutzerzahl festlegen",
        f"{EMOJI_KICK} **Alle entfernen**\n> Entferne alle Nutzer aus dem Kanal",
        f"{EMOJI_TRANSFER} **Übertragen**\n> Übertrage den Kanalbesitz",
    ]
    embed = discord.Embed(
        title=f"{EMOJI_INFO} Sprachkanal Steuerung",
        description="\n".join(info_lines),
        color=discord.Color.from_rgb(108, 83, 245)
    )
    embed.add_field(
        name="Aktionen",
        value="\n\n".join(controls_lines),
        inline=False
    )
    embed.set_thumbnail(url=owner.display_avatar.url)
    embed.set_footer(text="Verwalte deinen privaten Sprachkanal ganz einfach! 🚀")

    await channel.send(
        content=f"{owner.mention} Hier ist dein Steuerungs-Panel für den Sprachkanal:",
        embed=embed,
        view=VoiceChannelPanel(owner, channel)
    )
