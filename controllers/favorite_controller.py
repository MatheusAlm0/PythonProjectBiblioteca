from flask import Blueprint, request, jsonify
from services.favorite_service import FavoriteService
from exceptions.custom_exceptions import BadRequestException

favorite_bp = Blueprint('favorite_bp', __name__)


@favorite_bp.route('/api/users/<user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    """Adiciona um livro aos favoritos do usuário"""
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
    """Remove um livro dos favoritos do usuário"""
    try:
        result = FavoriteService.remove_favorite(user_id, book_id)
        return jsonify(result), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorite_bp.route('/api/users/<user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    """Retorna todos os livros favoritos do usuário"""
    try:
        favorites = FavoriteService.get_favorites(user_id)
        return jsonify(favorites), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorite_bp.route('/api/users/<user_id>/favorites/check/<book_id>', methods=['GET'])
def check_favorite(user_id, book_id):
    """Verifica se um livro está nos favoritos"""
    try:
        is_favorite = FavoriteService.is_favorite(user_id, book_id)
        return jsonify({"is_favorite": is_favorite}), 200
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500