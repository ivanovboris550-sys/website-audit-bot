# bot_part_7.py - Часть 7/7
# Админ-команды, обработчик ошибок, запуск бота

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

# === Импорт необходимых функций из других частей ===
try:
    from bot_part_1 import BOT_TOKEN, ADMIN_CHAT_ID, log_action
    logger.info("✅ bot_part_1 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_1: {e}")
    sys.exit(1)

try:
    from bot_part_6 import handle_message, main_menu_markup
    logger.info("✅ bot_part_6 загружена")
except ImportError as e:
    logger.critical(f"❌ Ошибка импорта bot_part_6: {e}")
    sys.exit(1)


# === Команда /admin_check — проверка работоспособности (только для админа) ===
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
                text=f"⚠️ Ошибка у пользователя `{update.effective_user.name}`:\n```\n{context.error}\n```",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ Не удалось отправить уведомление админу: {e}")


# === Главная функция запуска бота ===
async def main():
    """Создаёт Application и запускает polling."""
    try:
        # Для Windows (если нужно)
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Создание Application
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавление обработчиков
        application.add_handler(CommandHandler("start", lambda u, c: handle_message(u, c)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CommandHandler("admin_check", admin_check))
        application.add_error_handler(error_handler)

        logger.info("🚀 Бот запущен. Ожидание команд...")

        # Запуск polling
        await application.run_polling(
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
