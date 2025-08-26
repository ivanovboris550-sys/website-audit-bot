# bot_part_3.py - Часть 3/7
# Функции: check_meta, find_broken_links, check_robots_and_sitemap

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

def check_meta(url):
    """
    Парсит основные SEO-метатеги: title, h1, description, viewport, canonical, lang, og:tags
    """
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        if response.status_code != 200:
            return {"error": f"Статус {response.status_code}", "url": url}

        soup = BeautifulSoup(response.content, 'html.parser')
        html_tag = soup.find('html')

        # H1
        h1_tag = soup.find('h1')
        h1 = h1_tag.get_text(strip=True) if h1_tag else None

        # Title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else None

        # Meta Description
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc_tag.get("content") if meta_desc_tag else None

        # Viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        has_viewport = bool(viewport)

        # Canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        has_canonical = bool(canonical)

        # Язык (lang)
        lang = html_tag.get('lang') if html_tag else None

        # hreflang
        hreflang = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
        has_hreflang = len(hreflang) > 0

        # OG-теги
        og_tags = {
            "og:title": bool(soup.find('meta', property="og:title")),
            "og:description": bool(soup.find('meta', property="og:description")),
            "og:image": bool(soup.find('meta', property="og:image")),
            "og:url": bool(soup.find('meta', property="og:url"))
        }

        return {
            "h1": h1,
            "title": title,
            "meta_description": meta_description,
            "viewport": has_viewport,
            "canonical": has_canonical,
            "lang": lang,
            "hreflang": has_hreflang,
            "og_tags": og_tags,
            "error": None
        }

    except Exception as e:
        print(f"❌ Ошибка при парсинге мета-тегов: {e}")
        return {"error": str(e), "url": url}


def find_broken_links(url):
    """
    Находит битые внутренние ссылки (404, 500 и т.д.)
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        base_netloc = urlparse(url).netloc
        broken_links = []

        for link in links:
            full_url = urljoin(url, link['href'])

            # Проверяем только внутренние ссылки
            if urlparse(full_url).netloc == base_netloc:
                try:
                    # Используем HEAD для экономии трафика
                    head_response = requests.head(full_url, timeout=5, allow_redirects=True)
                    if head_response.status_code >= 400:
                        broken_links.append({
                            "url": full_url,
                            "status": head_response.status_code,
                            "text": link.get_text(strip=True)[:50] or "N/A"
                        })
                except requests.RequestException as e:
                    broken_links.append({
                        "url": full_url,
                        "status": "Ошибка",
                        "text": link.get_text(strip=True)[:50] or "N/A"
                    })

        return broken_links

    except Exception as e:
        print(f"❌ Ошибка при поиске битых ссылок: {e}")
        return []


def check_robots_and_sitemap(url):
    """
    Проверяет наличие robots.txt и sitemap.xml
    """
    results = {
        "robots_txt": "N/A",
        "sitemap_xml": "N/A",
        "issues": []
    }

    try:
        # Проверка robots.txt
        robots_url = url.rstrip("/") + "/robots.txt"
        robots_response = requests.get(robots_url, timeout=10)
        if robots_response.status_code == 200:
            if "Disallow" in robots_response.text or "Allow" in robots_response.text:
                results["robots_txt"] = "✅ Доступен"
            else:
                results["robots_txt"] = "⚠ Пустой"
        else:
            results["robots_txt"] = "❌ Не найден"
    except Exception as e:
        results["robots_txt"] = "❌ Ошибка"
        results["issues"].append(f"robots.txt: {str(e)}")

    try:
        # Проверка sitemap.xml
        sitemap_url = url.rstrip("/") + "/sitemap.xml"
        sitemap_response = requests.get(sitemap_url, timeout=10)
        if sitemap_response.status_code == 200 and "<urlset" in sitemap_response.text.lower():
            results["sitemap_xml"] = "✅ Доступен"
        else:
            results["sitemap_xml"] = "❌ Не найден"
    except Exception as e:
        results["sitemap_xml"] = "❌ Ошибка"
        results["issues"].append(f"sitemap.xml: {str(e)}")

    return results
