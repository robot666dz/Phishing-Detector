
# 🛡 ФишингДетектор — Система обнаружения фишинга

**Курсовая работа**
**Тема:** Применение искусственного интеллекта для обнаружения фишинговых атак
**Студент:** Саадаллах М.З.
**Группа:** Б9124.10.03.01 (Направление: 10.03.01 Информационная безопасность)
Версия: 1.0 | Язык: Русский | Платформа: Web
---

## 📋 Описание проекта

**ФишингДетектор** — интеллектуальная система обнаружения фишинговых атак, ориентированная на российский интернет-сегмент. Система сочетает эвристический анализ с искусственным интеллектом (GigaChat от Сбера) для выявления мошеннических ссылок и сообщений.

### Функциональность:
- 🔗 **Анализ URL** — проверка ссылок на признаки фишинга
- 📨 **Анализ сообщений** — сканирование текста писем, SMS, сообщений мессенджеров
- 🌐 **WHOIS-верификация** — проверка возраста и регистратора домена
- 🎭 **Детектор спуфинга** — алгоритм Левенштейна для поиска доменов-двойников
- 🤖 **ИИ-анализ** — интеграция с GigaChat API для глубокого анализа угроз с учетом российской специфики
- 📊 **Взвешенная оценка риска** — балльная система от 0 до 100
- 🇷🇺 **База РФ** — верифицированные домены банков, госорганов, компаний

---

## 🏗 Архитектура


```

phishing-detector/
├── frontend/              # Статический веб-интерфейс
│   ├── index.html         # Главная страница
│   ├── style.css          # Стили (тёмная тема, адаптивная)
│   └── app.js             # JavaScript логика + демо-режим
│
├── backend/               # Python Flask API
│   ├── app.py             # Flask приложение, маршруты API
│   ├── analyzer.py        # Ядро анализа фишинга
│   └── requirements.txt   # Python зависимости
│
└── docs/
└── README.md          # Документация

```

---

## 🚀 Запуск проекта

### Вариант 1: Только Frontend (демо-режим, без бэкенда)

Просто откройте файл `frontend/index.html` в браузере. 
Система автоматически работает в демо-режиме с реалистичными результатами.

```bash
# Или через простой HTTP-сервер
cd frontend
python3 -m http.server 8080
# Откройте: http://localhost:8080

```

---

### Вариант 2: Полный запуск с бэкендом

#### Шаг 1: Настройка окружения Python

```bash
cd backend
python3 -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

```

#### Шаг 2: Установка зависимостей

```bash
pip install -r requirements.txt

```

#### Шаг 3: Настройка переменных окружения

Создайте файл `backend/.env`:

```
GIGACHAT_CLIENT_ID=your_gigachat_client_id_here
GIGACHAT_CLIENT_SECRET=your_gigachat_client_secret_here
GIGACHAT_MODEL=GigaChat

```

Получить API ключи: https://developers.sber.ru/studio

#### Шаг 4: Запуск бэкенда

```bash
python app.py
# Сервер запустится на: http://localhost:5000

```

#### Шаг 5: Настройка frontend

В файле `frontend/app.js` измените строку:

```javascript
// Было:
DEMO_MODE: true

// Стало:
DEMO_MODE: false

```

#### Шаг 6: Запуск frontend

```bash
cd frontend
python3 -m http.server 8080

```

Откройте: **http://localhost:8080**

---

## 🌐 Деплой на хостинг

### Frontend (статический хостинг)

**Вариант A: GitHub Pages** (бесплатно)

```bash
# Создайте репозиторий на GitHub
git init
git add frontend/
git commit -m "Initial commit"
git push origin main
# Включите GitHub Pages в настройках репозитория

```

