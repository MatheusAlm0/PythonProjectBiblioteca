from flask import Blueprint, request, jsonify
from exceptions.custom_exceptions import BadRequestException
from data.db import SessionLocal
from services.session_manager import is_logged_in

rating_bp = Blueprint('rating_bp', __name__)


def get_rating_service():
    """Helper para criar service com sessão do banco"""
    from services.rating_service import RatingService
    return RatingService(SessionLocal())


def check_logged_in(user_id):
    """Verifica se o usuário está logado (igual ao favorite_controller)"""
    if not user_id:
        return jsonify({
            'error': 'user_id é obrigatório',
            'code': 'MISSING_USER_ID'
        }), 400

    if not is_logged_in(user_id):
        return jsonify({
            'error': 'Você não está logado. Faça login primeiro.',
            'code': 'NOT_LOGGED_IN'
        }), 401

    return None


@rating_bp.route('/api/ratings', methods=['POST'])
def adicionar_avaliacao():
    """
    Adiciona uma avaliação (requer estar logado)
    Body: {
        "user_id": "32a332b3-5a60-40e8-8b8c-61518f9de5b0",
        "google_books_id": "n3vng7gyGCYC",
        "estrelas": 5,
        "comentario": "Excelente!"
    }
    """
    service = get_rating_service()
    try:
        body = request.get_json() or {}

        user_id = body.get('user_id')
        google_books_id = body.get('google_books_id')
        estrelas = body.get('estrelas')
        comentario = body.get('comentario')

        # Verificar se está logado
        auth_error = check_logged_in(user_id)
        if auth_error:
            return auth_error

        # Validações
        if not google_books_id:
            raise BadRequestException("O campo 'google_books_id' é obrigatório.")

        if not estrelas or not isinstance(estrelas, int) or not (1 <= estrelas <= 5):
            raise BadRequestException("O campo 'estrelas' deve ser um número entre 1 e 5.")

        # Adicionar avaliação
        resultado = service.adicionar_avaliacao(
            google_books_id=google_books_id,
            usuario_id=user_id,
            estrelas=estrelas,
            comentario=comentario
        )

        return jsonify({
            "success": True,
            "message": resultado['message']
        }), 201

    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>', methods=['DELETE'])
def remover_avaliacao(google_books_id):
    """
    Remove uma avaliação (requer estar logado)
    Query param: user_id
    """
    service = get_rating_service()
    try:
        user_id = request.args.get('user_id')

        # Verificar se está logado
        auth_error = check_logged_in(user_id)
        if auth_error:
            return auth_error

        sucesso = service.remover_avaliacao(google_books_id, user_id)

        if sucesso:
            return jsonify({
                "success": True,
                "message": "Avaliação removida com sucesso!"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Avaliação não encontrada."
            }), 404

    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>/stats', methods=['GET'])
def obter_estatisticas(google_books_id):
    """Retorna estatísticas de avaliações (não requer login)"""
    service = get_rating_service()
    try:
        stats = service.obter_estatisticas(google_books_id)

        if stats is None:
            return jsonify({
                "error": "Livro sem avaliações."
            }), 404

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>', methods=['GET'])
def listar_avaliacoes(google_books_id):
    """Lista avaliações de um livro (não requer login)"""
    service = get_rating_service()
    try:
        limite = request.args.get('limite', 10, type=int)

        avaliacoes = service.obter_avaliacoes(google_books_id, limite)

        return jsonify({
            "google_books_id": google_books_id,
            "avaliacoes": avaliacoes,
            "total": len(avaliacoes)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>/check', methods=['GET'])
def verificar_avaliacao(google_books_id):
    """
    Verifica se usuário já avaliou (requer estar logado)
    Query param: user_id
    """
    service = get_rating_service()
    try:
        user_id = request.args.get('user_id')

        # Verificar se está logado
        auth_error = check_logged_in(user_id)
        if auth_error:
            return auth_error

        resultado = service.usuario_ja_avaliou(google_books_id, user_id)

        return jsonify(resultado), 200

    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()