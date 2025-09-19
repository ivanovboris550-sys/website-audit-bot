# bot_part_5.py - Часть 5/7
# Генерация PDF-отчётов с помощью fpdf2

from fpdf2 import FPDF
import os
from datetime import datetime
import base64
from io import BytesIO

# === Класс для создания PDF ===
class AuditPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Анализ сайта — Отчёт', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Страница {self.page_no()}', align='C')

    def add_title(self, text):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, text, ln=True)
        self.ln(5)

    def add_subtitle(self, text):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, text, ln=True)
        self.ln(3)

    def add_paragraph(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(4)

    def add_code_block(self, text):
        self.set_font('Courier', '', 9)
        self.set_text_color(128, 0, 0)
        self.multi_cell(0, 5, text)
        self.ln(4)

    def add_result_row(self, label, value, status=""):
        self.set_font('Arial', '', 10)
        self.cell(70, 6, label, border=1)
        self.cell(80, 6, str(value), border=1)
        if status == "✅":
            self.set_text_color(0, 128, 0)
        elif status == "❌":
            self.set_text_color(255, 0, 0)
        else:
            self.set_text_color(0, 0, 0)
        self.cell(30, 6, status, border=1, ln=True)
        self.set_text_color(0, 0, 0)

    def add_image_from_base64(self, img_data, title=""):
        if not img_data:
            return
        try:
            # Декодируем base64
            img_bytes = base64.b64decode(img_data.split(",")[1])
            img_buffer = BytesIO(img_bytes)
            
            # Сохраняем временный файл
            temp_path = "/tmp/chart_temp.png"
            with open(temp_path, "wb") as f:
                f.write(img_buffer.read())
            img_buffer.seek(0)

            # Добавляем изображение в PDF
            self.image(temp_path, x=10, w=180)
            os.remove(temp_path)  # Удаляем временный файл
            self.ln(5)
        except Exception as e:
            self.add_paragraph(f"⚠ Ошибка добавления графика: {str(e)}")
            self.ln(5)


# === Генерация PDF по результатам аудита ===
def generate_pdf_report(chat_id: int, url: str, result: dict, meta: dict, ssl_result: dict, mobile: dict, broken_links: dict, comparison: dict, expert_comment: str, uptime_chart: str = None, load_time_chart: str = None):
    """
    Создаёт PDF-отчёт на основе всех данных.
    Возвращает путь к файлу.
    """
    pdf = AuditPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Заголовок
    pdf.add_title("🔍 Полный аудит сайта")
    pdf.add_paragraph(f"Сайт: {url}")
    pdf.add_paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    pdf.ln(10)

    # 1. Общая доступность
    pdf.add_subtitle("🌐 Доступность и производительность")
    pdf.add_result_row("URL", result.get("url", ""), "✅" if result.get("is_ok") else "❌")
    pdf.add_result_row("Статус", result.get("status", "N/A"), "✅" if result.get("is_ok") else "❌")
    pdf.add_result_row("Время загрузки", result.get("load_time", "N/A"))
    pdf.add_result_row("Размер страницы", f"{result.get('size_kb', 'N/A')} KB")

    # 2. SSL
    pdf.add_subtitle("🔒 SSL-сертификат")
    if ssl_result.get("error"):
        pdf.add_paragraph(f"Ошибка: {ssl_result['error']}")
    else:
        pdf.add_result_row("Действителен", "✅" if ssl_result.get("valid") else "❌")
        pdf.add_result_row("Выдан", ssl_result.get("issued_to", "N/A"))
        pdf.add_result_row("Кем выдан", ssl_result.get("issued_by", "N/A"))
        pdf.add_result_row("Истекает", ssl_result.get("expires", "N/A"))

    # 3. Мобильная версия
    pdf.add_subtitle("📱 Мобильная версия")
    pdf.add_result_row("Загружается", "✅" if mobile.get("is_ok") else "❌")
    pdf.add_result_row("Время загрузки", mobile.get("load_time", "N/A"))
    pdf.add_result_row("Размер", f"{mobile.get('size_kb', 'N/A')} KB")

    # 4. SEO
    pdf.add_subtitle("🔎 SEO и метатеги")
    pdf.add_result_row("Title", meta.get("title", "N/A"))
    pdf.add_result_row("Meta Description", meta.get("meta_description", "N/A"))
    pdf.add_result_row("Количество H1", len(meta.get("h1", [])))
    for i, h1 in enumerate(meta.get("h1", [])[:3]):
        pdf.add_paragraph(f"H1 {i+1}: {h1}")

    pdf.add_result_row("OG Title", "✅" if meta["og_tags"].get("og:title") else "❌")
    pdf.add_result_row("OG Description", "✅" if meta["og_tags"].get("og:description") else "❌")
    pdf.add_result_row("OG Image", "✅" if meta["og_tags"].get("og:image") else "❌")

    # 5. robots.txt и sitemap.xml
    pdf.add_subtitle("📄 robots.txt и sitemap.xml")
    pdf.add_result_row("robots.txt", "✅" if result.get("robots_exists") else "❌")
    pdf.add_result_row("sitemap.xml", "✅" if result.get("sitemap_exists") else "❌")

    # 6. Битые ссылки
    pdf.add_subtitle("🔗 Битые ссылки")
    if broken_links.get("error"):
        pdf.add_paragraph(f"Ошибка при проверке: {broken_links['error']}")
    else:
        pdf.add_paragraph(f"Найдено битых ссылок: {broken_links.get('broken', 0)} из {broken_links.get('total', 0)}")
        for link in broken_links.get("links", [])[:10]:  # Только первые 10
            if "404" in link["status"]:
                pdf.add_code_block(f"{link['url']} → {link['status']}")

    # 7. Сравнение с конкурентом
    pdf.add_subtitle("🆚 Сравнение с конкурентом")
    pdf.add_paragraph(
        f"<strong>Ваш сайт:</strong><br>"
        f"• Время загрузки: {comparison['load_time']['your']}<br>"
        f"• Размер: {comparison['size_kb']['your']} KB<br>"
        f"<strong>Конкурент:</strong><br>"
        f"• Время загрузки: {comparison['load_time']['comp']}<br>"
        f"• Размер: {comparison['size_kb']['comp']} KB"
    )

    # 8. Комментарий эксперта
    pdf.add_subtitle("👨‍💻 Комментарий от Бориса")
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, expert_comment.replace("<strong>", "").replace("</strong>", ""))
    pdf.ln(5)

    # 9. Графики
    if uptime_chart:
        pdf.add_subtitle("📈 История доступности")
        pdf.add_image_from_base64(uptime_chart)

    if load_time_chart:
        pdf.add_subtitle("⏱ История времени загрузки")
        pdf.add_image_from_base64(load_time_chart)

    # Финальное сообщение
    pdf.add_subtitle("📌 Рекомендации")
    pdf.add_paragraph("• Убедитесь, что все битые ссылки исправлены.")
    pdf.add_paragraph("• Ускорьте загрузку сайта с помощью сжатия и кэширования.")
    pdf.add_paragraph("• Проверьте корректность редиректов и canonical.")

    # Сохраняем PDF
    filename = f"reports/audit_{chat_id}_{int(datetime.now().timestamp())}.pdf"
    pdf.output(filename)
    return filename


logger.info("✅ Часть 5/7: Генерация PDF-отчётов готова")
