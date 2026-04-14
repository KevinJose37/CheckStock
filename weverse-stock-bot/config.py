import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "5"))
TARGET_URL = os.getenv("TARGET_URL", "https://shop.weverse.io/es/shop/USD/artists/2/sales/54189?shopAndCurrency=USD&artistId=2&saleId=54189")

# Feature flag to switch between fast requests and playwright fallback
USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "False").lower() in ("true", "1", "yes", "t")

# Basic validation
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_here":
    print("⚠️ ADVERTENCIA: TELEGRAM_BOT_TOKEN no está configurado correctamente.")
if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "your_chat_id_here":
    print("⚠️ ADVERTENCIA: TELEGRAM_CHAT_ID no está configurado correctamente.")
