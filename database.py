import sqlite3
import logging
from datetime import datetime, timedelta
import json
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="roleplay_bot.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def initialize(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dni TEXT UNIQUE,
                    dni_issued_at TIMESTAMP,
                    nombre TEXT,
                    apellido TEXT,
                    edad INTEGER,
                    fecha_nacimiento TEXT,
                    sexo TEXT,
                    nacionalidad TEXT
                )
            ''')
            
            # Tabla de cuentas bancarias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bank_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bank_name TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, bank_name)
                )
            ''')
            
            # Tabla de transacciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de multas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    officer_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    reason TEXT NOT NULL,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid BOOLEAN DEFAULT FALSE,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (officer_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de préstamos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    interest_rate REAL DEFAULT 0.05,
                    due_date TIMESTAMP NOT NULL,
                    paid BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de inventario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    value REAL DEFAULT 0.0,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de licencias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    license_type TEXT NOT NULL,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    valid BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, license_type)
                )
            ''')
            
            # Tabla de sanciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sanctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    staff_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    duration_hours INTEGER,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (staff_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de arrestos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS arrests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    officer_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    arrested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    released_at TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (officer_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de tienda
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shop_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    available BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de historias de usuario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    story_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabla de incautaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seizures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    officer_id INTEGER NOT NULL,
                    model TEXT NOT NULL,
                    license_plate TEXT NOT NULL,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (officer_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente")
            
            # Insertar elementos de tienda por defecto
            self._populate_default_shop_items()
    
    def _populate_default_shop_items(self):
        """Puebla la tienda con elementos por defecto"""
        default_items = [
            ("Seguro de vehiculo", 300.0, "Seguro para protección vehicular", "seguros"),
            ("Beretta M9", 1750.0, "Pistola Beretta M9 para portación", "armas"),
            ("Dron", 2000.0, "Dron para vigilancia y uso recreativo", "tecnologia"),
            ("Bate", 15.0, "Bate de béisbol", "herramientas"),
            ("Navaja", 30.0, "Navaja plegable", "herramientas"),
            ("Spray", 45.0, "Spray de defensa personal", "herramientas"),
            ("Casa pequeña", 15000.0, "Casa residencial pequeña", "propiedades"),
            ("Establecimiento empresarial", 20000.0, "Local comercial para negocio", "propiedades"),
            ("Casa de campo", 25000.0, "Casa en zona rural", "propiedades"),
            ("Casa grande", 35000.0, "Casa residencial grande", "propiedades")
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for item in default_items:
                cursor.execute('''
                    INSERT OR IGNORE INTO shop_items (name, price, description, category)
                    VALUES (?, ?, ?, ?)
                ''', item)
            
            conn.commit()
    
    def register_user(self, user_id: int, username: str):
        """Registra un nuevo usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)
            ''', (user_id, username))
            
            conn.commit()
    
    def get_user_balance(self, user_id: int, bank_name: str = "Banco Central"):
        """Obtiene el balance de un usuario en un banco específico"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT balance FROM bank_accounts
                WHERE user_id = ? AND bank_name = ?
            ''', (user_id, bank_name))
            
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def get_user_total_balance(self, user_id: int):
        """Obtiene el balance total de un usuario en todos los bancos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(balance) FROM bank_accounts
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0
    
    def deduct_payment(self, user_id: int, amount: float):
        """Descuenta dinero del usuario, priorizando el banco con más fondos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener cuentas ordenadas por balance (mayor a menor)
            cursor.execute('''
                SELECT bank_name, balance 
                FROM bank_accounts 
                WHERE user_id = ? AND balance > 0
                ORDER BY balance DESC
            ''', (user_id,))
            
            accounts = cursor.fetchall()
            remaining_amount = amount
            
            for bank_name, balance in accounts:
                if remaining_amount <= 0:
                    break
                
                deduct = min(remaining_amount, balance)
                
                cursor.execute('''
                    UPDATE bank_accounts
                    SET balance = balance - ?
                    WHERE user_id = ? AND bank_name = ?
                ''', (deduct, user_id, bank_name))
                
                remaining_amount -= deduct
            
            conn.commit()
            return remaining_amount == 0  # True si se pudo descontar todo
    
    def create_bank_account(self, user_id: int, bank_name: str):
        """Crea una cuenta bancaria para un usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO bank_accounts (user_id, bank_name, balance)
                VALUES (?, ?, ?)
            ''', (user_id, bank_name, Config.INITIAL_BALANCE))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_balance(self, user_id: int, amount: float, bank_name: str = "Banco Central"):
        """Actualiza el balance de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE bank_accounts
                SET balance = balance + ?
                WHERE user_id = ? AND bank_name = ?
            ''', (amount, user_id, bank_name))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def add_transaction(self, user_id: int, transaction_type: str, amount: float, description: str = None):
        """Añade una transacción al historial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, transaction_type, amount, description))
            
            conn.commit()
    
    def create_user_story(self, user_id: int, story_text: str):
        """Crea una historia de usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_stories (user_id, story_text)
                VALUES (?, ?)
            ''', (user_id, story_text))
            conn.commit()
    
    def get_user_story(self, user_id: int):
        """Obtiene la historia de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT story_text, created_at FROM user_stories
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()
    
    def create_seizure(self, user_id: int, officer_id: int, model: str, license_plate: str, image_url: str = None):
        """Crea un registro de incautación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO seizures (user_id, officer_id, model, license_plate, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, officer_id, model, license_plate, image_url))
            seizure_id = cursor.lastrowid
            conn.commit()
            return seizure_id
    
    def update_user_dni_info(self, user_id: int, nombre: str, apellido: str, edad: int, fecha_nacimiento: str, sexo: str, nacionalidad: str):
        """Actualiza la información personal del DNI de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET nombre = ?, apellido = ?, edad = ?, fecha_nacimiento = ?, sexo = ?, nacionalidad = ?
                WHERE user_id = ?
            ''', (nombre, apellido, edad, fecha_nacimiento, sexo, nacionalidad, user_id))
            conn.commit()
    
    def revoke_license(self, user_id: int, license_type: str):
        """Revoca una licencia de usuario"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE licenses 
                SET valid = FALSE
                WHERE user_id = ? AND license_type = ?
            ''', (user_id, license_type))
            conn.commit()
