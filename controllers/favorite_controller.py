from flask import Blueprint, request, jsonify
from services.favorite_service import FavoriteService
from services.session_manager import is_logged_in
from exceptions.custom_exceptions import BadRequestException

favorite_bp = Blueprint('favorite_bp', __name__)


def check_logged_in(user_id):
    if not is_logged_in(user_id):
        return jsonify({
            'error': 'Você não está logado. Faça login primeiro.',
            'code': 'NOT_LOGGED_IN'
        }), 401
    return None


@favorite_bp.route('/api/users/<user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    auth_error = check_logged_in(user_id)
    if auth_error:
        return auth_error

    try:
        body = request.get_json() or {}
        book_id = body.get('book_id')

        if not book_id:
            raise BadRequestException("O campo 'book_id' é obrigatório.")

        result = FavoriteService.add_favorite(user_id, book_id)
        return jsonify(result), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorite_bp.route('/api/users/<user_id>/favorites/<book_id>', methods=['DELETE'])
def remove_favorite(user_id, book_id):
    auth_error = check_logged_in(user_id)
    if auth_error:
        return auth_error

    try:
        result = FavoriteService.remove_favorite(user_id, book_id)
        return jsonify(result), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorite_bp.route('/api/users/<user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    auth_error = check_logged_in(user_id)
    if auth_error:
        return auth_error

    try:
        favorites = FavoriteService.get_favorites(user_id)
        return jsonify(favorites), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorite_bp.route('/api/users/<user_id>/favorites/check/<book_id>', methods=['GET'])
def check_favorite(user_id, book_id):
    auth_error = check_logged_in(user_id)
    if auth_error:
        return auth_error

    try:
        is_favorite = FavoriteService.is_favorite(user_id, book_id)
        return jsonify({"is_favorite": is_favorite}), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500