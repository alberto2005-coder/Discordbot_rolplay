import discord
from datetime import datetime, timedelta
import random
from config import Config

def has_role(member: discord.Member, required_roles: list) -> bool:
    """Verifica si un miembro tiene alguno de los roles requeridos"""
    if not member.roles:
        return False
    
    member_roles = [role.name.lower() for role in member.roles]
    
    for required_role in required_roles:
        if required_role.lower() in member_roles:
            return True
    
    return False

def format_currency(amount: float) -> str:
    """Formatea una cantidad de dinero"""
    return f"{amount:,.2f} €"

def format_datetime(dt: datetime) -> str:
    """Formatea una fecha y hora"""
    return dt.strftime("%d/%m/%Y %H:%M")

def create_embed(title: str, description: str = None, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Crea un embed básico"""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.timestamp = datetime.utcnow()
    return embed

def create_error_embed(message: str) -> discord.Embed:
    """Crea un embed de error"""
    return create_embed("❌ Error", message, discord.Color.red())

def create_success_embed(message: str) -> discord.Embed:
    """Crea un embed de éxito"""
    return create_embed("✅ Éxito", message, discord.Color.green())

def create_warning_embed(message: str) -> discord.Embed:
    """Crea un embed de advertencia"""
    return create_embed("⚠️ Advertencia", message, discord.Color.orange())

def roll_dice() -> int:
    """Simula el lanzamiento de un dado"""
    return random.randint(1, 6)

def casino_game(bet_amount: float) -> tuple:
    """Simula un juego de casino simple"""
    player_roll = roll_dice() + roll_dice()
    house_roll = roll_dice() + roll_dice()
    
    if player_roll > house_roll:
        # Jugador gana
        winnings = bet_amount * 2
        return True, winnings, f"🎲 Jugador: {player_roll} | Casa: {house_roll}"
    elif player_roll == house_roll:
        # Empate
        return None, bet_amount, f"🎲 Jugador: {player_roll} | Casa: {house_roll} (Empate)"
    else:
        # Casa gana
        return False, 0, f"🎲 Jugador: {player_roll} | Casa: {house_roll}"

def generate_dni() -> str:
    """Genera un número de DNI aleatorio"""
    return f"{random.randint(10000000, 99999999)}"

def calculate_loan_payment(amount: float, interest_rate: float = Config.LOAN_INTEREST_RATE) -> float:
    """Calcula el pago total de un préstamo con intereses"""
    return amount * (1 + interest_rate)

def is_valid_amount(amount: float) -> bool:
    """Verifica si una cantidad es válida"""
    return amount > 0 and amount <= 999999999

def get_bank_list() -> str:
    """Obtiene la lista de bancos disponibles"""
    return ", ".join(Config.AVAILABLE_BANKS)

async def send_dm(user: discord.User, embed: discord.Embed) -> bool:
    """Envía un mensaje directo a un usuario"""
    try:
        await user.send(embed=embed)
        return True
    except discord.Forbidden:
        return False
    except Exception:
        return False

def parse_mention(mention: str) -> int:
    """Extrae el ID de usuario de una mención"""
    if mention.startswith('<@') and mention.endswith('>'):
        mention = mention[2:-1]
        if mention.startswith('!'):
            mention = mention[1:]
        try:
            return int(mention)
        except ValueError:
            return None
    return None

def get_role_hierarchy() -> dict:
    """Devuelve la jerarquía de roles para verificaciones"""
    return {
        "owners": 10,
        "staff": 8,
        "mod": 6,
        "dt": 5,
        "miembro de un cuerpo policial": 4,
        "encargado economía": 3,
        "verificado": 2,
        "civil": 2,
        "empleado": 1,
        "desempleado": 1,
        "deudor": 0
    }
