# bot_part_6.py - Часть 6/7 (переписана с нуля)
# Обработка сообщений и меню

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from urllib.parse import urlparse

# === Глобальные переменные (не меняем) ===
main_menu_keyboard = [
    ["🔍 Бесплатная проверка"],
    ["💳 Базовый аудит — 300 руб"],
    ["🚀 Продвинутый аудит — 700 руб"],
    ["📌 Мониторинг — 1000 руб/мес"],
    ["📘 О боте", "⭐ Отзывы"],
    ["❓ FAQ"]
]

# Кнопка оплаты — только ЮMoney
payment_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Оплатить через ЮMoney", url="https://yoomoney.ru/to/4100119272378518")]
])

# === Проверка URL ===
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# === Основная функция обработки ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # === Обработка кнопок ===
    if text == "🔍 Бесплатная проверка":
        await update.message.reply_text("Введите ссылку на сайт:")
        context.user_data['check_type'] = 'free'

    elif text == "💳 Базовый аудит — 300 руб":
        await update.message.reply_text("Введите ссылку на сайт для базового аудита:")
        context.user_data['check_type'] = 'basic'

    elif text == "🚀 Продвинутый аудит — 700 руб":
        await update.message.reply_text("Введите ссылку на сайт для продвинутого аудита:")
        context.user_data['check_type'] = 'advanced'

    elif text == "📌 Мониторинг — 1000 руб/мес":
        await update.message.reply_text(
            "📌 <b>Мониторинг — 1000 руб/мес</b>\n"
            "✅ Проверка каждые 5 минут\n"
            "✅ Уведомления при падении\n"
            "💳 <b>Оплата:</b> ЮMoney: <code>4100 1192 7237 8518</code>\n"
            "📤 После оплаты пришлите чек на Iv.vboris@yandex.ru",
            parse_mode='HTML',
            reply_markup=payment_keyboard
        )

    elif text == "📘 О боте":
        await update.message.reply_text(
            "🤖 <b>Website Audit Bot</b>\n\n"
            "Проверяю сайты на SEO, производительность и доступность.\n\n"
            "🔹 Бесплатная проверка\n"
            "🔹 Базовый и продвинутый аудит\n"
            "🔹 Мониторинг 24/7",
            parse_mode='HTML'
        )

    elif text == "⭐ Отзывы":
        await update.message.reply_text(
            "⭐ <b>Отзывы клиентов</b>\n\n"
            "<i>«Трафик вырос на 30% после аудита»</i> — @client3\n"
            "<i>«Уведомили о падении за 5 минут»</i> — @client2\n\n"
            "💬 Напишите на Iv.vboris@yandex.ru — добавлю ваш отзыв!",
            parse_mode='HTML'
        )

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "❓ <b>Частые вопросы</b>\n\n"
            "<b>Когда пришлют отчёт?</b>\n"
            "В течение 1 часа после оплаты.\n\n"
            "<b>Работает ли мониторинг 24/7?</b>\n"
            "Да, проверка каждые 5 минут.",
            parse_mode='HTML'
        )

    # === Обработка введённого URL ===
    elif context.user_data.get('check_type') in ['free', 'basic', 'advanced']:
        if not is_valid_url(text):
            await update.message.reply_text("❌ Некорректный URL. Пример: https://example.com")
            return

        url = text
        check_type = context.user_data['check_type']

        # Импорты (чтобы избежать циклических проблем)
        from bot_part_2 import check_website, check_ssl

        # Выполняем проверку
        result = check_website(url)
        ssl_result = check_ssl(url)

        # Формируем ответ
        message = (
            f"📊 <b>Результат проверки</b>\n"
            f"🔹 <b>Сайт:</b> {result['url']}\n"
            f"✅ <b>Доступность:</b> {result['status']}\n"
            f"⏱ <b>Скорость:</b> {result.get('load_time', 'N/A')}\n"
            f"🔐 <b>SSL:</b> {'✅ Действителен' if ssl_result.get('valid') else '❌ Недействителен'}"
        )

        await update.message.reply_text(message, parse_mode='HTML')

        # Показываем оплату для платных аудитов
        if check_type in ['basic', 'advanced']:
            payment_info = (
                f"{'🚀' if check_type == 'advanced' else '💳'} <b>Аудит — {700 if check_type == 'advanced' else 300} руб</b>\n"
                "✅ Включает полный SEO-анализ\n\n"
                "💳 <b>Оплата:</b> ЮMoney: <code>4100 1192 7237 8518</code>\n\n"
                "📤 <b>После оплаты:</b>\n"
                "1. Скриншот чека\n"
                "2. На email: <code>Iv.vboris@yandex.ru</code>\n"
                "3. Указать: ссылку и куда выслать отчёт"
            )
            await update.message.reply_text(payment_info, parse_mode='HTML', reply_markup=payment_keyboard)

        # Очистка
        context.user_data.clear()

    # === Неизвестная команда ===
    else:
        await update.message.reply_text(
            "🔴 Неизвестная команда. Выберите из меню.",
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        )
