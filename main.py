from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
from config import (
    COMPROBANTE1_CONFIG,
    COMPROBANTE4_CONFIG,
    COMPROBANTE_MOVIMIENTO_CONFIG,
    COMPROBANTE_MOVIMIENTO2_CONFIG,
    COMPROBANTE_QR_CONFIG,
    COMPROBANTE_MOVIMIENTO3_CONFIG
)
from utils import generar_comprobante
from auth_system import AuthSystem
import os
import logging
from uuid import uuid4
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === OBTENER CONFIGURACIÓN DE VARIABLES DE ENTORNO ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ La variable de entorno BOT_TOKEN no está definida.")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ALLOWED_GROUP = int(os.getenv("ALLOWED_GROUP", "0"))
OWNER = os.getenv("OWNER", "Soporte")

# Initialize authorization system
auth_system = AuthSystem(ADMIN_ID, ALLOWED_GROUP)
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        if not auth_system.can_use_bot(user_id, chat_id):
            await update.message.reply_text("🚫 Acceso denegado: No tienes permiso para usar este bot.")
            return
    
        keyboard = [
            [InlineKeyboardButton("💸 Nequi", callback_data="comprobante1")],
            [InlineKeyboardButton("🔄 Transfiya", callback_data="comprobante4")],
            [InlineKeyboardButton("📱 QR Comprobante", callback_data="comprobante_qr")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            "✨ ¡Hola! Soy tu asistente de comprobantes falsos 🎭\n\n"
            "📌 Selecciona el tipo de comprobante que deseas generar:"
        )
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    except Exception as e:
        logger.error(f"Error in start command for user {user_id} in chat {chat_id}: {str(e)}")
        await update.message.reply_text("⚠️ Error al iniciar el bot. Intenta de nuevo.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        chat_id = query.message.chat.id
        tipo = query.data or "default"

        if not auth_system.can_use_bot(user_id, chat_id):
            await query.message.reply_text("🚫 Acceso denegado: No tienes permiso para usar este bot.")
            return

        user_data_store[user_id] = {"step": 0, "tipo": tipo, "session_id": str(uuid4())}

        prompts = {
            "comprobante1": "👤 ¿Cuál es tu nombre (para el comprobante)?",
            "comprobante4": "📱 Por favor, escribe tu número de celular (solo números, sin espacios ni guiones):",
            "comprobante_qr": "🏬 ¿Cuál es el nombre del negocio o persona receptora?",
        }

        await query.message.reply_text(
            prompts.get(tipo, "🔍 Por favor, inicia ingresando los datos solicitados:")
        )
    
    except Exception as e:
        logger.error(f"Error in button_handler for user {user_id} in chat {chat_id}: {str(e)}")
        await query.message.reply_text("⚠️ Error al procesar la selección. Intenta de nuevo.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    try:
        if not auth_system.can_use_bot(user_id, chat_id):
            await update.message.reply_text("🚫 Acceso denegado: No tienes permiso para usar este bot.")
            return

        if user_id not in user_data_store:
            await update.message.reply_text("🔄 Por favor, inicia con /start")
            return

        data = user_data_store[user_id]
        tipo = data["tipo"]
        step = data["step"]

        # --- NEQUI (AHORA CON 4 PASOS) ---
        if tipo == "comprobante1":
            if step == 0:
                data["nombre_comprobante"] = text  # Nombre abreviado
                data["step"] = 1
                await update.message.reply_text("👤 ¿Cuál es tu nombre completo (para el movimiento)?")
            elif step == 1:
                data["nombre_movimiento"] = text  # Nombre completo
                data["step"] = 2
                await update.message.reply_text("📱 Por favor, escribe tu número de celular (solo números, sin espacios ni guiones):")
            elif step == 2:
                if not text.isdigit():
                    await update.message.reply_text("⚠️ El número debe contener solo dígitos. Inténtalo de nuevo.")
                    return
                data["telefono"] = text
                data["step"] = 3
                await update.message.reply_text("💰 ¿Cuál es el monto de la transacción? (Ej: 50000)")
            elif step == 3:
                if not text.lstrip("-").isdigit():
                    await update.message.reply_text("⚠️ El valor debe ser un número entero (sin puntos ni comas). Ej: 100000")
                    return
                data["valor"] = int(text)

                # === Generar comprobante (usa nombre_comprobante) ===
                datos_comprobante = {
                    "nombre": data["nombre_comprobante"],
                    "telefono": data["telefono"],
                    "valor": data["valor"]
                }
                output_path = generar_comprobante(datos_comprobante, COMPROBANTE1_CONFIG)

                # === Generar movimiento (usa nombre_movimiento en mayúsculas) ===
                datos_movimiento = {
                    "nombre": data["nombre_movimiento"].upper(),
                    "valor": -abs(data["valor"])
                }
                output_path_mov = generar_comprobante(datos_movimiento, COMPROBANTE_MOVIMIENTO_CONFIG)

                # === Enviar ===
                with open(output_path, "rb") as f1, open(output_path_mov, "rb") as f2:
                    await update.message.reply_media_group(
                        media=[
                            InputMediaDocument(f1, filename="Comprobante.png"),
                            InputMediaDocument(f2, filename="Movimiento.png")
                        ]
                    )
                user = update.effective_user
                user_display = user.first_name
                if user.username:
                    user_display += f" (@{user.username})"
                await update.message.reply_text(
                    f"✅ ¡Comprobante & Movimiento generado!\n\n🆔 Usuario: {user_display}"
                )

                # Limpiar
                for path in [output_path, output_path_mov]:
                    if path and os.path.exists(path):
                        os.remove(path)
                del user_data_store[user_id]

        # --- TRANSFIYA (sin cambios en flujo) ---
        elif tipo == "comprobante4":
            if step == 0:
                if not text.isdigit():
                    await update.message.reply_text("⚠️ El número debe contener solo dígitos. Inténtalo de nuevo.")
                    return
                data["telefono"] = text
                data["step"] = 1
                await update.message.reply_text("💰 ¿Cuál es el monto de la transacción? (Ej: 50000)")
            elif step == 1:
                if not text.lstrip("-").isdigit():
                    await update.message.reply_text("⚠️ El valor debe ser un número entero (sin puntos ni comas). Ej: 100000")
                    return
                data["valor"] = int(text)

                output_path = None
                output_path_mov = None
                try:
                    output_path = generar_comprobante(data, COMPROBANTE4_CONFIG)
                    data_mov2 = {"telefono": data["telefono"], "valor": -abs(data["valor"]), "nombre": data["telefono"]}
                    output_path_mov2 = generar_comprobante(data_mov2, COMPROBANTE_MOVIMIENTO2_CONFIG)

                    with open(output_path, "rb") as f1, open(output_path_mov2, "rb") as f2:
                        await update.message.reply_media_group(
                            media=[
                                InputMediaDocument(f1, filename="Comprobante.png"),
                                InputMediaDocument(f2, filename="Movimiento.png")
                            ]
                        )
                    user = update.effective_user
                    user_display = user.first_name
                    if user.username:
                        user_display += f" (@{user.username})"
                    await update.message.reply_text(
                        f"✅ ¡Comprobante & Movimiento generado!\n\n🆔 Usuario: {user_display}"
                    )
                except Exception as e:
                    logger.exception("Error en Transfiya")
                    await update.message.reply_text("❌ Error al generar los comprobantes. Verifica los datos e intenta de nuevo.")
                finally:
                    for path in [output_path, output_path_mov2]:
                        if path and os.path.exists(path):
                            os.remove(path)
                del user_data_store[user_id]

        # --- QR COMPROBANTE (ACTUALIZADO A 8 PASOS) ---
        elif tipo == "comprobante_qr":
            if step == 0:
                data["nombre"] = text
                data["step"] = 1
                await update.message.reply_text("🔑 Por favor, ingresa la llave (Llave):")
            elif step == 1:
                data["llave"] = text
                data["step"] = 2
                await update.message.reply_text("🏦 ¿Cuál es el banco destino (Banco destino)?")
            elif step == 2:
                data["banco_destino"] = text
                data["step"] = 3
                await update.message.reply_text("💰 ¿Cuál es el monto de la transacción? (Ej: 50000)")
            elif step == 3:
                if not text.lstrip("-").isdigit():
                    await update.message.reply_text("⚠️ El valor debe ser un número entero (sin puntos ni comas). Ej: 100000")
                    return
                data["valor"] = int(text)
                data["step"] = 4
                await update.message.reply_text("📅 Por favor, ingresa la fecha (Fecha):")
            elif step == 4:
                data["fecha"] = text
                data["step"] = 5
                await update.message.reply_text("🔢 Por favor, ingresa la referencia (Referencia):")
            elif step == 5:
                data["referencia"] = text
                data["step"] = 6
                await update.message.reply_text("📱 Por favor, ingresa desde donde se hizo el envío (Desde donde se hizo el envío):")
            elif step == 6:
                data["origen_envio"] = text
                data["step"] = 7
                await update.message.reply_text("💧 Por favor, ingresa de dónde salió la plata (¿De dónde salió la plata?):")
            elif step == 7:
                data["disponible"] = text

                output_path = None
                output_path_movqr = None
                try:
                    # Preparamos los datos para el comprobante QR
                    datos_qr = {
                        "nombre": data["nombre"],
                        "llave": data["llave"],
                        "banco_destino": data["banco_destino"],
                        "valor1": f"${data['valor']:,}".replace(",", ".") + ",00",
                        "fecha": data["fecha"],
                        "referencia": data["referencia"],
                        "origen_envio": data["origen_envio"],
                        "disponible": data["disponible"]
                    }
                    output_path = generar_comprobante(datos_qr, COMPROBANTE_QR_CONFIG)
                    
                    # Preparamos los datos para el movimiento
                    datos_movimiento = {
                        "nombre": data["nombre"].upper(),
                        "valor": -abs(data["valor"])
                    }
                    output_path_movqr = generar_comprobante(datos_movimiento, COMPROBANTE_MOVIMIENTO3_CONFIG)

                    # Enviamos ambos archivos
                    with open(output_path, "rb") as f1, open(output_path_movqr, "rb") as f2:
                        await update.message.reply_media_group(
                            media=[
                                InputMediaDocument(f1, filename="Comprobante_QR.png"),
                                InputMediaDocument(f2, filename="Movimiento_QR.png")
                            ]
                        )
                    user = update.effective_user
                    user_display = user.first_name
                    if user.username:
                        user_display += f" (@{user.username})"
                    await update.message.reply_text(
                        f"✅ ¡Comprobante QR & Movimiento generado!\n\n🆔 Usuario: {user_display}"
                    )
                except Exception as e:
                    logger.exception("Error en QR")
                    await update.message.reply_text("❌ Error al generar los comprobantes. Verifica los datos e intenta de nuevo.")
                finally:
                    for path in [output_path, output_path_movqr]:
                        if path and os.path.exists(path):
                            os.remove(path)
                del user_data_store[user_id]

    except Exception as e:
        logger.error(f"Error in handle_message for user {user_id} in chat {chat_id}: {str(e)}")
        await update.message.reply_text("⚠️ Error al procesar los datos. Por favor, inténtalo de nuevo.")

# === Comandos admin (sin cambios) ===
async def gratis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        if user_id == ADMIN_ID or auth_system.is_admin(user_id):
            logger.info(f"Admin {user_id} executed /gratis in chat {chat_id}")
            auth_system.set_gratis_mode(True)
            await update.message.reply_text("✅ Modo GRATIS activado: Todos pueden usar el bot.")
        else:
            if chat_id != ALLOWED_GROUP:
                await update.message.reply_text("🚫 Este comando solo puede usarse en el grupo autorizado.")
                return
            await update.message.reply_text("🚫 Solo el administrador puede usar este comando.")
    except Exception as e:
        logger.error(f"Error in gratis_command: {str(e)}")
        await update.message.reply_text("⚠️ Error al activar modo gratis.")

async def off_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        if user_id == ADMIN_ID or auth_system.is_admin(user_id):
            logger.info(f"Admin {user_id} executed /off in chat {chat_id}")
            auth_system.set_gratis_mode(False)
            await update.message.reply_text("✅ Modo OFF activado: Solo usuarios autorizados.")
        else:
            if chat_id != ALLOWED_GROUP:
                await update.message.reply_text("🚫 Este comando solo puede usarse en el grupo autorizado.")
                return
            await update.message.reply_text("🚫 Solo el administrador puede usar este comando.")
    except Exception as e:
        logger.error(f"Error in off_command: {str(e)}")
        await update.message.reply_text("⚠️ Error al desactivar modo gratis.")

async def agregar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        if user_id == ADMIN_ID or auth_system.is_admin(user_id):
            if not context.args:
                await update.message.reply_text("❓ Uso: /agregar <id_usuario>")
                return
            target_user_id = int(context.args[0])
            auth_system.add_user(target_user_id)
            await update.message.reply_text(f"✅ Usuario {target_user_id} autorizado.")
        else:
            await update.message.reply_text("🚫 Solo el administrador puede usar este comando.")
    except ValueError:
        await update.message.reply_text("⚠️ ID de usuario inválido.")
    except Exception as e:
        logger.error(f"Error in agregar_command: {str(e)}")
        await update.message.reply_text("⚠️ Error al agregar usuario.")

async def eliminar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        if user_id == ADMIN_ID or auth_system.is_admin(user_id):
            if not context.args:
                await update.message.reply_text("❓ Uso: /eliminar <id_usuario>")
                return
            target_user_id = int(context.args[0])
            if auth_system.remove_user(target_user_id):
                await update.message.reply_text(f"✅ Usuario {target_user_id} desautorizado.")
            else:
                await update.message.reply_text(f"⚠️ Usuario {target_user_id} no estaba autorizado.")
        else:
            await update.message.reply_text("🚫 Solo el administrador puede usar este comando.")
    except ValueError:
        await update.message.reply_text("⚠️ ID de usuario inválido.")
    except Exception as e:
        logger.error(f"Error in eliminar_command: {str(e)}")
        await update.message.reply_text("⚠️ Error al eliminar usuario.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        if user_id == ADMIN_ID or auth_system.is_admin(user_id):
            stats = auth_system.get_stats()
            authorized_users = auth_system.get_authorized_users()
            message = (
                f"📊 **Estadísticas del Bot**\n\n"
                f"👥 Usuarios autorizados: {stats['total_authorized']}\n"
                f"🆓 Modo gratis: {'Activado' if stats['gratis_mode'] else 'Desactivado'}\n"
                f"📱 Grupo permitido: {stats['allowed_group']}\n\n"
            )
            if authorized_users:
                message += "👤 Usuarios autorizados:\n" + "\n".join(f"  • {uid}" for uid in authorized_users)
            else:
                message += "❌ No hay usuarios autorizados."
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("🚫 Solo el administrador puede usar este comando.")
    except Exception as e:
        logger.error(f"Error in stats_command: {str(e)}")
        await update.message.reply_text("⚠️ Error al obtener estadísticas.")

def main() -> None:
    try:
        logger.info(f"Initializing bot with admin ID: {ADMIN_ID}, allowed group: {ALLOWED_GROUP}")
        if not BOT_TOKEN or ":" not in BOT_TOKEN:
            raise ValueError("Invalid bot token")
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("gratis", gratis_command))
        app.add_handler(CommandHandler("off", off_command))
        app.add_handler(CommandHandler("agregar", agregar_command))
        app.add_handler(CommandHandler("eliminar", eliminar_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        port = int(os.environ.get("PORT", 10000))
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES
        )
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()