# bot_part_3.py - Часть 3/7
# Проверка метатегов, robots.txt, sitemap.xml, битых ссылок

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

# === Проверка метатегов (SEO) ===
def check_meta(url: str):
    """
    Извлекает и анализирует ключевые метатеги.
    Возвращает словарь с результатами.
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "WebsiteAuditBot/1.0"}
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Основные метатеги
        title_tag = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = soup.find_all('h1')
        og_tags = {
            'og:title': bool(soup.find('meta', property='og:title')),
            'og:description': bool(soup.find('meta', property='og:description')),
            'og:image': bool(soup.find('meta', property='og:image')),
            'og:url': bool(soup.find('meta', property='og:url'))
        }

        return {
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "meta_description": meta_description['content'] if meta_description else None,
            "h1": [tag.get_text(strip=True) for tag in h1_tags],
            "og_tags": og_tags,
            "error": None
        }
    except Exception as e:
        return {
            "title": None,
            "meta_description": None,
            "h1": [],
            "og_tags": {},
            "error": str(e)
        }


# === Проверка robots.txt и sitemap.xml ===
def check_robots_and_sitemap(url: str):
    """
    Проверяет наличие robots.txt и sitemap.xml.
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    results = {}

    # Проверка robots.txt
    try:
        robots_url = f"{base_url}/robots.txt"
        robots_response = requests.get(robots_url, timeout=10)
        results["robots_exists"] = robots_response.status_code == 200
        results["robots_content"] = robots_response.text[:500]  # первые 500 символов
    except Exception as e:
        results["robots_exists"] = False
        results["robots_error"] = str(e)

    # Проверка sitemap.xml
    try:
        sitemap_url = f"{base_url}/sitemap.xml"
        sitemap_response = requests.get(sitemap_url, timeout=10)
        results["sitemap_exists"] = sitemap_response.status_code == 200
        results["sitemap_size"] = len(sitemap_response.content)
    except Exception as e:
        results["sitemap_exists"] = False
        results["sitemap_error"] = str(e)

    return results


# === Поиск битых ссылок (упрощённо) ===
def find_broken_links(url: str, max_links: int = 50):
    """
    Находит битые ссылки на странице.
    Внимание: это упрощённая версия — не проверяет все страницы сайта.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        links = []
        for a_tag in soup.find_all('a', href=True)[:max_links]:  # ограничение для скорости
            link = a_tag['href']
            full_url = urljoin(url, link)

            # Пропускаем внешние ссылки и якоря
            if full_url.startswith(('http://', 'https://')) and urlparse(full_url).netloc != urlparse(url).netloc:
                continue
            if full_url.startswith('#'):
                continue

            try:
                link_response = requests.head(full_url, timeout=10, allow_redirects=True)
                is_ok = link_response.status_code < 400
            except:
                is_ok = False

            links.append({
                "url": full_url,
                "status": "✅ OK" if is_ok else "❌ 404",
                "code": link_response.status_code if 'link_response' in locals() else "N/A"
            })

        broken_count = sum(1 for link in links if "404" in link["status"])
        return {
            "total": len(links),
            "broken": broken_count,
            "links": links,
            "error": None
        }
    except Exception as e:
        return {
            "total": 0,
            "broken": 0,
            "links": [],
            "error": str(e)
        }


logger.info("✅ Часть 3/7: Функции проверки SEO, метатегов и битых ссылок загружены")
