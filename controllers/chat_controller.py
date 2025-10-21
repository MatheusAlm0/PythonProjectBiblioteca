import os
from flask import Blueprint, request, jsonify
from services.chat_service import ChatService
from exceptions.custom_exceptions import BadRequestException, APIException

chat_bp = Blueprint('chat_bp', __name__)


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    body = request.get_json() or {}
    message = body.get('message') or body.get('prompt')

    groq_key = request.headers.get('X-Groq-Key') or body.get('groq_key')
    if groq_key:
        os.environ['GROQ_API_KEY'] = groq_key

    api_key = request.headers.get('X-OpenAI-Key') or body.get('api_key')
    model = request.headers.get('X-OpenAI-Model') or body.get('model')

    try:
        answer = ChatService.ask(message, api_key=api_key, model=model)
        return jsonify({"answer": answer})
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except APIException as e:
        return jsonify({"error": e.message}), getattr(e, 'status_code', 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500