# 🎭 Bot de Roleplay - Valencia RP

Un bot completo de Discord diseñado para servidores de roleplay con sistemas económicos, policiales, administrativos y de gestión de usuarios.

## 📋 Índice

- [Requisitos de Roles](#requisitos-de-roles)
- [Comandos Económicos](#comandos-económicos)
- [Comandos de Licencias](#comandos-de-licencias)
- [Comandos de Inventario](#comandos-de-inventario)
- [Comandos Policiales](#comandos-policiales)
- [Comandos Administrativos](#comandos-administrativos)
- [Comandos Generales](#comandos-generales)
- [Sistema de Sueldos](#sistema-de-sueldos)
- [Configuración](#configuración)

## 🔐 Requisitos de Roles

### Roles Básicos
- **verificado**: Rol base requerido para la mayoría de comandos
- **civil**: Ciudadano con derechos civiles
- **dni**: Usuario con documentación oficial

### Roles Policiales
- **miembro de un cuerpo policial**: Agentes de policía general
- **dt**: Departamento de Tráfico (DDT)

### Roles Administrativos
- **mod**: Moderadores del servidor
- **staff**: Personal administrativo
- **owners**: Propietarios del servidor

### Roles Económicos
- **deudor**: Usuarios con préstamos pendientes

## 💰 Comandos Económicos

**Rol requerido:** `verificado`

### `/cuenta-crear`
- **Descripción:** Crear una cuenta bancaria en Banco Central
- **Parámetros:** 
  - `banco`: Banco donde crear la cuenta (Solo Banco Central disponible)
- **Saldo inicial:** 1.500 €

### `/cuenta-ver`
- **Descripción:** Ver información de tu cuenta bancaria
- **Muestra:** Saldo actual, banco, fecha de creación

### `/dinero-dar`
- **Descripción:** Transferir dinero a otro usuario
- **Parámetros:**
  - `usuario`: Usuario destinatario
  - `cantidad`: Cantidad a transferir
- **Límites:** Máximo 10.000 € por transferencia

### `/dinero-depositar`
- **Descripción:** Depositar dinero en efectivo a tu cuenta bancaria
- **Parámetros:**
  - `cantidad`: Cantidad a depositar

### `/dinero-retirar`
- **Descripción:** Retirar dinero de tu cuenta bancaria
- **Parámetros:**
  - `cantidad`: Cantidad a retirar

### `/casino`
- **Descripción:** Apostar dinero en el casino
- **Parámetros:**
  - `cantidad`: Cantidad a apostar
- **Límites:** Entre 10 € y 5.000 € por apuesta
- **Probabilidad:** 45% de ganar (ganancia x2)

### `/pedir-prestamo`
- **Descripción:** Solicitar un préstamo bancario
- **Parámetros:**
  - `cantidad`: Cantidad del préstamo
- **Límites:** Entre 100 € y 50.000 €
- **Interés:** 5% sobre el monto solicitado

### `/pagar-prestamo`
- **Descripción:** Pagar préstamos pendientes
- **Rol requerido:** `deudor` o `verificado`

### `/cobrar-sueldo`
- **Descripción:** Cobrar el sueldo según tu rol
- **Frecuencia:** Una vez cada 24 horas
- **Cantidad:** Varía según el rol (ver [Sistema de Sueldos](#sistema-de-sueldos))

## 📄 Comandos de Licencias

### `/solicitar-dni`
- **Descripción:** Solicitar un Documento Nacional de Identidad
- **Rol requerido:** `verificado`
- **Precio:** 150 €
- **Parámetros requeridos:**
  - `nombre`: Tu nombre
  - `apellido`: Tu apellido  
  - `edad`: Tu edad
  - `fecha_nacimiento`: Fecha en formato DD/MM/AAAA
  - `sexo`: Masculino/Femenino/Otro
  - `nacionalidad`: Tu nacionalidad
- **Efecto:** Asigna automáticamente el rol `DNI`

### `/solicitar-licencia-armas`
- **Descripción:** Solicitar licencia de portación de armas
- **Rol requerido:** `civil` + tener `DNI`
- **Precio:** 2.500 €
- **Duración:** 365 días
- **Efecto:** Asigna automáticamente el rol `Licencia de armas (Beretta M9)`

### `/solicitar-licencia-de-conducir`
- **Descripción:** Solicitar licencia de conducir
- **Rol requerido:** `civil` + tener `DNI`
- **Precio:** 1.000 €
- **Duración:** 365 días
- **Efecto:** Asigna automáticamente el rol `Licencia de conducir`

### `/ver-dni`
- **Descripción:** Ver información de tu DNI
- **Rol requerido:** `verificado`
- **Muestra:** Datos personales, número de DNI, fecha de emisión

### `/ver-licencia-de-armas`
- **Descripción:** Ver estado de tu licencia de armas
- **Rol requerido:** `verificado`
- **Muestra:** Estado, fecha de emisión, fecha de vencimiento

### `/ver-licencia-de-conducir`
- **Descripción:** Ver estado de tu licencia de conducir
- **Rol requerido:** `verificado`
- **Muestra:** Estado, fecha de emisión, fecha de vencimiento

## 🛍️ Comandos de Inventario

### `/tienda`
- **Descripción:** Ver todos los artículos disponibles en la tienda
- **Rol requerido:** `civil`
- **Categorías disponibles:**
  - **Seguros:** Seguro de vehículo (300 €)
  - **Armas:** Beretta M9 (1.750 €)
  - **Tecnología:** Dron (2.000 €)
  - **Herramientas:** Bate (15 €), Navaja (30 €), Spray (45 €)
  - **Propiedades:** Casa pequeña (15.000 €), Establecimiento empresarial (20.000 €), Casa de campo (25.000 €), Casa grande (35.000 €)

### `/comprar-objeto`
- **Descripción:** Comprar un artículo de la tienda
- **Rol requerido:** `verificado`
- **Parámetros:**
  - `objeto`: Nombre exacto del objeto
  - `cantidad`: Cantidad a comprar (por defecto: 1)
- **Efectos especiales:**
  - Seguros asignan roles automáticamente
  - Propiedades asignan roles específicos
  - Beretta M9 requiere licencia de armas

### `/inventario`
- **Descripción:** Ver tu inventario personal
- **Rol requerido:** `verificado`
- **Muestra:** Todos los objetos que posees y sus cantidades

### `/mirar-inventario`
- **Descripción:** Ver el inventario de otro usuario
- **Rol requerido:** `mod` o `staff`
- **Parámetros:**
  - `usuario`: Usuario cuyo inventario quieres ver

### `/armeria`
- **Descripción:** Ver tu arsenal de armas y estado de licencias
- **Rol requerido:** `verificado`
- **Muestra:** Armas en posesión y estado de licencia de armas

## 🚔 Comandos Policiales

### `/arrestar`
- **Descripción:** Arrestar a un usuario
- **Rol requerido:** `miembro de un cuerpo policial`
- **Parámetros:**
  - `usuario`: Usuario a arrestar
  - `razon`: Motivo del arresto
- **Efecto:** Registra el arresto en la base de datos, notifica al usuario

### `/multas-poner`
- **Descripción:** Imponer una multa a un usuario
- **Rol requerido:** `miembro de un cuerpo policial`
- **Parámetros:**
  - `usuario`: Usuario a multar
  - `cantidad`: Cantidad de la multa
  - `articulos`: Artículos del código penal infringidos
- **Límite máximo:** 1.500 € (infracciones mayores requieren arresto)

### `/multas-ver`
- **Descripción:** Ver las multas de un usuario
- **Rol requerido:** `miembro de un cuerpo policial`
- **Parámetros:**
  - `usuario`: Usuario cuyas multas quieres ver
- **Muestra:** Historial completo de multas (pagadas y pendientes)

### `/eliminar-multa`
- **Descripción:** Eliminar una multa específica
- **Rol requerido:** `miembro de un cuerpo policial`
- **Parámetros:**
  - `multa_id`: ID de la multa a eliminar

### `/pagar-multas`
- **Descripción:** Pagar todas las multas pendientes
- **Rol requerido:** `verificado`
- **Efecto:** Descuenta el dinero automáticamente de la cuenta

### `/revocar-licencia`
- **Descripción:** Revocar la licencia de un usuario
- **Rol requerido:** `miembro de un cuerpo policial`
- **Parámetros:**
  - `usuario`: Usuario al que revocar la licencia
  - `tipo_licencia`: Tipo de licencia (conducir/armas)
- **Efecto:** Revoca la licencia y quita el rol correspondiente

### `/incautar`
- **Descripción:** Incautar un vehículo
- **Rol requerido:** `dt` (DDT - Departamento de Tráfico)
- **Parámetros:**
  - `usuario`: Propietario del vehículo
  - `modelo`: Modelo del vehículo
  - `matricula`: Matrícula del vehículo
  - `imagen`: URL de imagen del vehículo (opcional)
- **Efecto:** Registra la incautación, notifica al propietario

## ⚙️ Comandos Administrativos

### `/banear`
- **Descripción:** Banear a un usuario del servidor
- **Rol requerido:** `staff`
- **Parámetros:**
  - `usuario`: Usuario a banear
  - `razon`: Motivo del baneo
  - `eliminar_mensajes`: Días de mensajes a eliminar (0-7)

### `/expulsar`
- **Descripción:** Expulsar a un usuario del servidor
- **Rol requerido:** `staff`
- **Parámetros:**
  - `usuario`: Usuario a expulsar
  - `razon`: Motivo de la expulsión

### `/poner-sancion`
- **Descripción:** Aplicar una sanción a un usuario
- **Rol requerido:** `mod` o `staff`
- **Parámetros:**
  - `usuario`: Usuario a sancionar
  - `tipo`: Tipo de sanción
  - `duracion`: Duración en horas
  - `razon`: Motivo de la sanción

### `/quitar-sancion`
- **Descripción:** Quitar una sanción activa
- **Rol requerido:** `staff` o `mod`
- **Parámetros:**
  - `sancion_id`: ID de la sanción a quitar

### `/sanciones-ver`
- **Descripción:** Ver las sanciones de un usuario
- **Rol requerido:** `mod` o `staff`
- **Parámetros:**
  - `usuario`: Usuario cuyas sanciones quieres ver

### `/mantenimiento`
- **Descripción:** Activar/desactivar modo mantenimiento
- **Rol requerido:** `owners`
- **Efecto:** Bloquea todos los comandos excepto para owners

### `/servidor`
- **Descripción:** Ver información del servidor
- **Rol requerido:** `owners`
- **Muestra:** Estadísticas de usuarios, cuentas, transacciones

### `/ck`
- **Descripción:** Character Kill - Eliminar todos los datos de un usuario
- **Rol requerido:** `owners`
- **Parámetros:**
  - `usuario`: Usuario cuyos datos eliminar
- **⚠️ PELIGRO:** Esta acción es irreversible

### `/eliminar-documentacion`
- **Descripción:** Eliminar documentación específica de un usuario
- **Rol requerido:** `owners`
- **Parámetros:**
  - `usuario`: Usuario objetivo
  - `tipo`: Tipo de documentación (dni/licencia_armas/licencia_conducir)

## 📚 Comandos Generales

### `/crear-historia`
- **Descripción:** Crear o actualizar tu historia personal
- **Rol requerido:** `verificado`
- **Parámetros:**
  - `historia`: Tu historia personal (máximo 1.000 caracteres)
- **Efecto:** Guarda tu historia en la base de datos

### `/ver-historia`
- **Descripción:** Ver la historia personal de un usuario
- **Rol requerido:** `verificado`
- **Parámetros:**
  - `usuario`: Usuario cuya historia quieres ver (opcional, por defecto: tu historia)

## 💼 Sistema de Sueldos

Los sueldos se pueden cobrar una vez cada 24 horas usando `/cobrar-sueldo`:

| Rol | Sueldo |
|-----|--------|
| Desempleado | 800 € |
| Empleado | 1.200 € |
| Jefe de empresa | 1.700 € |
| DT | 1.550 € |
| Bombero | 1.600 € |
| Miembro de un cuerpo sanitario | 1.600 € |
| Miembro de policía nacional | 1.700 € |
| Miembro de policía local | 1.650 € |
| Miembro de guardia civil | 1.800 € |
| Sub-jefe policía local | 1.800 € |
| Sub-jefe de bomberos | 1.800 € |
| Sub-jefe policía nacional | 2.000 € |
| Sub-jefe guardia civil | 2.200 € |
| Jefe policía local | 2.000 € |
| Jefe bomberos | 2.000 € |
| Jefe policía nacional | 2.200 € |
| Jefe guardia civil | 2.400 € |
| Premium | 5.000 € |

## ⚙️ Configuración

### Límites Económicos
- **Transferencia máxima:** 10.000 €
- **Apuesta mínima:** 10 €
- **Apuesta máxima:** 5.000 €
- **Préstamo mínimo:** 100 €
- **Préstamo máximo:** 50.000 €
- **Multa máxima:** 1.500 €

### Precios de Licencias
- **DNI:** 150 €
- **Licencia de Conducir:** 1.000 €
- **Licencia de Armas:** 2.500 €

### Configuración del Casino
- **Probabilidad de ganar:** 45%
- **Multiplicador de ganancia:** x2

## 🔧 Instalación y Configuración

### Requisitos
- Python 3.8+
- discord.py
- python-dotenv

### Variables de Entorno
```env
DISCORD_TOKEN=tu_token_de_discord
```

### Roles de Discord Requeridos
El bot requiere que el servidor tenga configurados los siguientes roles:
- `verificado`
- `civil`
- `DNI`
- `miembro de un cuerpo policial`
- `dt`
- `mod`
- `staff`
- `owners`
- `deudor`
- `Licencia de conducir`
- `Licencia de armas (Beretta M9)`
- Roles de propiedades (asignados automáticamente)
- Roles de seguros (asignados automáticamente)

### Base de Datos
El bot utiliza SQLite y crea automáticamente las tablas necesarias en el primer inicio.

## 📞 Soporte

Para soporte o reportar errores, contacta con los administradores del servidor.

---

**Total de comandos disponibles:** 43

**Última actualización:** Septiembre 2025


--

# English Version

# 🎭 Roleplay Bot — Valencia RP

A complete Discord bot designed for roleplay servers with economic, police, administrative and user-management systems.

## 📋 Index

- [Role Requirements](#role-requirements)
- [Economic Commands](#economic-commands)
- [License Commands](#license-commands)
- [Inventory Commands](#inventory-commands)
- [Police Commands](#police-commands)
- [Administrative Commands](#administrative-commands)
- [General Commands](#general-commands)
- [Salary System](#salary-system)
- [Configuration](#configuration)

## 🔐 Role Requirements

### Basic Roles
- **verificado (verified)**: Base role required for most commands
- **civil (citizen)**: Citizen with civil rights
- **dni**: User with official documentation

### Police Roles
- **miembro de un cuerpo policial (police officer)**: General police agents
- **dt**: Traffic Department (DDT)

### Administrative Roles
- **mod**: Server moderators
- **staff**: Administrative personnel
- **owners**: Server owners

### Economic Roles
- **deudor (debtor)**: Users with outstanding loans

## 💰 Economic Commands

**Required role:** `verificado`

### `/cuenta-crear`
- **Description:** Create a bank account at Banco Central
- **Parameters:**
  - `banco`: Bank where the account is created (Only Banco Central available)
- **Starting balance:** €1,500

### `/cuenta-ver`
- **Description:** View your bank account information
- **Shows:** Current balance, bank, creation date

### `/dinero-dar`
- **Description:** Transfer money to another user
- **Parameters:**
  - `usuario`: Recipient user
  - `cantidad`: Amount to transfer
- **Limits:** Maximum €10,000 per transfer

### `/dinero-depositar`
- **Description:** Deposit cash into your bank account
- **Parameters:**
  - `cantidad`: Amount to deposit

### `/dinero-retirar`
- **Description:** Withdraw money from your bank account
- **Parameters:**
  - `cantidad`: Amount to withdraw

### `/casino`
- **Description:** Bet money at the casino
- **Parameters:**
  - `cantidad`: Amount to bet
- **Limits:** Between €10 and €5,000 per bet
- **Win probability:** 45% (winnings x2)

### `/pedir-prestamo`
- **Description:** Request a bank loan
- **Parameters:**
  - `cantidad`: Loan amount
- **Limits:** Between €100 and €50,000
- **Interest:** 5% on the requested amount

### `/pagar-prestamo`
- **Description:** Pay outstanding loans
- **Required role:** `deudor` or `verificado`

### `/cobrar-sueldo`
- **Description:** Collect your salary according to your role
- **Frequency:** Once every 24 hours
- **Amount:** Varies by role (see [Salary System](#salary-system))

## 📄 License Commands

### `/solicitar-dni`
- **Description:** Request a National Identity Document (DNI)
- **Required role:** `verificado`
- **Price:** €150
- **Required parameters:**
  - `nombre`: Your first name
  - `apellido`: Your last name
  - `edad`: Your age
  - `fecha_nacimiento`: Date in DD/MM/YYYY format
  - `sexo`: Male/Female/Other
  - `nacionalidad`: Your nationality
- **Effect:** Automatically assigns the `DNI` role

### `/solicitar-licencia-armas`
- **Description:** Request a firearm carry license
- **Required role:** `civil` + must have `DNI`
- **Price:** €2,500
- **Duration:** 365 days
- **Effect:** Automatically assigns the role `Licencia de armas (Beretta M9)`

### `/solicitar-licencia-de-conducir`
- **Description:** Request a driver's license
- **Required role:** `civil` + must have `DNI`
- **Price:** €1,000
- **Duration:** 365 days
- **Effect:** Automatically assigns the role `Licencia de conducir`

### `/ver-dni`
- **Description:** View your DNI information
- **Required role:** `verificado`
- **Shows:** Personal data, DNI number, issue date

### `/ver-licencia-de-armas`
- **Description:** View the status of your firearm license
- **Required role:** `verificado`
- **Shows:** Status, issue date, expiration date

### `/ver-licencia-de-conducir`
- **Description:** View the status of your driver's license
- **Required role:** `verificado`
- **Shows:** Status, issue date, expiration date

## 🛍️ Inventory Commands

### `/tienda`
- **Description:** View all items available in the store
- **Required role:** `civil`
- **Available categories:**
  - **Insurance:** Vehicle insurance (€300)
  - **Weapons:** Beretta M9 (€1,750)
  - **Technology:** Drone (€2,000)
  - **Tools:** Bat (€15), Knife (€30), Spray (€45)
  - **Properties:** Small house (€15,000), Business establishment (€20,000), Country house (€25,000), Large house (€35,000)

### `/comprar-objeto`
- **Description:** Buy an item from the store
- **Required role:** `verificado`
- **Parameters:**
  - `objeto`: Exact name of the item
  - `cantidad`: Quantity to buy (default: 1)
- **Special effects:**
  - Insurance assigns roles automatically
  - Properties assign specific roles
  - Beretta M9 requires a firearm license

### `/inventario`
- **Description:** View your personal inventory
- **Required role:** `verificado`
- **Shows:** All items you own and their quantities

### `/mirar-inventario`
- **Description:** View another user's inventory
- **Required role:** `mod` or `staff`
- **Parameters:**
  - `usuario`: User whose inventory you want to see

### `/armeria`
- **Description:** View your arsenal and license status
- **Required role:** `verificado`
- **Shows:** Weapons in possession and firearm license status

## 🚔 Police Commands

### `/arrestar`
- **Description:** Arrest a user
- **Required role:** `miembro de un cuerpo policial`
- **Parameters:**
  - `usuario`: User to arrest
  - `razon`: Reason for the arrest
- **Effect:** Registers the arrest in the database, notifies the user

### `/multas-poner`
- **Description:** Issue a fine to a user
- **Required role:** `miembro de un cuerpo policial`
- **Parameters:**
  - `usuario`: User to fine
  - `cantidad`: Fine amount
  - `articulos`: Offended articles of the penal code
- **Maximum limit:** €1,500 (major infractions require arrest)

### `/multas-ver`
- **Description:** View a user's fines
- **Required role:** `miembro de un cuerpo policial`
- **Parameters:**
  - `usuario`: User whose fines you want to see
- **Shows:** Complete fine history (paid and pending)

### `/eliminar-multa`
- **Description:** Delete a specific fine
- **Required role:** `miembro de un cuerpo policial`
- **Parameters:**
  - `multa_id`: ID of the fine to delete

### `/pagar-multas`
- **Description:** Pay all pending fines
- **Required role:** `verificado`
- **Effect:** Automatically deducts the money from the account

### `/revocar-licencia`
- **Description:** Revoke a user's license
- **Required role:** `miembro de un cuerpo policial`
- **Parameters:**
  - `usuario`: User whose license is revoked
  - `tipo_licencia`: License type (driving/firearms)
- **Effect:** Revokes the license and removes the corresponding role

### `/incautar`
- **Description:** Seize a vehicle
- **Required role:** `dt` (DDT — Traffic Department)
- **Parameters:**
  - `usuario`: Owner of the vehicle
  - `modelo`: Vehicle model
  - `matricula`: Vehicle license plate
  - `imagen`: URL of a vehicle image (optional)
- **Effect:** Registers the seizure, notifies the owner

## ⚙️ Administrative Commands

### `/banear`
- **Description:** Ban a user from the server
- **Required role:** `staff`
- **Parameters:**
  - `usuario`: User to ban
  - `razon`: Reason for the ban
  - `eliminar_mensajes`: Days of messages to delete (0-7)

### `/expulsar`
- **Description:** Kick a user from the server
- **Required role:** `staff`
- **Parameters:**
  - `usuario`: User to kick
  - `razon`: Reason for the kick

### `/poner-sancion`
- **Description:** Apply a sanction to a user
- **Required role:** `mod` or `staff`
- **Parameters:**
  - `usuario`: User to sanction
  - `tipo`: Sanction type
  - `duracion`: Duration in hours
  - `razon`: Reason for the sanction

### `/quitar-sancion`
- **Description:** Remove an active sanction
- **Required role:** `staff` or `mod`
- **Parameters:**
  - `sancion_id`: ID of the sanction to remove

### `/sanciones-ver`
- **Description:** View a user's sanctions
- **Required role:** `mod` or `staff`
- **Parameters:**
  - `usuario`: User whose sanctions you want to see

### `/mantenimiento`
- **Description:** Enable/disable maintenance mode
- **Required role:** `owners`
- **Effect:** Blocks all commands except for owners

### `/servidor`
- **Description:** View server information
- **Required role:** `owners`
- **Shows:** User, account and transaction statistics

### `/ck`
- **Description:** Character Kill — Delete all of a user's data
- **Required role:** `owners`
- **Parameters:**
  - `usuario`: User whose data is deleted
- **⚠️ DANGER:** This action is irreversible

### `/eliminar-documentacion`
- **Description:** Delete specific documentation of a user
- **Required role:** `owners`
- **Parameters:**
  - `usuario`: Target user
  - `tipo`: Documentation type (dni/licencia_armas/licencia_conducir)

## 📚 General Commands

### `/crear-historia`
- **Description:** Create or update your personal story
- **Required role:** `verificado`
- **Parameters:**
  - `historia`: Your personal story (maximum 1,000 characters)
- **Effect:** Saves your story in the database

### `/ver-historia`
- **Description:** View a user's personal story
- **Required role:** `verificado`
- **Parameters:**
  - `usuario`: User whose story you want to see (optional, default: yours)

## 💼 Salary System

Salaries can be collected once every 24 hours using `/cobrar-sueldo`:

| Role | Salary |
|-----|--------|
| Unemployed | €800 |
| Employee | €1,200 |
| Business owner | €1,700 |
| DT (Traffic) | €1,550 |
| Firefighter | €1,600 |
| Health corps member | €1,600 |
| National police officer | €1,700 |
| Local police officer | €1,650 |
| Civil Guard member | €1,800 |
| Local police deputy chief | €2,000 |
| Deputy fire chief | €1,800 |
| National police deputy chief | €2,000 |
| Civil Guard deputy chief | €2,200 |
| Local police chief | €2,000 |
| Fire chief | €2,000 |
| National police chief | €2,200 |
| Civil Guard chief | €2,400 |
| Premium | €5,000 |

## ⚙️ Configuration

### Economic Limits
- **Maximum transfer:** €10,000
- **Minimum bet:** €10
- **Maximum bet:** €5,000
- **Minimum loan:** €100
- **Maximum loan:** €50,000
- **Maximum fine:** €1,500

### License Prices
- **DNI:** €150
- **Driver's License:** €1,000
- **Firearm License:** €2,500

### Casino Configuration
- **Win probability:** 45%
- **Winnings multiplier:** x2

## 🔧 Installation and Setup

### Requirements
- Python 3.8+
- discord.py
- python-dotenv

### Environment Variables
```env
DISCORD_TOKEN=your_discord_token
```

### Required Discord Roles
The bot requires the server to have the following roles configured:
- `verificado`
- `civil`
- `DNI`
- `miembro de un cuerpo policial`
- `dt`
- `mod`
- `staff`
- `owners`
- `deudor`
- `Licencia de conducir`
- `Licencia de armas (Beretta M9)`
- Property roles (assigned automatically)
- Insurance roles (assigned automatically)

### Database
The bot uses SQLite and automatically creates the required tables on first start.

## 📞 Support

For support or bug reports, contact the server administrators.

---

**Total available commands:** 43

**Last updated:** September 2025
