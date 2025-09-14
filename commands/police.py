import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from config import Config
from datetime import datetime, timedelta

class PoliceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="arrestar", description="Arrestar a un usuario")
    @app_commands.describe(
        usuario="Usuario a arrestar",
        razon="Razón del arresto"
    )
    async def arrestar(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        """Arrestar a un usuario"""
        if not has_role(interaction.user, ["miembro de un cuerpo policial"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros de un cuerpo policial pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes arrestarte a ti mismo."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(usuario.id, usuario.display_name)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya está arrestado
            cursor.execute('''
                SELECT COUNT(*) FROM arrests
                WHERE user_id = ? AND active = TRUE
            ''', (usuario.id,))
            
            if cursor.fetchone()[0] > 0:
                await interaction.response.send_message(
                    embed=create_error_embed("Este usuario ya está arrestado."),
                    ephemeral=True
                )
                return
            
            # Crear arresto
            cursor.execute('''
                INSERT INTO arrests (user_id, officer_id, reason)
                VALUES (?, ?, ?)
            ''', (usuario.id, interaction.user.id, razon))
            
            arrest_id = cursor.lastrowid
            conn.commit()
        
        # Crear embed de confirmación
        embed = create_success_embed(
            f"Usuario arrestado exitosamente\n"
            f"**Arrestado:** {usuario.display_name}\n"
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Razón:** {razon}\n"
            f"**ID Arresto:** #{arrest_id}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al arrestado
        dm_embed = create_embed(
            "🚔 Has sido arrestado",
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Razón:** {razon}\n"
            f"**Fecha:** {format_datetime(datetime.now())}",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="multas-poner", description="Poner una multa a un usuario")
    @app_commands.describe(
        usuario="Usuario a multar",
        cantidad="Cantidad de la multa",
        articulos="Artículos infringidos"
    )
    async def poner_multa(self, interaction: discord.Interaction, usuario: discord.Member, cantidad: float, articulos: str):
        """Poner una multa a un usuario"""
        if not has_role(interaction.user, ["miembro de un cuerpo policial"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros de un cuerpo policial pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if not is_valid_amount(cantidad) or cantidad > Config.MAX_FINE_AMOUNT:
            await interaction.response.send_message(
                embed=create_error_embed(f"Esta infracción supera los {format_currency(Config.MAX_FINE_AMOUNT)} y debe tramitarse como arresto."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes multarte a ti mismo."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(usuario.id, usuario.display_name)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear multa
            cursor.execute('''
                INSERT INTO fines (user_id, officer_id, amount, reason)
                VALUES (?, ?, ?, ?)
            ''', (usuario.id, interaction.user.id, cantidad, articulos))
            
            fine_id = cursor.lastrowid
            conn.commit()
        
        # Crear embed de confirmación
        embed = create_success_embed(
            f"Multa impuesta exitosamente\n"
            f"**Multado:** {usuario.display_name}\n"
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Cantidad:** {format_currency(cantidad)}\n"
            f"**Artículos:** {articulos}\n"
            f"**ID Multa:** #{fine_id}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al multado
        dm_embed = create_embed(
            "💸 Has recibido una multa",
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Cantidad:** {format_currency(cantidad)}\n"
            f"**Artículos:** {articulos}\n"
            f"**Fecha:** {format_datetime(datetime.now())}\n\n"
            f"Usa `/pagar-multas` para pagarla.",
            discord.Color.orange()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="multas-ver", description="Ver multas de un usuario")
    @app_commands.describe(usuario="Usuario del que ver las multas")
    async def ver_multas(self, interaction: discord.Interaction, usuario: discord.Member = None):
        """Ver multas de un usuario"""
        if not has_role(interaction.user, ["miembro de un cuerpo policial"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros de un cuerpo policial pueden usar este comando."),
                ephemeral=True
            )
            return
        
        target_user = usuario if usuario else interaction.user
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener multas
            cursor.execute('''
                SELECT f.id, f.amount, f.reason, f.issued_at, f.paid, u.username
                FROM fines f
                JOIN users u ON f.officer_id = u.user_id
                WHERE f.user_id = ?
                ORDER BY f.issued_at DESC
                LIMIT 10
            ''', (target_user.id,))
            
            fines = cursor.fetchall()
        
        embed = discord.Embed(
            title=f"🚨 Multas de {target_user.display_name}",
            color=discord.Color.orange()
        )
        
        if not fines:
            embed.description = "No tiene multas registradas."
        else:
            total_unpaid = 0
            fine_list = []
            
            for fine_id, amount, reason, issued_at, paid, officer in fines:
                status = "✅ Pagada" if paid else "❌ Pendiente"
                if not paid:
                    total_unpaid += amount
                
                fine_list.append(
                    f"**#{fine_id}** - {format_currency(amount)} - {status}\n"
                    f"Razón: {reason}\n"
                    f"Oficial: {officer}\n"
                    f"Fecha: {issued_at[:10]}\n"
                )
            
            embed.description = "\n".join(fine_list)
            
            if total_unpaid > 0:
                embed.add_field(
                    name="💰 Total Pendiente",
                    value=format_currency(total_unpaid),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="eliminar-multa", description="Eliminar una multa")
    @app_commands.describe(multa_id="ID de la multa a eliminar")
    async def eliminar_multa(self, interaction: discord.Interaction, multa_id: int):
        """Eliminar una multa"""
        if not has_role(interaction.user, ["miembro de un cuerpo policial"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros de un cuerpo policial pueden usar este comando."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la multa existe
            cursor.execute('''
                SELECT user_id, amount, reason FROM fines
                WHERE id = ?
            ''', (multa_id,))
            
            fine_data = cursor.fetchone()
            
            if not fine_data:
                await interaction.response.send_message(
                    embed=create_error_embed("Multa no encontrada."),
                    ephemeral=True
                )
                return
            
            # Eliminar multa
            cursor.execute('DELETE FROM fines WHERE id = ?', (multa_id,))
            conn.commit()
        
        user_id, amount, reason = fine_data
        user = self.bot.get_user(user_id)
        username = user.display_name if user else f"Usuario #{user_id}"
        
        embed = create_success_embed(
            f"Multa eliminada exitosamente\n"
            f"**ID:** #{multa_id}\n"
            f"**Usuario:** {username}\n"
            f"**Cantidad:** {format_currency(amount)}\n"
            f"**Razón:** {reason}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="incautar", description="Incautar objetos de un usuario")
    @app_commands.describe(
        usuario="Usuario al que incautar objetos",
        objeto="Nombre del objeto a incautar",
        cantidad="Cantidad a incautar"
    )
    async def incautar(self, interaction: discord.Interaction, usuario: discord.Member, objeto: str, cantidad: int = 1):
        """Incautar objetos de un usuario"""
        if not has_role(interaction.user, ["DT"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros del DT pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if cantidad <= 0:
            await interaction.response.send_message(
                embed=create_error_embed("La cantidad debe ser mayor a 0."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el usuario tiene el objeto
            cursor.execute('''
                SELECT quantity FROM inventory
                WHERE user_id = ? AND item_name = ?
            ''', (usuario.id, objeto))
            
            result = cursor.fetchone()
            
            if not result or result[0] < cantidad:
                await interaction.response.send_message(
                    embed=create_error_embed(f"{usuario.display_name} no tiene suficiente cantidad de {objeto}."),
                    ephemeral=True
                )
                return
            
            # Reducir cantidad del inventario
            new_quantity = result[0] - cantidad
            
            if new_quantity <= 0:
                cursor.execute('''
                    DELETE FROM inventory
                    WHERE user_id = ? AND item_name = ?
                ''', (usuario.id, objeto))
            else:
                cursor.execute('''
                    UPDATE inventory
                    SET quantity = ?
                    WHERE user_id = ? AND item_name = ?
                ''', (new_quantity, usuario.id, objeto))
            
            conn.commit()
        
        embed = create_success_embed(
            f"Incautación realizada exitosamente\n"
            f"**Usuario:** {usuario.display_name}\n"
            f"**Objeto:** {objeto}\n"
            f"**Cantidad:** {cantidad}\n"
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al usuario
        dm_embed = create_embed(
            "📦 Objetos incautados",
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Objeto:** {objeto}\n"
            f"**Cantidad:** {cantidad}\n"
            f"**Fecha:** {format_datetime(datetime.now())}",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="pagar-multas", description="Pagar tus multas pendientes")
    async def pagar_multas(self, interaction: discord.Interaction):
        """Pagar multas pendientes"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener multas pendientes
            cursor.execute('''
                SELECT id, amount FROM fines
                WHERE user_id = ? AND paid = FALSE
                ORDER BY issued_at ASC
            ''', (interaction.user.id,))
            
            fines = cursor.fetchall()
            
            if not fines:
                await interaction.response.send_message(
                    embed=create_warning_embed("No tienes multas pendientes."),
                    ephemeral=True
                )
                return
            
            total_amount = sum(fine[1] for fine in fines)
            
            # Verificar saldo suficiente
            balance = self.db.get_user_balance(interaction.user.id)
            if balance < total_amount:
                await interaction.response.send_message(
                    embed=create_error_embed(
                        f"No tienes suficiente dinero para pagar todas las multas.\n"
                        f"Total necesario: {format_currency(total_amount)}\n"
                        f"Tu saldo: {format_currency(balance)}"
                    ),
                    ephemeral=True
                )
                return
            
            # Pagar todas las multas
            for fine_id, amount in fines:
                cursor.execute('''
                    UPDATE fines
                    SET paid = TRUE, paid_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (fine_id,))
            
            conn.commit()
        
        # Actualizar balance
        self.db.update_balance(interaction.user.id, -total_amount)
        self.db.add_transaction(interaction.user.id, "pago_multas", -total_amount, f"Pago de {len(fines)} multas")
        
        embed = create_success_embed(
            f"Multas pagadas exitosamente\n"
            f"**Cantidad de multas:** {len(fines)}\n"
            f"**Total pagado:** {format_currency(total_amount)}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="revocar-licencia", description="Revocar una licencia a un usuario")
    @app_commands.describe(
        usuario="Usuario al que revocar la licencia",
        tipo_licencia="Tipo de licencia a revocar"
    )
    @app_commands.choices(tipo_licencia=[
        app_commands.Choice(name="Licencia de Conducir", value="conducir"),
        app_commands.Choice(name="Licencia de Armas", value="armas")
    ])
    async def revocar_licencia(self, interaction: discord.Interaction, usuario: discord.Member, tipo_licencia: str):
        """Revocar una licencia a un usuario"""
        if not has_role(interaction.user, ["miembro de un cuerpo policial"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros de un cuerpo policial pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes revocarte una licencia a ti mismo."),
                ephemeral=True
            )
            return
        
        # Revocar la licencia
        self.db.revoke_license(usuario.id, tipo_licencia)
        
        # Quitar el rol correspondiente
        try:
            if tipo_licencia == "conducir":
                role_name = "Licencia de conducir"
            else:  # armas
                role_name = "Licencia de armas (Beretta M9)"
            
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role and role in usuario.roles:
                await usuario.remove_roles(role)
        except Exception:
            pass  # Si no se puede quitar el rol, continúa sin error
        
        tipo_texto = "conducir" if tipo_licencia == "conducir" else "armas"
        
        embed = create_success_embed(
            f"Licencia revocada exitosamente\n"
            f"**Usuario:** {usuario.display_name}\n"
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Tipo:** Licencia de {tipo_texto}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al usuario
        dm_embed = create_embed(
            "❌ Licencia revocada",
            f"**Oficial:** {interaction.user.display_name}\n"
            f"**Licencia:** {tipo_texto}\n"
            f"**Fecha:** {format_datetime(datetime.now())}\n\n"
            f"Tu licencia de {tipo_texto} ha sido revocada.",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="incautar", description="Incautar un vehículo (solo DDT)")
    @app_commands.describe(
        usuario="Usuario al que incautar el vehículo",
        modelo="Modelo del vehículo",
        matricula="Matrícula del vehículo",
        imagen="URL de la imagen del vehículo (opcional)"
    )
    async def incautar(self, interaction: discord.Interaction, usuario: discord.Member, modelo: str, matricula: str, imagen: str = None):
        """Incautar un vehículo a un usuario (solo DDT)"""
        if not has_role(interaction.user, ["dt"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo los miembros del DDT pueden usar este comando."),
                ephemeral=True
            )
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("No puedes incautarte un vehículo a ti mismo."),
                ephemeral=True
            )
            return
        
        # Registrar incautación
        seizure_id = self.db.create_seizure(usuario.id, interaction.user.id, modelo, matricula, imagen)
        
        embed = create_success_embed(
            f"Vehículo incautado exitosamente\n"
            f"**Propietario:** {usuario.display_name}\n"
            f"**Oficial DDT:** {interaction.user.display_name}\n"
            f"**Modelo:** {modelo}\n"
            f"**Matrícula:** {matricula}\n"
            f"**ID Incautación:** #{seizure_id}\n"
            f"**Fecha:** {format_datetime(datetime.now())}"
        )
        
        if imagen:
            embed.set_image(url=imagen)
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al propietario
        dm_embed = create_embed(
            "🚗 Vehículo incautado",
            f"**Oficial DDT:** {interaction.user.display_name}\n"
            f"**Modelo:** {modelo}\n"
            f"**Matrícula:** {matricula}\n"
            f"**Fecha:** {format_datetime(datetime.now())}\n\n"
            f"Tu vehículo ha sido incautado por el DDT.",
            discord.Color.red()
        )
        await send_dm(usuario, dm_embed)