**Вариант B: Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.ru;
    root /var/www/phishing-detector/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass [http://127.0.0.1:5000/api/](http://127.0.0.1:5000/api/);
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

```

### Backend (Python Flask)

**На сервере Linux:**

```bash
# Установка зависимостей
pip install gunicorn

# Запуск через Gunicorn (продакшн)
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Или через systemd service
sudo nano /etc/systemd/system/phishing-detector.service

```

**phishing-detector.service:**

```ini
[Unit]
Description=ФишингДетектор API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/phishing-detector/backend
Environment="GIGACHAT_CLIENT_ID=your_gigachat_client_id_here"
Environment="GIGACHAT_CLIENT_SECRET=your_gigachat_client_secret_here"
Environment="GIGACHAT_MODEL=GigaChat"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target

```

```bash
sudo systemctl enable phishing-detector
sudo systemctl start phishing-detector

```

---

## 🔌 API Документация

### Базовый URL: `http://localhost:5000/api`

| Метод | Endpoint | Описание |
| --- | --- | --- |
| GET | `/health` | Проверка состояния сервера |
| POST | `/analyze/url` | Анализ URL |
| POST | `/analyze/message` | Анализ сообщения |
| POST | `/analyze/full` | Полный анализ |
| POST | `/domain/whois` | WHOIS информация |
| GET | `/stats` | Статистика системы |

### Примеры запросов:

**Анализ URL:**

```bash
curl -X POST http://localhost:5000/api/analyze/url \
  -H "Content-Type: application/json" \
  -d '{"url": "[https://gosuslugi-login.online/verify](https://gosuslugi-login.online/verify)"}'

```

**Анализ сообщения:**

```bash
curl -X POST http://localhost:5000/api/analyze/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ваш аккаунт заблокирован! Срочно перейдите...",
    "sender": "Сбербанк"
  }'

```

---

## 🔬 Алгоритм анализа

### Оценка риска URL (0–100 баллов):

| Признак | Вес |
| --- | --- |
| HTTP вместо HTTPS | +15 |
| Подозрительный TLD (.tk, .xyz, .ml...) | +20 |
| URL-шортенер | +25 |
| IP-адрес вместо домена | +35 |
| Спуфинг легитимного домена | +35-60 |
| Домен < 30 дней | +30 |
| Домен 30–180 дней | +15 |
| Верифицированный домен РФ | -30 |

### Оценка риска сообщений:

| Признак | Вес |
| --- | --- |
| Фишинговые ключевые слова | до +35 |
| Искусственная срочность | +20 |
| Запрос конфиденциальных данных | +35 |
| Несоответствие отправитель/домен | +40 |
| Нереалистичные предложения | +20 |

### Уровни риска:

| Баллы | Уровень |
| --- | --- |
| 0–14 | ✅ БЕЗОПАСНЫЙ |
| 15–29 | 🔍 НИЗКИЙ |
| 30–49 | ⚠️ СРЕДНИЙ |
| 50–69 | ⛔ ВЫСОКИЙ |
| 70–100 | 🚨 КРИТИЧЕСКИЙ |

---

## 🛠 Технологии

**Frontend:**

* HTML5, CSS3, Vanilla JavaScript
* Шрифты: Geologica, JetBrains Mono (Google Fonts)
* Адаптивный дизайн (mobile-first)

**Backend:**

* Python 3.10+
* Flask 3.0 + Flask-CORS
* python-whois (WHOIS API)
* GigaChat (Sber) AI API
* Gunicorn (production WSGI)

---

## 📚 Используемые источники

1. ГОСТ Р ИСО/МЭК 27001-2021 — Системы управления ИБ
2. Банк России — Методика выявления фишинговых ресурсов
3. Роскомнадзор — Реестр нарушителей
4. НКЦКИ (Национальный координационный центр по компьютерным инцидентам)
5. Levenshtein, V.I. (1966) — Binary codes capable of correcting deletions
6. PhishTank — Open Community Anti-Phishing Service

---

## ⚖️ Disclaimer

Данная система разработана исключительно в образовательных целях как курсовая работа по информационной безопасности. Не предназначена для использования в коммерческих или правоохранительных целях без соответствующей сертификации.

---

*ФишингДетектор v1.0 · Курсовая работа · Саадаллах М.З. · 2026*
