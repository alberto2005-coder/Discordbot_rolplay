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