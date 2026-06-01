"""
ai_client.py — GigaChat (Sber)
"""
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AIClient:
    AUTH_URL      = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    API_URL       = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    DEFAULT_MODEL = "GigaChat"

    def __init__(self):
        self.client_secret = os.getenv("GIGACHAT_CLIENT_SECRET", "")
        self.model         = os.getenv("GIGACHAT_MODEL", self.DEFAULT_MODEL)

        if not self.client_secret:
            print(" GIGACHAT_CLIENT_SECRET не указан в .env")
        else:
            print(f" ИИ-провайдер: GigaChat ({self.model})")

    def _get_token(self) -> str:
        headers = {
            "Authorization": f"Basic {self.client_secret}",
            "Content-Type":  "application/x-www-form-urlencoded",
            "RqUID":         str(uuid.uuid4()),
        }
        data = {"scope": "GIGACHAT_API_PERS"}

        resp = requests.post(
            self.AUTH_URL,
            headers=headers,
            data=data,
            timeout=15,
            verify=False
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def ask(self, prompt: str, max_tokens: int = 400) -> str:
        if not self.client_secret:
            return self._fallback("GIGACHAT_CLIENT_SECRET не настроен")
        try:
            return self._ask_gigachat(prompt, max_tokens)
        except Exception as e:
            return self._fallback(str(e))

    def _ask_gigachat(self, prompt: str, max_tokens: int) -> str:
        token = self._get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты эксперт по кибербезопасности в России. "
                        "Отвечай только на русском языке. "
                        "Будь конкретным и кратким."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        }
        resp = requests.post(
            self.API_URL,
            headers=headers,
            json=body,
            timeout=15,
            verify=False
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def _fallback(self, reason: str = "") -> str:
        print(f" ИИ недоступен: {reason}")
        return (
            "ИИ-анализ временно недоступен. "
            "Результаты основаны на эвристическом анализе системы. "
            "Проверьте GIGACHAT_CLIENT_SECRET в файле .env"
        )

    def check_connection(self) -> dict:
        try:
            result = self.ask("Напиши одно слово: работает", max_tokens=10)
            return {"status": "ok", "provider": "gigachat", "response": result[:50]}
        except Exception as e:
            return {"status": "error", "provider": "gigachat", "error": str(e)}