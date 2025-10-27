from data.db import SessionLocal, User
from exceptions.custom_exceptions import BadRequestException
from sqlalchemy.orm.attributes import flag_modified


class FavoriteService:

    @staticmethod
    def add_favorite(user_id, book_id):
        """Adiciona um livro aos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            # Inicializa lista se for None
            if user.favorite_books is None:
                user.favorite_books = []

            # Verifica se o livro já está nos favoritos
            if book_id in user.favorite_books:
                return {
                    "message": "Livro já está nos favoritos.",
                    "favorite_books": user.favorite_books
                }

            # Adiciona o livro aos favoritos
            user.favorite_books.append(book_id)

            # Marca a coluna como modificada (necessário para JSON no PostgreSQL)
            flag_modified(user, "favorite_books")

            session.commit()

            return {
                "message": "Livro adicionado aos favoritos com sucesso!",
                "favorite_books": user.favorite_books
            }
        except BadRequestException:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao adicionar favorito: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def remove_favorite(user_id, book_id):
        """Remove um livro dos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            if user.favorite_books is None or book_id not in user.favorite_books:
                raise BadRequestException("Livro não encontrado nos favoritos.")

            # Remove o livro dos favoritos
            user.favorite_books.remove(book_id)

            # Marca a coluna como modificada
            flag_modified(user, "favorite_books")

            session.commit()

            return {
                "message": "Livro removido dos favoritos com sucesso!",
                "favorite_books": user.favorite_books
            }
        except BadRequestException:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao remover favorito: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_favorites(user_id):
        """Retorna todos os IDs dos livros favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            return {
                "user_id": str(user.id),
                "username": user.username,
                "favorite_books": user.favorite_books or [],
                "total": len(user.favorite_books or [])
            }
        finally:
            session.close()

    @staticmethod
    def is_favorite(user_id, book_id):
        """Verifica se um livro está nos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            return book_id in (user.favorite_books or [])
        finally:
            session.close()
