from flask import Blueprint, request, jsonify
from services.book_service import BookService
from exceptions.custom_exceptions import BadRequestException

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/api/search', methods=['GET'])
def search_books():
    try:
        query = request.args.get('q')
        books = BookService.search_books(query)
        return jsonify(books)
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

