# bot_part_6.py - Часть 6/7
# Главное меню, обработка сообщений, оплата

# === Импорты в начале файла ===
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from urllib.parse import urlparse

# Импортируем функции из других частей
from bot_part_2 import check_website, check_ssl
from bot_part_3 import check_meta, find_broken_links, check_robots_and_sitemap
from bot_part_4 import add_to_history, generate_status_chart
from bot_part_5 import create_pdf_from_data

# === Клавиатуры ===
main_menu_keyboard = [
    ["🔍 Бесплатная проверка"],
    ["💳 Базовый аудит — 300 руб"],
    ["🚀 Продвинутый аудит — 700 руб"],
    ["📌 Мониторинг — 1000 руб/мес"],
    ["📘 О боте", "⭐ Отзывы"],
    ["❓ FAQ"]  # ✅ Кнопка FAQ восстановлена
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

# === Обработка текстовых команд ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user
    chat_id = user.id

    # === Кнопки меню ===
    if text == "📘 О боте":
        await about(update, context)
        return
    elif text == "❓ FAQ":
        await faq(update, context)
        return
    elif text == "⭐ Отзывы":
        await reviews(update, context)
        return

    # === Бесплатная проверка ===
    elif text == "🔍 Бесплатная проверка":
        await update.message.reply_text(
            "Введите ссылку на сайт для бесплатной проверки:"
        )
        context.user_data['check_type'] = 'free_check'

    # === Базовый аудит ===
    elif text == "💳 Базовый аудит — 300 руб":
        await update.message.reply_text(
            "Введите ссылку на сайт для базового аудита:"
        )
        context.user_data['check_type'] = 'basic'

    # === Продвинутый аудит ===
    elif text == "🚀 Продвинутый аудит — 700 руб":
        await update.message.reply_text(
            "Введите ссылку на сайт для продвинутого аудита:"
        )
        context.user_data['check_type'] = 'advanced'

    # === Мониторинг ===
    elif text == "📌 Мониторинг — 1000 руб/мес":
        await monitoring_info(update, context)

    # === Обработка ссылки после выбора услуги ===
    elif context.user_data.get('check_type') in ['free_check', 'basic', 'advanced']:
        if not is_valid_url(text):
            await update.message.reply_text("❌ Некорректный URL. Пример: https://example.com")
            return

        url = text
        check_type = context.user_data['check_type']

        # === Бесплатная проверка ===
        if check_type == 'free_check':
            result = check_website(url)
            ssl_result = check_ssl(url)
            message = (
                f"📊 <b>Базовая проверка</b>\n"
                f"🔹 <b>Сайт:</b> {result['url']}\n"
                f"✅ <b>Доступность:</b> {result['status']}\n"
                f"⏱ <b>Скорость:</b> {result.get('load_time', 'N/A')}\n"
                f"🔐 <b>SSL:</b> {'✅ Действителен' if ssl_result.get('valid') else '❌ Недействителен'}"
            )
            await update.message.reply_text(message, parse_mode='HTML')

        # === Базовый аудит ===
        elif check_type == 'basic':
            payment_info = (
                "📌 <b>Базовый аудит — 300 руб</b>\n"
                "✅ Включает:\n"
                "• Доступность, скорость, SSL\n"
                "• Наличие H1, title, meta description\n"
                "• Проверка viewport, canonical\n"
                "• Битые ссылки\n\n"

                "💳 <b>Оплата:</b>\n"
                "• ЮMoney: <code>4100 1192 7237 8518</code>\n\n"

                "📤 <b>После оплаты:</b>\n"
                "1. Сделайте скриншот чека\n"
                "2. Отправьте его на email: <code>Iv.vboris@yandex.ru</code>\n"
                "3. Укажите:\n"
                " • Ссылку на сайт\n"
                " • Куда выслать отчёт (Telegram, email)\n\n"
                "💬 Я свяжусь с вами в течение 1 часа."
            )
            await update.message.reply_text(payment_info, parse_mode='HTML', reply_markup=payment_keyboard)

        # === Продвинутый аудит ===
        elif check_type == 'advanced':
            payment_info = (
                "🚀 <b>Продвинутый аудит — 700 руб</b>\n"
                "✅ Включает всё из базового +:\n"
                "• Сравнение с конкурентом\n"
                "• Детальные рекомендации\n"
                "• Комментарий эксперта\n\n"

                "💳 <b>Оплата:</b>\n"
                "• ЮMoney: <code>4100 1192 7237 8518</code>\n\n"

                "📤 <b>После оплаты:</b>\n"
                "1. Сделайте скриншот чека\n"
                "2. Отправьте его на email: <code>Iv.vboris@yandex.ru</code>\n"
                "3. Укажите:\n"
                " • Ссылку на сайт\n"
                " • Куда выслать отчёт (Telegram, email)\n\n"
                "💬 Я свяжусь с вами в течение 1 часа."
            )
            await update.message.reply_text(payment_info, parse_mode='HTML', reply_markup=payment_keyboard)

        # === Очистка ===
        context.user_data.clear()

    # === Неизвестная команда ===
    else:
        await update.message.reply_text(
            "🔴 Неизвестная команда. Выберите действие из меню.",
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        )


# === Команда /about ===
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🤖 <b>Website Audit Bot</b>\n\n"
        "Проверяю сайты на SEO, производительность, безопасность и доступность.\n\n"
        "🔹 <b>Бесплатная проверка</b> — базовые метрики\n"
        "🔹 <b>Базовый аудит</b> — полный SEO-анализ\n"
        "🔹 <b>Продвинутый аудит</b> — сравнение с конкурентом + экспертный комментарий\n"
        "🔹 <b>Мониторинг</b> — 24/7 наблюдение за сайтом\n\n"
        "Создано для владельцев сайтов, маркетологов, SEO-специалистов."
    )
    await update.message.reply_text(message, parse_mode='HTML')


