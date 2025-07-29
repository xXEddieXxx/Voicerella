import discord
from discord import ui, Interaction

from app.voice_channel_modals import build_panel_embed
from logger import logger


class KickUserSelectView(ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner: discord.Member, panel):
        super().__init__(timeout=30)
        self.channel = channel
        self.owner = owner
        self.panel = panel

        options = [
            discord.SelectOption(
                label=member.display_name,
                value=str(member.id)
            )
            for member in channel.members if member != owner
        ]

        self.select = ui.Select(
            placeholder="Wähle einen Nutzer...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        logger.debug(f"KickUserSelectView erstellt für Kanal '{channel.name}' mit Optionen: {[opt.label for opt in options]}")

    async def select_callback(self, interaction: Interaction):
        try:
            member_id = int(self.select.values[0])
            member = self.channel.guild.get_member(member_id)
            if member is None or member == self.owner:
                logger.warning(f"Ungültige Auswahl in KickUserSelectView von {interaction.user.display_name} ({interaction.user.id})")
                await interaction.response.send_message(
                    "Ungültige Auswahl.",
                    ephemeral=True
                )
                return

            logger.info(f"{interaction.user.display_name} hat Kick für {member.display_name} in Kanal '{self.channel.name}' gewählt")
            await interaction.response.send_message(
                f"Möchtest du **{member.display_name}** wirklich aus dem Kanal entfernen?",
                ephemeral=True,
                view=ConfirmKickView(member, self.channel, self.panel)
            )
        except Exception as e:
            logger.error(f"Fehler in KickUserSelectView.select_callback: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Anzeigen der Entfernen-Bestätigung.",
                ephemeral=True
            )
        self.stop()

class ConfirmKickView(ui.View):
    def __init__(self, member: discord.Member, channel: discord.VoiceChannel, panel):
        super().__init__(timeout=15)
        self.member = member
        self.channel = channel
        self.panel = panel

    @ui.button(label="Ja, entfernen", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        try:
            await self.member.move_to(None)
            logger.info(f"{self.member.display_name} wurde von {interaction.user.display_name} aus Kanal '{self.channel.name}' entfernt")
            await interaction.response.send_message(
                f"✅ {self.member.mention} wurde aus dem Kanal entfernt.",
                ephemeral=True
            )
            if self.panel.panel_message:
                new_embed = build_panel_embed(self.panel.owner, self.channel)
                await self.panel.panel_message.edit(embed=new_embed)
                logger.debug(f"Panel-Embed nach Kick aktualisiert für Kanal '{self.channel.name}'")
        except Exception as e:
            logger.error(f"Fehler beim Entfernen von {self.member.display_name} aus Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                f"Fehler beim Entfernen: {e}",
                ephemeral=True
            )
        self.stop()

    @ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Kick-Vorgang abgebrochen von {interaction.user.display_name} in Kanal '{self.channel.name}'")
        await interaction.response.send_message(
            "Entfernen abgebrochen.",
            ephemeral=True
        )
        self.stop()

class TransferOwnershipSelectView(ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner: discord.Member, panel):
        super().__init__(timeout=30)
        self.channel = channel
        self.owner = owner
        self.panel = panel

        options = [
            discord.SelectOption(
                label=member.display_name,
                value=str(member.id)
            )
            for member in channel.members if member != owner
        ]

        self.select = ui.Select(
            placeholder="Wähle einen Nutzer...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        logger.debug(f"TransferOwnershipSelectView erstellt für Kanal '{channel.name}' mit Optionen: {[opt.label for opt in options]}")

    async def select_callback(self, interaction: Interaction):
        try:
            member_id = int(self.select.values[0])
            member = self.channel.guild.get_member(member_id)
            if member is None or member == self.owner:
                logger.warning(f"Ungültige Auswahl in TransferOwnershipSelectView von {interaction.user.display_name} ({interaction.user.id})")
                await interaction.response.send_message(
                    "Ungültige Auswahl.",
                    ephemeral=True
                )
                return

            logger.info(f"{interaction.user.display_name} möchte Kanalbesitz auf {member.display_name} übertragen in Kanal '{self.channel.name}'")
            await interaction.response.send_message(
                f"Möchtest du den Kanalbesitz wirklich an **{member.display_name}** übertragen?",
                ephemeral=True,
                view=ConfirmTransferOwnershipView(member, self.channel, self.panel)
            )
        except Exception as e:
            logger.error(f"Fehler in TransferOwnershipSelectView.select_callback: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Anzeigen der Besitzübergabe-Bestätigung.",
                ephemeral=True
            )
        self.stop()

class ConfirmTransferOwnershipView(ui.View):
    def __init__(self, member: discord.Member, channel: discord.VoiceChannel, panel):
        super().__init__(timeout=15)
        self.member = member
        self.channel = channel
        self.panel = panel

    @ui.button(label="Ja, übertragen", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        try:
            await self.channel.set_permissions(self.panel.owner, overwrite=None)
            await self.channel.set_permissions(self.member, connect=True, manage_channels=True)
            self.panel.owner = self.member
            logger.info(f"Besitz von Kanal '{self.channel.name}' übertragen an {self.member.display_name} durch {interaction.user.display_name}")

            await interaction.response.send_message(
                f"✅ Der Kanalbesitz wurde an **{self.member.display_name}** übertragen.",
                ephemeral=True
            )
            if self.panel.panel_message:
                new_embed = self.panel.build_panel_embed(self.panel.owner, self.channel)
                await self.panel.panel_message.edit(embed=new_embed)
                logger.debug(f"Panel-Embed nach Besitzübergabe aktualisiert für Kanal '{self.channel.name}'")
        except Exception as e:
            logger.error(f"Fehler bei der Besitzübergabe an {self.member.display_name} für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                f"Fehler bei der Besitzübergabe: {e}",
                ephemeral=True
            )
        self.stop()

    @ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Besitzübergabe abgebrochen von {interaction.user.display_name} in Kanal '{self.channel.name}'")
        await interaction.response.send_message(
            "Besitzübergabe abgebrochen.",
            ephemeral=True
        )
        self.stop()

class ConfirmCloseView(ui.View):
    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    @ui.button(label="Ja, Kanal löschen", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        try:
            await self.channel.delete(reason="Kanal durch Panel geschlossen")
            logger.info(f"Kanal '{self.channel.name}' gelöscht durch {interaction.user.display_name}")
            await interaction.response.send_message(
                "✅ Der Kanal wurde gelöscht.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Kanals '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                f"Fehler beim Löschen: {e}",
                ephemeral=True
            )

    @ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Kanal-Schließen abgebrochen von {interaction.user.display_name} in Kanal '{self.channel.name}'")
        await interaction.response.send_message(
            "Abgebrochen.",
            ephemeral=True
        )
        self.stop()
