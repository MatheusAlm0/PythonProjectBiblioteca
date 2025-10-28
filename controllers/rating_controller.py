from flask import Blueprint, request, jsonify
from exceptions.custom_exceptions import BadRequestException
from data.db import init_db

rating_bp = Blueprint('rating_bp', __name__)


def get_rating_service():
    """Helper para criar service com sessão do banco"""
    from services.rating_service import RatingService
    return RatingService(init_db())


@rating_bp.route('/api/ratings', methods=['POST'])
def adicionar_avaliacao():
    """
    Adiciona uma avaliação
    Body: {
        "google_books_id": "abc123",
        "usuario_id": 1,
        "estrelas": 5,
        "comentario": "Excelente!"
    }
    """
    service = get_rating_service()
    try:
        body = request.get_json() or {}
        
        google_books_id = body.get('google_books_id')
        usuario_id = body.get('usuario_id')
        estrelas = body.get('estrelas')
        comentario = body.get('comentario')
        
        # Validações
        if not google_books_id:
            raise BadRequestException("O campo 'google_books_id' é obrigatório.")
        
        if not usuario_id:
            raise BadRequestException("O campo 'usuario_id' é obrigatório.")
        
        if not estrelas or not isinstance(estrelas, int) or not (1 <= estrelas <= 5):
            raise BadRequestException("O campo 'estrelas' deve ser um número entre 1 e 5.")
        
        # Adicionar avaliação
        sucesso = service.adicionar_avaliacao(
            google_books_id=google_books_id,
            usuario_id=usuario_id,
            estrelas=estrelas,
            comentario=comentario
        )
        
        if sucesso:
            return jsonify({
                "success": True,
                "message": "Avaliação adicionada com sucesso!"
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao adicionar avaliação."
            }), 500
            
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
    """Remove uma avaliação"""
    service = get_rating_service()
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        
        if not usuario_id:
            raise BadRequestException("O parâmetro 'usuario_id' é obrigatório.")
        
        sucesso = service.remover_avaliacao(google_books_id, usuario_id)
        
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
    """Retorna estatísticas de avaliações"""
    service = get_rating_service()
    try:
        stats = service.obter_estatisticas(google_books_id)
        
        if stats is None:
            return jsonify({
                "error": "Livro não encontrado ou sem avaliações."
            }), 404
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()


@rating_bp.route('/api/ratings/<google_books_id>', methods=['GET'])
def listar_avaliacoes(google_books_id):
    """Lista avaliações de um livro"""
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
    """Verifica se usuário já avaliou"""
    service = get_rating_service()
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        
        if not usuario_id:
            raise BadRequestException("O parâmetro 'usuario_id' é obrigatório.")
        
        ja_avaliou = service.usuario_ja_avaliou(google_books_id, usuario_id)
        
        return jsonify({
            "ja_avaliou": ja_avaliou
        }), 200
        
    except BadRequestException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        service.db.close()