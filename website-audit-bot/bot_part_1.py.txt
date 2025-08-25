# bot_part_1.py - Часть 1/7
# Настройки, .env, логирование, глобальные переменные

import os
from dotenv import load_dotenv
import logging

# === Загрузка переменных окружения ===
load_dotenv()

# === Проверка обязательных переменных ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не задан BOT_TOKEN в .env файле")

try:
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
except (TypeError, ValueError):
    raise ValueError("❌ Не задан или некорректен ADMIN_CHAT_ID в .env файле")

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Глобальные переменные ===
# Хранение конкурента для сравнения
competitor_urls = {"default": None}  # Устанавливается через /set_competitor

# Активные задачи мониторинга
active_monitoring = {}

# Последний статус сайта (для уведомлений)
last_status = {}

# История проверок (для графиков)
monitoring_history = {}

# Подписки пользователей
user_subscriptions = {}

# === Папки ===
REPORTS_DIR = "reports"
FONTS_DIR = "fonts"

# Создаём папки при старте
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# === Константы ===
MONITORING_INTERVALS = {
    "5_min": 300,
    "10_min": 600,
    "30_min": 1800
}

# === Логирование старта ===
logger.info("✅ Часть 1/7: Настройки загружены, папки созданы")





