# Bot de Monitoreo de Stock Weverse

Bot en Python para monitorear una URL de producto en Weverse Shop y enviar alertas por Telegram cuando el estado deja de ser `AGOTADO`.

## Características

- Revisión de stock por `requests` + `BeautifulSoup` (rápido).
- Fallback automático con `Playwright` para páginas con JavaScript.
- Alertas por Telegram con anti-duplicados.
- Comando Telegram `/ping` para validar vida del bot.
- Logs en consola y en `bot.log`.
- Mensajes, alertas y avisos en español.

## Requisitos

- Python 3.10+ (local)
- Docker y Docker Compose (despliegue VPS recomendado)

## Configuración

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Completa tus variables en `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=5
TARGET_URL=https://shop.weverse.io/es/shop/USD/artists/2/sales/54189?shopAndCurrency=USD&artistId=2&saleId=54189
USE_PLAYWRIGHT=True
```

## Ejecución local

```bash
pip install -r requirements.txt
playwright install chromium
python bot.py
```

Opciones útiles:

```bash
python bot.py --test-alert
python bot.py --healthcheck
python bot.py --once
```

Validaciones rápidas:

- `python bot.py --test-alert`: valida envío a Telegram.
- `python bot.py --healthcheck`: valida scraping una vez.
- Desde Telegram: envía `/ping` al chat/grupo configurado y el bot responderá que está activo.

Al iniciar, el bot envía automáticamente un saludo de arranque y confirma que comenzó a monitorear.

## Docker (recomendado para VPS)

### Levantar con Docker Compose

```bash
docker compose up -d --build
```

### Ver logs

```bash
docker compose logs -f
```

### Detener

```bash
docker compose down
```

## Estructura del proyecto

- `bot.py`: bucle principal, logs y CLI.
- `checker.py`: lógica de detección de stock (`requests` + `Playwright`).
- `notifier.py`: integración con Telegram y formato de alertas.
- `config.py`: carga y validación de variables de entorno.
- `Dockerfile`: imagen lista para VPS.
- `docker-compose.yml`: despliegue simple 24/7.

## Recomendación para VPS

- Usa `restart: unless-stopped` (ya configurado).
- Ejecuta con un usuario no-root en el servidor.
- Guarda el `.env` solo en el VPS (nunca lo subas al repositorio).
