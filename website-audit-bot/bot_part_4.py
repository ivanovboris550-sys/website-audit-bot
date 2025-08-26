# bot_part_4.py - Часть 4/7
# Функции: мониторинг, хранение истории, генерация графиков

import matplotlib.pyplot as plt
import io
import base64
import asyncio
import datetime
import os

# === Функция добавления в историю ===
def add_to_history(chat_id, url, site_ok, ssl_ok, load_time=None, size_kb=None, error=None):
    """
    Добавляет результат проверки в историю для построения графика.
    Хранит только последние 100 записей.
    """
    now = datetime.datetime.now()
    if chat_id not in monitoring_history:
        monitoring_history[chat_id] = []

    monitoring_history[chat_id].append({
        "time": now.strftime("%d.%m %H:%M"),
        "url": url,
        "site_ok": site_ok,
        "ssl_ok": ssl_ok,
        "load_time": load_time,
        "size_kb": size_kb,
        "error": error
    })

    # Ограничиваем историю 100 последними записями
    if len(monitoring_history[chat_id]) > 100:
        monitoring_history[chat_id] = monitoring_history[chat_id][-100:]


# === Генерация графика активности ===
def generate_status_chart(history, url):
    """
    Генерирует график доступности сайта.
    Возвращает base64-изображение.
    """
    if not history:
        return None

    try:
        # Подготавливаем данные
        times = [entry["time"] for entry in history]
        site_status = [1 if entry["site_ok"] else 0 for entry in history]
        ssl_status = [1 if entry["ssl_ok"] else 0 for entry in history]

        # Создаём график
        plt.figure(figsize=(10, 4))
        plt.plot(times, site_status, marker='o', label='Доступность', color='green')
        plt.plot(times, ssl_status, marker='x', label='SSL', color='blue')
        plt.yticks([0, 1], ['Не работает', 'Работает'])
        plt.xticks(rotation=45, fontsize=8)
        plt.title(f'График активности: {url}')
        plt.legend()
        plt.tight_layout()

        # Сохраняем в буфер
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()

        # Кодируем в base64
        return base64.b64encode(img_buffer.read()).decode('utf-8')

    except Exception as e:
        print(f"❌ Ошибка генерации графика: {e}")
        return None


# === Фоновая задача мониторинга ===
async def start_monitoring_task(context, chat_id, url, interval=300, duration=604800):
    """
    Фоновая задача: проверяет сайт каждые `interval` секунд в течение `duration` секунд.
    Отправляет уведомления при падении и в конце сессии.
    """
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=duration)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Мониторинг запущен для: {url}\n⏱ Проверка каждые {interval // 60} мин\n📅 Продолжительность: {duration // 3600} ч"
    )

    last_site_status = True
    last_ssl_status = True

    while datetime.datetime.now() < end_time:
        try:
            # Проверяем сайт
            result = check_website(url)
            ssl_result = check_ssl(url)

            site_ok = result["is_ok"]
            ssl_ok = ssl_result.get("valid", False) if ssl_result.get("error") is None else False

            # Добавляем в историю
            add_to_history(
                chat_id=chat_id,
                url=url,
                site_ok=site_ok,
                ssl_ok=ssl_ok,
                load_time=result.get("load_time"),
                size_kb=result.get("size_kb"),
                error=result.get("error")
            )

            # Уведомляем при падении
            if last_site_status and not site_ok:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔴 Сайт упал!\n🌐 {url}\n⏱ {result.get('load_time', 'N/A')}\n⚠ {result.get('error', 'Неизвестная ошибка')}"
                )
            elif not last_site_status and site_ok:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🟢 Сайт восстановился!\n🌐 {url}"
                )

            last_site_status = site_ok
            last_ssl_status = ssl_ok

        except Exception as e:
            print(f"❌ Ошибка в задаче мониторинга: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠ Ошибка мониторинга: {e}"
            )

        # Ждём перед следующей проверкой
        await asyncio.sleep(interval)

    # В конце сессии — отправляем отчёт
    history = monitoring_history.get(chat_id, [])
    chart_img = generate_status_chart(history, url)

    report = f"📊 Завершён мониторинг для: {url}\n"
    if history:
        up_count = sum(1 for h in history if h["site_ok"])
        total = len(history)
        uptime = round(up_count / total * 100, 1)
        report += f"📈 Доступность: {uptime}% ({up_count}/{total})\n"
    else:
        report += "📈 Нет данных для анализа\n"

    await context.bot.send_message(chat_id=chat_id, text=report)

    if chart_img:
        temp_path = f"temp_chart_{chat_id}.png"
        with open(temp_path, "wb") as f:
            f.write(base64.b64decode(chart_img))
        await context.bot.send_photo(chat_id=chat_id, photo=open(temp_path, 'rb'))
        os.remove(temp_path)

    # Удаляем задачу из активных
    if chat_id in active_monitoring:
        del active_monitoring[chat_id]
