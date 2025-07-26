import discord
from discord import ui, Interaction

class RenameChannelModal(ui.Modal, title="Rename Channel"):
    new_name = ui.TextInput(label="New channel name", max_length=100)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: Interaction):
        await self.channel.edit(name=self.new_name.value)
        await interaction.response.send_message("Channel renamed.", ephemeral=True)


class SetUserLimitModal(ui.Modal, title="Set User Limit"):
    limit = ui.TextInput(label="Max users", placeholder="Enter a number", required=True)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: Interaction):
        try:
            num = int(self.limit.value)
            await self.channel.edit(user_limit=num)
            await interaction.response.send_message("User limit updated.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)


class TransferOwnershipModal(ui.Modal, title="Transfer Ownership"):
    new_owner_id = ui.TextInput(label="User ID to transfer to", placeholder="Paste user ID here")

    def __init__(self, channel: discord.VoiceChannel, panel):
        super().__init__()
        self.channel = channel
        self.panel = panel

    async def on_submit(self, interaction: Interaction):
        new_owner = self.channel.guild.get_member(int(self.new_owner_id.value))
        if new_owner is None:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return
        # Update permissions and ownership
        await self.channel.set_permissions(self.panel.owner, overwrite=None)
        await self.channel.set_permissions(new_owner, connect=True, manage_channels=True)
        self.panel.owner = new_owner
        await interaction.response.send_message(f"Ownership transferred to {new_owner.display_name}.", ephemeral=True)
