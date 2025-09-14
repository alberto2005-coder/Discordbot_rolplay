import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv
from config import Config

# Cargar variables de entorno
load_dotenv()
from database import Database
from commands.economic import EconomicCommands
from commands.police import PoliceCommands
from commands.admin import AdminCommands
from commands.licenses import LicenseCommands
from commands.inventory import InventoryCommands
from commands.general import GeneralCommands

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class RoleplayBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.db = Database()
        
    async def setup_hook(self):
        """Se ejecuta cuando el bot está listo"""
        # Agregar cogs primero
        await self.add_cog(EconomicCommands(self))
        await self.add_cog(PoliceCommands(self))
        await self.add_cog(AdminCommands(self))
        await self.add_cog(LicenseCommands(self))
        await self.add_cog(InventoryCommands(self))
        await self.add_cog(GeneralCommands(self))
        
        # Sincronizar comandos slash después de cargar los cogs
        try:
            synced = await self.tree.sync()
            logger.info(f"Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            logger.error(f"Error al sincronizar comandos: {e}")
        
    async def on_ready(self):
        logger.info(f'{self.user} está conectado y listo!')
        logger.info(f'Conectado a {len(self.guilds)} servidores')
        
        # Cambiar el estado del bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="el servidor de roleplay"
            )
        )

def main():
    """Función principal para ejecutar el bot"""
    # Obtener token desde variables de entorno
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("Token de Discord no encontrado en las variables de entorno")
        return
    
    # Crear e inicializar la base de datos
    db = Database()
    db.initialize()
    
    # Crear y ejecutar el bot
    bot = RoleplayBot()
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Token de Discord inválido")
    except Exception as e:
        logger.error(f"Error al ejecutar el bot: {e}")

if __name__ == "__main__":
    main()
