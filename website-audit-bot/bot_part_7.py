# bot_part_7.py - Часть 7/7
# Запуск бота, админ-команды

import asyncio
import logging
import sys
import os
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Глобальная переменная для доступа к app (если нужно) ===
app = None

# === Попытка импорта частей бота ===
try:
    from bot_part_1 import BOT_TOKEN, ADMIN_CHAT_ID, start
    logger.info("✅ Часть 1/7: bot_part_1 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_1: {e}")
    sys.exit(1)

try:
    from bot_part_6 import handle_message
    logger.info("✅ Часть 6/7: bot_part_6 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_6: {e}")
    sys.exit(1)


# === Обработчик ошибок ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует исключения, возникающие при обработке обновлений."""
    if isinstance(update, Update):
        user = update.effective_user
        chat_id = update.effective_chat.id
        message = f"❗️ Ошибка у пользователя @{user.username} ({chat_id}): {context.error}"
    else:
        message = f"❗️ Фатальная ошибка: {context.error}"

    logger.error(message, exc_info=context.error)


# === Команда /admin (доступна только администратору) ===
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 У вас нет доступа к этой команде.")
        return

    stats_file = "bot_stats.csv"
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'rb') as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename="статистика_бота.csv",
                    caption="📊 Статистика использования бота"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Не удалось отправить файл: {e}")
    else:
        await update.message.reply_text("📂 Файл статистики не найден.")


# === Главная функция запуска бота ===
async def main():
    """Создаёт Application и запускает polling."""
    global app

    try:
        # Для Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Создание Application
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавление обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_error_handler(error_handler)

        logger.info("🚀 Бот запущен. Ожидание команд...")

        # Запуск polling
        await application.run_polling(
            drop_pending_updates=True,
            timeout=30
        )

    except Exception as e:
        logger.critical(f"🔴 Фатальная ошибка при запуске бота: {e}")
        raise


# === Точка входа для выполнения скрипта ===
if __name__ == "__main__":
    try:
        # Запуск основной асинхронной функции
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную (Ctrl+C)")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
