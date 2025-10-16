import os
from flask import Blueprint, request, jsonify
from services.chat_service import ChatService
from exceptions.custom_exceptions import BadRequestException, APIException

chat_bp = Blueprint('chat_bp', __name__)


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    # Parse inputs outside try so they are available in exception handlers
    body = request.get_json() or {}
    message = body.get('message') or body.get('prompt')

    print(f"[DEBUG CONTROLLER] Body: {body}")
    print(f"[DEBUG CONTROLLER] All Headers: {dict(request.headers)}")

    # Prefer header X-OpenAI-Key; fallback to body.api_key
    api_key = request.headers.get('X-OpenAI-Key') or body.get('api_key')

    # Groq API key (grátis!)
    groq_key = request.headers.get('X-Groq-Key') or body.get('groq_key')

    print(f"[DEBUG CONTROLLER] groq_key extracted: {groq_key}")

    if groq_key:
        os.environ['GROQ_API_KEY'] = groq_key
        print(f"[DEBUG CONTROLLER] GROQ_API_KEY set in environment")

    # Hugging Face token (optional) - APENAS se explicitamente fornecido
    # NÃO pega do Authorization header automaticamente (isso causa problemas)
    hf_token = request.headers.get('X-HF-Token') or body.get('hf_token')

    print(f"[DEBUG CONTROLLER] api_key: {bool(api_key)}")
    print(f"[DEBUG CONTROLLER] hf_token: {bool(hf_token)}")
    print(f"[DEBUG CONTROLLER] groq_key: {bool(groq_key)}")

    # REMOVIDO: não pega mais do Authorization header automaticamente
    # A API pública do HF funciona melhor SEM token

    # Allow a test/mock mode via header or environment
    use_mock_header = request.headers.get('X-Use-Mock')
    use_mock = True if str(use_mock_header).lower() == 'true' else False

    # Allow overriding the model via header or body (OpenAI model or HF model)
    model = request.headers.get('X-OpenAI-Model') or body.get('model')
    hf_model = request.headers.get('X-HF-Model') or body.get('hf_model')

    try:
        answer = ChatService.ask(message, api_key=api_key, hf_token=hf_token, use_mock=use_mock, model=model,
                                 hf_model=hf_model)
        return jsonify({"answer": answer})
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except APIException as e:
        # Return the message and the proper status code carried by the APIException
        return jsonify({"error": e.message}), getattr(e, 'status_code', 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500