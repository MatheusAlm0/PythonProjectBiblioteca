from flask import Blueprint, request, jsonify
from exceptions.custom_exceptions import BadRequestException
from data.db import SessionLocal
from services.session_manager import is_logged_in

rating_bp = Blueprint('rating_bp', __name__)


def get_rating_service():
    from services.rating_service import RatingService
    return RatingService(SessionLocal())


def check_logged_in(user_id):
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


@rating_bp.route('/api/users/<user_id>/ratings', methods=['POST'])
def adicionar_avaliacao(user_id):
    auth_error = check_logged_in(user_id)
    if auth_error:
        return auth_error

    service = get_rating_service()
    try:
        body = request.get_json() or {}

        google_books_id = body.get('google_books_id')
        estrelas = body.get('estrelas')
        comentario = body.get('comentario')

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

        return jsonify({"message": resultado['message']}), 201

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
    service = get_rating_service()
    try:
        user_id = request.args.get('user_id')

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


@rating_bp.route('/api/ratings/user/<user_id>', methods=['GET'])
def listar_avaliacoes_usuario(user_id):
    """Lista todas as avaliações de um usuário"""
    service = get_rating_service()
    try:
        auth_error = check_logged_in(user_id)
        if auth_error:
            return auth_error

        avaliacoes = service.obter_avaliacoes_usuario(user_id)

        return jsonify({
            "user_id": user_id,
            "ratings": avaliacoes,
            "total": len(avaliacoes)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>/stats', methods=['GET'])
def obter_estatisticas(google_books_id):
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
    service = get_rating_service()
    try:
        user_id = request.args.get('user_id')

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