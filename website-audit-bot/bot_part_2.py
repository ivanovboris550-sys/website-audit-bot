# bot_part_2.py - Часть 2/7
# Проверка доступности сайта, SSL, заголовков, производительности

import requests
import ssl
import socket
import time
from urllib.parse import urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# === Проверка доступности сайта (HTTP) ===
def check_website(url: str, timeout: int = 10):
    """
    Проверяет, отвечает ли сайт по HTTP.
    Возвращает словарь с результатами.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        start_time = time.time()
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "WebsiteAuditBot/1.0"}
        )
        load_time = round(time.time() - start_time, 2)
        status_code = response.status_code
        status = "✅ Работает" if status_code == 200 else f"❌ Ошибка {status_code}"
        size_kb = round(len(response.content) / 1024, 2)
        charset_ok = "utf-8" in response.headers.get("Content-Type", "").lower()

        return {
            "url": url,
            "is_ok": status_code == 200,
            "status": status,
            "status_code": status_code,
            "load_time": f"{load_time} сек",
            "size_kb": size_kb,
            "headers": dict(response.headers),
            "charset_ok": charset_ok,
            "error": None
        }
    except requests.exceptions.Timeout:
        return {
            "url": url,
            "is_ok": False,
            "status": "🔴 Таймаут",
            "error": "Превышено время ожидания",
            "load_time": "N/A",
            "size_kb": "N/A"
        }
    except requests.exceptions.ConnectionError:
        return {
            "url": url,
            "is_ok": False,
            "status": "🔴 Нет подключения",
            "error": "Не удалось подключиться к серверу",
            "load_time": "N/A",
            "size_kb": "N/A"
        }
    except Exception as e:
        return {
            "url": url,
            "is_ok": False,
            "status": "🔴 Ошибка",
            "error": str(e),
            "load_time": "N/A",
            "size_kb": "N/A"
        }


# === Проверка SSL-сертификата ===
def check_ssl(url: str):
    """
    Проверяет валидность SSL-сертификата.
    Возвращает словарь с данными или ошибкой.
    """
    parsed = urlparse(url)
    hostname = parsed.netloc.split(":")[0] if ":" in parsed.netloc else parsed.netloc

    if not hostname:
        return {"valid": False, "error": "Неверный URL"}

    port = 443
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert['subject'])
                issuer = dict(x[0] for x in cert['issuer'])
                expires = cert['notAfter']

                # Проверим, действителен ли сертификат сейчас
                expires_dt = datetime.strptime(expires, "%b %d %H:%M:%S %Y %Z")
                now = datetime.utcnow()
                valid_now = now < expires_dt

                return {
                    "valid": valid_now,
                    "hostname": hostname,
                    "issued_to": subject.get('commonName', 'N/A'),
                    "issued_by": issuer.get('commonName', 'N/A'),
                    "expires": expires,
                    "expired": not valid_now,
                    "error": None
                }
    except ssl.SSLError as e:
        return {"valid": False, "error": f"SSL ошибка: {str(e)}"}
    except socket.gaierror:
        return {"valid": False, "error": "Не удалось разрешить DNS"}
    except Exception as e:
        return {"valid": False, "error": f"Ошибка подключения: {str(e)}"}


# === Проверка мобильной версии (упрощённо) ===
def check_mobile(url: str):
    """
    Проверяет сайт с User-Agent мобильного устройства.
    """
    mobile_headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
    }

    try:
        start_time = time.time()
        response = requests.get(url, headers=mobile_headers, timeout=10)
        load_time = round(time.time() - start_time, 2)
        size_kb = round(len(response.content) / 1024, 2)

        return {
            "is_ok": response.status_code == 200,
            "load_time": f"{load_time} сек",
            "size_kb": size_kb,
            "status_code": response.status_code,
            "error": None
        }
    except Exception as e:
        return {
            "is_ok": False,
            "load_time": "N/A",
            "size_kb": "N/A",
            "status_code": "N/A",
            "error": str(e)
        }


# === Проверка PageSpeed (отключена — требует внешнего API) ===
def get_pagespeed_result(url: str):
    """
    Заглушка для PageSpeed. Можно использовать внешний API, но это платно.
    Сейчас возвращается заглушка.
    """
    return {
        "score": "N/A",
        "fcp": "N/A",
        "lcp": "N/A",
        "cls": "N/A",
        "error": "PageSpeed не поддерживается на этом хостинге"
    }


logger.info("✅ Часть 2/7: Функции проверки сайта, SSL и мобильной версии загружены")
