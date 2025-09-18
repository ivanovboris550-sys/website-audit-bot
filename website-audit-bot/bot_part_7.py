# bot_part_7.py - Часть 7/7
# Админ-команды, запуск бота (стабильный запуск)

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

# === Глобальная переменная для токена (если не используется .env) ===
# Убедитесь, что BOT_TOKEN и ADMIN_CHAT_ID загружены из bot_part_1
try:
    from bot_part_1 import BOT_TOKEN, ADMIN_CHAT_ID, start
    logger.info("✅ bot_part_1 загружен")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_1: {e}")
    sys.exit(1)

try:
    from bot_part_6 import handle_message
    logger.info("✅ bot_part_6 загружен")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_6: {e}")
    sys.exit(1)


# === Команда /admin_check — проверка работоспособности ===
async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для администратора — тестовая команда."""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Доступ запрещён.")
        return
    await update.message.reply_text("🟢 Бот работает, сервер жив.")


# === Обработчик ошибок ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Логирует все ошибки, возникающие в работе бота."""
    logger.error(f"🔴 Произошла ошибка: {context.error}", exc_info=True)

    # Опционально: отправить сообщение администратору
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ Ошибка у пользователя {update.effective_user.name}: `{context.error}`",
                parse_mode="Markdown"
            )
        except:
            pass


# === Главная функция запуска бота ===
async def main():
    """Создаёт Application и запускает polling."""
    try:
        # Для Windows (если нужно)
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Создание Application
        app = Application.builder().token(BOT_TOKEN).build()

        # Добавление обработчиков
        app.add_handler(CommandHandler("start", start))
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
        logger.critical(f"💥 Критическая ошибка при запуске: {e}")
        raise


# === Точка входа ===
if __name__ == "__main__":
    try:
        # Запускаем main через asyncio.run() — стандартный способ
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную (Ctrl+C)")
    except Exception as e:
        logger.critical(f"💀 Фатальная ошибка: {e}")
