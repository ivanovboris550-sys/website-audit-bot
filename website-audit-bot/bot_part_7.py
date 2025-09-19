# bot_part_7.py - Часть 7/7 (ФИНАЛЬНЫЙ РАБОЧИЙ ВАРИАНТ)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import logging
import sys

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Импорт из других частей ===
try:
    from bot_part_1 import BOT_TOKEN, ADMIN_CHAT_ID
    logger.info("✅ bot_part_1 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_1: {e}")
    sys.exit(1)

try:
    from bot_part_6 import handle_message
    logger.info("✅ bot_part_6 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_6: {e}")
    sys.exit(1)


# === Команда /admin_check (для админа) ===
async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_CHAT_ID:
        await update.message.reply_text("🟢 Бот работает!")


# === Обработчик ошибок ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"🔴 Ошибка: {context.error}", exc_info=True)


# === Главная функция запуска ===
async def main():
    """Создаёт Application и запускает polling."""
    try:
        # Для Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Создание приложения
        app = Application.builder().token(BOT_TOKEN).build()

        # Добавление обработчиков
        app.add_handler(CommandHandler("start", lambda u, c: handle_message(u, c)))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CommandHandler("admin_check", admin_check))
        app.add_error_handler(error_handler)

        logger.info("🚀 Бот запущен. Ожидание команд...")

        # Запуск polling
        await app.run_polling(
            drop_pending_updates=True,
            timeout=30
        )

    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        raise


# === Точка входа ===
if __name__ == "__main__":
    try:
        # ЕДИНСТВЕННЫЙ правильный способ для v20+
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"💀 Фатальная ошибка: {e}")
