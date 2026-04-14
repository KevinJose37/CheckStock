import time
import argparse
import logging
import random
import sys
from colorama import init, Fore, Style

from config import CHECK_INTERVAL, TARGET_URL, USE_PLAYWRIGHT
from checker import check_stock
from notifier import send_alert

# Initialize colorama for colored terminal output
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.CYAN}%(asctime)s{Style.RESET_ALL} [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Bot de monitoreo de stock de Weverse")
    parser.add_argument("--test-alert", action="store_true", help="Envía un mensaje de prueba a Telegram y termina")
    parser.add_argument("--healthcheck", action="store_true", help="Ejecuta una verificación única y muestra diagnósticos")
    parser.add_argument("--once", action="store_true", help="Ejecuta una única revisión de stock y termina")
    args = parser.parse_args()

    # Handle special CLI arguments
    if args.test_alert:
        logger.info("Enviando alerta de prueba a Telegram...")
        if send_alert(TARGET_URL, is_test=True):
            logger.info(f"{Fore.GREEN}Alerta de prueba enviada correctamente.")
        else:
            logger.error(f"{Fore.RED}No se pudo enviar la alerta de prueba. Revisa tu configuración en .env.")
        return

    if args.healthcheck:
        logger.info(f"Ejecutando healthcheck (modo Playwright: {USE_PLAYWRIGHT})...")
        stock_status = check_stock()
        if stock_status is True:
            logger.info(f"{Fore.GREEN}OK. Se detectó stock durante el healthcheck.")
        elif stock_status is False:
            logger.info(f"{Fore.YELLOW}OK. Diagnóstico correcto, pero el producto está AGOTADO.")
        else:
            logger.error(f"{Fore.RED}FALLO. No se pudo determinar el estado del stock. Revisa los logs.")
        return

    # Normal Bot Loop execution
    logger.info(f"{Fore.MAGENTA}Iniciando bot de stock de Weverse... 🚀")
    logger.info(f"URL monitoreada: {TARGET_URL}")
    logger.info(f"Intervalo de revisión: {CHECK_INTERVAL} segundos (+ jitter aleatorio)")
    logger.info(f"Fallback con Playwright: {'Activado' if USE_PLAYWRIGHT else 'Desactivado'}")
    
    alert_triggered = False

    while True:
        try:
            logger.info(f"{Fore.LIGHTBLACK_EX}Revisando stock...")
            stock_available = check_stock()
            
            if stock_available is True:
                if not alert_triggered:
                    logger.info(f"{Fore.GREEN}🚨 ¡STOCK DETECTADO! Enviando alerta...")
                    success = send_alert(TARGET_URL)
                    if success:
                        logger.info(f"{Fore.GREEN}✅ Alerta enviada correctamente. El bot silenciará avisos hasta que vuelva a agotarse.")
                        alert_triggered = True  # Prevent duplicate spam
                    else:
                        logger.error(f"{Fore.RED}❌ No se pudo enviar la alerta. Se reintentará en el próximo ciclo.")
                else:
                    logger.debug("Hay stock, pero ya se había disparado una alerta antes. Se evita el duplicado.")
                    
            elif stock_available is False:
                logger.info(f"{Fore.YELLOW}Estado: AGOTADO.")
                alert_triggered = False  # Reset the trigger if it goes out of stock again
                
            else:
                logger.warning(f"{Fore.RED}Estado: error desconocido al revisar stock.")

            if args.once:
                logger.info("Revisión única finalizada (--once). Cerrando.")
                break
                
            # Add random jitter between 0.5 and 2.0 seconds to prevent getting blocked by basic anti-bot algorithms
            jitter = random.uniform(0.5, 2.0)
            sleep_time = CHECK_INTERVAL + jitter
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info(f"\n{Fore.YELLOW}Bot detenido manualmente por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            logger.error(f"{Fore.RED}Error inesperado en el bucle principal: {e}")
            logger.info(f"Reintentando en {CHECK_INTERVAL} segundos...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
