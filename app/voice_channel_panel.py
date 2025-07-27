import discord
from discord import ui, Interaction, ButtonStyle

from logger import logger

from app.voice_channel_modals import (
    RenameChannelModal,
    SetUserLimitModal,
    build_panel_embed,
)
from app.voice_channel_views import (
    KickUserSelectView,
    TransferOwnershipSelectView,
    ConfirmCloseView,
)

class VoiceChannelPanel(ui.View):
    def __init__(self, member: discord.Member, channel: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.owner = member
        self.channel = channel
        self.panel_message = None
        logger.debug(f"VoiceChannelPanel initialisiert für {member.display_name} in Kanal '{channel.name}' (ID: {channel.id})")

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.owner.id:
            logger.warning(f"Zugriffsversuch von {interaction.user.display_name} (ID: {interaction.user.id}) auf Panel von {self.owner.display_name}")
            await interaction.response.send_message(
                "Nur der Besitzer kann dieses Panel benutzen.", ephemeral=True
            )
            return False
        logger.debug(f"Panel-Zugriff erlaubt für Besitzer {self.owner.display_name}")
        return True

    @ui.button(label="Kanal umbenennen", style=ButtonStyle.primary, row=0)
    async def rename(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Rename-Button gedrückt von {interaction.user.display_name} für Kanal '{self.channel.name}'")
        try:
            await interaction.response.send_modal(RenameChannelModal(self.channel, self))
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Rename-Modals für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Öffnen des Umbenennen-Modals.", ephemeral=True
            )

    @ui.button(label="Nutzerlimit setzen", style=ButtonStyle.secondary, row=0)
    async def set_limit(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Nutzerlimit-Button gedrückt von {interaction.user.display_name} für Kanal '{self.channel.name}'")
        try:
            await interaction.response.send_modal(SetUserLimitModal(self.channel, self))
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Nutzerlimit-Modals für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Öffnen des Nutzerlimit-Modals.", ephemeral=True
            )

    @ui.button(label="Nutzer entfernen", style=ButtonStyle.danger, row=0)
    async def kick_user(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Nutzer entfernen-Button gedrückt von {interaction.user.display_name} für Kanal '{self.channel.name}'")
        try:
            kickable_members = [
                m for m in self.channel.members if m != self.owner
            ]
            if not kickable_members:
                logger.info(f"Keine weiteren Nutzer zum Entfernen in Kanal '{self.channel.name}'")
                await interaction.response.send_message(
                    "Kein weiterer Nutzer zum Entfernen gefunden.",
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                "Wähle einen Nutzer zum Entfernen aus:",
                ephemeral=True,
                view=KickUserSelectView(self.channel, self.owner, self)
            )
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der KickUserSelectView für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Anzeigen der Nutzer-Auswahl.",
                ephemeral=True
            )

    @ui.button(label="Besitz übertragen", style=ButtonStyle.success, row=0)
    async def transfer(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Besitz übertragen-Button gedrückt von {interaction.user.display_name} für Kanal '{self.channel.name}'")
        try:
            transferrable_members = [
                m for m in self.channel.members if m != self.owner
            ]
            if not transferrable_members:
                logger.info(f"Keine weiteren Nutzer für Besitzübergabe in Kanal '{self.channel.name}'")
                await interaction.response.send_message(
                    "Kein weiterer Nutzer für Besitzübergabe gefunden.",
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                "Wähle einen Nutzer, an den du den Kanalbesitz übertragen möchtest:",
                ephemeral=True,
                view=TransferOwnershipSelectView(self.channel, self.owner, self)
            )
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der TransferOwnershipSelectView für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Anzeigen der Nutzer-Auswahl.",
                ephemeral=True
            )

    @ui.button(label="Kanal schließen", style=ButtonStyle.danger, row=0)
    async def close_channel(self, interaction: Interaction, button: ui.Button):
        logger.info(f"Kanal schließen-Button gedrückt von {interaction.user.display_name} für Kanal '{self.channel.name}'")
        try:
            await interaction.response.send_message(
                "⚠️ Bist du sicher, dass du den Kanal schließen möchtest? Diese Aktion kann nicht rückgängig gemacht werden.",
                ephemeral=True,
                view=ConfirmCloseView(self.channel)
            )
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der ConfirmCloseView für Kanal '{self.channel.name}': {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Fehler beim Anzeigen des Schließen-Bestätigungsdialogs.",
                ephemeral=True
            )

async def send_voice_channel_panel(
    channel: discord.VoiceChannel,
    owner: discord.Member
) -> discord.Message:
    try:
        embed = build_panel_embed(owner, channel)
        view = VoiceChannelPanel(owner, channel)
        message = await channel.send(
            content=f"{owner.mention} Hier ist dein **Sprachkanal-Panel**:",
            embed=embed,
            view=view
        )
        view.panel_message = message
        logger.info(f"Panel-Nachricht erfolgreich gesendet für Kanal '{channel.name}' (ID: {channel.id}) und Besitzer {owner.display_name}")
        return message
    except Exception as e:
        logger.error(f"Fehler beim Senden des Panels für Kanal '{channel.name}': {e}", exc_info=True)
        raise
