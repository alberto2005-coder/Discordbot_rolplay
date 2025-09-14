import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from config import Config
from datetime import datetime, timedelta

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="banear", description="Banear a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a banear",
        razon="Razón del baneo",
        eliminar_mensajes="Días de mensajes a eliminar (0-7)"
    )
    async def banear(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "No especificada", eliminar_mensajes: int = 0):
        """Banear a un usuario del servidor"""
        if not has_role(interaction.user, ["staff"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo el staff puede usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes banearte a ti mismo."),
                ephemeral=True
            )
            return
        
        if eliminar_mensajes < 0 or eliminar_mensajes > 7:
            eliminar_mensajes = 0
        
        try:
            # Enviar mensaje privado antes del baneo
            dm_embed = create_embed(
                "🔨 Has sido baneado",
                f"**Servidor:** {interaction.guild.name}\n"
                f"**Moderador:** {interaction.user.display_name}\n"
                f"**Razón:** {razon}\n"
                f"**Fecha:** {format_datetime(datetime.now())}",
                discord.Color.red()
            )
            await send_dm(usuario, dm_embed)
            
            # Banear usuario
            await usuario.ban(reason=f"Baneado por {interaction.user.display_name}: {razon}", delete_message_days=eliminar_mensajes)
            
            # Crear embed de confirmación
            embed = create_success_embed(
                f"Usuario baneado exitosamente\n"
                f"**Usuario:** {usuario.display_name} ({usuario.id})\n"
                f"**Moderador:** {interaction.user.display_name}\n"
                f"**Razón:** {razon}\n"
                f"**Mensajes eliminados:** {eliminar_mensajes} días\n"
                f"**Fecha:** {format_datetime(datetime.now())}"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=create_error_embed("No tengo permisos para banear a este usuario."),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=create_error_embed(f"Error al banear usuario: {str(e)}"),
                ephemeral=True
            )
    
    @app_commands.command(name="expulsar", description="Expulsar a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a expulsar",
        razon="Razón de la expulsión"
    )
    async def expulsar(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "No especificada"):
        """Expulsar a un usuario del servidor"""
        if not has_role(interaction.user, ["staff"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo el staff puede usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes expulsarte a ti mismo."),
                ephemeral=True
            )
            return
        
        try:
            # Enviar mensaje privado antes de la expulsión
            dm_embed = create_embed(
                "👢 Has sido expulsado",
                f"**Servidor:** {interaction.guild.name}\n"
                f"**Moderador:** {interaction.user.display_name}\n"
                f"**Razón:** {razon}\n"
                f"**Fecha:** {format_datetime(datetime.now())}",
                discord.Color.orange()
            )
            await send_dm(usuario, dm_embed)
            
            # Expulsar usuario
            await usuario.kick(reason=f"Expulsado por {interaction.user.display_name}: {razon}")
            
            # Crear embed de confirmación
            embed = create_success_embed(
                f"Usuario expulsado exitosamente\n"
                f"**Usuario:** {usuario.display_name} ({usuario.id})\n"
                f"**Moderador:** {interaction.user.display_name}\n"
                f"**Razón:** {razon}\n"
                f"**Fecha:** {format_datetime(datetime.now())}"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=create_error_embed("No tengo permisos para expulsar a este usuario."),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=create_error_embed(f"Error al expulsar usuario: {str(e)}"),
                ephemeral=True
            )
    
    @app_commands.command(name="poner-sancion", description="Poner una sanción a un usuario")
    @app_commands.describe(
        usuario="Usuario a sancionar",
        razon="Razón de la sanción",
        duracion_horas="Duración en horas (0 para permanente)"
    )
    async def poner_sancion(self, interaction: discord.Interaction, usuario: discord.Member, razon: str, duracion_horas: int = 0):
        """Poner una sanción a un usuario"""
        if not has_role(interaction.user, ["mod", "staff"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo moderadores y staff pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes sancionarte a ti mismo."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(usuario.id, usuario.display_name)
        
        expires_at = None
        if duracion_horas > 0:
            expires_at = datetime.now() + timedelta(hours=duracion_horas)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear sanción
            cursor.execute('''
                INSERT INTO sanctions (user_id, staff_id, reason, duration_hours, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario.id, interaction.user.id, razon, duracion_horas, expires_at))
            
            sanction_id = cursor.lastrowid
            conn.commit()
        
        # Crear embed de confirmación
        duration_text = f"{duracion_horas} horas" if duracion_horas > 0 else "Permanente"
        expires_text = f"\n**Expira:** {format_datetime(expires_at)}" if expires_at else ""
        
        embed = create_success_embed(
            f"Sanción impuesta exitosamente\n"
            f"**Usuario:** {usuario.display_name}\n"
            f"**Moderador:** {interaction.user.display_name}\n"
            f"**Razón:** {razon}\n"
            f"**Duración:** {duration_text}\n"
            f"**ID Sanción:** #{sanction_id}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
            f"{expires_text}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al usuario sancionado
        dm_embed = create_embed(
            "⚠️ Has recibido una sanción",
            f"**Servidor:** {interaction.guild.name}\n"
            f"**Moderador:** {interaction.user.display_name}\n"
            f"**Razón:** {razon}\n"
            f"**Duración:** {duration_text}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
            f"{expires_text}",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="quitar-sancion", description="Quitar una sanción a un usuario")
    @app_commands.describe(sancion_id="ID de la sanción a quitar")
    async def quitar_sancion(self, interaction: discord.Interaction, sancion_id: int):
        """Quitar una sanción específica"""
        if not has_role(interaction.user, ["staff", "mod"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo moderadores y staff pueden usar este comando."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la sanción existe y está activa
            cursor.execute('''
                SELECT user_id, reason FROM sanctions
                WHERE id = ? AND active = TRUE
            ''', (sancion_id,))
            
            sanction_data = cursor.fetchone()
            
            if not sanction_data:
                await interaction.response.send_message(
                    embed=create_error_embed("Sanción no encontrada o ya inactiva."),
                    ephemeral=True
                )
                return
            
            # Desactivar sanción
            cursor.execute('''
                UPDATE sanctions
                SET active = FALSE
                WHERE id = ?
            ''', (sancion_id,))
            
            conn.commit()
        
        user_id, reason = sanction_data
        user = self.bot.get_user(user_id)
        username = user.display_name if user else f"Usuario #{user_id}"
        
        embed = create_success_embed(
            f"Sanción removida exitosamente\n"
            f"**ID:** #{sancion_id}\n"
            f"**Usuario:** {username}\n"
            f"**Razón original:** {reason}\n"
            f"**Removida por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al usuario
        if user:
            dm_embed = create_embed(
                "✅ Sanción removida",
                f"**Servidor:** {interaction.guild.name}\n"
                f"**Moderador:** {interaction.user.display_name}\n"
                f"**ID Sanción:** #{sancion_id}\n"
                f"**Fecha:** {format_datetime(datetime.now())}",
                discord.Color.green()
            )
            await send_dm(user, dm_embed)
    
    @app_commands.command(name="sanciones-ver", description="Ver sanciones de un usuario")
    @app_commands.describe(usuario="Usuario del que ver las sanciones")
    async def ver_sanciones(self, interaction: discord.Interaction, usuario: discord.Member = None):
        """Ver sanciones de un usuario"""
        if not has_role(interaction.user, ["mod", "staff"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo moderadores y staff pueden usar este comando."),
                ephemeral=True
            )
            return
        
        target_user = usuario if usuario else interaction.user
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener sanciones
            cursor.execute('''
                SELECT s.id, s.reason, s.issued_at, s.expires_at, s.active, u.username
                FROM sanctions s
                JOIN users u ON s.staff_id = u.user_id
                WHERE s.user_id = ?
                ORDER BY s.issued_at DESC
                LIMIT 10
            ''', (target_user.id,))
            
            sanctions = cursor.fetchall()
        
        embed = discord.Embed(
            title=f"⚖️ Sanciones de {target_user.display_name}",
            color=discord.Color.red()
        )
        
        if not sanctions:
            embed.description = "No tiene sanciones registradas."
        else:
            active_count = 0
            sanction_list = []
            
            for sanction_id, reason, issued_at, expires_at, active, staff in sanctions:
                status = "🔴 Activa" if active else "⚪ Inactiva"
                if active:
                    active_count += 1
                
                expiry_text = ""
                if expires_at:
                    expiry_text = f"\nExpira: {expires_at[:16]}"
                
                sanction_list.append(
                    f"**#{sanction_id}** - {status}\n"
                    f"Razón: {reason}\n"
                    f"Staff: {staff}\n"
                    f"Fecha: {issued_at[:16]}"
                    f"{expiry_text}\n"
                )
            
            embed.description = "\n".join(sanction_list)
            
            if active_count > 0:
                embed.add_field(
                    name="📊 Sanciones Activas",
                    value=str(active_count),
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="mantenimiento", description="Activar/desactivar modo mantenimiento")
    @app_commands.describe(activar="True para activar, False para desactivar")
    async def mantenimiento(self, interaction: discord.Interaction, activar: bool):
        """Activar o desactivar modo mantenimiento"""
        if not has_role(interaction.user, ["owners"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los owners pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if activar:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="🔧 En mantenimiento"
            )
            status = discord.Status.do_not_disturb
            message = "Modo mantenimiento activado"
        else:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="el servidor de roleplay"
            )
            status = discord.Status.online
            message = "Modo mantenimiento desactivado"
        
        await self.bot.change_presence(activity=activity, status=status)
        
        embed = create_success_embed(
            f"{message}\n"
            f"**Activado por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="servidor", description="Información del servidor")
    async def servidor(self, interaction: discord.Interaction):
        """Mostrar información del servidor"""
        if not has_role(interaction.user, ["owners"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los owners pueden usar este comando."),
                ephemeral=True
            )
            return
        
        guild = interaction.guild
        
        # Contar usuarios por roles
        role_counts = {}
        for member in guild.members:
            for role in member.roles[1:]:  # Excluir @everyone
                if role.name in role_counts:
                    role_counts[role.name] += 1
                else:
                    role_counts[role.name] = 1
        
        embed = discord.Embed(
            title=f"📊 Información de {guild.name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👥 Miembros",
            value=f"Total: {guild.member_count}\nHumanos: {len([m for m in guild.members if not m.bot])}\nBots: {len([m for m in guild.members if m.bot])}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Creado",
            value=format_datetime(guild.created_at),
            inline=True
        )
        
        embed.add_field(
            name="👑 Propietario",
            value=guild.owner.display_name if guild.owner else "Desconocido",
            inline=True
        )
        
        embed.add_field(
            name="📋 Canales",
            value=f"Texto: {len(guild.text_channels)}\nVoz: {len(guild.voice_channels)}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Roles",
            value=str(len(guild.roles)),
            inline=True
        )
        
        embed.add_field(
            name="😀 Emojis",
            value=str(len(guild.emojis)),
            inline=True
        )
        
        # Mostrar roles más comunes
        if role_counts:
            top_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            role_text = "\n".join([f"{role}: {count}" for role, count in top_roles])
            embed.add_field(
                name="🏷️ Roles más comunes",
                value=role_text,
                inline=False
            )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ck", description="Character Kill - Eliminar completamente un personaje")
    @app_commands.describe(usuario="Usuario al que hacer CK")
    async def character_kill(self, interaction: discord.Interaction, usuario: discord.Member):
        """Eliminar completamente un personaje del sistema"""
        if not has_role(interaction.user, ["owners"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los owners pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes hacerte CK a ti mismo."),
                ephemeral=True
            )
            return
        
        # Confirmar la acción
        confirm_embed = create_warning_embed(
            f"⚠️ **ADVERTENCIA DE CHARACTER KILL**\n\n"
            f"Estás a punto de eliminar COMPLETAMENTE el personaje de {usuario.display_name}.\n"
            f"Esto incluye:\n"
            f"• Todas las cuentas bancarias y dinero\n"
            f"• Todo el inventario y objetos\n"
            f"• Todas las licencias (DNI, armas, conducir)\n"
            f"• Historial de transacciones\n"
            f"• Multas, préstamos y sanciones\n"
            f"• Arrestos y historial policial\n\n"
            f"**ESTA ACCIÓN NO SE PUEDE DESHACER**\n"
            f"Escribe 'CONFIRMAR CK' para proceder."
        )
        
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
        
        # Esperar confirmación del usuario
        def check(m):
            return m.author == interaction.user and m.content == "CONFIRMAR CK"
        
        try:
            await self.bot.wait_for('message', check=check, timeout=30.0)
        except:
            timeout_embed = create_error_embed("Tiempo agotado. Character Kill cancelado.")
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)
            return
        
        # Proceder con el CK
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Eliminar todas las referencias del usuario
            tables_to_clean = [
                'bank_accounts', 'transactions', 'fines', 'loans', 
                'inventory', 'licenses', 'sanctions', 'arrests'
            ]
            
            for table in tables_to_clean:
                cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (usuario.id,))
            
            # Eliminar el usuario principal
            cursor.execute('DELETE FROM users WHERE user_id = ?', (usuario.id,))
            
            conn.commit()
        
        # Crear embed de confirmación
        ck_embed = create_success_embed(
            f"Character Kill ejecutado exitosamente\n"
            f"**Usuario:** {usuario.display_name} ({usuario.id})\n"
            f"**Ejecutado por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}\n\n"
            f"Todos los datos del personaje han sido eliminados permanentemente."
        )
        
        await interaction.followup.send(embed=ck_embed)
        
        # Notificar al usuario
        dm_embed = create_embed(
            "💀 Character Kill Ejecutado",
            f"**Servidor:** {interaction.guild.name}\n"
            f"**Ejecutado por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}\n\n"
            f"Tu personaje ha sido eliminado completamente del sistema de roleplay.",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="eliminar-documentacion", description="Eliminar documentación específica de un usuario")
    @app_commands.describe(
        usuario="Usuario al que eliminar documentación",
        tipo="Tipo de documentación a eliminar"
    )
    @app_commands.choices(tipo=[
        app_commands.Choice(name="DNI", value="dni"),
        app_commands.Choice(name="Licencia de Armas", value="armas"),
        app_commands.Choice(name="Licencia de Conducir", value="conducir"),
        app_commands.Choice(name="Todas las Licencias", value="todas_licencias"),
        app_commands.Choice(name="Todo", value="todo")
    ])
    async def eliminar_documentacion(self, interaction: discord.Interaction, usuario: discord.Member, tipo: str):
        """Eliminar documentación específica de un usuario"""
        if not has_role(interaction.user, ["owners"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los owners pueden usar este comando."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if tipo == "dni":
                # Eliminar DNI
                cursor.execute('''
                    UPDATE users 
                    SET dni = NULL, dni_issued_at = NULL
                    WHERE user_id = ?
                ''', (usuario.id,))
                
                cursor.execute('''
                    DELETE FROM licenses
                    WHERE user_id = ? AND license_type = 'dni'
                ''', (usuario.id,))
                
                doc_text = "DNI"
                
            elif tipo == "armas":
                # Eliminar licencia de armas
                cursor.execute('''
                    DELETE FROM licenses
                    WHERE user_id = ? AND license_type = 'armas'
                ''', (usuario.id,))
                
                doc_text = "Licencia de Armas"
                
            elif tipo == "conducir":
                # Eliminar licencia de conducir
                cursor.execute('''
                    DELETE FROM licenses
                    WHERE user_id = ? AND license_type = 'conducir'
                ''', (usuario.id,))
                
                doc_text = "Licencia de Conducir"
                
            elif tipo == "todas_licencias":
                # Eliminar todas las licencias
                cursor.execute('''
                    DELETE FROM licenses
                    WHERE user_id = ?
                ''', (usuario.id,))
                
                doc_text = "Todas las Licencias"
                
            elif tipo == "todo":
                # Eliminar toda la documentación
                cursor.execute('''
                    UPDATE users 
                    SET dni = NULL, dni_issued_at = NULL
                    WHERE user_id = ?
                ''', (usuario.id,))
                
                cursor.execute('''
                    DELETE FROM licenses
                    WHERE user_id = ?
                ''', (usuario.id,))
                
                doc_text = "Toda la Documentación"
            
            conn.commit()
        
        # Crear embed de confirmación
        embed = create_success_embed(
            f"Documentación eliminada exitosamente\n"
            f"**Usuario:** {usuario.display_name}\n"
            f"**Documentación:** {doc_text}\n"
            f"**Eliminado por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al usuario
        dm_embed = create_embed(
            "📄 Documentación Eliminada",
            f"**Servidor:** {interaction.guild.name}\n"
            f"**Documentación:** {doc_text}\n"
            f"**Eliminado por:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}",
            discord.Color.orange()
        )
        await send_dm(usuario, dm_embed)
