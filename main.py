from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Импортируем наши модули
from modules.infrastructure import analyze_infrastructure
from modules.typosquatting import check_typosquatting
from modules.content_analyzer import analyze_content
from modules.ai_analyst import get_ai_verdict

app = FastAPI(
    title="AI Phishing Detector API", 
    description="Комплексная система интеллектуального обнаружения фишинга"
)

class URLRequest(BaseModel):
    url: str

@app.post("/api/v1/analyze")
async def analyze_target_url(request: URLRequest):
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL не может быть пустым")
        
    # Шаг 1: Инфраструктурный анализ (WHOIS / DNS)
    infra_results = analyze_infrastructure(url)
    
    # Шаг 2: Анализ на подмену известных брендов
    typo_results = check_typosquatting(url)
    
    # Шаг 3: Контентный анализ (Скрейпинг текста и поиск триггеров)
    content_results = analyze_content(url)
    
    # Шаг 4: Интеграция данных и ИИ-аналитика
    ai_verdict = get_ai_verdict(infra_results, typo_results, content_results)
    
    # Собираем финальный структурированный ответ для фронтенда
    final_report = {
        "target_url": url,
        "infrastructure": infra_results,
        "typosquatting": typo_results,
        "content_analysis": content_results,
        "ai_verdict": ai_verdict
    }
    
    return final_report

if name == "main":
    # Запуск сервера на порту 8000
    uvicorn.run("main.py:app", host="127.0.0.1", port=8000, reload=True)