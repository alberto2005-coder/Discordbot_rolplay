import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from datetime import datetime

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="crear-historia", description="Crear tu historia personal")
    @app_commands.describe(historia="Tu historia personal (máximo 1000 caracteres)")
    async def crear_historia(self, interaction: discord.Interaction, historia: str):
        """Crear o actualizar la historia personal del usuario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden crear su historia."),
                ephemeral=True
            )
            return
        
        if len(historia) > 1000:
            await interaction.response.send_message(
                embed=create_error_embed("La historia no puede exceder los 1000 caracteres."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(interaction.user.id, interaction.user.display_name)
        
        # Guardar la historia
        self.db.create_user_story(interaction.user.id, historia)
        
        embed = create_success_embed(
            f"Historia personal guardada exitosamente\n"
            f"**Usuario:** {interaction.user.display_name}\n"
            f"**Longitud:** {len(historia)} caracteres\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ver-historia", description="Ver la historia personal de un usuario")
    @app_commands.describe(usuario="Usuario del que ver la historia (opcional)")
    async def ver_historia(self, interaction: discord.Interaction, usuario: discord.Member = None):
        """Ver la historia personal de un usuario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver historias."),
                ephemeral=True
            )
            return
        
        target_user = usuario if usuario else interaction.user
        
        # Obtener la historia
        story_data = self.db.get_user_story(target_user.id)
        
        if not story_data:
            name = target_user.display_name if usuario else "tu"
            await interaction.response.send_message(
                embed=create_warning_embed(f"No se encontró historia para {name}. Usa `/crear-historia` para crear una."),
                ephemeral=True
            )
            return
        
        story_text, created_at = story_data
        
        embed = discord.Embed(
            title=f"📖 Historia de {target_user.display_name}",
            description=story_text,
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📅 Creada",
            value=created_at[:19].replace("T", " "),
            inline=True
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))