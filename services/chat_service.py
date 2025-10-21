import os
import requests
from exceptions.custom_exceptions import (
    BadRequestException,
    UnauthorizedException,
    RateLimitException
)

class ChatService:
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    @staticmethod
    def ask(message, api_key=None, model=None, hf_token=None, hf_model=None, **kwargs):
        if not message or not str(message).strip():
            raise BadRequestException("O campo 'message' é obrigatório e não pode estar vazio.")

        groq_key = api_key or os.environ.get('GROQ_API_KEY')
        if not groq_key:
            raise BadRequestException("GROQ_API_KEY não configurada")

        response = requests.post(
            ChatService.GROQ_API_URL,
            json={
                "model": model or "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 401:
            raise UnauthorizedException("Groq API key inválida")
        if response.status_code == 429:
            raise RateLimitException("Rate limit do Groq atingido")
        if response.status_code != 200:
            raise Exception(f"Groq error: {response.status_code}")

        return response.json()['choices'][0]['message']['content']