# bot_part_4.py - Часть 4/7
# Функции: мониторинг, хранение истории, генерация графиков

import matplotlib.pyplot as plt
import io
import base64
import asyncio
import datetime
import os
from typing import Dict, List

# === Глобальный словарь для хранения истории (в реальном проекте используйте БД) ===
monitoring_history = {}

# === Функция добавления в историю ===
def add_to_history(chat_id: int, url: str, site_ok: bool, ssl_ok: bool, load_time=None, size_kb=None, error=None):
    """
    Добавляет результат проверки в историю для построения графика.
    Хранит только последние 15 записей (для актуальности).
    """
    now = datetime.datetime.now()
    entry = {
        "time": now.strftime("%H:%M"),
        "url": url,
        "site_ok": site_ok,
        "ssl_ok": ssl_ok,
        "load_time": load_time,
        "size_kb": size_kb,
        "error": error
    }

    if chat_id not in monitoring_history:
        monitoring_history[chat_id] = []

    # Добавляем новую запись
    monitoring_history[chat_id].append(entry)

    # Оставляем только последние 15 записей
    if len(monitoring_history[chat_id]) > 15:
        monitoring_history[chat_id] = monitoring_history[chat_id][-15:]


# === Генерация графика доступности сайта ===
def generate_uptime_chart(chat_id: int) -> str:
    """
    Создаёт график uptime (работает / не работает) за последние проверки.
    Возвращает base64 строку изображения.
    """
    if chat_id not in monitoring_history or not monitoring_history[chat_id]:
        return None

    history = monitoring_history[chat_id]
    times = [entry["time"] for entry in history]
    values = [1 if entry["site_ok"] else 0 for entry in history]

    plt.figure(figsize=(10, 4))
    plt.plot(times, values, marker='o', linestyle='-', color='#2E8B57', linewidth=2, markersize=6)
    plt.title("📈 Доступность сайта", fontsize=14, fontweight='bold')
    plt.ylabel("Статус", fontsize=12)
    plt.xlabel("Время", fontsize=12)
    plt.yticks([0, 1], ['Не работает', 'Работает'])
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return f"image/png;base64,{img_base64}"


# === Генерация графика времени загрузки ===
def generate_load_time_chart(chat_id: int) -> str:
    """
    Создаёт график времени загрузки сайта.
    Возвращает base64 строку изображения.
    """
    if chat_id not in monitoring_history or not monitoring_history[chat_id]:
        return None

    history = monitoring_history[chat_id]
    times = [entry["time"] for entry in history]
    load_times = [float(entry["load_time"].split()[0]) if entry["load_time"] and entry["load_time"] != "N/A" else 0 for entry in history]

    plt.figure(figsize=(10, 4))
    plt.bar(times, load_times, color='#4682B4', alpha=0.7)
    plt.title("⏱ Время загрузки сайта", fontsize=14, fontweight='bold')
    plt.ylabel("Секунды", fontsize=12)
    plt.xlabel("Время", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return f"image/png;base64,{img_base64}"


# === Фоновая задача мониторинга ===
async def start_monitoring_task(context: any, chat_id: int, url: str):
    """
    Асинхронная задача, которая каждые 5 минут проверяет сайт.
    Если сайт упал — отправляет уведомление.
    """
    last_status = None
    last_ssl_status = None

    while True:
        try:
            from bot_part_2 import check_website, check_ssl

            # Проверка сайта
            result = check_website(url)
            site_ok = result.get("is_ok", False)
            load_time = result.get("load_time", "N/A")
            size_kb = result.get("size_kb", "N/A")

            # Проверка SSL
            ssl_result = check_ssl(url)
            ssl_ok = ssl_result.get("valid", False)

            # Добавляем в историю
            add_to_history(chat_id, url, site_ok, ssl_ok, load_time, size_kb)

            # Уведомляем при изменении статуса
            if last_status is not None and not site_ok and last_status == True:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔴 Сайт упал!\n\n🌐 {url}\n🕒 {datetime.datetime.now().strftime('%d.%m %H:%M')}",
                    parse_mode='HTML'
                )
            elif last_status is not None and site_ok and not last_status:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🟢 Сайт восстановлен!\n\n🌐 {url}\n🕒 {datetime.datetime.now().strftime('%d.%m %H:%M')}",
                    parse_mode='HTML'
                )

            last_status = site_ok
            last_ssl_status = ssl_ok

        except Exception as e:
            print(f"❌ Ошибка в фоновом мониторинге: {e}")
            add_to_history(chat_id, url, False, False, error=str(e))

        # Пауза 5 минут
        await asyncio.sleep(300)


logger.info("✅ Часть 4/7: Функции мониторинга и графиков загружены")
