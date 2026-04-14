import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

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
