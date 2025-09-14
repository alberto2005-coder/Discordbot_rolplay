import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from config import Config
import random

class EconomicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="cuenta-crear", description="Crear una cuenta bancaria")
    @app_commands.describe(banco="Nombre del banco donde crear la cuenta")
    @app_commands.choices(banco=[
        app_commands.Choice(name="Banco Central", value="Banco Central")
    ])
    async def crear_cuenta(self, interaction: discord.Interaction, banco: str):
        """Crear una nueva cuenta bancaria"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(interaction.user.id, interaction.user.display_name)
        
        # Crear cuenta bancaria
        success = self.db.create_bank_account(interaction.user.id, banco)
        
        if success:
            embed = create_success_embed(
                f"Cuenta creada exitosamente en {banco} con un saldo inicial de {format_currency(Config.INITIAL_BALANCE)}"
            )
        else:
            embed = create_error_embed(f"Ya tienes una cuenta en {banco}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cuenta-ver", description="Ver información de tus cuentas bancarias")
    async def ver_cuenta(self, interaction: discord.Interaction):
        """Ver información de las cuentas bancarias del usuario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="💳 Información de Cuentas Bancarias",
            color=discord.Color.blue()
        )
        
        for banco in Config.AVAILABLE_BANKS:
            balance = self.db.get_user_balance(interaction.user.id, banco)
            if balance > 0:
                embed.add_field(
                    name=f"🏦 {banco}",
                    value=f"Saldo: {format_currency(balance)}",
                    inline=True
                )
        
        if len(embed.fields) == 0:
            embed.description = "No tienes cuentas bancarias. Usa `/cuenta-crear` para crear una."
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dinero-dar", description="Dar dinero a otro usuario")
    @app_commands.describe(
        usuario="Usuario al que dar dinero",
        cantidad="Cantidad a dar",
        banco="Banco desde el cual transferir"
    )
    @app_commands.choices(banco=[
        app_commands.Choice(name="Banco Central", value="Banco Central")
    ])
    async def dar_dinero(self, interaction: discord.Interaction, usuario: discord.Member, cantidad: float, banco: str = "Banco Central"):
        """Transferir dinero a otro usuario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        if not is_valid_amount(cantidad):
            await interaction.response.send_message(
                embed=create_error_embed("Cantidad inválida."),
                ephemeral=True
            )
            return
        
        # Verificar saldo suficiente
        sender_balance = self.db.get_user_balance(interaction.user.id, banco)
        if sender_balance < cantidad:
            await interaction.response.send_message(
                embed=create_error_embed("No tienes suficiente dinero."),
                ephemeral=True
            )
            return
        
        # Registrar usuario receptor si no existe
        self.db.register_user(usuario.id, usuario.display_name)
        
        # Realizar transferencia
        self.db.update_balance(interaction.user.id, -cantidad, banco)
        self.db.update_balance(usuario.id, cantidad, banco)
        
        # Registrar transacciones
        self.db.add_transaction(interaction.user.id, "transferencia_enviada", -cantidad, f"Transferencia a {usuario.display_name}")
        self.db.add_transaction(usuario.id, "transferencia_recibida", cantidad, f"Transferencia de {interaction.user.display_name}")
        
        embed = create_success_embed(
            f"Transferencia realizada: {format_currency(cantidad)} enviados a {usuario.display_name} desde {banco}"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notificar al receptor
        dm_embed = create_embed(
            "💰 Transferencia Recibida",
            f"Has recibido {format_currency(cantidad)} de {interaction.user.display_name} en {banco}",
            discord.Color.green()
        )
        await send_dm(usuario, dm_embed)
    
    @app_commands.command(name="dinero-depositar", description="Depositar dinero en efectivo al banco")
    @app_commands.describe(
        cantidad="Cantidad a depositar",
        banco="Banco donde depositar"
    )
    @app_commands.choices(banco=[
        app_commands.Choice(name="Banco Central", value="Banco Central")
    ])
    async def depositar_dinero(self, interaction: discord.Interaction, cantidad: float, banco: str = "Banco Central"):
        """Depositar dinero en efectivo al banco"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        if not is_valid_amount(cantidad):
            await interaction.response.send_message(
                embed=create_error_embed("Cantidad inválida."),
                ephemeral=True
            )
            return
        
        # Actualizar balance
        self.db.update_balance(interaction.user.id, cantidad, banco)
        self.db.add_transaction(interaction.user.id, "deposito", cantidad, f"Depósito en {banco}")
        
        embed = create_success_embed(
            f"Depósito realizado: {format_currency(cantidad)} depositados en {banco}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dinero-retirar", description="Retirar dinero del banco")
    @app_commands.describe(
        cantidad="Cantidad a retirar",
        banco="Banco desde donde retirar"
    )
    @app_commands.choices(banco=[
        app_commands.Choice(name="Banco Central", value="Banco Central")
    ])
    async def retirar_dinero(self, interaction: discord.Interaction, cantidad: float, banco: str = "Banco Central"):
        """Retirar dinero del banco"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        if not is_valid_amount(cantidad):
            await interaction.response.send_message(
                embed=create_error_embed("Cantidad inválida."),
                ephemeral=True
            )
            return
        
        # Verificar saldo suficiente
        balance = self.db.get_user_balance(interaction.user.id, banco)
        if balance < cantidad:
            await interaction.response.send_message(
                embed=create_error_embed("No tienes suficiente dinero en el banco."),
                ephemeral=True
            )
            return
        
        # Actualizar balance
        self.db.update_balance(interaction.user.id, -cantidad, banco)
        self.db.add_transaction(interaction.user.id, "retiro", -cantidad, f"Retiro de {banco}")
        
        embed = create_success_embed(
            f"Retiro realizado: {format_currency(cantidad)} retirados de {banco}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="casino", description="Jugar en el casino")
    @app_commands.describe(cantidad="Cantidad a apostar")
    async def casino(self, interaction: discord.Interaction, cantidad: float):
        """Jugar en el casino"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        if cantidad < Config.CASINO_MIN_BET or cantidad > Config.CASINO_MAX_BET:
            await interaction.response.send_message(
                embed=create_error_embed(f"La apuesta debe estar entre {format_currency(Config.CASINO_MIN_BET)} y {format_currency(Config.CASINO_MAX_BET)}"),
                ephemeral=True
            )
            return
        
        # Verificar saldo suficiente
        balance = self.db.get_user_balance(interaction.user.id)
        if balance < cantidad:
            await interaction.response.send_message(
                embed=create_error_embed("No tienes suficiente dinero."),
                ephemeral=True
            )
            return
        
        # Jugar
        result, amount, game_info = casino_game(cantidad)
        
        if result is True:
            # Ganó
            self.db.update_balance(interaction.user.id, amount - cantidad)
            self.db.add_transaction(interaction.user.id, "casino_ganancia", amount - cantidad, "Ganancia en casino")
            embed = create_success_embed(f"🎉 ¡Ganaste!\n{game_info}\nGanaste: {format_currency(amount - cantidad)}")
        elif result is False:
            # Perdió
            self.db.update_balance(interaction.user.id, -cantidad)
            self.db.add_transaction(interaction.user.id, "casino_perdida", -cantidad, "Pérdida en casino")
            embed = create_error_embed(f"😔 Perdiste\n{game_info}\nPerdiste: {format_currency(cantidad)}")
        else:
            # Empate
            embed = create_warning_embed(f"🤝 Empate\n{game_info}\nRecuperas tu apuesta: {format_currency(cantidad)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pedir-prestamo", description="Solicitar un préstamo")
    @app_commands.describe(
        cantidad="Cantidad del préstamo",
        banco="Banco donde depositar el préstamo"
    )
    @app_commands.choices(banco=[
        app_commands.Choice(name="Banco Central", value="Banco Central")
    ])
    async def pedir_prestamo(self, interaction: discord.Interaction, cantidad: float, banco: str = "Banco Central"):
        """Solicitar un préstamo"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        if cantidad > Config.MAX_LOAN_AMOUNT or not is_valid_amount(cantidad):
            await interaction.response.send_message(
                embed=create_error_embed(f"La cantidad del préstamo debe ser máximo {format_currency(Config.MAX_LOAN_AMOUNT)}"),
                ephemeral=True
            )
            return
        
        # Verificar que el usuario tenga cuenta en el banco seleccionado
        balance = self.db.get_user_balance(interaction.user.id, banco)
        if balance < 0:  # No existe la cuenta
            await interaction.response.send_message(
                embed=create_error_embed(f"No tienes cuenta en {banco}. Usa `/cuenta-crear` primero."),
                ephemeral=True
            )
            return
        
        # Calcular fecha de vencimiento (30 días)
        due_date = datetime.now() + timedelta(days=30)
        total_payment = calculate_loan_payment(cantidad)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya tiene préstamos activos
            cursor.execute('''
                SELECT COUNT(*) FROM loans
                WHERE user_id = ? AND paid = FALSE
            ''', (interaction.user.id,))
            
            active_loans = cursor.fetchone()[0]
            
            if active_loans > 0:
                await interaction.response.send_message(
                    embed=create_error_embed("Ya tienes un préstamo activo. Págalo antes de solicitar otro."),
                    ephemeral=True
                )
                return
            
            # Crear préstamo
            cursor.execute('''
                INSERT INTO loans (user_id, amount, due_date)
                VALUES (?, ?, ?)
            ''', (interaction.user.id, cantidad, due_date))
            
            conn.commit()
        
        # Añadir dinero a la cuenta especificada
        self.db.update_balance(interaction.user.id, cantidad, banco)
        self.db.add_transaction(interaction.user.id, "prestamo", cantidad, f"Préstamo de {format_currency(cantidad)} en {banco}")
        
        embed = create_success_embed(
            f"Préstamo aprobado!\n"
            f"Cantidad: {format_currency(cantidad)}\n"
            f"Banco: {banco}\n"
            f"Total a pagar: {format_currency(total_payment)}\n"
            f"Fecha límite: {format_datetime(due_date)}\n"
            f"Interés: {Config.LOAN_INTEREST_RATE * 100}%"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="pagar-prestamo", description="Pagar un préstamo")
    async def pagar_prestamo(self, interaction: discord.Interaction):
        """Pagar préstamos pendientes"""
        if not has_role(interaction.user, ["deudor", "verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("No tienes permisos para usar este comando."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener préstamos activos
            cursor.execute('''
                SELECT id, amount, due_date FROM loans
                WHERE user_id = ? AND paid = FALSE
                ORDER BY due_date ASC
            ''', (interaction.user.id,))
            
            loans = cursor.fetchall()
            
            if not loans:
                await interaction.response.send_message(
                    embed=create_warning_embed("No tienes préstamos pendientes."),
                    ephemeral=True
                )
                return
            
            # Pagar el primer préstamo
            loan_id, original_amount, due_date = loans[0]
            total_payment = calculate_loan_payment(original_amount)
            
            # Verificar saldo suficiente (balance total de todos los bancos)
            balance = self.db.get_user_total_balance(interaction.user.id)
            if balance < total_payment:
                await interaction.response.send_message(
                    embed=create_error_embed(f"No tienes suficiente dinero. Necesitas {format_currency(total_payment)}. Balance actual: {format_currency(balance)}"),
                    ephemeral=True
                )
                return
            
            # Realizar pago
            cursor.execute('''
                UPDATE loans SET paid = TRUE
                WHERE id = ?
            ''', (loan_id,))
            
            conn.commit()
        
        # Realizar pago automáticamente del banco con más fondos
        success = self.db.deduct_payment(interaction.user.id, total_payment)
        if not success:
            await interaction.response.send_message(
                embed=create_error_embed("Error al procesar el pago del préstamo."),
                ephemeral=True
            )
            return
        
        self.db.add_transaction(interaction.user.id, "pago_prestamo", -total_payment, f"Pago de préstamo #{loan_id}")
        
        embed = create_success_embed(
            f"Préstamo pagado exitosamente!\n"
            f"Cantidad pagada: {format_currency(total_payment)}\n"
            f"Préstamo original: {format_currency(original_amount)}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
