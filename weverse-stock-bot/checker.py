import requests
from bs4 import BeautifulSoup
import logging
from config import TARGET_URL, USE_PLAYWRIGHT

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Connection": "keep-alive",
}

def analyze_html_for_stock(html_content: str) -> bool:
    """
    Analiza el DOM HTML para determinar el estado del stock.
    Returns:
      True si HAY STOCK (ya no aparece AGOTADO o el botón no está deshabilitado)
      False si NO HAY STOCK (AGOTADO y deshabilitado)
      None si no se encontró el botón (puede requerir renderizado JS)
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # We look for the checkout button
    buttons = soup.find_all("button", attrs={"name": "checkout"})
    
    if not buttons:
        return None
        
    for btn in buttons:
        btn_text = btn.get_text(strip=True).upper()
        is_disabled = btn.has_attr("disabled")
        
        # If text is not AGOTADO, or if it isn't disabled, item is in stock
        if "AGOTADO" not in btn_text or not is_disabled:
            return True
        else:
            return False
            
    return None

def check_stock_requests(url: str) -> bool:
    """
    Ruta rápida: usa requests y BeautifulSoup para revisar stock.
    Devuelve None si no puede determinarlo (ej: página SPA).
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        status = analyze_html_for_stock(response.text)
        if status is not None:
            return status
            
        logger.debug("No se pudo encontrar el botón con requests. La página puede requerir renderizado con JavaScript.")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red durante la revisión con requests: {e}")
        return None

def check_stock_playwright(url: str) -> bool:
    """
    Ruta de respaldo: usa Playwright para renderizar JS y extraer el botón.
    Devuelve None si ocurre un error.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright no está instalado. Instálalo con: pip install playwright && playwright install")
        return None
        
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9,es;q=0.8"})
            
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for the checkout button to appear
            try:
                page.wait_for_selector("button[name='checkout']", timeout=10000)
            except Exception:
                logger.debug("No se encontró el botón de checkout con Playwright después de 10 segundos.")
                pass # Continue to analyze page source anyway
            
            content = page.content()
            browser.close()
            
            status = analyze_html_for_stock(content)
            return status if status is not None else False
            
    except Exception as e:
        logger.error(f"Error de Playwright: {e}")
        return None

def check_stock() -> bool:
    """
    Orquesta la lógica de revisión de stock.
    Devuelve True si hay stock, False en caso contrario.
    """
    if not USE_PLAYWRIGHT:
        status = check_stock_requests(TARGET_URL)
        if status is not None:
            return status
            
        logger.debug("La ruta rápida con requests no pudo determinar el stock. Probando fallback con Playwright...")
    
    # Try Playwright if:
    # 1. USE_PLAYWRIGHT is True in config
    # 2. Or requests fast-path was enabled but resulted in None (JS required)
    status = check_stock_playwright(TARGET_URL)
    if status is not None:
        return status
        
    # Si ambos métodos fallan, devolvemos False para evitar alertas de falso positivo
    logger.error("No se pudo determinar el estado del stock de forma confiable con ambos métodos.")
    return False
