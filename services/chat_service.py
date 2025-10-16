import os
import requests
from exceptions.custom_exceptions import BadRequestException, PaymentRequiredException, UnauthorizedException, \
    RateLimitException
from services.validation_service import ValidationService


class ChatService:
    OPENAI_CHAT_COMPLETIONS = "https://api.openai.com/v1/chat/completions"
    GROQ_CHAT_COMPLETIONS = "https://api.groq.com/openai/v1/chat/completions"

    @staticmethod
    def ask(message, api_key=None, hf_token=None, use_mock=False, model=None, hf_model=None):
        # Validate input
        ValidationService.validate_chat_message(message)

        # If model explicitly requests mock/free
        if (model and str(model).lower() in ('mock', 'free', 'free-mock')) or use_mock:
            return ChatService._generate_mock_recommendation(message)

        print("[DEBUG] Starting API calls...")

        # Try Groq first (free and fast!)
        groq_key = os.environ.get('GROQ_API_KEY')
        print(f"[DEBUG] Groq key available: {bool(groq_key)}")

        if groq_key:
            try:
                result = ChatService._call_groq(message, groq_key)
                print("[DEBUG] Groq success!")
                return result
            except Exception as e:
                print(f"[DEBUG] Groq failed: {str(e)}")

        # Try OpenAI if API key is available
        api_key = api_key or os.environ.get('OPENAI_API_KEY')

        if api_key:
            try:
                return ChatService._call_openai(message, api_key, model)
            except Exception as e:
                print(f"[DEBUG] OpenAI failed: {str(e)}")

        # Try Hugging Face if token is provided
        hf_token = hf_token or os.environ.get('HUGGINGFACE_API_KEY')

        if hf_token:
            try:
                return ChatService._call_huggingface(message, hf_token, hf_model)
            except Exception as e:
                print(f"[DEBUG] HuggingFace failed: {str(e)}")

        # No API available
        raise BadRequestException(
            "❌ Nenhuma API de IA disponível.\n\n"
            "Para usar IA de verdade, escolha uma opção:\n\n"
            "1️⃣ Groq (GRÁTIS, rápido) ⭐ RECOMENDADO:\n"
            "   - Crie conta: https://console.groq.com\n"
            "   - Gere API key grátis\n"
            "   - Adicione no header 'X-Groq-Key'\n\n"
            "2️⃣ OpenAI (pago, ~$0.002/requisição):\n"
            "   - Crie conta: https://platform.openai.com\n"
            "   - Gere API key e adicione no header 'X-OpenAI-Key'\n\n"
            "3️⃣ Hugging Face (grátis, mais lento):\n"
            "   - Gere token 'Read': https://huggingface.co/settings/tokens\n"
            "   - Adicione no header 'X-HF-Token'\n\n"
            "4️⃣ Modo Mock (sem IA):\n"
            "   - Adicione no body: {'model': 'mock'}"
        )

    @staticmethod
    def _call_groq(message: str, api_key: str):
        """Chama API do Groq (GRÁTIS e RÁPIDO)"""
        print(f"[DEBUG] Calling Groq API...")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um bibliotecário experiente. Recomende livros em português, com título, autor, número aproximado de páginas e motivo da recomendação. Seja detalhado e útil."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(
            ChatService.GROQ_CHAT_COMPLETIONS,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"[DEBUG] Groq response status: {response.status_code}")

        if response.status_code == 401:
            raise UnauthorizedException("Groq API key inválida. Gere uma nova em https://console.groq.com/keys")

        if response.status_code == 429:
            raise RateLimitException("Rate limit do Groq atingido. Aguarde alguns segundos.")

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")

        data = response.json()
        content = data['choices'][0]['message']['content']

        return f"🤖 [Groq AI - LLaMA 3]\n\n{content}"

    @staticmethod
    def _call_openai(message: str, api_key: str, model: str = None):
        """Chama API da OpenAI"""
        selected_model = model or os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": selected_model,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um bibliotecário experiente. Recomende livros em português, com título, autor, número aproximado de páginas e motivo da recomendação."
                },
                {
                    "role": "user",
                    "content": str(message)
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(
            ChatService.OPENAI_CHAT_COMPLETIONS,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            try:
                err = response.json()
                err_info = err.get('error', {}) if isinstance(err, dict) else {}
                err_type = err_info.get('type')
                err_message = err_info.get('message') or str(err)

                if err_type == 'insufficient_quota' or response.status_code == 402:
                    raise PaymentRequiredException(err_message)
                if response.status_code == 401:
                    raise UnauthorizedException(err_message)
                if response.status_code == 429:
                    raise RateLimitException(err_message)

                raise Exception(f"OpenAI API error: {err}")
            except ValueError:
                raise Exception(f"OpenAI API returned status {response.status_code}.")

        data = response.json()
        try:
            return data['choices'][0]['message']['content']
        except Exception:
            raise Exception("Resposta inesperada da OpenAI API.")

    @staticmethod
    def _call_huggingface(message: str, token: str, model: str = None):
        """Chama API do Hugging Face"""
        selected_model = model or 'gpt2'
        url = f"https://api-inference.huggingface.co/models/{selected_model}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        prompt = f"Recomende um livro sobre: {message}\nRecomendação:"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 401:
            raise UnauthorizedException(
                "Token do Hugging Face inválido. Gere um novo token com permissão 'Read' em https://huggingface.co/settings/tokens")

        if response.status_code == 429:
            raise RateLimitException("Rate limit atingido no Hugging Face.")

        if response.status_code != 200:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")

        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get('generated_text', str(data))
            return str(data)
        except:
            return response.text

    @staticmethod
    def _generate_mock_recommendation(message: str) -> str:
        """Gera resposta inteligente baseada em palavras-chave"""
        msg_lower = message.lower()

        # Verifica se é uma pergunta sobre livros/recomendação
        is_book_request = any(word in msg_lower for word in [
            'livro', 'book', 'ler', 'leitura', 'recomend', 'sugest', 'indic'
        ])

        # Se NÃO for sobre livros, responde de forma genérica
        if not is_book_request:
            if any(word in msg_lower for word in ['olá', 'oi', 'hello', 'hey']):
                return "Olá! 👋\n\nSou um assistente de recomendações de livros. Como posso ajudar?"

            return f"Recebi sua mensagem, mas estou operando em modo limitado.\n\n💡 Para ter uma IA completa, adicione a chave do Groq (grátis) no header 'X-Groq-Key'.\n\nPosso ajudar com recomendações de livros se preferir!"

        # Se for sobre livros, continua com o sistema de recomendações
        recommendations = []

        if any(word in msg_lower for word in ['ia', 'inteligência artificial', 'ai', 'machine learning']):
            recommendations = [
                "📚 'Inteligência Artificial' de Stuart Russell e Peter Norvig — ~1200 páginas",
                "📚 'Vida 3.0' de Max Tegmark — ~380 páginas",
                "📚 'Superinteligência' de Nick Bostrom — ~350 páginas"
            ]
        elif any(word in msg_lower for word in ['python', 'programação']):
            recommendations = [
                "📚 'Python Fluente' de Luciano Ramalho — ~800 páginas",
                "📚 'Automatize Tarefas Maçantes' de Al Sweigart — ~500 páginas"
            ]
        else:
            recommendations = [
                "📚 'Sapiens' de Yuval Harari — ~450 páginas",
                "📚 'O Gene Egoísta' de Richard Dawkins — ~360 páginas"
            ]

        result = "[MODO MOCK]\n\n"
        result += "\n".join(recommendations)
        result += "\n\n💡 Para IA real grátis, use Groq: https://console.groq.com"

        return result