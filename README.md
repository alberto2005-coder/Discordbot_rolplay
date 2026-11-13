# Bot de rol para Discord — Valencia RP

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.5.2-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/SQLite-local-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)

[Español](#español) · [English](#english)

---

## Español

### Índice

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Permisos e intents](#permisos-e-intents)
- [Roles del servidor](#roles-del-servidor)
- [Comandos de economía](#comandos-de-economía)
- [Comandos de licencias](#comandos-de-licencias)
- [Comandos de inventario](#comandos-de-inventario)
- [Comandos de policía](#comandos-de-policía)
- [Comandos de administración](#comandos-de-administración)
- [Comandos de historia](#comandos-de-historia)
- [Flujo de juego](#flujo-de-juego)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Límites y estado actual](#límites-y-estado-actual)
- [Seguridad](#seguridad)
- [Licencia](#licencia)

### Descripción

Bot de Discord para un servidor de **roleplay** (Valencia RP). Implementa una economía con banco, casino y préstamos; un sistema de DNI y licencias; tienda e inventario; multas, arrestos e incautaciones; sanciones y herramientas de administración; y una historia personal por personaje.

Está escrito en **Python** con **discord.py 2.5** y usa **SQLite** como base de datos local. Todos los comandos son **slash commands** con nombres en español, y el bot responde con embeds.

> [!NOTE]
> «Valencia RP» es un servidor ficticio de rol. El proyecto no tiene relación con cuerpos de seguridad reales.

### Características

- **Economía**: cuenta bancaria, transferencias, depósitos, retiradas, casino, préstamos al 5 % y pago de deudas.
- **Documentación**: DNI con datos personales y licencias de armas y de conducir con caducidad.
- **Inventario**: tienda por categorías, compra por cantidad y asignación automática de roles.
- **Policía**: arrestos, multas con artículos del código penal, revocación de licencias e incautación de vehículos por el DDT.
- **Administración**: baneos, expulsiones, sanciones temporales o permanentes, información del servidor y borrado de documentación.
- **Personajes**: historia personal de hasta 1.000 caracteres y *Character Kill* con confirmación escrita.
- **Persistencia**: SQLite crea las tablas y los artículos de la tienda en el primer arranque.

### Requisitos

- **Python 3.11** o superior (lo exige `pyproject.toml`).
- Una aplicación de Discord con un **bot** y su token.
- Los **intents** *Server Members* y *Message Content* activados.
- Permisos de **Gestionar roles**, **Banear miembros**, **Expulsar miembros**, **Enviar mensajes**, **Insertar enlaces** y **Leer historial de mensajes**.

### Instalación

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -U "discord.py>=2.5.2" python-dotenv
```

También puedes usar **uv**, ya que el repositorio incluye `pyproject.toml` y `uv.lock`:

```bash
uv sync
uv run main.py
```

> [!IMPORTANT]
> `requirements_completo.txt` es una lista amplia de dependencias opcionales que incluye paquetes solo para Linux (`uvloop`, `systemd-python`). Para ejecutar el bot basta con `discord.py` y `python-dotenv`; no instales el archivo completo en Windows.

### Configuración

1. Copia `.env.example` a `.env`:

   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux / macOS
   ```

2. Escribe el token del bot:

   ```env
   DISCORD_TOKEN=tu_token_de_discord
   ```

3. Arranca el bot:

   ```bash
   python main.py
   ```

Al iniciar, `Database.initialize()` crea `roleplay_bot.db` y carga la tienda por defecto. Los comandos slash se sincronizan en `setup_hook()`; Discord puede tardar hasta una hora en mostrarlos la primera vez.

### Permisos e intents

En el **Portal de desarrolladores de Discord**:

- *Bot → Privileged Gateway Intents*: activa **Server Members Intent** y **Message Content Intent**.
- *OAuth2 → URL Generator*: marca los scopes `bot` y `applications.commands`, y los permisos indicados en [Requisitos](#requisitos).
- El rol del bot debe estar **por encima** de los roles que asigna o retira (por ejemplo, `DNI` o `Licencia de conducir`).

El intent de miembros es necesario para consultar roles y el de contenido para leer la confirmación `CONFIRMAR CK`.

### Roles del servidor

Crea estos roles con el **nombre exacto** (la comprobación ignora mayúsculas y minúsculas, pero no espacios ni tildes):

| Rol | Uso |
|---|---|
| `verificado` | Base para la mayoría de comandos |
| `civil` | Tienda y solicitud de licencias de armas y conducir |
| `DNI` | Se asigna automáticamente al emitir el DNI |
| `miembro de un cuerpo policial` | Arrestos, multas y revocación de licencias |
| `DT` | Incautación de vehículos (el código acepta `dt` o `DT`) |
| `mod` | Sanciones y consulta de inventarios ajenos |
| `staff` | Baneos, expulsiones, sanciones y consulta de inventarios |
| `owners` | Mantenimiento, información del servidor, CK y borrado de documentación |
| `deudor` | Permite pagar préstamos (también `verificado`) |
| `Licencia de conducir` | Se asigna automáticamente al aprobar la licencia |
| `Licencia de armas (Beretta M9)` | Se asigna automáticamente al aprobar la licencia |
| `seguro vehicular` | Se asigna al comprar el seguro de vehículo |
| `propietario casa pequeña`, `propietario empresa`, `propietario casa campo`, `propietario casa grande` | Se asignan al comprar la propiedad |

### Comandos de economía

| Comando | Rol | Qué hace | Límites |
|---|---|---|---|
| `/cuenta-crear` | `verificado` | Crea una cuenta en Banco Central | Saldo inicial de 1.500 € |
| `/cuenta-ver` | `verificado` | Muestra las cuentas con saldo | Las cuentas a 0 € no aparecen |
| `/dinero-dar` | `verificado` | Transfiere dinero a otro usuario | Sin tope propio; limitado por el saldo |
| `/dinero-depositar` | `verificado` | Suma dinero a la cuenta bancaria | No existe una cartera de efectivo separada |
| `/dinero-retirar` | `verificado` | Resta dinero de la cuenta bancaria | Requiere saldo suficiente |
| `/casino` | `verificado` | Apuesta a 2d6 contra la casa | Apuesta de 10 € a 1.000 €; el empate devuelve la apuesta; la victoria paga 2× |
| `/pedir-prestamo` | `verificado` | Concede un préstamo al 5 % | Máximo 10.000 €; vence a los 30 días; solo un préstamo activo |
| `/pagar-prestamo` | `deudor` o `verificado` | Paga el préstamo más antiguo | Descuenta del banco con más saldo |

El casino lanza dos dados de seis caras para el jugador y dos para la casa. La probabilidad de ganar es 575/1296 ≈ **44,4 %**; el empate (146/1296) devuelve la apuesta.

### Comandos de licencias

| Comando | Rol | Qué hace | Precio y duración |
|---|---|---|---|
| `/solicitar-dni` | `verificado` | Emite un DNI con nombre, apellidos, edad, nacimiento, sexo y nacionalidad | 100 €; válido 10 años |
| `/solicitar-licencia-armas` | `civil` con DNI | Emite la licencia de armas | 500 €; 365 días |
| `/solicitar-licencia-de-conducir` | `civil` con DNI | Emite la licencia de conducir | 300 €; 5 años |
| `/ver-dni` | `verificado` | Muestra los datos y el número de DNI | — |
| `/ver-licencia-de-armas` | `verificado` | Muestra estado, expedición y caducidad | — |
| `/ver-licencia-de-conducir` | `verificado` | Muestra estado, expedición y caducidad | — |

El DNI se genera con un número aleatorio de ocho cifras y asigna el rol `DNI`. Las licencias de armas y conducir exigen tener DNI y asignan su rol al concederse.

### Comandos de inventario

| Comando | Rol | Qué hace |
|---|---|---|
| `/tienda` | `civil` | Muestra el catálogo agrupado por categorías |
| `/comprar-objeto` | `verificado` | Compra un objeto por su nombre exacto y cantidad |
| `/inventario` | `verificado` | Lista tus objetos y cantidades |
| `/mirar-inventario` | `mod` o `staff` | Consulta el inventario de otro usuario |
| `/armeria` | `verificado` | Muestra tus armas y el estado de la licencia |

**Catálogo inicial**

| Categoría | Artículos |
|---|---|
| Seguros | Seguro de vehículo — 300 € |
| Armas | Beretta M9 — 1.750 € |
| Tecnología | Dron — 2.000 € |
| Herramientas | Bate — 15 € · Navaja — 30 € · Spray — 45 € |
| Propiedades | Casa pequeña — 15.000 € · Establecimiento empresarial — 20.000 € · Casa de campo — 25.000 € · Casa grande — 35.000 € |

Comprar un artículo de `ITEM_ROLES` asigna automáticamente su rol. La Beretta M9 asigna `Licencia de armas (Beretta M9)` al comprarla; el código **no** comprueba que el usuario tuviera antes esa licencia.

### Comandos de policía

| Comando | Rol | Qué hace | Notas |
|---|---|---|---|
| `/arrestar` | `miembro de un cuerpo policial` | Registra un arresto y avisa al usuario | No permite arrestar dos veces al mismo personaje |
| `/multas-poner` | `miembro de un cuerpo policial` | Impone una multa con los artículos infringidos | Máximo 1.500 €; las infracciones mayores se tramitan como arresto |
| `/multas-ver` | `miembro de un cuerpo policial` | Muestra el historial de multas | Incluye pagadas y pendientes |
| `/eliminar-multa` | `miembro de un cuerpo policial` | Elimina una multa por ID | — |
| `/pagar-multas` | `verificado` | Paga todas las multas pendientes | Descuenta automáticamente del banco |
| `/revocar-licencia` | `miembro de un cuerpo policial` | Revoca la licencia de conducir o de armas | Quita también el rol correspondiente |
| `/incautar` | `DT` | Registra la incautación de un vehículo | Pide propietario, modelo, matrícula e imagen opcional |

### Comandos de administración

| Comando | Rol | Qué hace | Notas |
|---|---|---|---|
| `/banear` | `staff` | Banea a un usuario y le avisa por mensaje directo | Puede borrar de 0 a 7 días de mensajes |
| `/expulsar` | `staff` | Expulsa a un usuario | Pide el motivo |
| `/poner-sancion` | `mod` o `staff` | Aplica una sanción | Motivo y duración en horas; `0` = permanente |
| `/quitar-sancion` | `mod` o `staff` | Elimina una sanción por ID | — |
| `/sanciones-ver` | `mod` o `staff` | Muestra las sanciones de un usuario | — |
| `/mantenimiento` | `owners` | Cambia la presencia del bot a «no molestar» | **No** bloquea los comandos |
| `/servidor` | `owners` | Muestra miembros, canales, roles, emojis y roles más comunes | — |
| `/ck` | `owners` | *Character Kill*: borra los datos del personaje | Hay que escribir `CONFIRMAR CK` en 30 segundos; es irreversible |
| `/eliminar-documentacion` | `owners` | Borra DNI, licencias o ambas cosas | Opciones: `dni`, `armas`, `conducir`, `todas_licencias`, `todo` |

`/ck` elimina cuentas, transacciones, multas, préstamos, inventario, licencias, sanciones y arrestos del usuario. No incluye las historias personales ni los registros de incautaciones.

### Comandos de historia

| Comando | Rol | Qué hace | Notas |
|---|---|---|---|
| `/crear-historia` | `verificado` | Crea o actualiza la historia del personaje | Máximo 1.000 caracteres |
| `/ver-historia` | `verificado` | Muestra tu historia o la de otro usuario | El usuario es opcional |

### Flujo de juego

1. Un administrador crea los roles de la sección [Roles del servidor](#roles-del-servidor) y da `verificado` a los jugadores.
2. El jugador abre su cuenta con `/cuenta-crear` y solicita el DNI con `/solicitar-dni`.
3. Con el DNI puede pedir las licencias de conducir y de armas.
4. Compra objetos y propiedades en `/tienda`; los roles se asignan solos.
5. La policía impone multas y arrestos; el DDT incauta vehículos.
6. Los moderadores aplican sanciones y los owners pueden hacer CK o borrar documentación.

### Estructura del proyecto

```text
Discordbot_rolplay/
├── main.py                    # Arranque, intents y carga de cogs
├── config.py                  # Precios, límites, sueldos y nombres de roles
├── database.py                # Esquema SQLite y consultas
├── utils.py                   # Embeds, roles, casino y formato
├── commands/
│   ├── admin.py               # Baneos, sanciones, CK y servidor
│   ├── economic.py            # Banco, casino y préstamos
│   ├── general.py             # Historias de personaje
│   ├── inventory.py           # Tienda e inventario
│   ├── licenses.py            # DNI y licencias
│   └── police.py              # Arrestos, multas e incautaciones
├── .env.example
├── pyproject.toml
├── requirements_completo.txt
├── uv.lock
├── LICENSE
└── README.md
```

Cada módulo de `commands/` es un **cog** que se registra en `setup_hook()`. La lógica compartida (comprobación de roles, embeds, dados y cálculo de préstamos) vive en `utils.py`.

### Base de datos

SQLite guarda todo en `roleplay_bot.db`, en el directorio desde el que se ejecuta el bot. El archivo está en `.gitignore`.

| Tabla | Contenido |
|---|---|
| `users` | Usuarios, DNI y datos personales |
| `bank_accounts` | Saldo por usuario y banco |
| `transactions` | Historial de movimientos |
| `fines` | Multas y estado de pago |
| `loans` | Préstamos, vencimiento y estado |
| `inventory` | Objetos por usuario |
| `licenses` | DNI, armas y conducir con caducidad |
| `sanctions` | Sanciones y expiración |
| `arrests` | Arrestos activos e históricos |
| `shop_items` | Catálogo de la tienda |
| `user_stories` | Historias personales |
| `seizures` | Vehículos incautados por el DDT |

Haz copia de seguridad de `roleplay_bot.db` antes de actualizar el bot o de ejecutar `/ck`.

### Límites y estado actual

- El código registra **37 comandos**, no 43 como anunciaba el README anterior.
- `config.py` define una tabla de **sueldos**, pero **no existe** el comando `/cobrar-sueldo` que la utilice.
- `/incautar` de objetos y `/incautar` de vehículos comparten nombre. Al definir dos métodos `incautar` en la misma clase, solo se registra el de vehículos; la variante de objetos es código muerto.
- `/mantenimiento` solo cambia el estado del bot; no impide ejecutar comandos.
- `/dinero-depositar` y `/dinero-retirar` modifican el saldo bancario; no hay una cartera de efectivo independiente.
- No hay tests automatizados ni migraciones de esquema.
- El proyecto no está pensado para producción a gran escala: SQLite y un único proceso son suficientes para un servidor pequeño.

### Seguridad

- **Nunca** subas `.env` ni `roleplay_bot.db`: contienen el token y datos de los usuarios.
- Usa el principio de **mínimo privilegio** en Discord y coloca el rol del bot por encima solo de los roles que debe gestionar.
- La base de datos **no está cifrada**. Si el servidor es público, avisa a los jugadores de qué datos guarda el bot.
- El token se lee de `DISCORD_TOKEN`; si se filtra, regenera el token en el Portal de desarrolladores.
- Los mensajes y embeds están en español y no se traducen automáticamente.

### Licencia

**MIT** — consulta [LICENSE](LICENSE). Puedes usar, copiar, modificar y distribuir el código, también comercialmente, siempre que conserves el aviso de copyright. © 2025 Alberto Ortiz Sánchez.

---

## English

### Table of contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Permissions and intents](#permissions-and-intents)
- [Server roles](#server-roles)
- [Economy commands](#economy-commands)
- [License commands](#license-commands)
- [Inventory commands](#inventory-commands)
- [Police commands](#police-commands)
- [Administration commands](#administration-commands)
- [Story commands](#story-commands)
- [Game flow](#game-flow)
- [Project structure](#project-structure)
- [Database](#database)
- [Limits and current state](#limits-and-current-state)
- [Security](#security)
- [License](#license)

### Overview

A Discord bot for a **roleplay** server (Valencia RP). It provides a bank-based economy with a casino and loans; an ID and licence system; a shop and inventory; fines, arrests and vehicle seizures; sanctions and admin tools; and a personal story per character.

It is written in **Python** with **discord.py 2.5** and stores data in a local **SQLite** database. Every command is a **slash command** with a Spanish name, and responses use embeds.

> [!NOTE]
> “Valencia RP” is a fictional roleplay server. The project is not affiliated with any real law-enforcement agency.

### Features

- **Economy**: bank account, transfers, deposits, withdrawals, casino, 5% loans and debt repayment.
- **Documentation**: national ID with personal data, plus firearm and driving licences with expiry dates.
- **Inventory**: shop by category, quantity purchases and automatic role assignment.
- **Police**: arrests, fines with penal-code articles, licence revocation and vehicle seizures by the traffic department.
- **Administration**: bans, kicks, temporary or permanent sanctions, server information and document deletion.
- **Characters**: a personal story of up to 1,000 characters and a *Character Kill* with typed confirmation.
- **Persistence**: SQLite creates the tables and the default shop on first start.

### Requirements

- **Python 3.11** or later (required by `pyproject.toml`).
- A Discord application with a **bot** and its token.
- The **Server Members** and **Message Content** intents enabled.
- **Manage Roles**, **Ban Members**, **Kick Members**, **Send Messages**, **Embed Links** and **Read Message History** permissions.

### Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -U "discord.py>=2.5.2" python-dotenv
```

You can also use **uv**, since the repository includes `pyproject.toml` and `uv.lock`:

```bash
uv sync
uv run main.py
```

> [!IMPORTANT]
> `requirements_completo.txt` is a broad list of optional dependencies that includes Linux-only packages (`uvloop`, `systemd-python`). Running the bot only needs `discord.py` and `python-dotenv`; do not install the whole file on Windows.

### Configuration

1. Copy `.env.example` to `.env`:

   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux / macOS
   ```

2. Set the bot token:

   ```env
   DISCORD_TOKEN=your_discord_token
   ```

3. Start the bot:

   ```bash
   python main.py
   ```

On startup, `Database.initialize()` creates `roleplay_bot.db` and seeds the default shop. Slash commands are synchronised in `setup_hook()`; Discord may take up to an hour to show them the first time.

### Permissions and intents

In the **Discord Developer Portal**:

- *Bot → Privileged Gateway Intents*: enable **Server Members Intent** and **Message Content Intent**.
- *OAuth2 → URL Generator*: select the `bot` and `applications.commands` scopes and the permissions listed in [Requirements](#requirements).
- The bot role must sit **above** any role it adds or removes (for example, `DNI` or `Licencia de conducir`).

The members intent is needed to read roles and the message-content intent to read the `CONFIRMAR CK` confirmation.

### Server roles

Create these roles with the **exact name** (matching is case-insensitive, but spaces and accents must match):

| Role | Purpose |
|---|---|
| `verificado` | Base role for most commands |
| `civil` | Shop and firearm/driving licence requests |
| `DNI` | Assigned automatically when the ID is issued |
| `miembro de un cuerpo policial` | Arrests, fines and licence revocation |
| `DT` | Vehicle seizure (the code accepts `dt` or `DT`) |
| `mod` | Sanctions and viewing other inventories |
| `staff` | Bans, kicks, sanctions and viewing other inventories |
| `owners` | Maintenance, server info, CK and document deletion |
| `deudor` | Allows loan repayment (alongside `verificado`) |
| `Licencia de conducir` | Assigned automatically when the driving licence is approved |
| `Licencia de armas (Beretta M9)` | Assigned automatically when the firearm licence is approved |
| `seguro vehicular` | Assigned when vehicle insurance is purchased |
| `propietario casa pequeña`, `propietario empresa`, `propietario casa campo`, `propietario casa grande` | Assigned when the property is purchased |

### Economy commands

| Command | Role | What it does | Limits |
|---|---|---|---|
| `/cuenta-crear` | `verificado` | Opens an account at Banco Central | €1,500 starting balance |
| `/cuenta-ver` | `verificado` | Lists accounts with a balance | Accounts at €0 are not shown |
| `/dinero-dar` | `verificado` | Transfers money to another user | No explicit cap; limited by the balance |
| `/dinero-depositar` | `verificado` | Adds money to the bank account | There is no separate cash wallet |
| `/dinero-retirar` | `verificado` | Removes money from the bank account | Requires sufficient balance |
| `/casino` | `verificado` | Bets 2d6 against the house | €10–€1,000 bet; a tie returns the stake; a win pays 2× |
| `/pedir-prestamo` | `verificado` | Grants a loan at 5% | Maximum €10,000; due in 30 days; one active loan |
| `/pagar-prestamo` | `deudor` or `verificado` | Repays the oldest loan | Deducted from the bank with the highest balance |

The casino rolls two six-sided dice for the player and two for the house. The win chance is 575/1296 ≈ **44.4%**; a tie (146/1296) returns the stake.

### License commands

| Command | Role | What it does | Price and duration |
|---|---|---|---|
| `/solicitar-dni` | `verificado` | Issues an ID with first name, surname, age, birth date, sex and nationality | €100; valid for 10 years |
| `/solicitar-licencia-armas` | `civil` with ID | Issues the firearm licence | €500; 365 days |
| `/solicitar-licencia-de-conducir` | `civil` with ID | Issues the driving licence | €300; 5 years |
| `/ver-dni` | `verificado` | Shows ID data and number | — |
| `/ver-licencia-de-armas` | `verificado` | Shows status, issue and expiry dates | — |
| `/ver-licencia-de-conducir` | `verificado` | Shows status, issue and expiry dates | — |

The ID is generated as a random eight-digit number and assigns the `DNI` role. Firearm and driving licences require an ID and assign their role when granted.

### Inventory commands

| Command | Role | What it does |
|---|---|---|
| `/tienda` | `civil` | Shows the catalogue grouped by category |
| `/comprar-objeto` | `verificado` | Buys an item by exact name and quantity |
| `/inventario` | `verificado` | Lists your items and quantities |
| `/mirar-inventario` | `mod` or `staff` | Views another user's inventory |
| `/armeria` | `verificado` | Shows your weapons and licence status |

**Default catalogue**

| Category | Items |
|---|---|
| Insurance | Vehicle insurance — €300 |
| Weapons | Beretta M9 — €1,750 |
| Technology | Drone — €2,000 |
| Tools | Bat — €15 · Knife — €30 · Spray — €45 |
| Properties | Small house — €15,000 · Business establishment — €20,000 · Country house — €25,000 · Large house — €35,000 |

Buying an item listed in `ITEM_ROLES` assigns its role automatically. The Beretta M9 assigns `Licencia de armas (Beretta M9)` on purchase; the code does **not** check whether the user already held that licence.

### Police commands

| Command | Role | What it does | Notes |
|---|---|---|---|
| `/arrestar` | `miembro de un cuerpo policial` | Records an arrest and notifies the user | A character cannot be arrested twice |
| `/multas-poner` | `miembro de un cuerpo policial` | Issues a fine with the offending articles | Maximum €1,500; major offences go through arrest |
| `/multas-ver` | `miembro de un cuerpo policial` | Shows the fine history | Includes paid and pending fines |
| `/eliminar-multa` | `miembro de un cuerpo policial` | Deletes a fine by ID | — |
| `/pagar-multas` | `verificado` | Pays all pending fines | Deducted from the bank automatically |
| `/revocar-licencia` | `miembro de un cuerpo policial` | Revokes the driving or firearm licence | Also removes the matching role |
| `/incautar` | `DT` | Records a vehicle seizure | Requires owner, model, plate and an optional image |

### Administration commands

| Command | Role | What it does | Notes |
|---|---|---|---|
| `/banear` | `staff` | Bans a user and sends a DM | Can delete 0–7 days of messages |
| `/expulsar` | `staff` | Kicks a user | Requires a reason |
| `/poner-sancion` | `mod` or `staff` | Applies a sanction | Reason and duration in hours; `0` = permanent |
| `/quitar-sancion` | `mod` or `staff` | Removes a sanction by ID | — |
| `/sanciones-ver` | `mod` or `staff` | Shows a user's sanctions | — |
| `/mantenimiento` | `owners` | Sets the bot presence to “do not disturb” | Does **not** block commands |
| `/servidor` | `owners` | Shows members, channels, roles, emojis and top roles | — |
| `/ck` | `owners` | *Character Kill*: deletes the character's data | Type `CONFIRMAR CK` within 30 seconds; irreversible |
| `/eliminar-documentacion` | `owners` | Deletes the ID, licences or both | Options: `dni`, `armas`, `conducir`, `todas_licencias`, `todo` |

`/ck` deletes the user's accounts, transactions, fines, loans, inventory, licences, sanctions and arrests. It does not include personal stories or seizure records.

### Story commands

| Command | Role | What it does | Notes |
|---|---|---|---|
| `/crear-historia` | `verificado` | Creates or updates the character story | Maximum 1,000 characters |
| `/ver-historia` | `verificado` | Shows your story or another user's | The user is optional |

### Game flow

1. An administrator creates the roles from [Server roles](#server-roles) and gives players `verificado`.
2. The player opens an account with `/cuenta-crear` and requests an ID with `/solicitar-dni`.
3. With the ID, the player can request driving and firearm licences.
4. Items and properties are bought in `/tienda`; roles are assigned automatically.
5. Police issue fines and arrests; the traffic department seizes vehicles.
6. Moderators apply sanctions, and owners can run CK or delete documents.

### Project structure

```text
Discordbot_rolplay/
├── main.py                    # Startup, intents and cog loading
├── config.py                  # Prices, limits, salaries and role names
├── database.py                # SQLite schema and queries
├── utils.py                   # Embeds, roles, casino and formatting
├── commands/
│   ├── admin.py               # Bans, sanctions, CK and server info
│   ├── economic.py            # Bank, casino and loans
│   ├── general.py             # Character stories
│   ├── inventory.py           # Shop and inventory
│   ├── licenses.py            # ID and licences
│   └── police.py              # Arrests, fines and seizures
├── .env.example
├── pyproject.toml
├── requirements_completo.txt
├── uv.lock
├── LICENSE
└── README.md
```

Each module in `commands/` is a **cog** registered in `setup_hook()`. Shared logic (role checks, embeds, dice and loan maths) lives in `utils.py`.

### Database

SQLite stores everything in `roleplay_bot.db`, in the directory the bot runs from. The file is git-ignored.

| Table | Contents |
|---|---|
| `users` | Users, ID and personal data |
| `bank_accounts` | Balance per user and bank |
| `transactions` | Transaction history |
| `fines` | Fines and payment status |
| `loans` | Loans, due date and status |
| `inventory` | Items per user |
| `licenses` | ID, firearm and driving licences with expiry |
| `sanctions` | Sanctions and expiry |
| `arrests` | Active and past arrests |
| `shop_items` | Shop catalogue |
| `user_stories` | Personal stories |
| `seizures` | Vehicles seized by the traffic department |

Back up `roleplay_bot.db` before upgrading the bot or running `/ck`.

### Limits and current state

- The code registers **37 commands**, not the 43 claimed by the previous README.
- `config.py` defines a **salary** table, but the `/cobrar-sueldo` command that would use it **does not exist**.
- Item seizure and vehicle seizure share the `/incautar` name. Defining two `incautar` methods in the same class means only the vehicle version is registered; the item variant is dead code.
- `/mantenimiento` only changes the bot's presence; it does not prevent commands from running.
- `/dinero-depositar` and `/dinero-retirar` change the bank balance; there is no separate cash wallet.
- There are no automated tests and no schema migrations.
- The project is not built for large-scale production: SQLite and a single process are enough for a small server.

### Security

- **Never** commit `.env` or `roleplay_bot.db`: they hold the token and user data.
- Apply **least privilege** on Discord and place the bot role only above the roles it must manage.
- The database is **not encrypted**. If the server is public, tell players what data the bot stores.
- The token is read from `DISCORD_TOKEN`; if it leaks, regenerate it in the Developer Portal.
- Messages and embeds are in Spanish and are not translated automatically.

### License

**MIT** — see [LICENSE](LICENSE). You may use, copy, modify and distribute the code, including commercially, as long as you keep the copyright notice. © 2025 Alberto Ortiz Sánchez.
