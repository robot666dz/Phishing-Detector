

import re
import json
import math
import socket
import urllib.parse
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import whois as whois_lib
from ai_client import AIClient


class PhishingAnalyzer:
    """Основной класс анализа фишинга"""

    # Легитимные домены российских компаний
    LEGITIMATE_RUSSIAN_DOMAINS = {
        'sberbank.ru': 'Сбербанк',
        'sber.ru': 'Сбербанк',
        'vtb.ru': 'ВТБ Банк',
        'alfabank.ru': 'Альфа-Банк',
        'tinkoff.ru': 'Тинькофф Банк',
        'raiffeisen.ru': 'Райффайзен Банк',
        'gosuslugi.ru': 'Госуслуги',
        'mos.ru': 'Mos.ru',
        'nalog.ru': 'ФНС России',
        'pfr.gov.ru': 'СФР (ПФР)',
        'cbr.ru': 'Центральный Банк',
        'mail.ru': 'Mail.ru',
        'yandex.ru': 'Яндекс',
        'vk.com': 'ВКонтакте',
        'ozon.ru': 'Ozon',
        'wildberries.ru': 'Wildberries',
        'avito.ru': 'Авито',
        'mvd.ru': 'МВД России',
        'fsb.ru': 'ФСБ России',
        'kremlin.ru': 'Кремль',
        'government.ru': 'Правительство РФ',
        'mts.ru': 'МТС',
        'beeline.ru': 'Билайн',
        'megafon.ru': 'МегаФон',
        'tele2.ru': 'Tele2',
        'rosseti.ru': 'Россети',
        'gazprom.ru': 'Газпром',
        'rosneft.ru': 'Роснефть',
        'lukoil.ru': 'ЛУКОЙЛ',
        'sberinsurance.ru': 'СберСтрахование',
        'rgs.ru': 'Росгосстрах',
        'ingos.ru': 'Ингосстрах',
    }

    #  Фишинговые паттерны 
    PHISHING_KEYWORDS_RU = [
        'срочно', 'немедленно', 'заблокирован', 'подтвердите', 'верификация',
        'истекает', 'выиграли', 'бесплатно', 'ограниченное время', 'действуйте сейчас',
        'ваш аккаунт', 'подозрительная активность', 'безопасность нарушена',
        'обновите данные', 'подтвердите личность', 'введите пароль', 'секретный код',
        'выплата', 'компенсация', 'возврат средств', 'налоговый вычет',
        'лотерея', 'приз', 'бонус', 'акция', 'скидка 90%',
        'ваши данные украдены', 'вирус обнаружен', 'техподдержка',
    ]

    PHISHING_KEYWORDS_EN = [
        'urgent', 'verify', 'suspended', 'account', 'confirm', 'password',
        'click here', 'limited time', 'act now', 'winner', 'prize',
        'free gift', 'security alert', 'unusual activity', 'update required',
    ]

    #  Подозрительные TLD 
    SUSPICIOUS_TLDS = [
        '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw',
        '.cc', '.click', '.download', '.link', '.site', '.online',
        '.top', '.club', '.stream', '.gdn', '.racing', '.win',
        '.bid', '.loan', '.trade', '.science', '.date', '.faith',
    ]

    #  URL-шортенеры 
    URL_SHORTENERS = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly',
        'short.ly', 'rb.gy', 'cutt.ly', 'u.to', 'is.gd',
        'v.gd', 'clck.ru', 'c.pxl.to',
    ]

    def __init__(self):
        self.ai = AIClient()  # читает .env

    
    # АНАЛИЗ URL


    def analyze_url(self, url: str) -> Dict:
        """Полный анализ URL"""
        findings = []
        risk_score = 0

        # Нормализация URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '').strip()
            if not domain:
                parsed = urllib.parse.urlparse('http://' + url)
                domain = parsed.netloc.lower().replace('www.', '').strip()
            base_domain = self._get_base_domain(domain) if domain else url.strip()
        except Exception:
            return {
                "error": "Невалидный URL",
                "risk_score": 100,
                "risk_level": "ВЫСОКИЙ",
                "verdict": "Ошибка анализа — проверьте формат URL",
                "recommendation": "Введите корректный URL, например: https://example.ru",
                "findings": [], "checks": {}, "whois": {}, "ai_analysis": {}
            }

        checks = {}

        # 1. Проверка HTTP vs HTTPS
        if parsed.scheme == 'http':
            risk_score += 15
            findings.append({
                "type": "warning",
                "category": "Протокол",
                "message": "Сайт использует незащищённый протокол HTTP (без шифрования)",
                "weight": 15
            })
            checks['ssl'] = {"status": "fail", "message": "Нет SSL/TLS шифрования"}
        else:
            checks['ssl'] = {"status": "pass", "message": "HTTPS шифрование активно"}

        # 2. Проверка на подозрительный TLD
        for tld in self.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                risk_score += 20
                findings.append({
                    "type": "danger",
                    "category": "Домен",
                    "message": f"Подозрительный домен верхнего уровня: {tld}",
                    "weight": 20
                })
                checks['tld'] = {"status": "fail", "message": f"Высокорисковый TLD: {tld}"}
                break
        else:
            checks['tld'] = {"status": "pass", "message": "Нормальный TLD"}

        # 3. Проверка URL-шортенеров
        for shortener in self.URL_SHORTENERS:
            if shortener in domain:
                risk_score += 25
                findings.append({
                    "type": "danger",
                    "category": "Сокращение URL",
                    "message": f"Используется сервис сокращения URL ({shortener}) — скрывает реальный адрес",
                    "weight": 25
                })
                checks['shortener'] = {"status": "fail", "message": "URL скрыт через шортенер"}
                break
        else:
            checks['shortener'] = {"status": "pass", "message": "Прямая ссылка"}

        # 4. IP-адрес вместо домена
        ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_pattern.match(domain):
            risk_score += 35
            findings.append({
                "type": "danger",
                "category": "IP-адрес",
                "message": "URL содержит IP-адрес вместо доменного имени — признак фишинга",
                "weight": 35
            })
            checks['ip_url'] = {"status": "fail", "message": "IP-адрес вместо домена"}
        else:
            checks['ip_url'] = {"status": "pass", "message": "Доменное имя используется"}

        # 5. Слишком длинный URL
        if len(url) > 100:
            risk_score += 10
            findings.append({
                "type": "warning",
                "category": "Длина URL",
                "message": f"Необычно длинный URL ({len(url)} символов)",
                "weight": 10
            })

        # 6. Спуфинг легитимных доменов
        spoof_result = self._check_domain_spoofing(domain, base_domain)
        if spoof_result:
            risk_score += spoof_result['weight']
            findings.append(spoof_result['finding'])
            checks['spoofing'] = {
                "status": "fail",
                "message": spoof_result['finding']['message']
            }
        else:
            checks['spoofing'] = {"status": "pass", "message": "Споофинг не обнаружен"}

        # 7. Числа вместо букв (sber-bank1.ru)
        if re.search(r'\d', base_domain.split('.')[0]):
            risk_score += 10
            findings.append({
                "type": "warning",
                "category": "Имя домена",
                "message": "Домен содержит цифры — часто встречается при подделке брендов",
                "weight": 10
            })

        # 8. Слишком много дефисов
        subdomain = parsed.netloc.lower()
        if subdomain.count('-') >= 3:
            risk_score += 15
            findings.append({
                "type": "warning",
                "category": "Структура домена",
                "message": f"Много дефисов в URL ({subdomain.count('-')}) — подозрительная структура",
                "weight": 15
            })

        # 9. Легитимный домен
        if base_domain in self.LEGITIMATE_RUSSIAN_DOMAINS:
            risk_score = max(0, risk_score - 30)
            company = self.LEGITIMATE_RUSSIAN_DOMAINS[base_domain]
            findings.append({
                "type": "success",
                "category": "Репутация",
                "message": f"Домен принадлежит известной организации: {company}",
                "weight": -30
            })
            checks['reputation'] = {"status": "pass", "message": f"Верифицированный домен ({company})"}
        else:
            checks['reputation'] = {"status": "unknown", "message": "Домен не в базе верифицированных"}

        # 10. WHOIS информация
        whois_data = self._get_whois_safe(base_domain)
        checks['whois'] = whois_data

        _age = whois_data.get('domain_age_days')
        _age = int(_age) if _age is not None else None

        if _age is not None and _age < 30:
            risk_score += 30
            findings.append({
                "type": "danger",
                "category": "Возраст домена",
                "message": f"Домен создан менее 30 дней назад ({_age} дн.) — высокий риск",
                "weight": 30
            })
        elif _age is not None and _age < 180:
            risk_score += 15
            findings.append({
                "type": "warning",
                "category": "Возраст домена",
                "message": f"Домен относительно новый ({_age} дн.)",
                "weight": 15
            })
        elif _age is None:
            findings.append({
                "type": "info",
                "category": "Возраст домена",
                "message": "Не удалось определить возраст домена (WHOIS недоступен)",
                "weight": 0
            })

        # ИИ-анализ
        ai_analysis = self._ai_analyze_url(url, domain, findings)

        risk_score = min(100, max(0, risk_score))

        return {
            "url": url,
            "domain": domain,
            "base_domain": base_domain,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "verdict": self._get_verdict(risk_score),
            "recommendation": self._get_recommendation(risk_score),
            "findings": findings,
            "checks": checks,
            "whois": whois_data,
            "ai_analysis": ai_analysis,
            "analyzed_at": datetime.now().isoformat()
        }

    
    # АНАЛИЗ СООБЩЕНИЙ
    

    def analyze_message(self, message: str, sender: str = '') -> Dict:
        """Анализ текстового сообщения"""
        findings = []
        risk_score = 0

        # 1. Поиск фишинговых ключевых слов
        found_keywords_ru = []
        for kw in self.PHISHING_KEYWORDS_RU:
            if kw.lower() in message.lower():
                found_keywords_ru.append(kw)

        found_keywords_en = []
        for kw in self.PHISHING_KEYWORDS_EN:
            if kw.lower() in message.lower():
                found_keywords_en.append(kw)

        if found_keywords_ru:
            kw_score = min(35, len(found_keywords_ru) * 8)
            risk_score += kw_score
            findings.append({
                "type": "danger" if len(found_keywords_ru) > 2 else "warning",
                "category": "Ключевые слова",
                "message": f"Обнаружены фишинговые слова: {', '.join(found_keywords_ru[:5])}",
                "weight": kw_score
            })

        if found_keywords_en:
            risk_score += 10
            findings.append({
                "type": "warning",
                "category": "Иностранный язык",
                "message": f"Английские фишинговые слова в русском сообщении: {', '.join(found_keywords_en[:3])}",
                "weight": 10
            })

        # 2. Извлечение и анализ URL из сообщения
        urls_in_message = self._extract_urls(message)
        url_findings = []

        for url in urls_in_message:
            parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
            url_domain = parsed.netloc.lower().replace('www.', '')
            base = self._get_base_domain(url_domain)

            # Проверка соответствия отправителя и домена
            if sender:
                mismatch = self._check_sender_url_mismatch(sender, url_domain)
                if mismatch:
                    risk_score += 40
                    findings.append({
                        "type": "danger",
                        "category": "Несоответствие отправителя",
                        "message": mismatch,
                        "weight": 40
                    })
                    url_findings.append({
                        "url": url,
                        "issue": "Домен не соответствует отправителю"
                    })

            # Быстрая проверка URL
            quick_url_risk = self._quick_url_check(url, base)
            if quick_url_risk > 0:
                risk_score += quick_url_risk
                url_findings.append({
                    "url": url,
                    "risk": quick_url_risk,
                    "issue": "Подозрительный URL"
                })

        if urls_in_message:
            findings.append({
                "type": "info",
                "category": "Ссылки в сообщении",
                "message": f"Найдено {len(urls_in_message)} ссылок: {', '.join(urls_in_message[:3])}",
                "urls": url_findings,
                "weight": 0
            })

        # 3. Срочность и давление
        urgency_patterns = [
            r'(\d+)\s*час[а-я]*\s*(осталось|до конца|для подтверждения)',
            r'сегодня.*последний день',
            r'немедленн[а-я]+\s+перейдите',
            r'срочно.{0,20}(нажмите|перейдите|позвоните)',
        ]
        for pattern in urgency_patterns:
            if re.search(pattern, message.lower()):
                risk_score += 20
                findings.append({
                    "type": "danger",
                    "category": "Давление и срочность",
                    "message": "Создаётся искусственная срочность — типичная фишинговая тактика",
                    "weight": 20
                })
                break

        # 4. Запросы личных данных
        data_request_patterns = [
            r'(введите|укажите|сообщите).{0,30}(пароль|код|pin|cvv|номер карты)',
            r'(пришлите|отправьте).{0,20}(паспорт|снилс|инн|данные)',
            r'код.{0,10}(подтверждения|верификации|смс)',
        ]
        for pattern in data_request_patterns:
            if re.search(pattern, message.lower()):
                risk_score += 35
                findings.append({
                    "type": "danger",
                    "category": "Запрос данных",
                    "message": "Сообщение запрашивает конфиденциальные данные (пароли, коды, данные карты)",
                    "weight": 35
                })
                break

        # 5. Орфографические ошибки
        spelling_score = self._check_spelling_errors(message)
        if spelling_score > 0:
            risk_score += spelling_score
            findings.append({
                "type": "warning",
                "category": "Орфография",
                "message": "Обнаружены характерные для фишинга орфографические паттерны",
                "weight": spelling_score
            })

        # 6. Слишком хорошее предложение
        offer_patterns = [
            r'выигра[а-я]+\s+\d+',
            r'\d+\s*(тысяч|миллион|рублей)\s+(бесплатно|в подарок)',
            r'получите\s+\d+%\s+скидк',
        ]
        for pattern in offer_patterns:
            if re.search(pattern, message.lower()):
                risk_score += 20
                findings.append({
                    "type": "warning",
                    "category": "Слишком выгодное предложение",
                    "message": "Нереалистично выгодное предложение — классический признак мошенничества",
                    "weight": 20
                })
                break

        # ИИ-анализ сообщения
        ai_analysis = self._ai_analyze_message(message, sender, findings)

        risk_score = min(100, max(0, risk_score))

        return {
            "message_preview": message[:200] + ('...' if len(message) > 200 else ''),
            "sender": sender,
            "urls_found": urls_in_message,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "verdict": self._get_verdict(risk_score),
            "recommendation": self._get_recommendation(risk_score),
            "findings": findings,
            "keywords_found": {
                "russian": found_keywords_ru,
                "english": found_keywords_en
            },
            "ai_analysis": ai_analysis,
            "analyzed_at": datetime.now().isoformat()
        }

    
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    

    def _get_base_domain(self, domain: str) -> str:
        """Извлечение базового домена"""
        if not domain:
            return ''
        domain = domain.split(':')[0].strip()
        parts = domain.split('.')
        if len(parts) >= 2:
            if parts[-1] in ['ru', 'uk', 'au', 'nz'] and parts[-2] in ['co', 'com', 'org', 'net', 'gov']:
                return '.'.join(parts[-3:]) if len(parts) >= 3 else domain
            return '.'.join(parts[-2:])
        return domain

    def _check_domain_spoofing(self, domain: str, base_domain: str) -> Optional[Dict]:
        """Проверка на подделку легитимных доменов"""
        domain_name = base_domain.split('.')[0].lower()

        for legit_domain, company in self.LEGITIMATE_RUSSIAN_DOMAINS.items():
            legit_name = legit_domain.split('.')[0].lower()

            if base_domain == legit_domain:
                continue

            distance = self._levenshtein(domain_name, legit_name)
            if 1 <= distance <= 2:
                return {
                    "weight": 45,
                    "finding": {
                        "type": "danger",
                        "category": "Спуфинг домена",
                        "message": (f"Домен '{base_domain}' очень похож на официальный "
                                    f"'{legit_domain}' ({company}) — расстояние {distance} символа"),
                        "weight": 45
                    }
                }

            if legit_name in domain_name and base_domain != legit_domain:
                if len(domain_name) > len(legit_name) + 1:
                    return {
                        "weight": 35,
                        "finding": {
                            "type": "danger",
                            "category": "Спуфинг домена",
                            "message": (f"Домен содержит название '{company}' "
                                        f"({legit_name}) как часть другого домена"),
                            "weight": 35
                        }
                    }

            cyrillic_map = {'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'х': 'x'}
            normalized = domain_name
            for cyr, lat in cyrillic_map.items():
                normalized = normalized.replace(cyr, lat)
            if normalized != domain_name and self._levenshtein(normalized, legit_name) <= 1:
                return {
                    "weight": 60,
                    "finding": {
                        "type": "danger",
                        "category": "IDN Спуфинг",
                        "message": (f"Обнаружены кириллические символы, визуально схожие с латинскими "
                                    f"— имитация {company}"),
                        "weight": 60
                    }
                }

        return None

    def _levenshtein(self, s1: str, s2: str) -> int:
        """Расстояние Левенштейна"""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    def _extract_urls(self, text: str) -> List[str]:
        """Извлечение URLs из текста"""
        url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+|'
            r'www\.[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}[^\s]*|'
            r'[a-zA-Z0-9][a-zA-Z0-9-]*\.(ru|рф|com|org|net|io|online|site)[^\s]*',
            re.IGNORECASE
        )
        return list(set(url_pattern.findall(text)))

    def _check_sender_url_mismatch(self, sender: str, url_domain: str) -> Optional[str]:
        """Проверка несоответствия отправителя и URL"""
        sender_lower = sender.lower()

        expected_domains = {}
        for domain, company in self.LEGITIMATE_RUSSIAN_DOMAINS.items():
            company_words = company.lower().replace(' ', '').replace('-', '')
            domain_name = domain.split('.')[0]
            expected_domains[company_words] = domain
            expected_domains[domain_name] = domain

        for company_key, legit_domain in expected_domains.items():
            if company_key in sender_lower.replace(' ', '').replace('-', ''):
                url_base = self._get_base_domain(url_domain)
                if url_base != legit_domain:
                    return (f"Сообщение якобы от '{sender}', "
                            f"но ссылка ведёт на '{url_domain}' вместо ожидаемого '{legit_domain}' — "
                            f"признак фишинга!")
        return None

    def _quick_url_check(self, url: str, base_domain: str) -> int:
        """Быстрая оценка риска URL"""
        score = 0
        if not url.startswith('https://'):
            score += 10
        for tld in self.SUSPICIOUS_TLDS:
            if base_domain.endswith(tld):
                score += 20
                break
        for shortener in self.URL_SHORTENERS:
            if shortener in url:
                score += 25
                break
        return score

    def _check_spelling_errors(self, text: str) -> int:
        """Проверка на характерные орфографические паттерны"""
        score = 0

        phishing_typos = [
            r'[аa][кk][аa][уy][нn][тt]',
            r'[сc][бb][еe][рr]',
            r'[гg][оo][сc][уy][сc][лl]',
        ]
        for pattern in phishing_typos:
            if re.search(pattern, text.lower()):
                score += 25
                break

        if re.search(r'\s{3,}', text):
            score += 5

        if re.search(r'[.,!?][а-яА-Яa-zA-Z]', text):
            score += 5

        return min(score, 30)

    def _get_whois_safe(self, domain: str) -> Dict:
        """Безопасный WHOIS запрос"""
        try:
            w = whois_lib.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            age_days = None
            age_str = "Неизвестно"
            if creation_date:
                if isinstance(creation_date, str):
                    creation_date = datetime.strptime(creation_date[:10], '%Y-%m-%d')
                delta = datetime.now() - creation_date
                age_days = delta.days
                if age_days < 30:
                    age_str = f"{age_days} дней ⚠️ НОВЫЙ"
                elif age_days < 365:
                    age_str = f"{age_days} дней ({age_days // 30} мес.)"
                else:
                    age_str = f"{age_days} дней ({age_days // 365} лет)"

            registrar = w.registrar or "Неизвестен"
            country = w.country or "Неизвестна"

            return {
                "status": "success",
                "domain": domain,
                "registrar": str(registrar)[:100],
                "country": str(country),
                "creation_date": str(creation_date)[:10] if creation_date else "Неизвестно",
                "domain_age_days": int(age_days) if age_days is not None else None,
                "domain_age_str": age_str,
                "expiration_date": str(w.expiration_date)[:10] if w.expiration_date else "Неизвестно",
                "name_servers": [str(ns) for ns in (w.name_servers or [])[:3]],
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Не удалось получить WHOIS: {str(e)[:100]}",
                "domain": domain,
                "domain_age_days": None,
                "domain_age_str": "Недоступно"
            }

    def get_domain_info(self, domain: str) -> Dict:
        """Публичный метод получения информации о домене"""
        domain = domain.lower().replace('www.', '').strip()
        whois_data = self._get_whois_safe(domain)

        try:
            ip = socket.gethostbyname(domain)
            whois_data['ip_address'] = ip
        except Exception:
            whois_data['ip_address'] = "Не удалось определить"

        whois_data['is_known_legitimate'] = domain in self.LEGITIMATE_RUSSIAN_DOMAINS
        if domain in self.LEGITIMATE_RUSSIAN_DOMAINS:
            whois_data['known_as'] = self.LEGITIMATE_RUSSIAN_DOMAINS[domain]

        return whois_data

    
    # ИИ АНАЛИЗ (Sber GigaChat)
    

    def _ai_analyze_url(self, url: str, domain: str, existing_findings: List) -> Dict:
        """ИИ-анализ URL через Sber GigaChat"""
        try:
            findings_summary = '; '.join([f['message'] for f in existing_findings[:5]])

            prompt = f"""Ты эксперт по кибербезопасности в России. Проанализируй этот URL на признаки фишинга.

URL: {url}
Домен: {domain}
Уже найденные проблемы: {findings_summary or 'Не обнаружено'}

Дай краткий профессиональный анализ на русском языке (3-4 предложения):
1. Общая оценка подозрительности
2. Дополнительные признаки, которые не были упомянуты
3. Главный совет пользователю

Отвечай только по делу, без вступлений."""

            text = self.ai.ask(prompt, max_tokens=350)
            return {
                "status": "success",
                "analysis": text,
                "model": "GigaChat"
            }

        except Exception as e:
            return {
                "status": "error",
                "analysis": "ИИ-анализ через GigaChat временно недоступен. Результаты основаны на эвристическом анализе.",
                "model": "GigaChat",
                "error": str(e)[:100]
            }

    def _ai_analyze_message(self, message: str, sender: str, existing_findings: List) -> Dict:
        """ИИ-анализ сообщения через Sber GigaChat"""
        try:
            findings_summary = '; '.join([f['message'] for f in existing_findings[:5]])

            prompt = f"""Ты эксперт по информационной безопасности России. Проанализируй это сообщение на признаки социальной инженерии и фишинга.

Отправитель: {sender or 'Неизвестен'}
Сообщение: {message[:500]}
Уже найденные признаки: {findings_summary or 'Не обнаружено'}

Дай краткий анализ на русском языке:
1. Оценка: это фишинг/мошенничество или легитимное сообщение?
2. Какие психологические манипуляции используются (если есть)?
3. На что пользователю следует обратить особое внимание?
4. Конкретная рекомендация (3-4 предложения максимум)

Будь конкретным и практичным."""

            text = self.ai.ask(prompt, max_tokens=400)
            return {
                "status": "success",
                "analysis": text,
                "model": "GigaChat"
            }

        except Exception as e:
            return {
                "status": "error",
                "analysis": "ИИ-анализ через GigaChat временно недоступен. Используются стандартные эвристические правила.",
                "model": "GigaChat",
                "error": str(e)[:100]
            }

    
    # ОЦЕНКИ И ВЕРДИКТЫ
    

    def _get_risk_level(self, score: int) -> str:
        if score >= 70:
            return "КРИТИЧЕСКИЙ"
        elif score >= 50:
            return "ВЫСОКИЙ"
        elif score >= 30:
            return "СРЕДНИЙ"
        elif score >= 15:
            return "НИЗКИЙ"
        else:
            return "БЕЗОПАСНЫЙ"

    def _get_verdict(self, score: int) -> str:
        if score >= 70:
            return "ФИШИНГ — Не открывайте эту ссылку!"
        elif score >= 50:
            return "ВЕРОЯТНЫЙ ФИШИНГ — Крайне подозрительно"
        elif score >= 30:
            return "ПОДОЗРИТЕЛЬНО — Требует проверки"
        elif score >= 15:
            return "НЕБОЛЬШОЙ РИСК — Будьте осторожны"
        else:
            return "ВЕРОЯТНО БЕЗОПАСНО — Признаков фишинга не обнаружено"

    def _get_recommendation(self, score: int) -> str:
        if score >= 70:
            return ("🚫 НЕ переходите по ссылке! Не вводите никакие данные. "
                    "Сообщите об этом в Роскомнадзор или Банк России (при финансовом мошенничестве).")
        elif score >= 50:
            return ("⚠️ Настоятельно рекомендуем не переходить по ссылке. "
                    "Если это важное уведомление — проверьте через официальный сайт организации напрямую.")
        elif score >= 30:
            return ("🔍 Перепроверьте источник сообщения. Свяжитесь с организацией "
                    "через официальные каналы для подтверждения.")
        elif score >= 15:
            return ("ℹ️ Соблюдайте осторожность. Проверьте адресную строку браузера "
                    "перед вводом любых данных.")
        else:
            return ("✅ Ресурс выглядит легитимным. Тем не менее, всегда проверяйте "
                    "адресную строку и наличие HTTPS.")