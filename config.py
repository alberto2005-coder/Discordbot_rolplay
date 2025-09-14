import os

class Config:
    # Configuración del bot
    BOT_PREFIX = "!"
    
    # Nombres de los bancos disponibles
    AVAILABLE_BANKS = ["Banco Central"]
    
    # Configuración económica
    INITIAL_BALANCE = 1500.0
    MAX_LOAN_AMOUNT = 10000.0
    LOAN_INTEREST_RATE = 0.05  # 5%
    CASINO_MIN_BET = 10.0
    CASINO_MAX_BET = 1000.0
    
    # Configuración de roles (IDs de roles de Discord)
    ROLES = {
        "owners": "owners",
        "staff": "staff", 
        "mod": "mod",
        "dt": "DT",
        "verificado": "verificado",
        "miembro_policial": "miembro de un cuerpo policial",
        "civil": "civil",
        "deudor": "deudor",
        "encargado_economia": "encargado economía",
        "desempleado": "desempleado",
        "empleado": "empleado"
    }
    
    # Configuración de licencias
    LICENSE_PRICES = {
        "dni": 100.0,
        "armas": 500.0,
        "conducir": 300.0
    }
    
    # Configuración de multas
    DEFAULT_FINE_AMOUNTS = {
        "exceso_velocidad": 200.0,
        "conducir_sin_licencia": 500.0,
        "portar_armas_ilegales": 1000.0,
        "alteracion_orden": 300.0
    }
    
    # Configuración de sueldos
    SALARY_AMOUNTS = {
        "desempleado": 800.0,
        "empleado": 1200.0,
        "jefe de empresa": 1700.0,
        "dt": 1550.0,
        "bombero": 1600.0,
        "miembro de un cuerpo sanitario": 1600.0,
        "miembro de policía nacional": 1700.0,
        "miembro de policía local": 1650.0,
        "miembro de guardia civil": 1800.0,
        "sub-jefe policía local": 1800.0,
        "sub-jefe de bomberos": 1800.0,
        "sub-jefe policía nacional": 2000.0,
        "sub-jefe guardia civil": 2200.0,
        "jefe policía local": 2000.0,
        "jefe bomberos": 2000.0,
        "jefe policía nacional": 2200.0,
        "jefe guardia civil": 2400.0,
        "premium": 5000.0
    }
    
    # Límite máximo de multas
    MAX_FINE_AMOUNT = 1500.0
    
    # Roles que se asignan automáticamente al comprar items
    ITEM_ROLES = {
        "seguro de vehiculo": "seguro vehicular",
        "casa pequeña": "propietario casa pequeña",
        "establecimiento empresarial": "propietario empresa",
        "casa de campo": "propietario casa campo",
        "casa grande": "propietario casa grande",
        "beretta m9": "licencia de armas (beretta m9)"
    }
    
    # Duración de licencias en días
    LICENSE_DURATION_DAYS = {
        "dni": 3650,  # 10 años
        "armas": 365,  # 1 año
        "conducir": 1825  # 5 años
    }
