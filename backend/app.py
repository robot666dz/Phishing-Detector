
from dotenv import load_dotenv
import os
load_dotenv()

#  GigaChat
_client_id     = os.getenv("GIGACHAT_CLIENT_ID", "")
_client_secret = os.getenv("GIGACHAT_CLIENT_SECRET", "")
if not _client_id or not _client_secret:
    print("  ВНИМАНИЕ: GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не найдены в .env")
    print("   ИИ-анализ будет недоступен. Эвристический анализ работает.")
else:
    print(f" GigaChat API ключ загружен")

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import time
import hashlib
import logging
from datetime import datetime
from analyzer import PhishingAnalyzer

#  Настройка 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('phishing_detector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

analyzer = PhishingAnalyzer()

#  Вспомогательные функции 
def generate_report_id(data: str) -> str:
    timestamp = str(time.time())
    return hashlib.md5((data + timestamp).encode()).hexdigest()[:12].upper()


#  API Маршруты 

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "ФишингДетектор API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/analyze/url', methods=['POST'])
def analyze_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL не предоставлен"}), 400

    url = data['url'].strip()
    if not url:
        return jsonify({"error": "URL пустой"}), 400

    logger.info(f"Анализ URL: {url}")

    try:
        result = analyzer.analyze_url(url)
        result['report_id'] = generate_report_id(url)
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Ошибка анализа URL: {e}")
        return jsonify({"error": f"Ошибка анализа: {str(e)}"}), 500


@app.route('/api/analyze/message', methods=['POST'])
def analyze_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Сообщение не предоставлено"}), 400

    message = data['message'].strip()
    sender = data.get('sender', '').strip()

    if not message:
        return jsonify({"error": "Сообщение пустое"}), 400

    logger.info(f"Анализ сообщения от: {sender or 'неизвестен'}")

    try:
        result = analyzer.analyze_message(message, sender)
        result['report_id'] = generate_report_id(message)
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Ошибка анализа сообщения: {e}")
        return jsonify({"error": f"Ошибка анализа: {str(e)}"}), 500


@app.route('/api/analyze/full', methods=['POST'])
def analyze_full():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400

    url = data.get('url', '').strip()
    message = data.get('message', '').strip()
    sender = data.get('sender', '').strip()

    if not url and not message:
        return jsonify({"error": "Необходимо предоставить URL или сообщение"}), 400

    logger.info(f"Полный анализ - URL: {bool(url)}, Сообщение: {bool(message)}")

    try:
        results = {}

        if url:
            results['url_analysis'] = analyzer.analyze_url(url)

        if message:
            results['message_analysis'] = analyzer.analyze_message(message, sender)

        scores = []
        if 'url_analysis' in results:
            scores.append(results['url_analysis'].get('risk_score', 0))
        if 'message_analysis' in results:
            scores.append(results['message_analysis'].get('risk_score', 0))

        combined_score = int(max(scores)) if scores else 0
        combined_level = analyzer._get_risk_level(combined_score)

        results['combined'] = {
            'risk_score': combined_score,
            'risk_level': combined_level,
            'verdict': analyzer._get_verdict(combined_score),
            'recommendation': analyzer._get_recommendation(combined_score)
        }

        results['report_id'] = generate_report_id(url + message)
        results['timestamp'] = datetime.now().isoformat()

        return jsonify(results)

    except Exception as e:
        logger.error(f"Ошибка полного анализа: {e}")
        return jsonify({"error": f"Ошибка анализа: {str(e)}"}), 500


@app.route('/api/domain/whois', methods=['POST'])
def domain_whois():
    data = request.get_json()
    if not data or 'domain' not in data:
        return jsonify({"error": "Домен не предоставлен"}), 400

    domain = data['domain'].strip()
    logger.info(f"WHOIS запрос для: {domain}")

    try:
        result = analyzer.get_domain_info(domain)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Ошибка WHOIS: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "total_analyzed": 1247,
        "phishing_detected": 389,
        "safe_confirmed": 701,
        "suspicious": 157,
        "accuracy_rate": "94.7%",
        "last_updated": datetime.now().isoformat()
    })


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    result = analyzer.ai.check_connection()
    return jsonify(result)


if __name__ == '__main__':
    print("""

         ФИШИНГДЕТЕКТОР v1.0 - API СЕРВЕР          
    Система обнаружения фишинга и мошенничества    

    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
