# bot_part_7.py - Часть 7/7
# Админ-команды, запуск бота

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import logging
import sys
import os

# === Фикс для Windows (если запускаете локально) ===
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Глобальные переменные (импортируются из bot_part_1) ===
# competitor_urls, active_monitoring, monitoring_history
# Должны быть объявлены в bot_part_1.py

# === Импорт функций из других частей ===
try:
    from bot_part_1 import (
        BOT_TOKEN,
        ADMIN_CHAT_ID,
        competitor_urls,
        active_monitoring,
        monitoring_history
    )
    from bot_part_2 import check_website, check_ssl, check_mobile
    from bot_part_3 import check_meta, find_broken_links, check_robots_and_sitemap
    from bot_part_4 import start_monitoring_task, add_to_history, generate_status_chart
    from bot_part_5 import create_pdf_from_data
    from bot_part_6 import handle_message, main_menu_keyboard
except Exception as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    raise

# === Админ-команда: установка конкурента ===
async def set_competitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Устанавливает сайт-конкурент для сравнения"""
    if update.message.chat_id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text("❗ Укажите сайт-конкурент: /set_competitor ваш-сайт.com")
        return

    competitor = context.args[0].strip()
    if not competitor.startswith(("http://", "https://")):
        competitor = "https://" + competitor

    # Сохраняем
    competitor_urls["default"] = competitor
    await update.message.reply_text(f"✅ Конкурент установлен: {competitor}")


# === Админ-команда: проверка сайта (для теста) ===
async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает полный аудит и отправляет PDF (только для админа)"""
    if update.message.chat_id != ADMIN_CHAT_ID:
        return

    if not context.args:
        await update.message.reply_text("❗ Укажите ссылку: /admin_check ваш-сайт.com")
        return

    url = context.args[0]
    chat_id = update.message.chat_id

    await update.message.reply_text("🔧 Запускаю полный аудит...")

    # === Выполняем проверки ===
    result = check_website(url)
    if not result["is_ok"]:
        await update.message.reply_text(f"❌ Не удалось проверить сайт:\n{result['error']}")
        return

    meta = check_meta(url)
    broken_links = find_broken_links(url)
    mobile = check_mobile(url)
    robots = check_robots_and_sitemap(url)

    # === Сравнение с конкурентом ===
    comp_url = competitor_urls.get("default")
    comparison = None
    if comp_url:
        comparison = compare_with_competitor(url, comp_url)
    else:
        await update.message.reply_text("⚠ Внимание: конкурент не установлен. Установите через /set_competitor")

    # === Генерация графика ===
    add_to_history(chat_id, url, result["is_ok"], result.get("ssl", {}).get("valid", False))
    chart_img = generate_status_chart(monitoring_history.get(chat_id, []), url)

    # === Подготовка данных для PDF ===
    data = {
        "url": url,
        "result": result,
        "meta": meta,
        "broken_links": broken_links,
        "mobile": mobile,
        "robots": robots,
        "comparison": comparison,
        "chart_img": chart_img
    }

    # === Генерация PDF ===
    pdf_path = create_pdf_from_data(chat_id, data, report_type="advanced")
    if pdf_path and os.path.exists(pdf_path):
        await update.message.reply_text("✅ Аудит завершён! Отправляю отчёт...")
        with open(pdf_path, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=chat_id,
                document=pdf_file,
                filename="Продвинутый_аудит.pdf"
            )
        os.remove(pdf_path)
    else:
        await update.message.reply_text("❌ Ошибка генерации PDF-отчёта.")


# === Функция сравнения с конкурентом ===
def compare_with_competitor(your_url, competitor_url=None):
    """
    Сравнивает ваш сайт с конкурентом.
    """
    if not competitor_url:
        competitor_url = competitor_urls.get("default")
    if not competitor_url:
        return None

    try:
        # Проверка вашего сайта
        your_result = check_website(your_url)
        your_meta = check_meta(your_url) if your_result["is_ok"] else {}
        your_mobile = check_mobile(your_url) if your_result["is_ok"] else {}

        # Проверка конкурента
        comp_result = check_website(competitor_url)
        comp_meta = check_meta(competitor_url) if comp_result["is_ok"] else {}
        comp_mobile = check_mobile(competitor_url) if comp_result["is_ok"] else {}

        def safe_get(d, key, default="N/A"):
            return d.get(key, default) if d and "error" not in d else "Ошибка"

        def safe_len(s):
            return len(s) if s and s != "N/A" and s != "Ошибка" else 0

        return {
            "your_url": your_url,
            "competitor_url": competitor_url,
            "title": {
                "your": safe_get(your_meta, "title"),
                "comp": safe_get(comp_meta, "title"),
                "your_len": safe_len(safe_get(your_meta, "title")),
                "comp_len": safe_len(safe_get(comp_meta, "title"))
            },
            "h1": {
                "your": safe_get(your_meta, "h1"),
                "comp": safe_get(comp_meta, "h1")
            },
            "viewport": {
                "your": "✅ Есть" if safe_get(your_meta, "viewport", False) else "❌ Отсутствует",
                "comp": "✅ Есть" if safe_get(comp_meta, "viewport", False) else "❌ Отсутствует"
            },
            "canonical": {
                "your": "✅ Есть" if safe_get(your_meta, "canonical", False) else "❌ Отсутствует",
                "comp": "✅ Есть" if safe_get(comp_meta, "canonical", False) else "❌ Отсутствует"
            },
            "load_time": {
                "your": safe_get(your_result, "load_time"),
                "comp": safe_get(comp_result, "load_time")
            },
            "size_kb": {
                "your": safe_get(your_result, "size_kb"),
                "comp": safe_get(comp_result, "size_kb")
            },
            "mobile_load_time": {
                "your": safe_get(your_mobile, "load_time"),
                "comp": safe_get(comp_mobile, "load_time")
            }
        }
    except Exception as e:
        print(f"❌ Ошибка при сравнении с конкурентом: {e}")
        return None


# === Запуск бота ===
async def main():
    """Запускает бота"""
    try:
        # Создаём приложение
        app = Application.builder().token(BOT_TOKEN).build()

        # === Обработчики команд ===
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "Добро пожаловать! Выберите действие из меню.",
                reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
            )

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("set_competitor", set_competitor))
        app.add_handler(CommandHandler("admin_check", admin_check))

        # === Обработчик текстовых сообщений ===
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # === Запуск ===
        logger.info("✅ Бот запущен. Ожидание команд...")
        await app.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")


# === Запуск (для Python 3.7+) ===
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
