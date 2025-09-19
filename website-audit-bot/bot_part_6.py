# bot_part_6.py - Часть 6/7
# Обработка команд, главное меню, оплата, начало аудита

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
import re
from urllib.parse import urlparse

# === Клавиатуры ===
main_menu_keyboard = [
    ["🔍 Бесплатная проверка"],
    ["💳 Базовый аудит — 300 руб"],
    ["🚀 Продвинутый аудит — 700 руб"],
    ["📌 Мониторинг — 1000 руб/мес"],
    ["📞 Связаться с экспертом"]
]

back_keyboard = [["Назад"]]

main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=False)
back_markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)


# === Функция: проверка валидности URL ===
def is_valid_url(url: str) -> bool:
    """Проверяет, является ли строка корректным URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# === Основной обработчик сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все входящие сообщения от пользователя."""
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    username = update.effective_user.username or update.effective_user.full_name

    # Логируем действие
    from bot_part_1 import log_action
    log_action(chat_id, username, "message", text)

    # === Команда /start ===
    if text == "/start":
        await update.message.reply_text(
            "Привет! 👋 Я — ваш персональный помощник по анализу сайтов.\n\n"
            "Я помогу:\n"
            "• Проверить сайт на ошибки\n"
            "• Проанализировать SEO\n"
            "• Запустить мониторинг\n"
            "• Дать экспертные рекомендации\n\n"
            "Выберите действие:",
            reply_markup=main_menu_markup
        )
        return

    # === Главное меню ===
    elif text == "🔍 Бесплатная проверка":
        await update.message.reply_text(
            "Введите URL сайта для бесплатной проверки (например, https://example.com):",
            reply_markup=back_markup
        )
        context.user_data['state'] = 'awaiting_free_check'
        return

    elif text == "💳 Базовый аудит — 300 руб":
        await update.message.reply_text(
            "Введите URL сайта для базового аудита:",
            reply_markup=back_markup
        )
        context.user_data['state'] = 'awaiting_basic_audit'
        return

    elif text == "🚀 Продвинутый аудит — 700 руб":
        await update.message.reply_text(
            "Введите URL сайта для продвинутого аудита:",
            reply_markup=back_markup
        )
        context.user_data['state'] = 'awaiting_advanced_audit'
        return

    elif text == "📌 Мониторинг — 1000 руб/мес":
        await update.message.reply_text(
            "Введите URL сайта для подключения ежемесячного мониторинга:",
            reply_markup=back_markup
        )
        context.user_data['state'] = 'awaiting_monitoring'
        return

    elif text == "📞 Связаться с экспертом":
        await update.message.reply_text(
            "Свяжитесь с экспертом: @ivanovboris550\n\n"
            "Он ответит в течение 15 минут.",
            reply_markup=main_menu_markup
        )
        return

    elif text == "Назад":
        await update.message.reply_text("Выберите действие:", reply_markup=main_menu_markup)
        context.user_data.clear()
        return

    # === Ожидание URL для бесплатной проверки ===
    elif context.user_data.get('state') == 'awaiting_free_check':
        if not is_valid_url(text):
            await update.message.reply_text("❌ Некорректный URL. Введите полный адрес, например: https://example.com")
            return

        url = text
        context.user_data['url'] = url
        context.user_data['audit_type'] = 'free'

        keyboard = [
            [InlineKeyboardButton("✅ Да, начать", callback_data="confirm_start")],
            [InlineKeyboardButton("🔄 Изменить сайт", callback_data="change_url")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Сайт: {url}\n\n"
            "Начать бесплатную проверку?",
            reply_markup=reply_markup
        )

    # === Все остальные состояния обрабатываются аналогично ===
    elif context.user_data.get('state') in ['awaiting_basic_audit', 'awaiting_advanced_audit', 'awaiting_monitoring']:
        if not is_valid_url(text):
            await update.message.reply_text("❌ Некорректный URL. Введите полный адрес, например: https://example.com")
            return

        url = text
        audit_map = {
            'awaiting_basic_audit': 'basic',
            'awaiting_advanced_audit': 'advanced',
            'awaiting_monitoring': 'monitoring'
        }
        context.user_data['url'] = url
        context.user_data['audit_type'] = audit_map[context.user_data['state']]

        keyboard = [
            [InlineKeyboardButton("✅ Да, начать", callback_data="confirm_start")],
            [InlineKeyboardButton("🔄 Изменить сайт", callback_data="change_url")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        prices = {'basic': '300 руб', 'advanced': '700 руб', 'monitoring': '1000 руб/мес'}
        price_text = prices[context.user_data['audit_type']]

        await update.message.reply_text(
            f"Сайт: {url}\nТип услуги: {price_text}\n\n"
            "Подтвердите запуск?",
            reply_markup=reply_markup
        )

    # === Неизвестная команда ===
    else:
        await update.message.reply_text(
            "🔴 Неизвестная команда. Выберите действие из меню.",
            reply_markup=main_menu_markup
        )


logger.info("✅ Часть 6/7: Обработчик сообщений и меню загружены")
