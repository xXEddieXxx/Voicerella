import discord
from discord import ui, Interaction, ButtonStyle

from app.voice_channel_modals import RenameChannelModal, SetUserLimitModal, TransferOwnershipModal

EMOJI_RENAME = "✏️"
EMOJI_LIMIT = "👥"
EMOJI_KICK = "🥾"
EMOJI_TRANSFER = "🔄"

class VoiceChannelPanel(ui.View):
    def __init__(self, member: discord.Member, channel: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.owner = member
        self.channel = channel

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message(
                "You're not allowed to control this channel.", ephemeral=True)
            return False
        return True

    @ui.button(emoji=EMOJI_RENAME, style=ButtonStyle.primary, label=None)
    async def rename(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(RenameChannelModal(self.channel))

    @ui.button(emoji=EMOJI_LIMIT, style=ButtonStyle.secondary, label=None)
    async def set_limit(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(SetUserLimitModal(self.channel))

    @ui.button(emoji=EMOJI_KICK, style=ButtonStyle.danger, label=None)
    async def kick_all(self, interaction: Interaction, button: ui.Button):
        for member in self.channel.members:
            if member != self.owner:
                await member.move_to(None)
        await interaction.response.send_message("All users kicked.", ephemeral=True)

    @ui.button(emoji=EMOJI_TRANSFER, style=ButtonStyle.success, label=None)
    async def transfer(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(TransferOwnershipModal(self.channel, self))


async def send_voice_channel_panel(channel: discord.VoiceChannel, owner: discord.Member):
    embed = discord.Embed(
        title="Voice Channel Controls",
        description=(
            f"{EMOJI_RENAME} **Rename** – Change your channel name\n"
            f"{EMOJI_LIMIT} **Limit** – Set max users\n"
            f"{EMOJI_KICK} **Kick** – Remove all users\n"
            f"{EMOJI_TRANSFER} **Transfer** – Give ownership"
        ),
        color=discord.Color.blurple()
    )
    embed.set_author(name=owner.display_name, icon_url=owner.display_avatar.url)
    await channel.send(
        content=f"{owner.mention}, here is your channel control panel:",
        embed=embed,
        view=VoiceChannelPanel(owner, channel)
    )
