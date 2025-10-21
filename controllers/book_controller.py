from flask import Blueprint, request, jsonify
from services.book_service import BookService
from exceptions.custom_exceptions import BadRequestException

book_bp = Blueprint('book_bp', __name__)


@book_bp.route('/api/books', methods=['POST'])
def search_books():
    try:
        body = request.get_json() or {}
        query = body.get('findBook')
        books = BookService.search_books(query)
        return jsonify(books)
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@book_bp.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        books = BookService.search_books_by_id(book_id)
        return jsonify(books)
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500