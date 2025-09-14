import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from utils import *
from config import Config

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="tienda", description="Ver la tienda de objetos")
    async def tienda(self, interaction: discord.Interaction):
        """Mostrar la tienda de objetos"""
        if not has_role(interaction.user, ["civil"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo civiles pueden acceder a la tienda."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, price, description, category FROM shop_items
                WHERE available = TRUE
                ORDER BY category, price ASC
            ''')
            
            items = cursor.fetchall()
        
        if not items:
            await interaction.response.send_message(
                embed=create_warning_embed("La tienda está cerrada temporalmente."),
                ephemeral=True
            )
            return
        
        # Agrupar por categorías
        categories = {}
        for name, price, description, category in items:
            if category not in categories:
                categories[category] = []
            categories[category].append((name, price, description))
        
        embed = discord.Embed(
            title="🏪 Tienda de Objetos",
            description="Usa `/comprar-objeto` para comprar un artículo",
            color=discord.Color.gold()
        )
        
        for category, category_items in categories.items():
            item_list = []
            for name, price, description in category_items:
                item_list.append(f"**{name}** - {format_currency(price)}\n{description}\n")
            
            embed.add_field(
                name=f"📦 {category.title()}",
                value="\n".join(item_list),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="comprar-objeto", description="Comprar un objeto de la tienda")
    @app_commands.describe(
        objeto="Nombre del objeto a comprar",
        cantidad="Cantidad a comprar"
    )
    async def comprar_objeto(self, interaction: discord.Interaction, objeto: str, cantidad: int = 1):
        """Comprar un objeto de la tienda"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden comprar objetos."),
                ephemeral=True
            )
            return
        
        if cantidad <= 0:
            await interaction.response.send_message(
                embed=create_error_embed("La cantidad debe ser mayor a 0."),
                ephemeral=True
            )
            return
        
        # Registrar usuario si no existe
        self.db.register_user(interaction.user.id, interaction.user.display_name)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el objeto existe y está disponible
            cursor.execute('''
                SELECT price, description FROM shop_items
                WHERE name = ? AND available = TRUE
            ''', (objeto,))
            
            item_data = cursor.fetchone()
            
            if not item_data:
                await interaction.response.send_message(
                    embed=create_error_embed("Objeto no encontrado o no disponible."),
                    ephemeral=True
                )
                return
            
            price, description = item_data
            total_cost = price * cantidad
            
            # Verificar saldo suficiente (balance total de todos los bancos)
            balance = self.db.get_user_total_balance(interaction.user.id)
            if balance < total_cost:
                await interaction.response.send_message(
                    embed=create_error_embed(f"No tienes suficiente dinero. Necesitas {format_currency(total_cost)}. Balance actual: {format_currency(balance)}"),
                    ephemeral=True
                )
                return
            
            # Verificar si ya tiene el objeto en el inventario
            cursor.execute('''
                SELECT quantity FROM inventory
                WHERE user_id = ? AND item_name = ?
            ''', (interaction.user.id, objeto))
            
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Actualizar cantidad existente
                new_quantity = existing_item[0] + cantidad
                cursor.execute('''
                    UPDATE inventory
                    SET quantity = ?
                    WHERE user_id = ? AND item_name = ?
                ''', (new_quantity, interaction.user.id, objeto))
            else:
                # Añadir nuevo objeto al inventario
                cursor.execute('''
                    INSERT INTO inventory (user_id, item_name, quantity, value)
                    VALUES (?, ?, ?, ?)
                ''', (interaction.user.id, objeto, cantidad, price))
            
            conn.commit()
        
        # Cobrar el objeto
        success = self.db.deduct_payment(interaction.user.id, total_cost)
        if not success:
            await interaction.response.send_message(
                embed=create_error_embed("Error al procesar el pago."),
                ephemeral=True
            )
            return
        
        self.db.add_transaction(interaction.user.id, "compra_objeto", -total_cost, f"Compra de {cantidad}x {objeto}")
        
        # Asignar rol automáticamente si corresponde
        role_message = ""
        if objeto.lower() in Config.ITEM_ROLES:
            role_name = Config.ITEM_ROLES[objeto.lower()]
            try:
                # Buscar el rol en el servidor
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    await interaction.user.add_roles(role)
                    role_message = f"\n**Rol asignado:** {role_name}"
            except Exception:
                pass  # Si no se puede asignar el rol, continúa sin error
        
        embed = create_success_embed(
            f"Compra realizada exitosamente\n"
            f"**Objeto:** {objeto}\n"
            f"**Cantidad:** {cantidad}\n"
            f"**Precio unitario:** {format_currency(price)}\n"
            f"**Total:** {format_currency(total_cost)}\n"
            f"**Descripción:** {description}{role_message}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="inventario", description="Ver tu inventario")
    async def inventario(self, interaction: discord.Interaction):
        """Ver el inventario del usuario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver su inventario."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT item_name, quantity, value, acquired_at FROM inventory
                WHERE user_id = ?
                ORDER BY acquired_at DESC
            ''', (interaction.user.id,))
            
            items = cursor.fetchall()
        
        embed = discord.Embed(
            title=f"🎒 Inventario de {interaction.user.display_name}",
            color=discord.Color.blue()
        )
        
        if not items:
            embed.description = "Tu inventario está vacío. Visita la `/tienda` para comprar objetos."
        else:
            total_value = 0
            item_list = []
            
            for item_name, quantity, value, acquired_at in items:
                item_value = value * quantity
                total_value += item_value
                
                item_list.append(
                    f"**{item_name}** x{quantity}\n"
                    f"Valor: {format_currency(item_value)}\n"
                    f"Adquirido: {acquired_at[:10]}\n"
                )
            
            embed.description = "\n".join(item_list)
            embed.add_field(
                name="💰 Valor Total",
                value=format_currency(total_value),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="mirar-inventario", description="Ver el inventario de otro usuario")
    @app_commands.describe(usuario="Usuario del que ver el inventario")
    async def mirar_inventario(self, interaction: discord.Interaction, usuario: discord.Member):
        """Ver el inventario de otro usuario (solo staff/mod)"""
        if not has_role(interaction.user, ["mod", "staff"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo moderadores y staff pueden ver inventarios de otros usuarios."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT item_name, quantity, value, acquired_at FROM inventory
                WHERE user_id = ?
                ORDER BY acquired_at DESC
            ''', (usuario.id,))
            
            items = cursor.fetchall()
        
        embed = discord.Embed(
            title=f"🔍 Inventario de {usuario.display_name}",
            color=discord.Color.orange()
        )
        
        if not items:
            embed.description = "Este usuario no tiene objetos en su inventario."
        else:
            total_value = 0
            item_list = []
            
            for item_name, quantity, value, acquired_at in items:
                item_value = value * quantity
                total_value += item_value
                
                item_list.append(
                    f"**{item_name}** x{quantity}\n"
                    f"Valor: {format_currency(item_value)}\n"
                    f"Adquirido: {acquired_at[:10]}\n"
                )
            
            embed.description = "\n".join(item_list)
            embed.add_field(
                name="💰 Valor Total",
                value=format_currency(total_value),
                inline=False
            )
        
        embed.set_footer(text=f"Consultado por {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="armeria", description="Ver tu colección de armas")
    async def armeria(self, interaction: discord.Interaction):
        """Ver las armas en el inventario"""
        if not has_role(interaction.user, ["verificado"]):
            await interaction.response.send_message(
                embed=create_error_embed("Solo usuarios verificados pueden ver su armería."),
                ephemeral=True
            )
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener armas del inventario
            cursor.execute('''
                SELECT i.item_name, i.quantity, i.value, i.acquired_at
                FROM inventory i
                JOIN shop_items s ON i.item_name = s.name
                WHERE i.user_id = ? AND s.category = 'armas'
                ORDER BY i.acquired_at DESC
            ''', (interaction.user.id,))
            
            weapons = cursor.fetchall()
            
            # Verificar licencia de armas
            cursor.execute('''
                SELECT expires_at, valid FROM licenses
                WHERE user_id = ? AND license_type = 'armas'
                ORDER BY issued_at DESC LIMIT 1
            ''', (interaction.user.id,))
            
            license_data = cursor.fetchone()
        
        embed = discord.Embed(
            title=f"🔫 Armería de {interaction.user.display_name}",
            color=discord.Color.red()
        )
        
        # Verificar estado de licencia
        license_status = "❌ Sin licencia"
        if license_data:
            expires_at, valid = license_data
            if valid and datetime.fromisoformat(expires_at) > datetime.now():
                license_status = "✅ Licencia válida"
            elif valid:
                license_status = "⚠️ Licencia expirada"
            else:
                license_status = "❌ Licencia revocada"
        
        embed.add_field(
            name="📋 Estado de Licencia",
            value=license_status,
            inline=False
        )
        
        if not weapons:
            embed.description = "No tienes armas en tu inventario."
        else:
            total_value = 0
            weapon_list = []
            
            for weapon_name, quantity, value, acquired_at in weapons:
                weapon_value = value * quantity
                total_value += weapon_value
                
                weapon_list.append(
                    f"**{weapon_name}** x{quantity}\n"
                    f"Valor: {format_currency(weapon_value)}\n"
                    f"Adquirido: {acquired_at[:10]}\n"
                )
            
            embed.description = "\n".join(weapon_list)
            embed.add_field(
                name="💰 Valor Total de Armas",
                value=format_currency(total_value),
                inline=True
            )
        
        if license_status == "❌ Sin licencia" and weapons:
            embed.add_field(
                name="⚠️ Advertencia",
                value="Portar armas sin licencia es ilegal",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