# === Команда /faq ===
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "❓ <b>Частые вопросы</b>\n\n"
        "<b>Как работает оплата?</b>\n"
        "Вы платите через ЮMoney (4100 1192 7237 8518), присылаете скриншот чека на email — я запускаю аудит.\n\n"
        "<b>Когда пришлют отчёт?</b>\n"
        "В течение 1 часа после оплаты.\n\n"
        "<b>Можно ли сравнить с несколькими конкурентами?</b>\n"
        "Сейчас — только с одним. Но вы можете заказать несколько аудитов.\n\n"
        "<b>Работает ли мониторинг 24/7?</b>\n"
        "Да, проверка каждые 5 минут. Уведомления при падении."
    )
    await update.message.reply_text(message, parse_mode='HTML')


# === Команда /reviews ===
async def reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "⭐ <b>Отзывы клиентов</b>\n\n"
        "<i>«Сравнение с конкурентом показало, что у меня хуже title и скорость. Исправил — трафик вырос на 30%»</i>\n"
        "— @client3\n\n"
        "<i>«Мониторинг спас мой бизнес. Уведомили о падении сайта за 5 минут до дедлайна»</i>\n"
        "— @client2\n\n"
        "<i>«Пользуюсь мониторингом 6 месяцев. Ни одного простоя не пропустил. Удобно, надёжно»</i>\n"
        "— @client4\n\n"
        "💬 У вас есть результат? Напишите на Iv.vboris@yandex.ru — добавлю в отзывы!"
    )
    await update.message.reply_text(message, parse_mode='HTML')


# === Команда /monitoring_info ===
async def monitoring_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "📌 <b>Мониторинг — 1000 руб/мес</b>\n"
        "✅ Проверка каждые 5 минут\n"
        "✅ Уведомления при падении\n"
        "✅ Еженедельные отчёты\n"
        "✅ График активности\n\n"
        "💳 <b>Оплата:</b>\n"
        "• ЮMoney: <code>4100 1192 7237 8518</code>\n\n"
        "📤 <b>После оплаты:</b>\n"
        "1. Пришлите скриншот чека на email: <code>Iv.vboris@yandex.ru</code>\n"
        "2. Укажите:\n"
        " • Ссылку на сайт\n"
        " • Желаемый интервал проверки (5/10/30 мин)\n\n"
        "💬 Я включу мониторинг в течение 1 часа."
    )
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=payment_keyboard)
