# simple_bot.py — простейший бот для проверки хостинга

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === Замените на ваш токен ===
BOT_TOKEN = "7957425521:AAEQcCqZbk8fmGsREWnSkhwgF43y7xGv-mc"

# === Обработчик команды /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Хостинг работает!\n\n"
        "🤖 Бот запущен.\n"
        "🔧 Это тестовый бот.\n\n"
        "Введите /test"
    )

# === Обработчик команды /test ===
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Всё в порядке! Код выполняется.")

# === Запуск бота ===
if __name__ == "__main__":
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))

    app.run_polling()
    print("Бот запущен!")
