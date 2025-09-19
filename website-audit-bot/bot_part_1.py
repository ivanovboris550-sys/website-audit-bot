# bot_part_1.py - Часть 1/7
# Импорты, .env, настройки, логирование

import os
import asyncio
import datetime
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import csv
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Фикс для Windows (если нужно) ===
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === Загрузка переменных окружения из .env ===
from dotenv import load_dotenv
load_dotenv()

# === Настройки бота ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

if not BOT_TOKEN:
    raise ValueError("❌ Переменная окружения BOT_TOKEN не найдена. Проверьте файл .env")

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Создание необходимых папок ===
os.makedirs("reports", exist_ok=True)
os.makedirs("monitored_sites", exist_ok=True)

# === Функция для записи статистики ===
def log_action(chat_id: int, username: str, action: str, details: str = ""):
    """Записывает действия пользователя в CSV-файл."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists("bot_stats.csv")
    with open("bot_stats.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Chat ID", "Username", "Action", "Details"])
        writer.writerow([timestamp, chat_id, username, action, details])

# === Глобальные переменные ===
total_checks = 0
total_audits = 0

logger.info("✅ Часть 1/7: Настройки загружены, папки созданы")
