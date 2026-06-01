`import whois
import dns.resolver
from datetime import datetime
from urllib.parse import urlparse

def analyze_infrastructure(url: str) -> dict:
    # Извлекаем чистый домен из URL
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
            age = (datetime.now() - creation_date).days
            result["age_days"] = age
            # Если домену меньше 6 месяцев (180 дней), это подозрительно
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