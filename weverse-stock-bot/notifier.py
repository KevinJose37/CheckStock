import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

_last_update_id = None

def send_telegram_message(message: str) -> bool:
    """
    Sends a message to the configured Telegram chat.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Faltan credenciales de Telegram o son inválidas en el archivo .env.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"No se pudo enviar el mensaje de Telegram: {e}")
        return False

def send_alert(url: str, is_test: bool = False) -> bool:
    """
    Constructs and sends the alert message.
    """
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if is_test:
        text = f"🧪 <b>ALERTA DE PRUEBA</b> 🧪\n\nTu bot de stock de Weverse está configurado correctamente.\n🕒 Fecha y hora: {now}"
    else:
        text = (
            f"🚨 <b>¡STOCK DETECTADO!</b> 🚨\n\n"
            f"El producto ya no aparece como AGOTADO o el botón de compra fue habilitado.\n\n"
            f"🛒 <a href='{url}'>Haz clic aquí para comprar</a>\n"
            f"🕒 Fecha y hora: {now}"
        )
    
    return send_telegram_message(text)


def send_startup_message(url: str, check_interval: int, use_playwright: bool) -> bool:
    """
    Envía un saludo al iniciar el bot para confirmar que quedó activo.
    """
    estado_playwright = "activado" if use_playwright else "desactivado"
    text = (
        "👋 <b>Bot iniciado correctamente</b>\n\n"
        "Ya comencé a monitorear el stock.\n"
        f"🔗 URL: <a href='{url}'>Producto monitoreado</a>\n"
        f"⏱️ Intervalo: {check_interval} segundos\n"
        f"🧠 Fallback Playwright: {estado_playwright}\n\n"
        "Comando disponible: /ping"
    )
    return send_telegram_message(text)


def process_telegram_commands() -> None:
    """
    Revisa comandos entrantes en Telegram y responde en el chat configurado.
    Comandos soportados:
    - /ping => confirma que el bot está activo.
    """
    global _last_update_id

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 1}
    if _last_update_id is not None:
        params["offset"] = _last_update_id + 1

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.debug(f"No se pudieron consultar comandos de Telegram: {e}")
        return
    except ValueError as e:
        logger.debug(f"Respuesta JSON inválida al consultar Telegram: {e}")
        return

    if not data.get("ok"):
        return

    updates = data.get("result", [])
    for update in updates:
        _last_update_id = update.get("update_id", _last_update_id)
        message = update.get("message", {})
        text = (message.get("text") or "").strip().lower()
        chat_id = str(message.get("chat", {}).get("id", ""))

        # Solo respondemos al chat configurado para evitar interacción externa.
        if not text or chat_id != str(TELEGRAM_CHAT_ID):
            continue

        if text.startswith("/ping"):
            send_telegram_message("✅ Bot activo y monitoreando stock en este momento.")
