import whois
import dns.resolver
from datetime import datetime, timezone
from urllib.parse import urlparse

def analyze_infrastructure(url: str) -> dict:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
    domain = domain.replace("www.", "")

    result = {
        "domain": domain,
        "age_days": -1,
        "has_mx_record": False,
        "is_new_domain": False,
        "error": None
    }

    # 1. Проверка WHOIS (Возраст домена)
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:
            # Приводим оба datetime к одному типу (UTC без tzinfo)
            now = datetime.now(timezone.utc)
            if creation_date.tzinfo is None:
                # naive → считаем что UTC
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            age = (now - creation_date).days
            result["age_days"] = age
            if age < 180:
                result["is_new_domain"] = True
    except Exception as e:
        result["error"] = f"WHOIS error: {str(e)}"

    # 2. Проверка DNS (Наличие почтового сервера MX)
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        result["has_mx_record"] = len(mx_records) > 0
    except Exception:
        result["has_mx_record"] = False

    return result
