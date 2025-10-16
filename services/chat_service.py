import os
import requests
from exceptions.custom_exceptions import (
    BadRequestException,
    PaymentRequiredException,
    UnauthorizedException,
    RateLimitException
)
# Assumindo que ValidationService existe e funciona
from services.validation_service import ValidationService


class ChatService:
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"

    # Prompt específico para livros
    BOOK_PROMPT = (
        "Você é um bibliotecário experiente que recomenda livros em português. "
        "Sempre inclua: título, autor, número aproximado de páginas e justificativa da recomendação."
    )

    # Prompt genérico (pode ser None ou um prompt simples)
    GENERAL_PROMPT = "Você é um assistente prestativo e experiente. Responda a todas as perguntas de forma concisa e útil."

    @staticmethod
    def _get_system_prompt(message: str) -> str:
        """Determina qual prompt de sistema usar com base na mensagem."""
        keywords = ["livro", "livros", "leitura", "conteúdo", "recomendações literárias"]

        # Converte a mensagem para minúsculas para a verificação
        message_lower = message.lower()

        # Verifica se alguma palavra-chave está na mensagem
        if any(keyword in message_lower for keyword in keywords):
            return ChatService.BOOK_PROMPT

        # Retorna o prompt genérico se nenhuma palavra-chave for encontrada
        return ChatService.GENERAL_PROMPT

    @staticmethod
    def ask(message, api_key=None, hf_token=None, use_mock=False, model=None, hf_model=None):
        ValidationService.validate_chat_message(message)

        # 1. Obter o prompt de sistema correto
        system_prompt = ChatService._get_system_prompt(message)

        if use_mock or (model and model.lower() == 'mock'):
            return ChatService._mock_response(message)

        # Ordem de prioridade: Groq (grátis) -> OpenAI (pago) -> HuggingFace (lento)
        groq_key = os.environ.get('GROQ_API_KEY')
        if groq_key:
            try:
                # Passa o system_prompt para a função de chamada
                return ChatService._call_groq(message, groq_key, system_prompt)
            except Exception as e:
                print(f"[WARN] Groq failed: {str(e)}")

        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if api_key:
            try:
                # Passa o system_prompt para a função de chamada
                return ChatService._call_openai(message, api_key, system_prompt, model)
            except Exception as e:
                print(f"[WARN] OpenAI failed: {str(e)}")

        hf_token = hf_token or os.environ.get('HUGGINGFACE_API_KEY')
        if hf_token:
            try:
                # Passa o system_prompt para a função de chamada
                return ChatService._call_huggingface(message, hf_token, system_prompt, hf_model)
            except Exception as e:
                print(f"[WARN] HuggingFace failed: {str(e)}")

        raise BadRequestException(
            "Nenhuma API key configurada. "
            "Configure GROQ_API_KEY (grátis), OPENAI_API_KEY ou HUGGINGFACE_API_KEY."
        )

    # ------------------ Métodos de Chamada (Alterados) ------------------

    @staticmethod
    def _call_groq(message: str, api_key: str, system_prompt: str) -> str:
        response = requests.post(
            ChatService.GROQ_API_URL,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    # Usa o system_prompt dinâmico
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        # ... (tratamento de erros Groq) ...
        if response.status_code == 401:
            raise UnauthorizedException("Groq API key inválida")
        if response.status_code == 429:
            raise RateLimitException("Rate limit do Groq atingido")
        if response.status_code != 200:
            raise Exception(f"Groq error: {response.status_code}")

        return response.json()['choices'][0]['message']['content']

    @staticmethod
    def _call_openai(message: str, api_key: str, system_prompt: str, model: str = None) -> str:
        selected_model = model or os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

        response = requests.post(
            ChatService.OPENAI_API_URL,
            json={
                "model": selected_model,
                "messages": [
                    # Usa o system_prompt dinâmico
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        # ... (tratamento de erros OpenAI) ...
        if response.status_code == 401:
            raise UnauthorizedException("OpenAI API key inválida")
        if response.status_code == 402:
            raise PaymentRequiredException("Créditos da OpenAI esgotados")
        if response.status_code == 429:
            raise RateLimitException("Rate limit da OpenAI atingido")
        if response.status_code != 200:
            raise Exception(f"OpenAI error: {response.status_code}")

        return response.json()['choices'][0]['message']['content']

    @staticmethod
    def _call_huggingface(message: str, token: str, system_prompt: str, model: str = None) -> str:
        selected_model = model or 'gpt2'
        url = f"{ChatService.HUGGINGFACE_API_URL}/{selected_model}"

        # O HuggingFace tem um formato diferente, o prompt inteiro é injetado no 'inputs'
        full_input = f"{system_prompt}\n\nUsuário: {message}\nAssistente:"

        response = requests.post(
            url,
            json={
                # Usa o full_input dinâmico
                "inputs": full_input,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                },
                "options": {"wait_for_model": True}
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        # ... (tratamento de erros HuggingFace) ...
        if response.status_code == 401:
            raise UnauthorizedException("HuggingFace token inválido")
        if response.status_code == 429:
            raise RateLimitException("Rate limit do HuggingFace atingido")
        if response.status_code != 200:
            raise Exception(f"HuggingFace error: {response.status_code}")

        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get('generated_text', str(data))
        return str(data)

    @staticmethod
    def _mock_response(message: str) -> str:
        # Mantenha o mock original
        return (
            f"[MODO MOCK]\n\n"
            f"Sua mensagem: '{message}'\n\n"
            f"Este é um modo de teste. Para usar IA real:\n"
            f"1. Groq (grátis): https://console.groq.com\n"
            f"2. OpenAI (pago): https://platform.openai.com\n"
            f"3. HuggingFace: https://huggingface.co/settings/tokens"
        )