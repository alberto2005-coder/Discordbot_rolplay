import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from config import Config
from datetime import datetime, timedelta

class LicenseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="solicitar-dni", description="Solicitar un DNI")
    @app_commands.describe(
        nombre="Tu nombre",
        apellido="Tu apellido",
        edad="Tu edad",
        fecha_nacimiento="Tu fecha de nacimiento (DD/MM/AAAA)",
        sexo="Tu sexo (Masculino/Femenino/Otro)",
        nacionalidad="Tu nacionalidad"
    )
    async def solicitar_dni(
        self, 
        interaction: discord.Interaction,
        nombre: str,
        apellido: str, 
        edad: int,
        fecha_nacimiento: str,
        sexo: str,
        nacionalidad: str
    ):
        """Solicitar un DNI"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden solicitar DNI."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(interaction.user.id, interaction.user.display_name)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya tiene DNI
            cursor.execute('''
                SELECT dni FROM users WHERE user_id = ? AND dni IS NOT NULL
            ''', (interaction.user.id,))
            
            existing_dni = cursor.fetchone()
            
            if existing_dni:
                await interaction.response.send_message(
                    embed=create_warning_embed(f"Ya tienes un DNI: {existing_dni[0]}"),
                    ephemeral=True
                )
                return
            
            # Verificar saldo suficiente (balance total de todos los bancos)
            balance = self.db.get_user_total_balance(interaction.user.id)
            dni_price = Config.LICENSE_PRICES["dni"]
            
            if balance < dni_price:
                await interaction.response.send_message(
                    embed=create_error_embed(f"No tienes suficiente dinero. Necesitas {format_currency(dni_price)}. Balance actual: {format_currency(balance)}"),
                    ephemeral=True
                )
                return
            
            # Generar DNI y actualizar usuario
            dni_number = generate_dni()
            cursor.execute('''
                UPDATE users 
                SET dni = ?, dni_issued_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (dni_number, interaction.user.id))
            
            # Actualizar información personal
            self.db.update_user_dni_info(interaction.user.id, nombre, apellido, edad, fecha_nacimiento, sexo, nacionalidad)
            
            # Asignar rol DNI automáticamente
            try:
                dni_role = discord.utils.get(interaction.guild.roles, name="DNI")
                if dni_role:
                    await interaction.user.add_roles(dni_role)
            except Exception:
                pass  # Si no se puede asignar el rol, continúa sin error
            
            # Crear licencia en tabla de licencias
            expires_at = datetime.now() + timedelta(days=Config.LICENSE_DURATION_DAYS["dni"])
            cursor.execute('''
                INSERT INTO licenses (user_id, license_type, expires_at)
                VALUES (?, ?, ?)
            ''', (interaction.user.id, "dni", expires_at))
            
            conn.commit()
        
        # Cobrar el DNI
        success = self.db.deduct_payment(interaction.user.id, dni_price)
        if not success:
            await interaction.response.send_message(
                embed=create_error_embed("Error al procesar el pago."),
                ephemeral=True
            )
            return
        
        self.db.add_transaction(interaction.user.id, "compra_dni", -dni_price, "Solicitud de DNI")
        
        embed = create_success_embed(
            f"DNI expedido exitosamente\n"
            f"**Número:** {dni_number}\n"
            f"**Nombre:** {nombre} {apellido}\n"
            f"**Edad:** {edad} años\n"
            f"**Fecha de nacimiento:** {fecha_nacimiento}\n"
            f"**Sexo:** {sexo}\n"
            f"**Nacionalidad:** {nacionalidad}\n"
            f"**Costo:** {format_currency(dni_price)}\n"
            f"**Fecha de expedición:** {format_datetime(datetime.now())}\n"
            f"**Válido hasta:** {format_datetime(expires_at)}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="solicitar-licencia-armas", description="Solicitar licencia de armas")
    async def solicitar_licencia_armas(self, interaction: discord.Interaction):
        """Solicitar licencia de armas"""
        if not has_role(interaction.user, ["civil"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo civiles pueden solicitar licencia de armas."),
                ephemeral=True
            )
            return
        
        # Verificar que tenga DNI
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dni FROM users WHERE user_id = ? AND dni IS NOT NULL
            ''', (interaction.user.id,))
            
            if not cursor.fetchone():
                await interaction.response.send_message(
                    embed=create_error_embed("Necesitas tener DNI para solicitar una licencia de armas."),
                    ephemeral=True
                )
                return
            
            # Verificar si ya tiene licencia válida
            cursor.execute('''
                SELECT expires_at FROM licenses
                WHERE user_id = ? AND license_type = ? AND valid = TRUE
            ''', (interaction.user.id, "armas"))
            
            existing_license = cursor.fetchone()
            
            if existing_license:
                expires_at = datetime.fromisoformat(existing_license[0])
                if expires_at > datetime.now():
                    await interaction.response.send_message(
                        embed=create_warning_embed(f"Ya tienes una licencia de armas válida hasta {format_datetime(expires_at)}"),
                        ephemeral=True
                    )
                    return
            
            # Verificar saldo suficiente (balance total de todos los bancos)
            balance = self.db.get_user_total_balance(interaction.user.id)
            license_price = Config.LICENSE_PRICES["armas"]
            
            if balance < license_price:
                await interaction.response.send_message(
                    embed=create_error_embed(f"No tienes suficiente dinero. Necesitas {format_currency(license_price)}. Balance actual: {format_currency(balance)}"),
                    ephemeral=True
                )
                return
            
            # Crear licencia
            expires_at = datetime.now() + timedelta(days=Config.LICENSE_DURATION_DAYS["armas"])
            cursor.execute('''
                INSERT OR REPLACE INTO licenses (user_id, license_type, expires_at, valid)
                VALUES (?, ?, ?, TRUE)
            ''', (interaction.user.id, "armas", expires_at))
            
            conn.commit()
        
        # Asignar rol de licencia de armas automáticamente
        try:
            armas_role = discord.utils.get(interaction.guild.roles, name="Licencia de armas (Beretta M9)")
            if armas_role:
                await interaction.user.add_roles(armas_role)
        except Exception:
            pass  # Si no se puede asignar el rol, continúa sin error
        
        # Cobrar la licencia
        success = self.db.deduct_payment(interaction.user.id, license_price)
        if not success:
            await interaction.response.send_message(
                embed=create_error_embed("Error al procesar el pago."),
                ephemeral=True
            )
            return
        
        self.db.add_transaction(interaction.user.id, "compra_licencia_armas", -license_price, "Licencia de armas")
        
        embed = create_success_embed(
            f"Licencia de armas expedida exitosamente\n"
            f"**Titular:** {interaction.user.display_name}\n"
            f"**Costo:** {format_currency(license_price)}\n"
            f"**Fecha de expedición:** {format_datetime(datetime.now())}\n"
            f"**Válida hasta:** {format_datetime(expires_at)}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="solicitar-licencia-de-conducir", description="Solicitar licencia de conducir")
    async def solicitar_licencia_conducir(self, interaction: discord.Interaction):
        """Solicitar licencia de conducir"""
        if not has_role(interaction.user, ["civil"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo civiles pueden solicitar licencia de conducir."),
                ephemeral=True
            )
            return
        
        # Verificar que tenga DNI
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dni FROM users WHERE user_id = ? AND dni IS NOT NULL
            ''', (interaction.user.id,))
            
            if not cursor.fetchone():
                await interaction.response.send_message(
                    embed=create_error_embed("Necesitas tener DNI para solicitar una licencia de conducir."),
                    ephemeral=True
                )
                return
            
            # Verificar si ya tiene licencia válida
            cursor.execute('''
                SELECT expires_at FROM licenses
                WHERE user_id = ? AND license_type = ? AND valid = TRUE
            ''', (interaction.user.id, "conducir"))
            
            existing_license = cursor.fetchone()
            
            if existing_license:
                expires_at = datetime.fromisoformat(existing_license[0])
                if expires_at > datetime.now():
                    await interaction.response.send_message(
                        embed=create_warning_embed(f"Ya tienes una licencia de conducir válida hasta {format_datetime(expires_at)}"),
                        ephemeral=True
                    )
                    return
            
            # Verificar saldo suficiente (balance total de todos los bancos)
            balance = self.db.get_user_total_balance(interaction.user.id)
            license_price = Config.LICENSE_PRICES["conducir"]
            
            if balance < license_price:
                await interaction.response.send_message(
                    embed=create_error_embed(f"No tienes suficiente dinero. Necesitas {format_currency(license_price)}. Balance actual: {format_currency(balance)}"),
                    ephemeral=True
                )
                return
            
            # Crear licencia
            expires_at = datetime.now() + timedelta(days=Config.LICENSE_DURATION_DAYS["conducir"])
            cursor.execute('''
                INSERT OR REPLACE INTO licenses (user_id, license_type, expires_at, valid)
                VALUES (?, ?, ?, TRUE)
            ''', (interaction.user.id, "conducir", expires_at))
            
            conn.commit()
        
        # Asignar rol de licencia de conducir automáticamente
        try:
            conducir_role = discord.utils.get(interaction.guild.roles, name="Licencia de conducir")
            if conducir_role:
                await interaction.user.add_roles(conducir_role)
        except Exception:
            pass  # Si no se puede asignar el rol, continúa sin error
        
        # Cobrar la licencia
        success = self.db.deduct_payment(interaction.user.id, license_price)
        if not success:
            await interaction.response.send_message(
                embed=create_error_embed("Error al procesar el pago."),
                ephemeral=True
            )
            return
        
        self.db.add_transaction(interaction.user.id, "compra_licencia_conducir", -license_price, "Licencia de conducir")
        
        embed = create_success_embed(
            f"Licencia de conducir expedida exitosamente\n"
            f"**Titular:** {interaction.user.display_name}\n"
            f"**Costo:** {format_currency(license_price)}\n"
            f"**Fecha de expedición:** {format_datetime(datetime.now())}\n"
            f"**Válida hasta:** {format_datetime(expires_at)}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ver-dni", description="Ver tu DNI")
    async def ver_dni(self, interaction: discord.Interaction):
        """Ver información del DNI"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver su DNI."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dni, dni_issued_at FROM users
                WHERE user_id = ? AND dni IS NOT NULL
            ''', (interaction.user.id,))
            
            dni_data = cursor.fetchone()
            
            if not dni_data:
                await interaction.response.send_message(
                    embed=create_warning_embed("No tienes DNI. Usa `/solicitar-dni` para obtener uno."),
                    ephemeral=True
                )
                return
        
        dni_number, issued_at = dni_data
        
        embed = discord.Embed(
            title="🆔 Documento Nacional de Identidad",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="📋 Número", value=dni_number, inline=True)
        embed.add_field(name="👤 Titular", value=interaction.user.display_name, inline=True)
        embed.add_field(name="📅 Expedido", value=issued_at[:10] if issued_at else "Desconocido", inline=True)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ver-licencia-de-armas", description="Ver tu licencia de armas")
    async def ver_licencia_armas(self, interaction: discord.Interaction):
        """Ver licencia de armas"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver sus licencias."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT issued_at, expires_at, valid FROM licenses
                WHERE user_id = ? AND license_type = ?
                ORDER BY issued_at DESC LIMIT 1
            ''', (interaction.user.id, "armas"))
            
            license_data = cursor.fetchone()
            
            if not license_data:
                await interaction.response.send_message(
                    embed=create_warning_embed("No tienes licencia de armas. Usa `/solicitar-licencia-armas` para obtener una."),
                    ephemeral=True
                )
                return
        
        issued_at, expires_at, valid = license_data
        expires_date = datetime.fromisoformat(expires_at)
        is_expired = expires_date < datetime.now()
        
        status_color = discord.Color.green()
        status_text = "✅ Válida"
        
        if not valid:
            status_color = discord.Color.red()
            status_text = "❌ Revocada"
        elif is_expired:
            status_color = discord.Color.orange()
            status_text = "⚠️ Expirada"
        
        embed = discord.Embed(
            title="🔫 Licencia de Portación de Armas",
            color=status_color
        )
        
        embed.add_field(name="👤 Titular", value=interaction.user.display_name, inline=True)
        embed.add_field(name="📅 Expedida", value=issued_at[:10], inline=True)
        embed.add_field(name="⏰ Expira", value=expires_at[:10], inline=True)
        embed.add_field(name="📊 Estado", value=status_text, inline=False)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ver-licencia-de-conducir", description="Ver tu licencia de conducir")
    async def ver_licencia_conducir(self, interaction: discord.Interaction):
        """Ver licencia de conducir"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver sus licencias."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT issued_at, expires_at, valid FROM licenses
                WHERE user_id = ? AND license_type = ?
                ORDER BY issued_at DESC LIMIT 1
            ''', (interaction.user.id, "conducir"))
            
            license_data = cursor.fetchone()
            
            if not license_data:
                await interaction.response.send_message(
                    embed=create_warning_embed("No tienes licencia de conducir. Usa `/solicitar-licencia-de-conducir` para obtener una."),
                    ephemeral=True
                )
                return
        
        issued_at, expires_at, valid = license_data
        expires_date = datetime.fromisoformat(expires_at)
        is_expired = expires_date < datetime.now()
        
        status_color = discord.Color.green()
        status_text = "✅ Válida"
        
        if not valid:
            status_color = discord.Color.red()
            status_text = "❌ Revocada"
        elif is_expired:
            status_color = discord.Color.orange()
            status_text = "⚠️ Expirada"
        
        embed = discord.Embed(
            title="🚗 Licencia de Conducir",
            color=status_color
        )
        
        embed.add_field(name="👤 Titular", value=interaction.user.display_name, inline=True)
        embed.add_field(name="📅 Expedida", value=issued_at[:10], inline=True)
        embed.add_field(name="⏰ Expira", value=expires_at[:10], inline=True)
        embed.add_field(name="📊 Estado", value=status_text, inline=False)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
